# coding=utf-8

from consts import *
# Для парсинга данных пользуемся struct
from bc import *
from struct import *


# Поиграемся с MySQL
import MySQLdb
# Поиграемся с JSON
import json

class Player:
	def __init__(self, id, name, params, socket, db):
		self.id = id
		self.name = name
		self.params = json.loads(params)
		self.socket = socket
		self.db = db

	# Функция запускает цикл в ожидании команд от клиента.
	# После прихода очередной команды запускает parse.
	def run(self):
		print 'Player "' + self.name + '" now run.'
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
		self.db.query("UPDATE user SET is_playing=0 WHERE id=" + str(self.id))
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
				if comId == C_LOGIN:
					pass
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
		pos += 2 + len(login)
		password = getUTF(data, pos)
		if password < 0:
			return -1
		# Окей, есть логин и пароль. Проверим существует ли такой
		# игрок и не играет ли он уже.
		cursor = db.cursor()
		# выполняем запрос
		rc = cursor.execute("SELECT id, is_playing, params FROM user WHERE login='" + login +
		"' AND password='" + password + "'")
		# Если rc (rows count) == 0, значит такой пары логин/пароль
		# в базе данных нет.
		if not rc:
			socket.sendall(pack('ihb', 3, S_WRONG_LOGIN, 1))
			return 0
		# Достаем данные
		data = cursor.fetchall()[0]
		# Если кто-то уже играет под этим логином, уходим
		if data[1] == 1:
			socket.sendall(pack('ihb', 3, S_WRONG_LOGIN, 2))
			return 0
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
			return -1
		elif len(login) > 16:
			return -1
		cursor = db.cursor()
		cursor.execute("SELECT id FROM user WHERE login='" + login + "'")
		if cursor.rowcount > 0:
			socket.sendall(pack('ihb', 3, S_REGISTER_FAILURE, 1))
			return 0
		cursor.close()
		pos += 2 + len(login)
		password = getUTF(data, pos)
		if password < 0:
			return -1
		elif len(password) != 32:
			return -1
		pos += 2 + len(password)
		strength = getChar(data, pos)
		pos += 1
		dexterity = getChar(data, pos)
		pos += 1
		intellect = getChar(data, pos)
		pos += 1
		health = getChar(data, pos)
		if strength < 10 or dexterity < 10 or intellect < 10 or health < 10:
			return -1
		usedOP = (strength - 10) * 10
		usedOP += (dexterity - 10) * 20
		usedOP += (intellect - 10) * 20
		usedOP += (health - 10) * 10
		if usedOP > 50:
			return -1
		params = {}
	else:
		return 0
