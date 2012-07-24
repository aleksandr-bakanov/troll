# coding=utf-8

# bc - bytes converter. Преобразование набора байт в числа и строки
from struct import unpack
# Импортируем пользовательские исключения
from userexc import UserExc

# Функция возвращает байт с указанной позиции pos в массиве data
# return signed char
def getChar (data, pos):
	if len(data) - pos < 1:
		raise UserExc()
	return unpack('b', data[pos:pos+1])[0]

# return bool
def getBool (data, pos):
	if len(data) - pos < 1:
		raise UserExc()
	return unpack('?', data[pos:pos+1])[0]

# return short int
def getShort (data, pos):
	if len(data) - pos < 2:
		raise UserExc()
	return unpack('h', data[pos:pos+2])[0]

# return int
def getInt (data, pos):
	if len(data) - pos < 4:
		raise UserExc()
	return unpack('i', data[pos:pos+4])[0]

# return float
def getFloat (data, pos):
	if len(data) - pos < 4:
		raise UserExc()
	return unpack('f', data[pos:pos+4])[0]

# return UTF-string
def getUTF (data, pos):
	# Проверим можно ли считать длину строки
	sl = getShort(data, pos)
	if sl < 0:
		raise UserExc()
	# Проверим теперь хватает ли данных чтобы считать строку
	if len(data) - pos - 2 < sl:
		raise UserExc()
	return unpack(str(sl) + 's', data[pos+2:pos+2+sl])[0]
