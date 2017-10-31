import spidev
import RPi.GPIO as GPIO


WRITE = 0
READ = 1

default =   [[0, 0, 0x022], [0, 1, 0x0ff], [0, 2, 0x1a0], [0, 3, 0x000], [0, 4, 0x31c],
			[0, 5, 0x000], [0, 6, 0x3ff], [0, 7, 0x024], [0, 8, 0x000], [0, 9, 0x00f],
			[0, 10, 0x000], [0, 11, 0x060], [0, 13, 0x000], [0, 14, 0x360], [0, 15, 0x242],
			[0, 16, 0x380], [0, 17, 0x000], [0, 18, 0x080], [0, 19, 0x05f], [0, 20, 0x1ea],
			[0, 21, 0x0bf], [0, 22, 0x1b8], [0, 23, 0x065], [0, 24, 0x24f], [0, 25, 0x3a8],
			[0, 26, 0x015], [0, 27, 0x180], [0, 28, 0x063], [0, 29, 0x000], [0, 30, 0x000],
			[0, 31, 0x000], [1, 1, 0x000], [1, 2, 0x000], [1, 3, 0x000], [1, 4, 0x380],
			[1, 5, 0x000], [1, 6, 0x000], [1, 7, 0x000], [1, 8, 0x1aa], [1, 9, 0x114],
			[1, 10, 0x354], [1, 11, 0x073], [1, 12, 0x000], [1, 13, 0x000], [1, 14, 0x000],
			[1, 15, 0x000], [1, 16, 0x000], [1, 17, 0x000], [1, 18, 0x000], [1, 19, 0x000],
			[1, 20, 0x000], [1, 21, 0x000], [1, 22, 0x000], [1, 23, 0x000], [1, 24, 0x0c4],
			[1, 25, 0x12b], [1, 26, 0x165], [1, 27, 0x000], [1, 28, 0x004], [1, 31, 0x000]]


setLocalAddrs = [0, 0, 0x023];
standbyMode = [0, 0, 0x026];
rxMode = [0, 0, 0x02A];
doutEn = [0, 14,0x362];

A1 = 15
A2 = 13


def bitmask(n):
	return int('1'*n, 2)

def bitread(n,i):
	return int("{0:02b}".format(n)[-(i+1)])	

def mensaje(rw, a, d):
	return ((rw<<15) | ((a & bitmask(5))<<10) | (d & bitmask(10)))



class Mixer():
	"""docstring for Mixer"""
	def __init__(self, spidev):
		global WRITE, READ, default, setLocalAddrs,standbyMode, rxMode, doutEn, A1, A2

		# GPIO config
		GPIO.setmode(GPIO.BOARD)
		GPIO.setup(A1, GPIO.OUT, initial=GPIO.LOW)
		GPIO.setup(A2, GPIO.OUT, initial=GPIO.LOW)

		#SPI config
		bus = 0
		device = 0
		self.spi = spidev
		self.spi.open(bus, device)
		self.spi.max_speed_hz = 1000000

		## LO parameters
		self.N = 0b01001000
		self.F = 0b10000000000000000000
		self.Flow = self.F & bitmask(10);
		self.Fhigh = (self.F >> 10) & bitmask(10);

	## Board actions
	def init_all(self):
		self.init_board(0)
		self.init_board(1)
		self.init_board(2)
		self.init_board(3)

	def init_board(self, board):
		self.select_board(board)
		for i in xrange(len(default)):
			if not default[i][0]:
				self.write_reg(default[i])
				if default[i+1][0]:
					self.write_reg(setLocalAddrs)
				else:
					self.write_reg(default[i])
		self.write_reg(standbyMode)
		self.write_reg(doutEn)
		self.write_reg(15, (self.get_default(15) & ~bitmask(7)) | self.N);
		self.write_reg(16, self.Fhigh);
		self.write_reg(17, self.Flow);
		self.write_reg(5,1)
		self.write_reg(rxMode)
		self.write_reg(5,0)
		print('Done configuring '+str(board))

	def select_board(self,board):
		assert(board<4)
		GPIO.output(A1, bitread(board,0))
		GPIO.output(A2, bitread(board,1))

	def standby(self, board):
		if board == 'all':
			for i in range(4):
				select_board(i)
				self.write_reg(standbyMode)
		else:
			select_board(board)
			self.write_reg(standbyMode)

	def set_gain(self, board, channel, value=255):
		self.select_board(board)
		self.write_reg(6, 1<<(channel+4) | (self.get_default(6) & bitmask(5)))
		self.write_reg(1, value | (self.get_default(1) & ~bitmask(8)))

	#SPI communication
	def write_reg(self, addrs, data = None):
		if data == None:
			self.write_reg(addrs[1],addrs[2])
			return
		m = mensaje(WRITE,addrs,data)
		send = [m >> 8, m & bitmask(8)]
		self.spi.xfer2(send)

	def read_reg(self, addrs):
		m = mensaje(READ,addrs,0)
		send = [m >> 8, m & bitmask(8)]
		read = self.spi.xfer2(send)
		return (read[0]<<8) | (read[1] & bitmask(8))

	def get_default(self, addrs):
		for i in default:
			if i[1] == addrs:
				return i[2]
		return -1

	def cleanGPIO(self):
		GPIO.cleanup()
