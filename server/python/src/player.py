# coding=utf-8

from consts import *
# Для парсинга данных пользуемся struct
from bc import *

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
		self.db.close()
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
					data = ''
					break
				# Если сообщение пришло целиком, отправляемся на парсинг
				if len(data) - INT_SIZE >= commandLen:
					break
			# Иначе, ждем еще байтов
			else:
				continue
		# Иначе, если нам уже известна длина сообщения, значит мы ждали
		# недостающих кусков. Нужно проверить хватает ли байтов теперь.
		elif len(data) + len(chunk) - INT_SIZE >= commandLen:
			break
		# Иначе нам снова не хватает байтов и мы продолжаем ждать
		else:
			continue

	if data:
		# Вот тут у нас в data есть полная команда. Начнем ее парсить.
		# Если это не C_LOGIN убиваем это еретическое соединение!
		commandId = getShort(data, 4)
		if commandId != C_LOGIN:
			socket.close()
			return
		# Иначе радостно считываем логин и пароль
		## TODO: Предусмотреть ситуацию возврата из getUTF -1
		else:
			pos = 6;
			login = getUTF(data, pos)
			pos += 2 + len(login)
			password = getUTF(data, pos)
			# Окей, есть логин и пароль. Проверим существует ли такой
			# игрок и не играет ли он уже.
			cursor = db.cursor()
			# выполняем запрос
			rc = cursor.execute("SELECT id, is_playing, params FROM user WHERE login='" + login +
			"' AND password='" + password + "'")
			# Если rc (rows count) == 0, значит такой пары логин/пароль
			# в базе данных нет.
			if not rc:
				db.close()
				socket.close()
				return
			# Достаем данные
			data = cursor.fetchall()[0]
			# Если кто-то уже играет под этим логином, уходим
			if data[1] == 1:
				db.close()
				socket.close()
				return
			# А если нет, отмечаем что данный логин уже занят
			cursor.execute("UPDATE user SET is_playing=1 WHERE id=" + str(data[0]))
			db.commit()
			cursor.close()
			# Создаем объект Player и передаем ему данные
			player = Player(data[0], login, data[2], socket, db)
			# Запускаем обработку данных игроком
			player.run()
			# После отключения клиента, которое произойдет в функции
			# player.run, закрываем сокет и завершаем поток
			# Собственно для этого ничего писать и не нужно

	socket.close()
