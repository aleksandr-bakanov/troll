# coding=utf-8
from consts import *
from random import shuffle
from struct import pack

# ======================================================================
#
# Класс ячейки поля боя
#
# ======================================================================
class Cell:
	def __init__(self, type, x, y):
		self.type = type
		self.x = x
		self.y = y

# ======================================================================
#
# Класс контролирующий бой
#
# ======================================================================
class FightController:
	def __init__(self, players):
		self.players = players
		for p in players:
			if p:
				p.fightController = self
		# Создаем карту
		self.map = self.createMap()
		# Расставляем игроков
		# Пока (и впредь?) будем расставлять игроков
		# так, чтобы в первый ход не пришлось встраивать в порядок
		# ходов мобов.
		self.players[0].fInfo["x"] = 0
		self.players[0].fInfo["y"] = 0
		self.players[0].fInfo["floor"] = 0
		self.knownArea = self.getKnownArea()
		self.moveOrder = self.createMoveOrder()
		self.sendStartInfo()
		# Отправляем известную территорию
		area = self.knownArea[:]
		area[0].insert(0, 0)
		self.sendAreaOpen(area)

	def sendStartInfo(self):
		comSize = 0
		data = pack('<hb', S_START_FIGHT_INFO, len(self.players))
		comSize += 3
		playerId = 0
		for p in self.players:
			if p:
				data += pack('<bbhh', playerId, p.fInfo["floor"], p.fInfo["x"], p.fInfo["y"])
				comSize += 6
			else:
				data += pack('<b', -1)
				comSize += 1
			playerId += 1
		for i in self.moveOrder:
			data += pack('<b', i)
		comSize += len(self.players) + 1
		data = pack('<i', comSize) + data
		playerId = 0
		for p in self.players:
			if p:
				p.sendData(data + pack('<b', playerId))
			playerId += 1

	# В эту функцию следует подавать уже подготовленный трехмерный массив.
	# area = [ [floor_id, cell, cell, ... ], ... ]
	def sendAreaOpen(self, area):
		comSize = 0
		data = pack('<b', len(area))
		comSize += 1
		for f in area:
			data += pack('<bh', f[0], len(f) - 1)
			comSize += 3
			for c in f:
				data += pack('<hhb', c.x, c.y, c.type)
				comSize += 5
				if c.type == CT_WALL:
					# Пока стены будут нерушимы, а потом wall_hp будем
					# доставать из cell.
					data += pack('<b', -1)
					comSize += 1
		data = pack('<i', comSize) + data
		for p in self.players:
			if p:
				p.sendData(data)

	def createMoveOrder(self):
		order = range(len(self.players))
		shuffle(order)
		return order

	# Функция отправки игрокам только что открытой ими зоны
	def sendOpenedArea(self, area):
		pass

	# Функция отправки игрокам только что открытых ими ключей
	def sendOpenedKeys(self, keys):
		pass

	def __del__(self):
		del self.players
		del self.map
		del self.knownArea

	def getKnownArea(self):
		return self.map[:]

	def createMap(self):
		map = [[]]
		i = 0
		j = 0
		while i < 3:
			map[0].append([])
			while j < 3:
				map[0][i].append(Cell(CT_FLOOR, j, i))
				j += 1
			j = 0
			i += 1
		return map

	def removePlayer(self, player):
		id = 0
		for p in self.players:
			if p == player:
				self.players[id] = None
				break
			id += 1
