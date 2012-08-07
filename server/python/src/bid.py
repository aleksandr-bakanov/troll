# coding=utf-8
import threading
# Класс заявки
class Bid:
	# @param op		ОП создателя заявки
	# @param cb		callback (timer end function)
	# @param count	max players count
	def __init__(self, id, op, cb, count):
		self.id = id
		self.op = op
		self.cb = cb
		self.startTimer()

	def startTimer(self):
		self.t = threading.Timer(10.0, self.cb, [self.id])
		self.t.start()

	def stopTimer(self):
		if self.t.is_alive():
			self.t.cancel()
