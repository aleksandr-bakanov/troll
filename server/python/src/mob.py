# coding=utf-8
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
		for p in fc.units:
			if p and not p.isMob and p.fInfo["floor"] == self.fInfo["floor"] and p.params["hitPoints"] > 0:
				# Смотрим расстояние до игрока
				floorId = self.fInfo["floor"]
				xs = self.fInfo["x"]
				ys = self.fInfo["y"]
				x = p.fInfo["x"]
				y = p.fInfo["y"]
				distance = fc.calculateWayLength(len(fc.map[floorId][0]), len(fc.map[floorId]), xs, ys, x, y)
				if distance <= 2:
					# TODO: Тут бы еще смотреть не загорожен ли чем игрок от моба
					fc.unitWantAttack(self, x, y)
					break
		fc.nextMove()
