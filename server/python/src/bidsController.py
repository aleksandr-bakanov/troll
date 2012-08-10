# coding=utf-8
import math
import bid
import threading
from player import players
from player import playersLock
# ======================================================================
#
# Класс управляющий заявками
#
# ======================================================================
class BidsController:
	def __init__(self):
		# Список заявок
		self.bids = []
		self.lock = threading.Lock()

	# Создание заявки. Заявка базируется на ОП создателя и максимальном
	# количестве игроков.
	# @param player	игрок создавший заявку
	def createBid(self, player, op, count):
		self.lock.acquire()
		id = self.findEmptyPlace(self.bids)
		b = bid.Bid(id, op, self.checkBidForStart, count)
		if id == len(self.bids):
			self.bids.append(b)
		else:
			self.bids[id] = b
		self.sayAboutNewBid(id)
		self.addPlayerToBid(id, player)
		self.lock.release()
	
	# Рассказать игрокам о новой заявке
	def sayAboutNewBid(self, id):
		playersLock.acquire()
		b = self.bids[id]
		for player in players:
			if player:
				player.sNewBid(id, b.op, b.count, b.curcount)
		playersLock.release()

	# Рассказать игрокам об обновлении состояния заявки
	def sayUpdateBid(self, id):
		playersLock.acquire()
		b = self.bids[id]
		for player in players:
			if player:
				player.sUpdateBid(id, b.curcount)
		playersLock.release()

	# Рассказать игрокам об удалении заявки
	def sayRemoveBid(self, id):
		playersLock.acquire()
		for player in players:
			if player:
				player.sRemoveBid(id)
		playersLock.release()

	# Добавления игрока в список игроков в заявке
	def addPlayerToBid(self, id, player):
		if id >= 0 and id < len(self.bids):
			b = self.bids[id]
			if b and math.fabs(player.params["usedOP"] - b.op) <= 5:
				b.addPlayer(player)
				self.sayUpdateBid(id)

	# Удаление игрока из списка игроков в заявке
	def removePlayerFromBid(self, id, player):
		if id >= 0 and id < len(self.bids):
			b = self.bids[id]
			if b:
				b.removePlayer(player)

	# Удаление заявки
	def deleteBid(self, id):
		self.lock.acquire()
		self.bids[id].stopTimer()
		self.bids[id] = None
		self.sayRemoveBid(id)
		self.lock.release()

	# Данная функция вызывается из заявки, время жизни которой
	# закончилось. Здесь проверяется состояние заявки. Если заявка
	# пуста, она удаляется. Если нет – бой стартует.
	def checkBidForStart(self, id):
		b = self.bids[id]
		if b.curcount == 0:
			self.deleteBid(id)
		else:
			# Start fight
			pass

	# Поиск свободного места в списке holder
	def findEmptyPlace(self, holder):
		id = 0
		for place in holder:
			if not place:
				break
			else:
				id += 1
		return id
