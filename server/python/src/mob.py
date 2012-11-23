# coding=utf-8
import random
from consts import *
# ======================================================================
#
# Базовый класс для мобов
#
# ======================================================================
class Mob:
	def __init__(self):
		self.isMob = True
		self.fightController = None
		self.params = {
			"hitPoints":0,
			"actPoints":0
		}
		self.fInfo = {
			"id":-1,
			"floor":0,
			"x":0,
			"y":0,
			"curWeapon":None
		}
		self.name = "mob"
		# Радиус обзора
		self.visionRadius = 2

	def __del__(self):
		print "~Mob", id(self)

	def makeMove(self):
		# Эту функцию должен переопределять каждый моб, наследующийся от этого класса
		if self.fightController:
			self.fightController.nextMove()

# ======================================================================
#
# Тестовый класс для настоящего моба
#
# ======================================================================
class Mob1(Mob):
	def __init__(self):
		Mob.__init__(self)
		self.params["hitPoints"] = 10
		self.params["actPoints"] = 4
		self.fInfo["curWeapon"] = {"id":1, "type":1, "name":"Тапки милосердия", "cost":10, "weight":2, "damage":"1k+1", "precision":9, "range":1, "damageRange":0, "points":2}
		self.name = "mob-1"

	def makeMove(self):
		# Напишем такой простейший ИИ: если в радиусе двух клеток замечается игрок, он атакуется,
		# после чего ход передается следующему игроку. Если же никого нет, начинаем ходить бродить
		# четыре шага в случайных направлениях. При этом пока не будем после каждого шага проверять
		# не нашли ли мы кого-нибудь.
		# Еще с этим брождением нужно как-то следить за тем, что моб может выйти на территорию, известную
		# игрокам. И тогда нужно будет о нем сообщить. Если игроки о нем еще не знают нужно выдать
		# полную информацию командой S_ADD_UNIT, а если уже знают, сообщить только координаты, откуда
		# пришел моб и куда он пришел.
		self.params["actPoints"] = 4
		# Переменная fc используется для сокращения записи
		fc = self.fightController
		# Берем клетки в радиусе self.visionRadius
		floorId = self.fInfo["floor"]
		xs = self.fInfo["x"]
		ys = self.fInfo["y"]
		cells = fc.getCellsInRadius(floorId, xs, ys, 0, self.visionRadius, False, True)
		# Флаг установится в True если была совершена атака
		wasAttack = False
		# Проходимся по клеткам, которые являются полом.
		for cell in cells:
			# Смотрим, есть ли на клетке юнит, не моб
			unit = fc.getUnitByCoordinates(floorId, cell.x, cell.y)
			if unit and not unit.isMob:
				# Если есть, атакуем его и уходим
				fc.unitWantAttack(self, cell.x, cell.y)
				wasAttack = True
				break
		# Если была совершена атака, передаем ход следующему игроку
		if wasAttack:
			fc.nextMove()
		# Иначе идем куда-нибудь
		else:
			# Допустим будем брать только шесть соседних клеток. Потом
			# выбирать из них случайную. Если она окажется непроходимой,
			# то удалим ее из списка выбора и возьмем следующую случайную
			# клетку. Как находим свободную, переходим в нее.
			cells = fc.getCellsInRadius(floorId, xs, ys, 0, 1, False, True)
			freeCellFound = False
			ind = -1
			while not freeCellFound and len(cells):
				ind = random.randint(0, len(cells) - 1)
				if not cells[ind].type == CT_FLOOR:
					del cells[ind]
					continue
				else:
					freeCellFound = True
			# Проверяем нашли ли ячейку, в которую можно пойти
			if freeCellFound:
				# Сначала перемещаем моба
				cell = cells[ind]
				oldX = self.fInfo["x"]
				oldY = self.fInfo["y"]
				self.fInfo["x"] = cell.x
				self.fInfo["y"] = cell.y
				# Потом смотрим, если моб пришел в ячейку, известную игрокам,
				# то отправляем им сообщение о перемещении моба.
				# Предварительно, если моба не было в moveOrder, т.е. игроки
				# о нем еще ничего не знали, нужно отправить команду S_ADD_UNIT.
				if cell in fc.knownArea[floorId]:
					if not self.fInfo["id"] in fc.moveOrder:
						# Пока будем просто добавлять моба в конец moveOrder
						fc.moveOrder.append(self.fInfo["id"])
						for p in fc.units:
							if p and not p.isMob:
								p.sAddUnit(self.fInfo["id"], self.fInfo["floor"], oldX, oldY, self.name, -1)
					# Теперь можно отправить команду S_MOVE_UNIT
					fc.moveUnit(self, [cell.x, cell.y], cell.x, cell.y)

				fc.nextMove()
			# Если не нашли свободную ячейку, просто передаем ход
			# следующему игроку
			else:
				fc.nextMove()
