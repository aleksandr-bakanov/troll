# coding=utf-8
import bid
import threading
from player import players
from player import playersLock
# Класс управляющий заявками
class BidsController:
	def __init__(self):
		# Список заявок
		self.bids = []
		self.lock = threading.Lock()

	def createBid(self, op, count):
		self.lock.acquire()
		id = self.findEmptyPlace()
		b = bid.Bid(id, op, self.deleteBid, count)
		if id == len(self.bids):
			self.bids.append(b)
		else:
			self.bids[id] = b
		self.lock.release()

	def addPlayerToBid(self, id, player):
		pass

	def removePlayerFromBid(self, id, player):
		pass

	def deleteBid(self, id):
		self.lock.acquire()
		self.bids[id].stopTimer()
		self.bids[id] = None
		self.lock.release()

	def findEmptyPlace(self):
		id = 0
		for place in self.bids:
			if not place:
				break
			else:
				id += 1
		return id
