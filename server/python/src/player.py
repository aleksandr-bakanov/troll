# coding=utf-8

from consts import *
# Для парсинга данных пользуемся struct
from bc import *
from struct import *


# Поиграемся с MySQL
import MySQLdb
# Поиграемся с JSON
import json
# Регулярные выражения
import re

class Player:
	def __init__(self, id, name, params, socket, db):
		self.id = id
		self.name = name
		self.params = json.loads(params)
		self.socket = socket
		self.db = db
		self.cursor = db.cursor()

	# Функция запускает цикл в ожидании команд от клиента.
	# После прихода очередной команды запускает parse.
	def run(self):
		print 'Player "' + self.name + '" now run.'
		# Отправляем S_LOGIN_SUCCESS
		self.sLoginSuccess()
		# Отправляем параметры персонажа
		self.sFullParams()
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
					if commandLen == 0:
						break
					if len(data) - INT_SIZE >= commandLen:
						ob = self.parse(data)
						data = data[ob:]
				else:
					continue
			elif len(data) + len(chunk) - INT_SIZE >= commandLen:
				ob = self.parse(data)
				data = data[ob:]
			else:
				continue
		# Уходя, обновляем is_playing в базе и закрываем с ней соединение
		self.cursor.execute("UPDATE user SET is_playing=0, params='" +
			json.dumps(self.params) + "' WHERE id=" + str(self.id))
		self.db.commit()
		self.cursor.close()
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
				else:
					pass
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
				operatedBytes -= INT_SIZE
				return operatedBytes
	
	# ==================================================================
	# Функции отправки команд клиенту
	# ==================================================================
	def sLoginSuccess(self):
		self.socket.sendall(pack('<ih', 2, S_LOGIN_SUCCESS))
	
	def sFullParams(self):
		nameLen = len(self.name)
		paramsJSON = json.dumps(self.params)
		paramsLen = len(paramsJSON)
		comSize = SHORT_SIZE * 3 + INT_SIZE + nameLen + paramsLen
		self.socket.sendall(pack('<ihih' + str(nameLen) + 'sh' + str(paramsLen) + 's',
			comSize, S_FULL_PARAMS, self.id, nameLen, self.name, paramsLen, paramsJSON))

	# ==================================================================
	# Функции-обработчики команд клиента
	# ==================================================================
	def cItemInfo(self, data):
		id = getShort(data, 0)
		if self.cursor.execute("SELECT params FROM items WHERE id=" + str(id)) == 1:
			params = str(self.cursor.fetchone()[0])
			paramsLen = len(params)
			comSize = SHORT_SIZE * 3 + paramsLen
			self.socket.sendall(pack('<ihhh' + str(paramsLen) + 's',
				comSize, S_ITEM_INFO, id, paramsLen, params))
		return SHORT_SIZE


# Функция принимающая сокет и ожидающая от клиента команды C_LOGIN
# Фактически эта функция запускается в отдельном потоке и далее,
# если клиент прислал верную пару логин/пароль, создается объект
# Player, который и обрабатывает дальнейшие команды, поступающие
# от клиента.
def run (socket):
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
				if commandLen == 0:
					socket.close()
					return
				# Если сообщение пришло целиком, отправляемся на парсинг
				if len(data) - INT_SIZE >= commandLen:
					result = parse(data, socket, db)
					print 'parse result = ', result
					if result < 0:
						break
			# Иначе, ждем еще байтов
			else:
				continue
		# Иначе, если нам уже известна длина сообщения, значит мы ждали
		# недостающих кусков. Нужно проверить хватает ли байтов теперь.
		elif len(data) + len(chunk) - INT_SIZE >= commandLen:
			result = parse(data, socket, db)
			if result < 0:
				break
		# Иначе нам снова не хватает байтов и мы продолжаем ждать
		else:
			continue

	db.close()
	socket.close()

# Какой-никакой, а parse
def parse(data, socket, db):
	# Читаем id команды
	comId = getShort(data, 4)
	if comId == C_LOGIN:
		pos = 6
		login = getUTF(data, pos)
		if login < 0:
			return -1
		utfLogin = login.decode('utf-8')
		if len(utfLogin) > 16:
			return -9
		pos += 2 + len(login)
		password = getUTF(data, pos)
		if password < 0:
			return -2
		utfPassword = password.decode('utf-8')
		if len(utfPassword) != 32:
			return -10
		# Окей, есть логин и пароль. Проверим существует ли такой
		# игрок и не играет ли он уже.
		cursor = db.cursor()
		# выполняем запрос
		rc = cursor.execute("SELECT id, is_playing, params FROM user WHERE login='" + login +
		"' AND password='" + password + "'")
		# Если rc (rows count) == 0, значит такой пары логин/пароль
		# в базе данных нет.
		if not rc:
			socket.sendall(pack('<ihb', 3, S_LOGIN_FAILURE, 1))
			return 3
		# Достаем данные
		data = cursor.fetchall()[0]
		# Если кто-то уже играет под этим логином, уходим
		if data[1] == 1:
			socket.sendall(pack('<ihb', 3, S_LOGIN_FAILURE, 2))
			return 4
		# А если нет, отмечаем что данный логин уже занят
		cursor.execute("UPDATE user SET is_playing=1 WHERE id=" + str(data[0]))
		db.commit()
		cursor.close()
		# Создаем объект Player и передаем ему данные
		player = Player(data[0], login, data[2], socket, db)
		# Запускаем обработку данных игроком
		player.run()
		return -1
	elif comId == C_REGISTER:
		## TODO: Проверить login на SQL-инъекции
		pos = 6
		login = getUTF(data, pos)
		if login < 0:
			return -3
		utfLogin = login.decode('utf-8')
		if len(utfLogin) > 16:
			return -4
		# Проверяем свободен ли логин
		cursor = db.cursor()
		cursor.execute("SELECT id FROM user WHERE login='" + login + "'")
		if cursor.rowcount > 0:
			cursor.close()
			socket.sendall(pack('<ihb', 3, S_REGISTER_FAILURE, 1))
			return 5
		cursor.close()
		# Проверим логин регуляркой
		## TODO: повнимательней отнестить к регулярному выражению
		# Черная магия!
		res = re.findall(u'[a-zA-Zа-яА-ЯЁё]+[a-zA-Zа-яА-Я0-9Ёё]*', login, re.U)
		if res == None or (len(res) > 0 and len(login) != len(res[0])):
			socket.sendall(pack('<ihb', 3, S_REGISTER_FAILURE, 2))
			return 6
		# Конец черной магии
		pos += 2 + len(login)
		password = getUTF(data, pos)
		if password < 0:
			return -5
		utfPassword = password.decode('utf-8')
		if len(utfPassword) != 32:
			return -6
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
			return -7
		usedOP = (strength - 10) * 10
		usedOP += (dexterity - 10) * 20
		usedOP += (intellect - 10) * 20
		usedOP += (health - 10) * 10
		if usedOP > 50:
			return -8
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
			"VALUES (NULL, '" + login + "', '" + password + "', '1', '" + json.dumps(params) + "')")
		db.commit()
		# Вытаскиваем id игрока
		cursor.execute("SELECT id FROM user WHERE login='" + login + "'")
		data = cursor.fetchall()[0]
		cursor.close()
		# Отсылаем сообщение об успешной авторизации
		socket.sendall(pack('<ih', 2, S_REGISTER_SUCCESS))
		# Создаем объект Player и передаем ему данные
		player = Player(data[0], login, json.dumps(params), socket, db)
		# Запускаем обработку данных игроком
		player.run()
		return -1
	else:
		return 0
