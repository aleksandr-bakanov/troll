# coding=utf-8
from consts import *
from random import shuffle
from struct import pack

# ======================================================================
#
# Класс ячейки поля боя для алгоритма AStar
#
# ======================================================================
class aStarCell:
	def __init__(self, x=0, y=0, px=0, py=0, f=0, g=0, h=0):
		self.x = x
		self.y = y
		self.px = px
		self.py = py
		self.f = f
		self.g = g
		self.h = h

# ======================================================================
#
# Класс ячейки поля боя
#
# ======================================================================
class Cell:
	def __init__(self, x=0, y=0, type=CT_FLOOR, hp=-1):
		self.type = type
		self.x = x
		self.y = y
		self.hp = hp

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
		self.players[0].fInfo["x"] = 1
		self.players[0].fInfo["y"] = 1
		self.players[0].fInfo["floor"] = 0
		
		self.knownArea = self.getKnownArea()
		self.moveOrder = self.createMoveOrder()
		self.sendStartInfo()
		# Отправляем известную территорию
		area = self.knownArea[:]
		area[0].insert(0, 0)
		self.sendAreaOpen(area)

	# Отправка клиентам начальной информации о бое.
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
		data = pack('<hb', S_AREA_OPEN, len(area))
		comSize += 3
		for f in area:
			floorId = f[0]
			f = f[1:]
			
			cellsCount = 0
			for a in f:
				for b in a:
					cellsCount += 1
			data += pack('<bh', floorId, cellsCount)
			comSize += 3
			
			for line in f:
				for c in line:
					data += pack('<hhb', c.x, c.y, c.type)
					comSize += 5
					if c.type == CT_WALL:
						# Пока стены будут нерушимы, а потом wall_hp будем
						# доставать из cell.
						data += pack('<b', c.hp)
						comSize += 1
		data = pack('<i', comSize) + data
		for p in self.players:
			if p:
				p.sendData(data)

	# В moveOrder должны храниться id юнитов. Первые id (с нулевого
	# по len(self.players) - 1) отведены для игроков, остальные под
	# мобов.
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

	# Временная функция. Ее следует заменить на sendOpenedArea.
	def getKnownArea(self):
		return self.map[:]

	def createMap(self):
		map = [[]]
		sizeX = 6
		sizeY = 6
		i = 0
		j = 0
		while i < sizeX:
			map[0].append([])
			while j < sizeY:
				cell = Cell(j, i)
				if i == 0 or i == sizeY - 1 or j == 0 or j == sizeX - 1 or (j == 3 and i == 2):
					cell.type = CT_WALL
				else:
					cell.type = CT_FLOOR
				map[0][i].append(cell)
				j += 1
			j = 0
			i += 1
		return map

	def sendChatMessage(self, message):
		for p in self.players:
			if p:
				p.sChatMessage(message)

	def finishFight(self):
		for p in self.players:
			if p:
				p.fightController = None
				self.removePlayer(p)
		self.map = None
		self.knownArea = None
		self.moveOrder = None
		del self

	# Удаление игрока в случае его отключения. Надо сюда дописать
	# умершвление уходящего игрока.
	def removePlayer(self, player):
		id = 0
		for p in self.players:
			if p == player:
				self.players[id] = None
				break
			id += 1
		# Подсчитаем количество оставшихся игроков
		count = 0
		for p in self.players:
			if p:
				count += 1
		if not count:
			self.finishFight()

	# Функция принимает координаты стартовой клетки и финишной.
	# Возвращает расстояние между этими клетками, т.е. сколько очков действия
	# затратит игрок на этот переход.
	def calculateWayLength(width, height, xs, ys, xe, ye):
		# Проверка на неверные данные
		if width <= 0 or height <= 0 or ys < 0 or ys >= height or xs < 0 or xs >= width or ye < 0 or ye >= height or xe < 0 or xe >= width:
			return -1
		result = 0
		dx = abs(xs - xe)
		dy = abs(ys - ye)
		# Чет -> чет || нечет -> нечет (имеется в виду y координаты)
		if (ys % 2 == 0 and ye % 2 == 0) or (ys % 2 != 0 and ye % 2 != 0):
			if dx >= dy - 1:
				result = dx + int(dy / 2)
			else:
				result = dy
		# Чет -> нечет
		elif ys % 2 == 0 and ye % 2 != 0:
			if xe < xs:
				dx -= 1
			if dx >= dy - int(dy / 2):
				result = dy + dx - int(dy / 2)
			else:
				result = dy
		# Нечет -> чет
		elif ys % 2 != 0 and ye % 2 == 0:
			if xe < xs:
				dx += 1
			if dx <= dy - int(dy / 2):
				result = dy
			else:
				result = dy + dx - (int(dy / 2) + 1)
		return result

	def aStar(self, floorId, x, y, tox, toy, impassible):
		# Для алгоритма aStar важно только то, является ли ячейка проходимой или нет.
		# 1 - проходима, 0 - непроходима
		map = []
		for row in range(len(self.map[floorId])):
			map.append([])
			for col in range(len(self.map[floorId][row])):
				if (self.map[floorId][row][col].type == CT_FLOOR):
					map[row].append(1)
				else:
					map[row].append(0)

		# Размеры этажа
		sizeX = len(map[0])
		sizeY = len(map)
		# Add impassible cells. Дополнительные непроходимые ячейки, образованные
		# юнитами, передаются в массиве impassible. (x, y, x, y, ...)
		for i in range(len(impassible) / 2):
			map[impassible[i*2 + 1]][impassible[i*2]] = 0
		# Creates open and close lists
		open = []
		close = []
		# Add start cell to open list
		# cc = currentCell
		hf = self.calculateWayLength(sizeX, sizeY, x, y, tox, toy)
		cc = aStarCell(x, y, 0, 0, hf, 0, hf)
		open.append(cc)
		isPathFound = False
		while not isPathFound:
			minFCellIndex = self.minFCell(open);
			# cc = currentCell
			cc = open[minFCellIndex];
			close.append(cc)
			del open[minFCellIndex]
			# ac = addedCell
			ac = aStarCell()
			acIndex = 0
			# To left
			if cc.x - 1 >= 0 and map[cc.y][cc.x - 1] != 0 and self.exist(cc.x - 1, cc.y, close) < 0:
				acIndex = self.exist(cc.x - 1, cc.y, open)
				if acIndex < 0:
					ac.x = cc.x - 1
					ac.y = cc.y
					ac.px = cc.x
					ac.py = cc.y
					ac.g = cc.g + 10
					ac.h = self.calculateWayLength(sizeX, sizeY, ac.x, ac.y, tox, toy)
					ac.f = ac.g + ac.h
					open.append(ac)
				else:
					ac = open[acIndex]
					if ac.g > (cc.g + 10):
						ac.px = cc.x
						ac.py = cc.y
						ac.g = cc.g + 10
						ac.f = ac.g + ac.h
			# To right
			if cc.x + 1 < sizeX and map[cc.y][cc.x + 1] != 0 and self.exist(cc.x + 1, cc.y, close) < 0:
				acIndex = self.exist(cc.x + 1, cc.y, open)
				if acIndex < 0:
					ac.x = cc.x + 1
					ac.y = cc.y
					ac.px = cc.x
					ac.py = cc.y
					ac.g = cc.g + 10
					ac.h = self.calculateWayLength(sizeX, sizeY, ac.x, ac.y, tox, toy)
					ac.f = ac.g + ac.h
					open.append(ac)
				else:
					ac = open[acIndex]
					if ac.g > (cc.g + 10):
						ac.px = cc.x
						ac.py = cc.y
						ac.g = cc.g + 10
						ac.f = ac.g + ac.h
			# To up-left
			# Здесь нужно уточнить координату X, т.к. она зависит от координаты Y.
			newX = cc.x if cc.y % 2 else cc.x - 1
			if cc.y - 1 >= 0 and map[cc.y - 1][newX] != 0 and self.exist(newX, cc.y - 1, close) < 0:
				acIndex = self.exist(newX, cc.y - 1, open)
				if acIndex < 0:
					ac.x = newX
					ac.y = cc.y - 1
					ac.px = cc.x
					ac.py = cc.y
					ac.g = cc.g + 10
					ac.h = self.calculateWayLength(sizeX, sizeY, ac.x, ac.y, tox, toy)
					ac.f = ac.g + ac.h
					open.append(ac)
				else:
					ac = open[acIndex]
					if ac.g > (cc.g + 10):
						ac.px = cc.x
						ac.py = cc.y
						ac.g = cc.g + 10
						ac.f = ac.g + ac.h
			# To up-right
			newX = cc.x + 1 if cc.y % 2 else cc.x
			if cc.y - 1 >= 0 and map[cc.y - 1][newX] != 0 and self.exist(newX, cc.y - 1, close) < 0:
				acIndex = self.exist(newX, cc.y - 1, open)
				if acIndex < 0:
					ac.x = newX
					ac.y = cc.y - 1
					ac.px = cc.x
					ac.py = cc.y
					ac.g = cc.g + 10
					ac.h = self.calculateWayLength(sizeX, sizeY, ac.x, ac.y, tox, toy)
					ac.f = ac.g + ac.h
					open.append(ac)
				else:
					ac = open[acIndex]
					if ac.g > (cc.g + 10):
						ac.px = cc.x
						ac.py = cc.y
						ac.g = cc.g + 10
						ac.f = ac.g + ac.h
			# To down-left
			newX = cc.x if cc.y % 2 else cc.x - 1
			if cc.y + 1 < sizeY and map[cc.y + 1][newX] != 0 and self.exist(newX, cc.y + 1, close) < 0:
				acIndex = self.exist(newX, cc.y + 1, open)
				if acIndex < 0:
					ac.x = newX
					ac.y = cc.y + 1
					ac.px = cc.x
					ac.py = cc.y
					ac.g = cc.g + 10
					ac.h = self.calculateWayLength(sizeX, sizeY, ac.x, ac.y, tox, toy)
					ac.f = ac.g + ac.h
					open.append(ac)
				else:
					ac = open[acIndex]
					if ac.g > (cc.g + 10):
						ac.px = cc.x
						ac.py = cc.y
						ac.g = cc.g + 10
						ac.f = ac.g + ac.h
			# To down-right
			newX = cc.x + 1 if cc.y % 2 else cc.x
			if cc.y + 1 < sizeY and map[cc.y + 1][newX] != 0 and self.exist(newX, cc.y + 1, close) < 0:
				acIndex = self.exist(newX, cc.y + 1, open)
				if acIndex < 0:
					ac.x = newX
					ac.y = cc.y + 1
					ac.px = cc.x
					ac.py = cc.y
					ac.g = cc.g + 10
					ac.h = self.calculateWayLength(sizeX, sizeY, ac.x, ac.y, tox, toy)
					ac.f = ac.g + ac.h
					open.append(ac)
				else:
					ac = open[acIndex]
					if ac.g > (cc.g + 10):
						ac.px = cc.x
						ac.py = cc.y
						ac.g = cc.g + 10
						ac.f = ac.g + ac.h
			if self.exist(tox, toy, open) >= 0:
				isPathFound = true
			if open.size() == 0:
				break

		result = []
		if isPathFound:
			rx = tox
			ry = toy
			ind = 0
			while not (rx == x and ry == y):
				result.append(ry)
				result.append(rx)
				ind = self.exist(rx, ry, open)
				if ind >= 0:
					cc = open[ind]
				else:
					cc = close[self.exist(rx, ry, close)]
				rx = cc.px
				ry = cc.py
		return result

	# Функция проверяет существование ячейки с координатами x, y в списке v.
	def exist(x, y, v):
		for i in range(len(v)):
			if v[i].x == x and v[i].y == y:
				return i
		return -1

	def minFCell(self, v):
		vlen = len(v)
		r = 0
		curF = 100
		nextF = 0
		for i in range(vlen):
			nextF = v[i].f
			if nextF < curF:
				curF = nextF
				r = i
		return r
