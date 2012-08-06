# coding=utf-8

from consts import *
# Для парсинга данных пользуемся struct
from bc import *
from struct import *
import threading


# Поиграемся с MySQL
import MySQLdb
# Поиграемся с JSON
import json
# Регулярные выражения
import re
# Импортируем пользовательские исключения
from userexc import UserExc

# Список всех игроков
players = []
# Мьютекс для общения с этим списком
playersLock = threading.Lock()

# ======================================================================
#
#  Класс обеспечивающий общение с клиентом.
#
# ======================================================================
class Player:
	def __init__(self, id, name, params, socket, db, bids):
		self.id = id
		self.name = name
		self.params = json.loads(params)
		self.socket = socket
		self.db = db
		self.cursor = db.cursor()
		self.bids = bids
		self.addSelfInPlayers()
		self.initBackpack()

	# ==================================================================
	# Две основные функции run и parse
	# ==================================================================
	# Функция запускает цикл в ожидании команд от клиента.
	# После прихода очередной команды запускает parse.
	def run(self):
		print 'Player "' + self.name + '" now run.'
		# Отправляем S_LOGIN_SUCCESS
		self.sLoginSuccess()
		# Отправляем параметры персонажа
		self.sFullParams()
		# Отправляем параметры магазина
		self.sShopItems()
		# Начинаем парсить данные приходящие от клиента
		data = ''
		commandLen = 0
		while True:
			chunk = self.socket.recv(1024)
			if not chunk:
				break
			data += chunk
			if not commandLen:
				if len(chunk) >= INT_SIZE:
					commandLen = getInt(chunk, 0)
					if commandLen <= 0:
						break
					if len(data) - INT_SIZE >= commandLen:
						try:
							ob = self.parse(data)
						except UserExc:
							break
						data = data[ob:]
				else:
					continue
			elif len(data) - INT_SIZE >= commandLen:
				try:
					ob = self.parse(data)
				except UserExc:
					break
				data = data[ob:]
			else:
				continue
		# Уходя, обновляем is_playing в базе и закрываем с ней соединение
		self.reduceParams()
		self.cursor.execute("UPDATE user SET is_playing=0," +
		" params=%s WHERE id=%s", (json.dumps(self.params), self.id))
		self.db.commit()
		self.cursor.close()
		# Не забываем удалиться из списка игроков
		self.deleteSelfFromPlayers()
		print 'Player "' + self.name + '" is gone.'
	
	# Функция возвращает количество обработанных байт
	# Ну и да, еще она вызывает функции-обработчики команд
	def parse(self, data):
		totalBytes = len(data)
		currentBytes = totalBytes
		operatedBytes = 0
		# До тех пор пока можем считать длину очередной команды...
		while currentBytes >= INT_SIZE:
			# Читаем длину команды
			comSize = getInt(data, operatedBytes)
			# Гоним в шею шутников
			if comSize <= 0:
				raise UserExc()
			operatedBytes += INT_SIZE
			# Если оставшегося куска сообщения хватает, чтобы запустить
			# его на парсинг, запускаем
			if totalBytes - operatedBytes >= comSize:
				# Читаем id команды
				comId = getShort(data, operatedBytes)
				operatedBytes += SHORT_SIZE
				# Вызываем соответствующую функцию. Все функции-обработчики
				# должны также возвращать количество обработанных ими байт.
				if comId == C_ITEM_INFO:
					operatedBytes += self.cItemInfo(data[operatedBytes:])
				elif comId == C_WEAR_ITEM:
					operatedBytes += self.cWearItem(data[operatedBytes:])
				elif comId == C_DROP_ITEM:
					operatedBytes += self.cDropItem(data[operatedBytes:])
				elif comId == C_SELL_ITEM:
					operatedBytes += self.cSellItem(data[operatedBytes:])
				elif comId == C_BUY_ITEM:
					operatedBytes += self.cBuyItem(data[operatedBytes:])
				elif comId == C_ADD_STAT:
					operatedBytes += self.cAddStat(data[operatedBytes:])
				# После обработки одной команды смотрим, есть ли еще
				# что обработать.
				# Если мы обработали все байты, переданные нам, возвращаем
				# их полное количество
				if operatedBytes == totalBytes:
					return operatedBytes
				# В противном случае мы отбрасываем обработанную часть
				# и делаем попытку обраборать оставшийся кусок
				else:
					currentBytes -= operatedBytes
			# Иначе мы должны сделать вид, что очередную команду мы
			# и не пытались обработать, и вообще тут не при чем.
			else:
				return operatedBytes - INT_SIZE
	
	# ==================================================================
	# Функции отправки команд клиенту
	# ==================================================================
	def sLoginSuccess(self):
		self.socket.sendall(pack('<ih', 2, S_LOGIN_SUCCESS))

	# Функция отправляет клиенту уже развернутые параметры персонажа.
	# В связи с этим потребность в команде S_ITEM_INFO может отпасть.
	def sFullParams(self):
		nameLen = len(self.name)
		paramsJSON = json.dumps(self.params)
		paramsLen = len(paramsJSON)
		comSize = SHORT_SIZE * 3 + INT_SIZE + nameLen + paramsLen
		self.socket.sendall(pack('<ihih' + str(nameLen) + 'sh' + str(paramsLen) + 's',
			comSize, S_FULL_PARAMS, self.id, nameLen, self.name, paramsLen, paramsJSON))

	# Функция отправляет клиенту всю таблицу items в json, чтобы у него
	# была информация о всех возможных предметах, которую он мог бы
	# просмотреть в магазине. Отправка этой команды еще раз ставит под
	# сомнение целесообразность команды S_ITEM_INFO.
	def sShopItems(self):
		self.cursor.execute("SELECT * FROM items")
		data = self.cursor.fetchall()
		items = {}
		for pair in data:
			items[str(pair[0])] = pair[1]
		items = json.dumps(items)
		itemsLen = len(items)
		comSize = SHORT_SIZE * 2 + itemsLen
		self.socket.sendall(pack('<ihh' + str(itemsLen) + 's',
			comSize, S_SHOP_ITEMS, itemsLen, items))

	# Функция сообщает игроку сколько у него денег.
	def sClientMoney(self):
		self.socket.sendall(pack('<ihi', 3, S_CLIENT_MONEY, self.params["money"]))

	# Функция извещает игрока о добавлении в рюкзак предмета с указанным
	# id, в указанном количестве.
	def sAddItem(self, id, count):
		self.socket.sendall(pack('<ihhb', 5, S_ADD_ITEM, id, count))

	# ==================================================================
	# Функции-обработчики команд клиента
	# ==================================================================
	# Функция возвращает клиенту параметры предмета с запрошенным id.
	# Если в базе нет предмета с таким id, сервер никак не отвечает
	# на данный запрос.
	def cItemInfo(self, data):
		id = getShort(data, 0)
		if self.cursor.execute("SELECT params FROM items WHERE id=%s", (id,)) == 1:
			params = unicode(self.cursor.fetchone()[0])
			paramsLen = len(params.encode('utf-8'))
			comSize = SHORT_SIZE * 3 + paramsLen
			self.socket.sendall(pack('<ihhh' + str(paramsLen) + 's',
				comSize, S_ITEM_INFO, id, paramsLen, params.encode('utf-8')))
		return SHORT_SIZE

	# Функция обрабатывает запрос клиента на одевание / снятие предмета.
	# Если предмета с запрошенным id нет в рюкзаке, сервер игнорирует
	# запрос.
	def cWearItem(self, data):
		id = str(getShort(data, 0))
		wear = getBool(data, SHORT_SIZE)
		place = getChar(data, SHORT_SIZE + BOOL_SIZE)
		if id in self.params["backpack"]:
			weared = self.params["backpack"][id]["weared"]
			count = self.params["backpack"][id]["count"]
			if wear:
				if weared < count:
					places = [1, 2, 3, 4]
					if place == PLACE_ARMOUR:
						self.params["armour"] = self.params["backpack"][id]
					elif place == PLACE_PANTS:
						self.params["pants"] = self.params["backpack"][id]
					elif place == PLACE_HAND_WEAPON:
						self.params["handWeapon"] = self.params["backpack"][id]
					elif place == PLACE_BELT_WEAPON:
						self.params["beltWeapon"] = self.params["backpack"][id]
					if place in places:
						self.params["backpack"][id]["weared"] += 1
					self.checkItemsProps()
			else:
				if weared > 0:
					places = [1, 2, 3, 4]
					if place == PLACE_ARMOUR:
						self.params["armour"] = 0
					elif place == PLACE_PANTS:
						self.params["pants"] = 0
					elif place == PLACE_HAND_WEAPON:
						self.params["handWeapon"] = 0
					elif place == PLACE_BELT_WEAPON:
						self.params["beltWeapon"] = 0
					if place in places:
						self.params["backpack"][id]["weared"] -= 1
					self.checkItemsProps()
		return SHORT_SIZE + BOOL_SIZE + CHAR_SIZE

	# Функция выполняет запрос клиента на выбрасывание предмета из
	# рюкзака. Если предмета с запрошенным id нет в рюкзаке, сервер
	# игнорирует запрос. Если предмет был одет, соответствующая ячейка
	# инвентаря освобождается.
	def cDropItem(self, data):
		id = str(getShort(data, 0))
		place = getChar(data, SHORT_SIZE)
		if id in self.params["backpack"]:
			weared = self.params["backpack"][id]["weared"]
			count = self.params["backpack"][id]["count"]
			if weared == count:
				self.params["backpack"][id]["weared"] -= 1
				if not place:
					self.removeWearedItem(int(id))
			self.params["backpack"][id]["count"] -= 1
			if self.params["backpack"][id]["count"] == 0:
				del self.params["backpack"][id]
			if place == PLACE_ARMOUR:
				self.params["armour"] = 0
			elif place == PLACE_PANTS:
				self.params["pants"] = 0
			elif place == PLACE_HAND_WEAPON:
				self.params["handWeapon"] = 0
			elif place == PLACE_BELT_WEAPON:
				self.params["beltWeapon"] = 0
			if place:
				self.checkItemsProps()
		return SHORT_SIZE + CHAR_SIZE

	# Функция выполняет запрос клиента на продажу предмета.
	# Если предмета с запрошенным id нет в рюкзаке, сервер игнорирует
	# запрос.
	def cSellItem(self, data):
		id = str(getShort(data, 0))
		if id in self.params["backpack"]:
			info = self.params["backpack"][id]
			cost = info["cost"]			
			weared = info["weared"]
			count = info["count"]
			if weared == count:
				info["weared"] -= 1
				self.removeWearedItem(int(id))
				self.checkItemsProps()
			info["count"] -= 1
			if info["count"] == 0:
				del self.params["backpack"][id]
			self.params["money"] += cost
			self.sClientMoney()
		return SHORT_SIZE

	# Функция выполняет запрос клиента на покупку предмета.
	# Если предмета с запрошенным id нет в базе, сервер игнорирует
	# запрос. Если у игрока не хватает денег, запрос также игнорируется.
	def cBuyItem(self, data):
		id = str(getShort(data, 0))
		if self.cursor.execute("SELECT params FROM items WHERE id=%s", (id,)) == 1:
			params = json.loads(self.cursor.fetchone()[0])
			if self.params["money"] >= params["cost"]:
				params["count"] = 1
				params["weared"] = 0
				self.addItem(params)
				self.params["money"] -= params["cost"]
				self.sClientMoney()
				self.sAddItem(int(id), 1)
		return SHORT_SIZE

	# Функция выполняет запрос клиента на увеличение одного из базовых
	# статов на единицу
	def cAddStat(self, data):
		stat = getChar(data, 0)
		if stat > 0 and stat < 5:
			names = ["strength", "dexterity", "intellect", "health"]
			s = names[stat - 1]
			cost = 0
			if stat == 1 or stat == 4:
				cost = 10
			else:
				cost = 20
			if self.params["unusedOP"] >= cost:
				self.params["unusedOP"] -= cost
				self.params["usedOP"] += cost
				self.params[s] += 1
				self.recalculateParams()
		return CHAR_SIZE

	# ==================================================================
	# Прочие функции
	# ==================================================================
	# Функция инициализации рюкзака. Функция разворачивает запись
	# рюкзака, извлеченную из базы. То же происходит с ячейками
	# инвентаря.
	def initBackpack(self):
		for id in self.params["backpack"]:
			count = self.params["backpack"][id]
			self.cursor.execute("SELECT params FROM items WHERE id=%s", (id,))
			params = json.loads(self.cursor.fetchone()[0])
			params["count"] = count
			params["weared"] = 0
			self.params["backpack"][id] = params
		a = ["armour", "pants", "beltWeapon", "handWeapon"]
		for n in a:
			if self.params[n] == 0:
				continue
			params = self.params["backpack"][str(self.params[n])]
			params["weared"] += 1
			self.params[n] = params
		self.checkItemsProps()

	# Функция удаляет из ячейки инвентаря персонажа первый попавшийся
	# предмет, id которого совпадает с запрашиваемым id. Порядок
	# удаления указан в списке places.
	def removeWearedItem(self, id):
		places = ["armour", "pants", "handWeapon", "beltWeapon"]
		for p in places:
			if self.params[p] and self.params[p]["id"] == id:
				self.params[p] = 0
				break

	# Подготовка параметров персонажа перед записью в базу. Чтобы не
	# хранить в базе развернутый backpack, он сворачивается до вида
	# {"id":count, "id":count, ... }. Развернутые ячейки инвентаря
	# заменяются на id предмета, лежащих в них.
	def reduceParams(self):
		for id in self.params["backpack"]:
			self.params["backpack"][id] = self.params["backpack"][id]["count"]
		places = ["armour", "pants", "beltWeapon", "handWeapon"]
		for p in places:
			if self.params[p]:
				self.params[p] = self.params[p]["id"]

	# Функция добавляет в рюкзак предмет. Если в рюкзаке уже имеются
	# предметы с таким id, то их количество увеличивается на единицу.
	# Иначе в рюкзаке создается новая запись. Параметр item суть
	# объект хранимый в json в таблице items, с добавлением свойств
	# count и weared.
	def addItem(self, item):
		id = str(item["id"])
		if id in self.params["backpack"]:
			self.params["backpack"][id]["count"] += 1
		else:
			self.params["backpack"][id] = item

	# Функция пересчитывает сопротивляемость игрока исходя из предметов,
	# одетых в ячейках "armour" и "pants".
	def checkItemsProps(self):
		self.params["resistance"] = 0
		places = ["armour", "pants"]
		for p in places:
			if self.params[p]:
				self.params["resistance"] += self.params[p]["resistance"]

	# Функция пересчета вторичных параметров игрока на основе первичных
	def recalculateParams(self):
		strength = self.params["strength"]
		dexterity = self.params["dexterity"]
		intellect = self.params["intellect"]
		health = self.params["health"]
		speed = (dexterity + health) / 4.0
		self.params["speed"] = speed
		self.params["hitPoints"] = health
		self.params["deviation"] = int(speed) + 3
		self.params["maxLoad"] = int((strength * strength) / 5.0)
		self.params["actPoints"] = int(speed)

	# Функция ищет свободное место в списке и возвращает индекс этого
	# места. Свободное место - занятое None.
	def findEmptyPlace(self, places):
		id = 0
		for place in places:
			if not place:
				break
			else:
				id += 1
		return id

	# Функция добавления себя в список игроков
	def addSelfInPlayers(self):
		playersLock.acquire()
		place = self.findEmptyPlace(players)
		if place == len(players):
			players.append(self)
		else:
			players[place] = self
		self.placeInPlayers = place
		playersLock.release()

	# Функция удаления себя из списка игроков
	def deleteSelfFromPlayers(self):
		playersLock.acquire()
		players[self.placeInPlayers] = None
		playersLock.release()

# ======================================================================
#
#  Функции, с которых начинается выполнение треда.
#
# ======================================================================
# Функция принимающая сокет и ожидающая от клиента команды C_LOGIN
# Фактически эта функция запускается в отдельном потоке и далее,
# если клиент прислал верную пару логин/пароль, создается объект
# Player, который и обрабатывает дальнейшие команды, поступающие
# от клиента.
def run (socket, bids):
	# Вот к нам подключился пользователь.
	# Пока будем ждать от него только команды C_LOGIN, так как если бы
	# он уже существовал в базе данных.
	# Подключаемся к базе данных
	db = MySQLdb.connect(host="localhost", user="root", passwd="1", db="troll", charset='utf8')
	# Начинаем ожидать байты от клиента
	data = ''
	commandLen = 0
	while True:
		# Получаем кусок сообщения
		chunk = socket.recv(128)
		# Если произошла ошибка, уходим
		if not chunk:
			break
		# Сохраним пришедший кусок сообщения
		data += chunk
		# Если нам еще не известна длина сообщения, пытаемся прочитать ее
		if not commandLen:
			# Смотрим есть ли хотя бы 4 байта для прочтения длины сообщения
			if len(chunk) >= INT_SIZE:
				# Читаем длину сообщения
				commandLen = getInt(chunk, 0)
				# Если какой-то шутник прислал '\x00\x00\x00\x00', уходим
				if commandLen <= 0:
					socket.close()
					return
				# Если сообщение пришло целиком, отправляемся на парсинг
				if len(data) - INT_SIZE >= commandLen:
					try:
						result = parse(data, socket, db, bids)
					except UserExc:
						break
			# Иначе, ждем еще байтов
			else:
				continue
		# Иначе, если нам уже известна длина сообщения, значит мы ждали
		# недостающих кусков. Нужно проверить хватает ли байтов теперь.
		elif len(data) - INT_SIZE >= commandLen:
			try:
				result = parse(data, socket, db, bids)
			except UserExc:
				break
		# Иначе нам снова не хватает байтов и мы продолжаем ждать
		else:
			continue

	db.close()
	socket.close()

# Какой-никакой, а parse
def parse(data, socket, db, bids):
	# Читаем id команды
	comId = getShort(data, 4)
	if comId == C_LOGIN:
		pos = 6
		login = getUTF(data, pos)
		utfLogin = login.decode('utf-8')
		if len(utfLogin) > 16:
			raise UserExc()
		pos += 2 + len(login)
		password = getUTF(data, pos)
		utfPassword = password.decode('utf-8')
		if len(utfPassword) != 32:
			raise UserExc()
		# Окей, есть логин и пароль. Проверим существует ли такой
		# игрок и не играет ли он уже.
		cursor = db.cursor()
		# выполняем запрос
		rc = cursor.execute("SELECT id, is_playing, params FROM user" +
		" WHERE login=%s AND password=%s", (login, password))
		# Если rc (rows count) == 0, значит такой пары логин/пароль
		# в базе данных нет.
		if not rc:
			socket.sendall(pack('<ihb', 3, S_LOGIN_FAILURE, 1))
			return
		# Достаем данные
		data = cursor.fetchall()[0]
		# Если кто-то уже играет под этим логином, уходим
		if data[1] == 1:
			socket.sendall(pack('<ihb', 3, S_LOGIN_FAILURE, 2))
			return
		# А если нет, отмечаем что данный логин уже занят
		cursor.execute("UPDATE user SET is_playing=1 WHERE id=%s", (data[0],))
		db.commit()
		cursor.close()
		# Создаем объект Player и передаем ему данные
		player = Player(data[0], login, data[2], socket, db, bids)
		# Запускаем обработку данных игроком
		player.run()
		del player
		raise UserExc()
	elif comId == C_REGISTER:
		pos = 6
		login = getUTF(data, pos)
		utfLogin = login.decode('utf-8')
		if len(utfLogin) > 16:
			raise UserExc()
		# Проверяем свободен ли логин
		cursor = db.cursor()
		cursor.execute("SELECT id FROM user WHERE login=%s", (login,))
		if cursor.rowcount > 0:
			cursor.close()
			socket.sendall(pack('<ihb', 3, S_REGISTER_FAILURE, 1))
			return
		cursor.close()
		# Проверим логин регуляркой
		# Черная магия!
		res = re.findall(u'[a-zA-Zа-яА-ЯЁё]+[a-zA-Zа-яА-Я0-9Ёё]*', login, re.U)
		if res == None or (len(res) > 0 and len(login) != len(res[0])):
			socket.sendall(pack('<ihb', 3, S_REGISTER_FAILURE, 2))
			return
		# Конец черной магии
		pos += 2 + len(login)
		password = getUTF(data, pos)
		utfPassword = password.decode('utf-8')
		if len(utfPassword) != 32:
			raise UserExc()
		pos += 2 + len(password)
		# Вычитываем статы персонажа
		strength = getChar(data, pos)
		pos += 1
		dexterity = getChar(data, pos)
		pos += 1
		intellect = getChar(data, pos)
		pos += 1
		health = getChar(data, pos)
		# Проверяем присланные данные
		if strength < 10 or dexterity < 10 or intellect < 10 or health < 10:
			raise UserExc()
		usedOP = (strength - 10) * 10
		usedOP += (dexterity - 10) * 20
		usedOP += (intellect - 10) * 20
		usedOP += (health - 10) * 10
		if usedOP > 50:
			raise UserExc()
		speed = (dexterity + health) / 4.0
		params = {
			"strength":strength,
			"dexterity":dexterity,
			"intellect":intellect,
			"health":health,
			"usedOP":usedOP,
			"unusedOP":50 - usedOP,
			"speed":speed,
			"hitPoints":health,
			"deviation":int(speed) + 3,
			"maxLoad":int((strength * strength) / 5.0),
			"energy":75,
			"handWeapon":0,
			"beltWeapon":0,
			"armour":0,
			"pants":0,
			"money":123,
			"actPoints":int(speed),
			"resistance":0,
			"perks":{},
			"backpack":{}
		}
		# Создаем запись в базе данных
		cursor = db.cursor()
		cursor.execute("INSERT INTO user (id, login, password, is_playing, params)" +
			"VALUES (NULL, %s, %s, '1', %s)", (login, password, json.dumps(params)))
		db.commit()
		# Вытаскиваем id игрока
		cursor.execute("SELECT id FROM user WHERE login='" + login + "'")
		data = cursor.fetchall()[0]
		cursor.close()
		# Отсылаем сообщение об успешной авторизации
		socket.sendall(pack('<ih', 2, S_REGISTER_SUCCESS))
		# Создаем объект Player и передаем ему данные
		player = Player(data[0], login, json.dumps(params), socket, db, bids)
		# Запускаем обработку данных игроком
		player.run()
		del player
		raise UserExc()
	else:
		return 0
