# coding=utf-8
from consts import *

# ======================================================================
#
# Класс ячейки поля боя
#
# ======================================================================
class Cell:
	def __init__(self, type):
		self.type = type

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
		self.players[0].fInfo["x"] = 0
		self.players[0].fInfo["y"] = 0
		self.players[0].fInfo["floor"] = 0
		# Теперь нужно узнать какие ячейки видят игроки и отправить им
		# начальные данные (т.е. эти ячейки, координаты других игроков,
		# и, порядок ходов). Пока (и впредь?) будем расставлять игроков
		# так, чтобы в первый ход не пришлось встраивать в порядок
		# ходов мобов.
		self.knownArea = self.getKnownArea()

	def getKnownArea(self):
		return self.map[:]

	def createMap(self):
		map = [[]]
		i = 0
		j = 0
		while i < 3:
			map[0].append([])
			while j < 3:
				map[0][i].append(Cell(CT_FLOOR))
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
