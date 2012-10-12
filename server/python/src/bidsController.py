# coding=utf-8
import math
import bid
import fightController
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
	def createBid(self, player, op, count, name):
		self.lock.acquire()
		id = self.findEmptyPlace(self.bids)
		b = bid.Bid(id, op, self.checkBidForStart, count, name)
		if id == len(self.bids):
			self.bids.append(b)
		else:
			self.bids[id] = b
		self.sayAboutNewBid(id)
		self.lock.release()
		self.addPlayerToBid(id, player)
	
	# Рассказать игрокам о новой заявке
	def sayAboutNewBid(self, id):
		playersLock.acquire()
		b = self.bids[id]
		for player in players:
			if player:
				player.sNewBid(id, b.op, b.count, b.curcount, b.name)
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
		self.lock.acquire()
		if id >= 0 and id < len(self.bids):
			b = self.bids[id]
			if b: # and math.fabs(player.params["usedOP"] - b.op) <= 5:
				b.addPlayer(player)
				self.sayUpdateBid(id)
				if b.curcount == b.count:
					b.t.cancel()
					# Возможно это станет проблемным местом.
					self.lock.release()
					self.checkBidForStart(b.id)
					return
		self.lock.release()

	# Удаление игрока из списка игроков в заявке
	def removePlayerFromBid(self, id, player):
		self.lock.acquire()
		if id >= 0 and id < len(self.bids):
			b = self.bids[id]
			if b:
				b.removePlayer(player)
				self.sayUpdateBid(id)
		self.lock.release()

	# Удаление заявки
	def deleteBid(self, id):
		self.lock.acquire()
		self.bids[id].stopTimer()
		self.bids[id].clear()
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
			print 'Start fight'
			self.startFight(b)
			self.deleteBid(id)
			pass

	# Функция запуска боя. Здесь нужно забрать нужную информацию
	# из заявки, потому что сразу после этой функции заявка удаляется.
	def startFight(self, bid):
		self.lock.acquire()
		fc = fightController.FightController(bid.players[:])
		self.lock.release()

	# Поиск свободного места в списке holder
	def findEmptyPlace(self, holder):
		id = 0
		for place in holder:
			if not place:
				break
			else:
				id += 1
		return id
