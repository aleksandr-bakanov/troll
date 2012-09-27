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
		self.players[0].fInfo["id"] = 0
		
		self.knownArea = self.getKnownArea()
		self.moveOrder = self.createMoveOrder()
		self.sendStartInfo()
		# Отправляем известную территорию
		area = self.knownArea[:]
		area[0].insert(0, 0)
		self.sendAreaOpen(area)
		del area[0][0]
		
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
		x = 0
		y = 0
		while y < sizeY:
			map[0].append([])
			while x < sizeX:
				cell = Cell(x, y)
				if x == 0 or x == sizeX - 1 or y == 0 or y == sizeY - 1 or (x == 3 and y == 2):
					cell.type = CT_WALL
				else:
					cell.type = CT_FLOOR
				map[0][y].append(cell)
				x += 1
			x = 0
			y += 1
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

	def unitWantMove(self, player, x, y):
		floor = player.fInfo["floor"]
		px = player.fInfo["x"]
		py = player.fInfo["y"]
		if x < 0 or y < 0 or self.map[floor][y][x].type != CT_FLOOR:
			return
		path = self.aStar(floor, px, py, x, y, [])
		if len(path) > 0:
			self.moveUnit(player, path, x, y)

	def moveUnit(self, player, path, x, y):
		player.fInfo["x"] = x
		player.fInfo["y"] = y
		# Не забыть отнять ОД
		for p in self.players:
			if p:
				p.sMoveUnit(player.fInfo["id"], path)
			

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
			if cc.y - 1 >= 0 and map[cc.y - 1][newX] != 0 and self.exist(newX, cc.y - 1, close) < 0:
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
			if cc.y - 1 >= 0 and map[cc.y - 1][newX] != 0 and self.exist(newX, cc.y - 1, close) < 0:
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
			if cc.y + 1 < sizeY and map[cc.y + 1][newX] != 0 and self.exist(newX, cc.y + 1, close) < 0:
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
			if cc.y + 1 < sizeY and map[cc.y + 1][newX] != 0 and self.exist(newX, cc.y + 1, close) < 0:
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
/**
 * Подсветка ячеек на расстоянии radius от ячейки, координаты
 * которой указаны в center. Если isActionArea == true, ячейки подсвечиваются красным,
 * иначе - серым.
 * @param	center
 * @param	radius
 * @param	isActionArea
 */
private function glowRadius(floorId:int, width:int, height:int, xc:int, yc:int, r1:int, r2:int, glowCenter:Boolean = false, isActionArea:Boolean = false):void
{
	var cells:Array = _cells[floorId] as Array;
	// Проверка на неверные данные
	if (width <= 0 || height <= 0 || !cells || yc < 0 || yc >= height || xc < 0 || xc >= width || r1 < 0 || r2 < 0 || (r1 >= r2 && r2 > 0))
		return;
	
	// Массив, в который будут собираться объекты вида { cell:cell, x:x, y:y }
	var array:Array = [];
	
	// Начальные значения переменных
	var lenStart:int = r2 * 2 + 1;
	var length:int = lenStart;
	var countDiscard:int = r1 * 2 + 1;
	var countAllow:int = length - countDiscard;
	var xs:int = xc - r2;
	var xe:int = xs + length - 1;
	var xcur:int = xs;
	var ycur:int = 0;
	var dy:int = 0;
	var cell:MovieClip;
	// Проходимся по вертикали r2 количество раз
	for (var a:int = 0; a <= r2 && r2 > 0; a++)
	{
		// Начинаем с центральной полосы
		for (var b:int = 0; b < length; b++)
		{
			if ((Math.abs(xs - xcur) < (countAllow / 2)) || (Math.abs(xe - xcur) < (countAllow / 2)))
			{
				if (dy == 0)
				{
					ycur = yc;
					if (xcur >= 0 && xcur < width)
					{
						cell = cells[ycur][xcur] as MovieClip;
						array.push( { cell:cell, x:xcur, y:ycur } );
					}
				}
				else
				{
					ycur = yc + dy;
					if (xcur >= 0 && xcur < width && ycur >= 0 && ycur < height)
					{
						cell = cells[ycur][xcur] as MovieClip;
						array.push( { cell:cell, x:xcur, y:ycur } );
					}
					ycur = yc - dy;
					if (xcur >= 0 && xcur < width && ycur >= 0 && ycur < height)
					{
						cell = cells[ycur][xcur] as MovieClip;
						array.push( { cell:cell, x:xcur, y:ycur } );
					}
				}
			}
			xcur++;
		}
		// При переходе на следующую полосу корректируем значения переменных
		if (((yc + a) % 2) > 0) 
			xs++;
		xcur = xs;
		
		length--;
		countDiscard--;
		dy++;
		countAllow = length - (dy <= r1 ? countDiscard : 0);
		xe = xs + length - 1;
	}
	
	if (glowCenter && xc >= 0 && xc < width && yc >= 0 && yc < height)
	{
		cell = cells[yc][xc] as MovieClip;
		array.push( { cell:cell, x:xc, y:yc } );
	}
	
	// Теперь, если ячейки необходимо подсветить серым цветом, т.е. не для показа радиуса
	// зонной атаки, нужно исключить из массива те ячейки которые будут недоступны из-за
	// препятствий на поле.
	if (!isActionArea)
	{
		// Будем просмотривать только те ячейки, которые являются препятствиями
		var obstacles:Array = getObstacles(array, xc, yc);
		// Удалим ячейки закрытые препятствиями
		array = reduceCellsByObstacles(xc, yc, array, obstacles);
		initCellsForChoising(array);
	}
	else
		glowActionAreaCells(array);
}

/**
 * Функция удаляет из массива cells те ячейки, которые перекрываются препятствиями,
 * представленными в массиве obstacles.
 * @param	xc
 * @param	yc
 * @param	cells		массив объектов вида { cell:cell, x:x, y:y }
 * @param	obstacles	массив точек, представляющих координаты ячеек-препятствий
 */
private function reduceCellsByObstacles(xc:int, yc:int, cells:Array, obstacles:Array):Array
{
	// Проходимся по всем ячейкам, содержащимся в cells
	for (var i:int = 0; i < cells.length; i++)
	{
		var o:Object = cells[i];
		if (isObstacled(xc, yc, o.x, o.y, obstacles))
		{
			cells.splice(i--, 1);
		}
	}
	return cells;
}

/**
 * Функция возвращает true если точку cell при наблюдении из (xc;yc) загораживает
 * какое-нибудь препятствие из obstacles.
 * @param	xc
 * @param	yc
 * @param	toX
 * @param	toY
 * @param	obstacles
 * @return
 */
private function isObstacled(xc:int, yc:int, toX:int, toY:int, obstacles:Array):Boolean
{
	// Визуальные координаты
	var vxc:Number = Number(xc) * VISUAL_CELL_WIDTH + (yc % 2 ? VISUAL_CELL_WIDTH / 2.0 : 0);
	var vyc:Number = Number(yc) * VISUAL_CELL_HEIGHT * 0.75;
	var vtoX:Number = Number(toX) * VISUAL_CELL_WIDTH + (toY % 2 ? VISUAL_CELL_WIDTH / 2.0 : 0);
	var vtoY:Number = Number(toY) * VISUAL_CELL_HEIGHT * 0.75;
	
	// Анализируем все препятствия
	for (var i:int = 0; i < obstacles.length; i++)
	{
		// Визуальные координаты текущего препятствие
		var vox:Number = obstacles[i].x * VISUAL_CELL_WIDTH + (int(obstacles[i].y) % 2 ? VISUAL_CELL_WIDTH / 2.0 : 0);
		var voy:Number = obstacles[i].y * VISUAL_CELL_HEIGHT * 0.75;
		
		// Во-первых узнаем, если расстояние до текущего препятствия больше
		// чем до целевой точки, можно пропустить это препятствие.
		if (Math.sqrt(Math.pow(vxc - vox, 2) + Math.pow(vyc - voy, 2)) > Math.sqrt(Math.pow(vxc - vtoX, 2) + Math.pow(vyc - vtoY, 2)))
			continue;
		
		// Иначе составляем нормальное уравнение прямой (по координатам точки наблюдения и препятствия)
		// и выясняем расстояние от целевой точки до этой прямой.
		// Если это расстояние меньше чем VISUAL_CELL_RADIUS, значит клетка не видна из точки наблюдения.
		var d:Number = getPerpDistance(vxc, vyc, vtoX, vtoY, vox, voy);
		if (d < VISUAL_CELL_RADIUS && !(toX == int(obstacles[i].x) && toY == int(obstacles[i].y)))
		{
			var R:Number = Math.sqrt(Math.pow(vtoX - vox, 2) + Math.pow(vtoY - voy, 2));
			var L:Number = Math.sqrt(Math.pow(vxc - vtoX, 2) + Math.pow(vyc - vtoY, 2));
			if (R < L) {
				return true;
			}
		}
	}
	return false;
}

/**
 * Функция возвращает расстояние от точки (vtoX, vtoY) до прямой, проходящей через
 * точки (vxc, vyc) и (vox, voy).
 * @param	vxc
 * @param	vyc
 * @param	vox
 * @param	voy
 * @param	vtoX
 * @param	vtoY
 * @return
 */
private function getPerpDistance(vxc:Number, vyc:Number, vtoX:Number, vtoY:Number, vox:Number, voy:Number):Number
{
	var A:Number = vyc - vtoY;
	var B:Number = vtoX - vxc;
	var C:Number = vxc * vtoY - vtoX * vyc;
	var d:Number = Math.abs( Number(A * vox + B * voy + C) / Math.sqrt(A * A + B * B) );
	return d;
}

/**
 * Функция возвращает массив точек, таких что клетки на соответствующих
 * координатах являются препятствием.
 * Функция получает массив объектов вида { cell:cell, x:x, y:y }
 * @return
 */
private function getObstacles(cells:Array, exceptX:int, exceptY:int):Array
{
	var r:Array = [];
	for (var i:int = 0; i < cells.length; i++)
		if (!(exceptX == cells[i].x && exceptY == cells[i].y) && cells[i].cell.info.type == CT_WALL)
			r.push(new Point(cells[i].x, cells[i].y));
	return r;
}
