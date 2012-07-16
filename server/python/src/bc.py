# coding=utf-8
# bc - bytes converter. Преобразование набора байт в числа и строки
from struct import unpack

# Функция возвращает байт с указанной позиции pos в массиве data
# return signed char
def getChar (data, pos):
	return unpack('b', data[pos:pos+1])[0]

# return bool
def getBool (data, pos):
	return unpack('?', data[pos:pos+1])[0]

# return short int
def getShort (data, pos):
	return unpack('h', data[pos:pos+2])[0]

# return int
def getInt (data, pos):
	return unpack('i', data[pos:pos+4])[0]

# return float
def getChar (data, pos):
	return unpack('f', data[pos:pos+4])[0]

# return UTF-string
def getUTF (data, pos):
	sl = getShort(data, pos)
	return unpack(str(sl) + 's', data[pos+2:pos+2+sl])[0]