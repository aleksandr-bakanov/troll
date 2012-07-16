# coding=utf-8

# Пока не знаю куда написать константы для id команд, напишу сюда
C_LOGIN = 2

# Для парсинга данных пользуемся struct
from bc import *

# Поиграемся с MySQL
import MySQLdb

class Player:
	def __init__(self, number):
		self.number = number

# Функция принимающая сокет и ожидающая от клиента команды C_LOGIN
# Фактически эта функция запускается в отдельном потоке и далее,
# если клиент прислал верную пару логин/пароль, создается объект
# Player, который и обрабатывает дальнейшие команды, поступающие
# от клиента.
def run (socket):
	# Вот к нам подключился пользователь.
	# Пока будем ждать от него только команды C_LOGIN, так как если бы
	# он уже существовал бы в базе данных.
	# Подключаемся к базе данных (не забываем указать кодировку,
	# а то в базу запишутся иероглифы)
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
			if len(chunk) >= 4:
				# Читаем длину сообщения
				commandLen = getInt(chunk, 0)
				# Если сообщение пришло целиком, отправляемся на парсинг
				if len(data) - 4 >= commandLen:
					break
			# Иначе, ждем еще байтов
			else:
				continue
		# Иначе, если нам уже известна длина сообщения, значит мы ждали
		# недостающих кусков. Нужно проверить хватает ли байтов теперь.
		elif len(data) + len(chunk) - 4 >= commandLen:
			break
		# Иначе нам снова не хватает байтов и мы продолжаем ждать
		else:
			continue

	# Вот тут у нас в data есть полная команда. Начнем ее парсить.
	# Если это не C_LOGIN убиваем это еретическое соединение!
	commandId = getShort(data, 4)
	if commandId != C_LOGIN:
		socket.close()
		return
	# Иначе радостно считываем логин и пароль
	else:
		pos = 6;
		login = getUTF(data, pos)
		pos += 2 + len(login)
		password = getUTF(data, pos)
		print 'Client!', login, password
	
	"""
	# Формируем курсор, с помощью которого можно исполнять SQL-запросы
	cursor = db.cursor()
	# Формируем запрос
	sql = "INSERT INTO user(id, login, password, params) VALUES (NULL, 'a', 'c4ca4238a0b923820dcc509a6f75849b', '{}')"
	# исполняем SQL-запрос
	cursor.execute(sql)
	# применяем изменения к базе данных
	db.commit()
	"""
	socket.close()
