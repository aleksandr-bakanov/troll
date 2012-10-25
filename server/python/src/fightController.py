# coding=utf-8
from math import *
from consts import *
from random import *
from struct import pack
import threading

# ======================================================================
#
# Класс ячейки поля боя для алгоритма AStar
#
# ======================================================================
class aStarCell:
	# x, y - собственные координаты ячейки
	# px, py - координаты родительской ячейки
	# h - расстояни до финишной ячейки (в шагах)
	# g - расстояни от стартовой ячейки (в условных единицах)
	# f - сумма h и g.
	def __init__(self, x=0, y=0, px=0, py=0, g=0, h=0, f=0):
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
	# x, y - координаты
	# type - тип
	# hp - жизни
	# keys - список ключей, которые нужно активизировать, чтобы открыть данную ячейку,
	# если она является дверью
	# key - id ключа, хранящегося в ячейке. Активизируется при взаимодействии с ячейкой.
	# toFloor, toX, toY - id этажа и координаты ячейки в которую переместится игрок, если
	# активизирует данную ячейку.
	def __init__(self, floor=0, x=0, y=0, type=CT_FLOOR, hp=-1, keys=None, key=-1, toFloor=-1, toX=-1, toY=-1):
		self.type = type
		self.floor = floor
		self.x = x
		self.y = y
		self.hp = hp
		self.keys = keys
		self.key = key
		self.toFloor = toFloor
		self.toX = toX
		self.toY = toY

# ======================================================================
#
# Класс контролирующий бой
#
# ======================================================================
class FightController:
	def __init__(self, players):
		self.players = players
		self.playersCount = 0
		i = 0
		for p in players:
			if p:
				p.fightController = self
				p.fInfo["x"] = 1 + i
				p.fInfo["y"] = 1
				p.fInfo["floor"] = 0
				p.fInfo["id"] = i
				# Создадим ссылку на текущее оружие
				p.fInfo["curWeapon"] = p.params["handWeapon"]
				# В начале боя у всех полные жизни
				p.params["hitPoints"] = p.params["health"]
				self.playersCount += 1
				i += 1
		# Список для отдельного хранения дверей
		self.doors = []
		# Создаем карту
		self.map = self.createMap()
		self.knownArea = self.getKnownArea()
		self.moveOrder = self.createMoveOrder()
		self.sendStartInfo()
		# Отправляем известную территорию
		self.sendOpenedArea(self.knownArea)
		#self.sendOpenedKeys(self.knownArea)
		# Переменная currentUnit содержит индекс id игрока в списке moveOrder,
		# которому дозволено совершать действия в данный момент.
		self.currentUnit = -1
		# Таймер ожидания хода
		self.nextMoveTimer = None
		# Запускаем первый ход
		self.nextMove()

	def nextMove(self):
		# Проверяем не нужно ли выключить предыдущий таймер
		# (такое может требоваться, если функция nextMove была вызвана не из таймера)
		if self.nextMoveTimer and self.nextMoveTimer.is_alive():
			self.nextMoveTimer.cancel()
		# Передаем ход следующему юниту
		self.currentUnit += 1
		if self.currentUnit >= len(self.moveOrder):
			self.currentUnit = 0
		# Если все неожиданно ушли или умерли, т.е. в moveOrder никого больше не осталось, то завершаем бой
		if len(self.moveOrder) == 0:
			self.finishFight()
			return
		# TODO: Здесь нужно проверять кто следующий юнит, если человек,
		# отправлять всем команду S_YOUR_MOVE, если бот, запускать ИИ.
		
		# Сначала отправляем команду
		for p in self.players:
			if p:
				p.sYourMove(self.moveOrder[self.currentUnit], SECONDS_TO_MOVE)
				if p.fInfo["id"] == self.players[self.moveOrder[self.currentUnit]].fInfo["id"]:
					p.params["actPoints"] = int(p.params["speed"])
		# Затем запускаем таймер ожидания
		self.nextMoveTimer = threading.Timer(SECONDS_TO_MOVE + 1, self.nextMove)
		self.nextMoveTimer.start()
		
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
				mes = unicode(p.name, 'utf-8')
				mesLen = len(mes.encode('utf-8'))
				data += pack('<h' + str(mesLen) + 's', mesLen, mes.encode('utf-8'))
				comSize += mesLen + SHORT_SIZE;
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

	# В эту функцию следует подавать уже подготовленный двумерный массив.
	# area = [ [cell, cell, ... ], ... ]
	def sendOpenedArea(self, area):
		comSize = 0
		# Пишем CMD_ID и floors_count, но сначала посчитаем количество непустых этажей
		floorsCount = 0
		for floor in area:
			if len(floor):
				floorsCount += 1
		if not floorsCount:
			return
		data = pack('<hb', S_AREA_OPEN, floorsCount)
		comSize += 3
		floorId = 0
		for floor in area:
			cellsCount = len(floor)
			if cellsCount:
				data += pack('<bh', floorId, cellsCount)
				comSize += 3
				for cell in floor:
					data += pack('<hhb', cell.x, cell.y, cell.type)
					comSize += 5
					# Дополнительные параметры пола
					if cell.type == CT_FLOOR:
						data += pack('<b', cell.toFloor)
						comSize += 1
						if cell.toFloor >= 0:
							data += pack('<hh', cell.toX, cell.toY)
							comSize += 4
					# Дополнительные параметры стены
					elif cell.type == CT_WALL:
						data += pack('<bh', cell.hp, cell.key)
						comSize += 3
					# Дополнительные параметры двери
					elif cell.type == CT_DOOR:
						lockCount = len(cell.keys)
						data += pack('<h', lockCount)
						comSize += 2
						if lockCount:
							for key in cell.keys:
								data += pack('<h', key)
								comSize += 2
			floorId += 1
		data = pack('<i', comSize) + data
		for p in self.players:
			if p:
				p.sendData(data)

	# В эту функцию следует подавать уже подготовленный двумерный массив.
	# area = [ [cell, cell, ... ], ... ]
	def sendOpenedKeys(self, area):
		# Так как пока в эту фукцию будет поступать тот же массив ячеек, что и в функцию sendOpenedArea,
		# будем обрабатывать (урезать) его прямо здесь. Точнее будем брать только те ячейки, в которых
		# действительно есть ключи.
		comSize = 0
		# Пишем CMD_ID и floors_count, но сначала посчитаем количество непустых этажей
		floorsCount = 0
		for floor in area:
			if len(floor):
				keysCount = 0
				for cell in floor:
					if cell.key >= 0:
						keysCount += 1
				if keysCount:
					floorsCount += 1
		if not floorsCount:
			return
		data = pack('<hb', S_KEYS_OPEN, floorsCount)
		comSize += 3
		floorId = 0
		for floor in area:
			# Вот здесь нужно посчитать сколько ячеек на самом деле наделено ключами
			keysCount = 0
			for cell in floor:
				if cell.key >= 0:
					keysCount += 1
			#print "keysCount =",keysCount
			if keysCount:
				data += pack('<bh', floorId, keysCount)
				comSize += 3
				for cell in floor:
					# И здесь не забыть проверить
					#print "  cell.key =",cell.key
					if cell.key >= 0:
						data += pack('<hhh', cell.key, cell.x, cell.y)
						comSize += 6
			floorId += 1
		data = pack('<i', comSize) + data
		for p in self.players:
			if p:
				p.sendData(data)

	# В moveOrder должны храниться id юнитов. Первые id (с нулевого
	# по len(self.players) - 1) отведены для игроков, остальные под
	# мобов.
	def createMoveOrder(self):
		order = range(len(self.players))
		#print "was",self.players[order[0]].params["speed"],self.players[order[1]].params["speed"]
		# Преждевременная оптимизация - корень всех зол. (Дональд Кнут)
		# Сортируем игроков по их скорости
		k = 0
		while k < self.playersCount - 1:
			i = k + 1
			curSpeed = self.players[order[k]].params["speed"]
			# j - индекс максимальной скорости в текущем подмассиве
			j = k
			while i < self.playersCount:
				#print "compare ",curSpeed,self.players[order[i]].params["speed"]
				if curSpeed < self.players[order[i]].params["speed"]:
					j = i	
				i += 1
			# Если j != k, то необходимо переставить их местами
			if j != k:
				tmp = order[k]
				order[k] = order[j]
				order[j] = tmp
			k += 1
		#print "now",self.players[order[0]].params["speed"],self.players[order[1]].params["speed"]
		return order

	def __del__(self):
		del self.players
		del self.map
		del self.knownArea
		del self.doors
		print "~FightController"

	# Функция определят какое поле известно игрокам в данный момент.
	def getKnownArea(self):
		result = []
		# Создаем этажи
		for floor in self.map:
			result.append([])

		# Следует заметить, что в self.knownArea хранится не трехмерный список,
		# а двумерный. Т.е. этаж является одномерным списком перечисляющим
		# известные игрокам клетки.
		for p in self.players:
			if p:
				floorId = p.fInfo["floor"]
				floorHeight = len(self.map[floorId])
				floorWidth = len(self.map[floorId][0])
				xc = p.fInfo["x"]
				yc = p.fInfo["y"]
				area = self.getCellsInRadius(floorId, floorWidth, floorHeight, xc, yc, 0, VIEW_RADIUS, True, True)
				inResult = set(result[floorId])
				inArea = set(area)
				newArea = inArea - inResult
				result[floorId] = result[floorId] + list(newArea)
		return result

	def createMap(self):
		map = [[],[]]
		sizeX = 10
		sizeY = 10
		walls = [[2,2],[4,2],[6,2],[8,2],[1,4],[3,4],[5,4],[7,4],[2,6],[4,6],[6,6],[8,6],[1,8],[3,8],[5,8],[7,8]]
		x = 0
		y = 0
		while y < sizeY:
			map[0].append([])
			while x < sizeX:
				cell = Cell(0, x, y)
				if x == 0 or x == sizeX - 1 or y == 0 or y == sizeY - 1 or [x,y] in walls:
					cell.type = CT_WALL
					if [x,y] in walls:
						cell.hp = randint(1, 6)
				else:
					cell.type = CT_FLOOR
					if x == 1 and y == 2:
						cell.toFloor = 1
						cell.toX = 8
						cell.toY = 7
				map[0][y].append(cell)
				if cell.type == CT_DOOR:
					self.doors.append(cell)
				x += 1
			x = 0
			y += 1
		# Проба второго этажа
		x = 0
		y = 0
		sizeX = 10
		sizeY = 10
		walls = [[2,1],[4,1],[6,1],[8,1],[1,3],[3,3],[5,3],[7,3],[2,5],[4,5],[6,5],[8,5],[1,7],[3,7],[5,7],[7,7]]
		while y < sizeY:
			map[1].append([])
			while x < sizeX:
				cell = Cell(1, x, y)
				if x == 0 or x == sizeX - 1 or y == 0 or y == sizeY - 1 or [x,y] in walls:
					cell.type = CT_WALL
					if [x,y] in walls:
						cell.hp = randint(1, 6)
				else:
					cell.type = CT_FLOOR
					if x == 8 and y == 8:
						cell.toFloor = 0
						cell.toX = 1
						cell.toY = 1
				map[1][y].append(cell)
				if cell.type == CT_DOOR:
					self.doors.append(cell)
				x += 1
			x = 0
			y += 1
		return map

	def sendChatMessage(self, message):
		for p in self.players:
			if p:
				p.sChatMessage(message)

	def finishFight(self):
		if self.nextMoveTimer and self.nextMoveTimer.is_alive():
			self.nextMoveTimer.cancel()
		self.nextMoveTimer = None
		id = 0
		for p in self.players:
			if p:
				p.sFinishFight()
				p.fightController = None
				self.players[id] = None
			id += 1
		self.map = None
		self.knownArea = None
		self.moveOrder = None
		self.players = None
		#del self

	# Удаление игрока в случае его отключения. Надо сюда дописать
	# умершвление уходящего игрока.
	def removePlayer(self, player):
		id = 0
		for p in self.players:
			if p == player:
				# Удалим игрока также из moveOrder
				i = -1
				try:
					i = self.moveOrder.index(p.fInfo["id"])
				except ValueError:
					pass
				if i >= 0 and i >= self.currentUnit:
					self.currentUnit -= 1
				if i >= 0:
					self.moveOrder.remove(p.fInfo["id"])
				self.players[id] = None
				# Сообщим остальным что игрок вышел
				for sp in self.players:
					if sp:
						sp.sKillUnit(p.fInfo["id"])
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
	def calculateWayLength(self, width, height, xs, ys, xe, ye):
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

	def unitWantAction(self, player, x, y):
		# Проверка дозволенности хода
		if player.params["hitPoints"] <= 0 or player.fInfo["id"] != self.moveOrder[self.currentUnit] or player.params["actPoints"] < ACTION_COST:
			return
		# Взаимодействовать с ячейкой можно только находясь в непосредственной близости от нее
		floorId = player.fInfo["floor"]
		xs = player.fInfo["x"]
		ys = player.fInfo["y"]
		# Проверка входных данных
		if x < 0 or y < 0 or x >= len(self.map[floorId][0]) or y >= len(self.map[floorId]):
			return
		distance = self.calculateWayLength(len(self.map[floorId][0]), len(self.map[floorId]), xs, ys, x, y)
		if distance != 1:
			return
		# Если не с чем взамодействовать, уходим
		cell = self.map[floorId][y][x]
		# На стенах могут быть ключи
		if cell.type == CT_WALL:
			if cell.key < 0:
				return
		# А на полу может быть переход между этажами
		elif cell.type == CT_FLOOR:
			if cell.toFloor < 0:
				return
		# Иначе, если игрок делает попытку взаимодействия не со стеной и не с полом, уходим
		else:
			return
		# Наконец-то есть с чем повзаимодействовать
		# Если это стена, то на ней точно есть ключ
		if cell.type == CT_WALL:
			wasOpened = self.useKey(cell.key)
			# TODO: Если wasOpened == True, нужно опросить всех игроков, что им стало видно после открытия двери.
			if wasOpened:
				area = self.getKnownArea()
				# Подготовим массив для функции sendOpenedArea
				result = []
				# Создаем этажи (пустые массивы этажей будут проигнорированы)
				for floor in self.map:
					result.append([])
				floorId = 0
				while floorId < len(area):
					if len(area[floorId]):
						inKnownArea = set(self.knownArea[floorId])
						inArea = set(area[floorId])
						newArea = inArea - inKnownArea
						self.knownArea[floorId] = self.knownArea[floorId] + list(newArea)
						result[floorId] = list(newArea)
					floorId += 1
				self.sendOpenedArea(result)
				#self.sendOpenedKeys(result)
		# Если же это пол, то это точно переход между этажами
		elif cell.type == CT_FLOOR:
			# Перемещаем юнита
			player.fInfo["floor"] = cell.toFloor
			player.fInfo["x"] = cell.toX
			player.fInfo["y"] = cell.toY
			# Находим ячейки, которые видно с этой позиции
			floorId = player.fInfo["floor"]
			floorHeight = len(self.map[floorId])
			floorWidth = len(self.map[floorId][0])
			area = self.getCellsInRadius(floorId, floorWidth, floorHeight, cell.toX, cell.toY, 0, VIEW_RADIUS, True, True)
			inKnownArea = set(self.knownArea[floorId])
			inArea = set(area)
			newArea = inArea - inKnownArea
			self.knownArea[floorId] = self.knownArea[floorId] + list(newArea)
			# Подготовим массив для функции sendOpenedArea
			result = []
			# Создаем этажи (пустые массивы этажей будут проигнорированы)
			for floor in self.map:
				result.append([])
			result[floorId] = list(newArea)
			# Игрокам нужно отправить newArea
			self.sendOpenedArea(result)
			#self.sendOpenedKeys(result)
			self.teleportUnit(player, cell.toFloor, cell.toX, cell.toY)
		player.params["actPoints"] -= ACTION_COST
		if player.params["actPoints"] == 0:
			self.nextMove()

	def teleportUnit(self, unit, floor, x, y):
		unit.fInfo["floor"] = floor
		unit.fInfo["x"] = x
		unit.fInfo["y"] = y
		# TODO: Не забыть отнять ОД
		for p in self.players:
			if p:
				p.sTeleportUnit(unit.fInfo["id"], floor, x, y)


	# Функция проходится по списку дверей и открывает замки соответствующие переданному ключу.
	# Если замков на двери больше нет, то ячейка превращается в пол.
	# Функция возращает True, если была открыта хотя бы одна дверь, т.к. после этого может потребоваться
	# исследовать вновь открытую территорию.
	def useKey(self, key):
		isOpened = False
		clen = len(self.doors)
		i = 0
		while i < clen:
			cell = self.doors[i]
			if key in cell.keys:
				cell.keys.remove(key)
			# Если ключей на двери не осталось, нужно превратить ее в пол и удалить из списка дверей
			if len(cell.keys) == 0:
				# Превращаем
				self.changeCellType(cell, CT_FLOOR)
				isOpened = True
				# Удаляем
				a = self.doors[0:i]
				b = self.doors[i+1:]
				self.doors = a + b
				i -= 1
				clen -= 1
			i += 1
		return isOpened

	# Функция изменяет тип ячейки и сообщает об этом игрокам
	def changeCellType(self, cell, type):
		cell.type = type
		for p in self.players:
			if p:
				p.sChangeCell(cell.floor, cell.x, cell.y, cell.type)

	def unitWantAttack(self, player, x, y):
		# Проверка дозволенности хода
		od = player.fInfo["curWeapon"]["points"] if player.fInfo["curWeapon"] else 1
		if player.params["hitPoints"] <= 0 or player.fInfo["id"] != self.moveOrder[self.currentUnit] or player.params["actPoints"] < od:
			return
		# Проверка на неверные координаты
		floor = player.fInfo["floor"]
		if y < 0 or y >= len(self.map[floor]) or x < 0 or x >= len(self.map[floor][y]):
			return
		# TODO: добавить сюда проверку возможности попадания по этой ячейке
		# то есть расстояние до нее и не загорожена ли она препятствием.

		unit = self.getUnitByCoordinates(floor, x, y)
		damage = 0
		if player.fInfo["curWeapon"]:
			damage = self.getDamage(player.fInfo["curWeapon"]["damage"])
		else:
			damage = self.getDamage("1k")
		if unit:
			# Атакуем юнита
			player.params["actPoints"] -= od
			# TODO: добавить сюда сопротивление цели
			if unit.params["hitPoints"] > 0:
				unit.params["hitPoints"] -= damage
				for p in self.players:
					if p:
						p.sUnitAttack(player.fInfo["id"], x, y)
						p.sUnitDamage(damage, unit.fInfo["id"])
				# Если юнит умер, сообщаем об этом. Кроме того нужно исключить его
				# из списка moveOrder, чтобы ему не передавался ход.
				# Если гибнет последний игрок, бой заканчивается (нужна отдельная функция
				# проверки завершения боя, т.к. могут быть различные условия его завершения)
				if unit.params["hitPoints"] <= 0:
					unit.params["hitPoints"] = 0
					for p in self.players:
						if p:
							# Шлём известие о смерти юнита
							p.sKillUnit(unit.fInfo["id"])
							# Если это умирающий юнит
							if p == unit:
								# Удалим его также из moveOrder
								if self.moveOrder.index(unit.fInfo["id"]) >= self.currentUnit:
									self.currentUnit -= 1
								self.moveOrder.remove(unit.fInfo["id"])

		elif self.map[floor][y][x].type == CT_WALL:
			cell = self.map[floor][y][x]
			if cell.hp > 0:
				player.params["actPoints"] -= od
				# Атакуем стену
				cell.hp -= damage
				for p in self.players:
					if p:
						p.sUnitAttack(player.fInfo["id"], x, y)
						p.sUnitDamage(damage, -1, floor, x, y)
				if cell.hp <= 0:
					cell.hp = 0
					self.changeCellType(cell, CT_FLOOR)
					# Тут стена рушится, поэтому нужно узнать не увидят ли игроки чего нового.
					for p in self.players:
						if p:
							# Находим ячейки, которые видно этому игроку
							floorId = p.fInfo["floor"]
							floorHeight = len(self.map[floorId])
							floorWidth = len(self.map[floorId][0])
							area = self.getCellsInRadius(floorId, floorWidth, floorHeight, p.fInfo["x"], p.fInfo["y"], 0, VIEW_RADIUS, True, True)
							inKnownArea = set(self.knownArea[floorId])
							inArea = set(area)
							newArea = inArea - inKnownArea
							self.knownArea[floorId] = self.knownArea[floorId] + list(newArea)
							# Подготовим массив для функции sendOpenedArea
							result = []
							# Создаем этажи (пустые массивы этажей будут проигнорированы)
							for floor in self.map:
								result.append([])
							result[floorId] = list(newArea)
							# Игрокам нужно отправить newArea
							self.sendOpenedArea(result)
		# Атака проведена, проверяем очки действия
		if player.params["actPoints"] == 0:
			self.nextMove()


	def getDamage(self, damageStr):
		arr = damageStr.split('k')
		k = int(arr[0])
		m = 0
		if len(arr) == 2 and arr[1] != '':
			m = int(arr[1])
		damage = 0
		for i in range(k):
			damage += randint(1, 6)
		damage += m
		return damage

	def getUnitByCoordinates(self, floor, x, y):
		unit = None
		for p in self.players:
			if p:
				if p.fInfo["floor"] == floor and p.fInfo["x"] == x and p.fInfo["y"] == y:
					unit = p
					break
		return unit


	def unitWantMove(self, player, x, y):
		# Проверка дозволенности хода
		if player.params["hitPoints"] <= 0 or player.fInfo["id"] != self.moveOrder[self.currentUnit]:
			return
		# Проверка на неверные координаты
		floor = player.fInfo["floor"]
		if y < 0 or y >= len(self.map[floor]) or x < 0 or x >= len(self.map[floor][y]):
			return
		px = player.fInfo["x"]
		py = player.fInfo["y"]
		if x < 0 or y < 0 or self.map[floor][y][x].type != CT_FLOOR:
			return
		path = self.aStar(floor, px, py, x, y, [])
		if player.params["actPoints"] < len(path) / 2:
			return
		if len(path) > 0:
			player.params["actPoints"] -= len(path) / 2
			# Теперь на каждом шаге игрока нужно проверять открытую им территорию.
			# Видимо будем слать шаг-[ячейки]-шаг-[ячейки].
			# Ячейки (территория) опциональны, т.к. игрок может ходить
			# по уже изведанной территории.
			while len(path):
				# Берем очередной шаг
				step = path[:2]
				path = path[2:]
				# Находим ячейки, которые видно с этой позиции
				floorId = player.fInfo["floor"]
				floorHeight = len(self.map[floorId])
				floorWidth = len(self.map[floorId][0])
				area = self.getCellsInRadius(floorId, floorWidth, floorHeight, step[0], step[1], 0, VIEW_RADIUS, True, True)
				inKnownArea = set(self.knownArea[floorId])
				inArea = set(area)
				newArea = inArea - inKnownArea
				self.knownArea[floorId] = self.knownArea[floorId] + list(newArea)
				# Подготовим массив для функции sendOpenedArea
				result = []
				# Создаем этажи (пустые массивы этажей будут проигнорированы)
				for floor in self.map:
					result.append([])
				result[floorId] = list(newArea)
				# Игрокам нужно отправить newArea
				self.sendOpenedArea(result)
				#self.sendOpenedKeys(result)
				self.moveUnit(player, step, step[0], step[1])
		if player.params["actPoints"] == 0:
			self.nextMove()

	def moveUnit(self, unit, path, x, y):
		unit.fInfo["x"] = x
		unit.fInfo["y"] = y
		# TODO: Не забыть отнять ОД
		for p in self.players:
			if p:
				p.sMoveUnit(unit.fInfo["id"], path)
			

#=======================================================================
# Алгоритм A*
#=======================================================================
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
		cc = aStarCell(x, y, 0, 0, 0, hf, hf)
		open.append(cc)
		isPathFound = False
		while not isPathFound:
			# Получаем индекс ячейки из открытого списка, ближайщей к финишной ячейке
			minFCellIndex = self.minFCell(open);
			# cc = current сell - текущая ячейка
			cc = open[minFCellIndex];
			# Добавляем текущую ячейку в закрытый список
			close.append(cc)
			# И удаляем ее из открытого списка
			del open[minFCellIndex]
			# ac = added сell - добавляемая ячейка
			acIndex = 0
			# To left
			if cc.x - 1 >= 0 and map[cc.y][cc.x - 1] != 0 and self.exist(cc.x - 1, cc.y, close) < 0:
				acIndex = self.exist(cc.x - 1, cc.y, open)
				if acIndex < 0:
					ac = aStarCell(cc.x - 1, cc.y, cc.x, cc.y)
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
					ac = aStarCell(cc.x + 1, cc.y, cc.x, cc.y)
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
			if cc.y - 1 >= 0 and newX < len(map[cc.y - 1]) and newX >= 0 and map[cc.y - 1][newX] != 0 and self.exist(newX, cc.y - 1, close) < 0:
				acIndex = self.exist(newX, cc.y - 1, open)
				if acIndex < 0:
					ac = aStarCell(newX, cc.y - 1, cc.x, cc.y)
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
			if cc.y - 1 >= 0 and newX < len(map[cc.y - 1]) and newX >= 0 and map[cc.y - 1][newX] != 0 and self.exist(newX, cc.y - 1, close) < 0:
				acIndex = self.exist(newX, cc.y - 1, open)
				if acIndex < 0:
					ac = aStarCell(newX, cc.y - 1, cc.x, cc.y)
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
			if cc.y + 1 < sizeY and newX < len(map[cc.y + 1]) and newX >= 0 and map[cc.y + 1][newX] != 0 and self.exist(newX, cc.y + 1, close) < 0:
				acIndex = self.exist(newX, cc.y + 1, open)
				if acIndex < 0:
					ac = aStarCell(newX, cc.y + 1, cc.x, cc.y)
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
			if cc.y + 1 < sizeY and newX < len(map[cc.y + 1]) and newX >= 0 and map[cc.y + 1][newX] != 0 and self.exist(newX, cc.y + 1, close) < 0:
				acIndex = self.exist(newX, cc.y + 1, open)
				if acIndex < 0:
					ac = aStarCell(newX, cc.y + 1, cc.x, cc.y)
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
				isPathFound = True
			if len(open) == 0:
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
		result.reverse()
		return result

	# Функция проверяет существование ячейки с координатами x, y в списке v.
	def exist(self, x, y, v):
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

#=======================================================================
# Алгоритм нахождения ячеек видимых из данной ячейки
#=======================================================================
	# Функция возвращает список ячеек на расстоянии radius от ячейки (xc;yc).
	# Если флаг checkObstacles установлен, будет проведена дополнительная проверка
	# на загораживание ячеек препятствиями.
	def getCellsInRadius(self, floorId, width, height, xc, yc, r1, r2, includeCenter = False, checkObstacles = False):
		cells = self.map[floorId]
		# Проверка на неверные данные
		if width <= 0 or height <= 0 or not cells or yc < 0 or yc >= height or xc < 0 or xc >= width or r1 < 0 or r2 < 0 or (r1 >= r2 and r2 > 0):
			return []
		
		# Массив, в который будут собираться объекты Cell
		array = []
		
		# Начальные значения переменных
		lenStart = r2 * 2 + 1
		length = lenStart
		countDiscard = r1 * 2 + 1
		countAllow = length - countDiscard
		xs = xc - r2
		xe = xs + length - 1
		xcur = xs
		ycur = 0
		dy = 0
		# Проходимся по вертикали r2 + 1 количество раз если r2 > 0
		if r2 > 0:
			for a in range(r2 + 1):
				# Начинаем с центральной полосы
				for b in range(length):
					if (abs(xs - xcur) < (countAllow / 2.0)) or (abs(xe - xcur) < (countAllow / 2.0)):
						if dy == 0:
							ycur = yc
							if xcur >= 0 and xcur < width:
								array.append(cells[ycur][xcur])
						else:
							ycur = yc + dy
							if xcur >= 0 and xcur < width and ycur >= 0 and ycur < height:
								array.append(cells[ycur][xcur])
							ycur = yc - dy
							if xcur >= 0 and xcur < width and ycur >= 0 and ycur < height:
								array.append(cells[ycur][xcur])
					xcur += 1
				# При переходе на следующую полосу корректируем значения переменных
				if ((yc + a) % 2) > 0:
					xs += 1
				xcur = xs
				
				length -= 1
				countDiscard -= 1
				dy += 1
				countAllow = length - (countDiscard if dy <= r1 else 0)
				xe = xs + length - 1
		
		if includeCenter and xc >= 0 and xc < width and yc >= 0 and yc < height:
			array.append(cells[yc][xc])
		# Теперь, если ячейки необходимо подсветить серым цветом, т.е. не для показа радиуса
		# зонной атаки, нужно исключить из массива те ячейки которые будут недоступны из-за
		# препятствий на поле.
		if checkObstacles:
			# Будем просмотривать только те ячейки, которые являются препятствиями
			obstacles = self.getObstacles(array, xc, yc)
			# Удалим ячейки закрытые препятствиями
			array = self.reduceCellsByObstacles(xc, yc, array, obstacles)

		return array


	# Функция удаляет из массива cells те ячейки, которые перекрываются препятствиями,
	# представленными в массиве obstacles.
	def reduceCellsByObstacles(self, xc, yc, cells, obstacles):
		# Проходимся по всем ячейкам, содержащимся в cells
		clen = len(cells)
		i = 0
		while i < clen:
			cell = cells[i]
			r = self.isObstacled(xc, yc, cell.x, cell.y, obstacles)
			if r:
				a = cells[0:i]
				b = cells[i+1:]
				cells = a + b
				i -= 1
				clen -= 1
			i += 1
		
		# А вот такой цикл чего-то не работает, видимо плохо я знаю Python,
		# приходится изворачиваться C-подобными циклами
		#for cell in cells:
		#	r = self.isObstacled(xc, yc, cell.x, cell.y, obstacles)
		#	print "isO: toX =",cell.x," toY =",cell.y," res =",r
		#	if r:
		#		cells.remove(cell)
		return cells

	
	# Функция возвращает true если точку (toX;toY) при наблюдении из (xc;yc) загораживает
	# какое-нибудь препятствие из obstacles.
	# @param	obstacles - массив объектов Cell
	def isObstacled(self, xc, yc, toX, toY, obstacles):
		# Визуальные координаты
		vxc = xc * VISUAL_CELL_WIDTH + (VISUAL_CELL_WIDTH / 2.0 if yc % 2 else 0)
		vyc = yc * VISUAL_CELL_HEIGHT * 0.75
		vtoX = toX * VISUAL_CELL_WIDTH + (VISUAL_CELL_WIDTH / 2.0 if toY % 2 else 0)
		vtoY = toY * VISUAL_CELL_HEIGHT * 0.75
		
		# Анализируем все препятствия
		for obstacle in obstacles:
			# Визуальные координаты текущего препятствия
			vox = obstacle.x * VISUAL_CELL_WIDTH + (VISUAL_CELL_WIDTH / 2.0 if obstacle.y % 2 else 0)
			voy = obstacle.y * VISUAL_CELL_HEIGHT * 0.75
			
			# Во-первых узнаем, если расстояние до текущего препятствия больше
			# чем до целевой точки, можно пропустить это препятствие.
			if sqrt(pow(vxc - vox, 2) + pow(vyc - voy, 2)) > sqrt(pow(vxc - vtoX, 2) + pow(vyc - vtoY, 2)):
				continue
			
			# Иначе составляем нормальное уравнение прямой (по координатам точки наблюдения и препятствия)
			# и выясняем расстояние от целевой точки до этой прямой.
			# Если это расстояние меньше чем VISUAL_CELL_RADIUS, значит клетка не видна из точки наблюдения.
			d = self.getPerpDistance(vxc, vyc, vtoX, vtoY, vox, voy)
			if d < VISUAL_CELL_RADIUS and not (toX == obstacle.x and toY == obstacle.y):
				R = sqrt(pow(vtoX - vox, 2) + pow(vtoY - voy, 2))
				L = sqrt(pow(vxc - vtoX, 2) + pow(vyc - vtoY, 2))
				if R < L:
					return True
		return False

	
	# Функция возвращает расстояние от точки (vtoX, vtoY) до прямой, проходящей через
	# точки (vxc, vyc) и (vox, voy).
	def getPerpDistance(self, vxc, vyc, vtoX, vtoY, vox, voy):
		A = vyc - vtoY
		B = vtoX - vxc
		C = vxc * vtoY - vtoX * vyc
		d = abs( (A * vox + B * voy + C) / sqrt(A * A + B * B) )
		return d

	# Функция возвращает массив точек, таких что клетки на соответствующих
	# координатах являются препятствием.
	# Функция получает массив объектов вида класса Cell
	def getObstacles(self, cells, exceptX, exceptY):
		r = []
		for cell in cells:
			if not (exceptX == cell.x and exceptY == cell.y) and (cell.type == CT_WALL or cell.type == CT_DOOR):
				r.append(cell)
		return r
