# coding=utf-8
import threading
# ======================================================================
#
# Класс заявки
#
# ======================================================================
class Bid:
	# @param op		ОП создателя заявки
	# @param cb		callback (timer end function)
	# @param count	max players count
	def __init__(self, id, op, cb, count, name):
		self.id = id
		self.op = op
		self.cb = cb
		self.count = count
		self.name = name
		self.players = []
		self.curcount = 0
		self.startTimer()

	def startTimer(self):
		self.t = threading.Timer(5.0, self.cb, [self.id])
		self.t.start()

	def stopTimer(self):
		if self.t.is_alive():
			self.t.cancel()

	def addPlayer(self, player):
		id = self.findEmptyPlace(self.players)
		if id == len(self.players):
			self.players.append(player)
		else:
			self.players[id] = player
		self.curcount += 1
		player.bidId = self.id
		#if self.curcount == self.count:
		#	self.t.cancel()
		#	self.cb(self.id)

	def removePlayer(self, player):
		id = 0
		for p in self.players:
			if p == player:
				player.bidId = -1
				self.players[id] = None
				self.curcount -= 1
				break
			id += 1

	def clear(self):
		id = 0
		for p in self.players:
			if p:
				p.bidId = -1
				self.players[id] = None
			id += 1

	# Поиск свободного места в списке holder
	def findEmptyPlace(self, holder):
		id = 0
		for place in holder:
			if not place:
				break
			else:
				id += 1
		return id
