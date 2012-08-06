# coding=utf-8
# Что за чудный язык Python! Чтобы иметь возможность писать комментарии
# на русском, нужно указывать кодировку utf-8.
# Импорт из каталога требует наличия в этом каталоге файла __init__.py

# Модуль обеспечивающий многопоточность
import threading
# Импортируем функцию run, которая будет запускаться в отдельном потоке
# при каждом подключении клиента.
from src.player import run

# При старте сервера делаем всех игроков не играющими
import MySQLdb
db = MySQLdb.connect(host="localhost", user="root", passwd="1", db="troll", charset='utf8')
c = db.cursor()
c.execute("UPDATE user SET is_playing = 0 WHERE 1")
db.commit()
c.close()
db.close()

# Создаем контроллер заявок.
import src.bidsController
bids = src.bidsController.BidsController()

# Создаем сервер и слушаем подключение клиентов
import socket
HOST = ''
# Порт выбран наугад.
PORT = 15856
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(32)
while 1:
	# Ждем подключения клиента
	conn, addr = server.accept()
	# После подключения клиента создаем поток, в котором и будет
	# происходить общение с клиентом.
	t = threading.Thread(target=run, args=(conn, bids))
	t.start()
	# В C++ (POSIX thread libraries) есть еще функция pthread_detach(),
	# которая "put a running thread in the detached state", т.е. при
	# завершении работы потока (в нашем случае функции run) освобождает
	# память, занимаемую потоком. Это можно проследить (по крайней мере
	# в Linux) с помощью команды ps -FL <номер_процесса>.
	# Но в Python я пока не нашел аналога pthread_detach(), да и не
	# знаю нужен ли он.
