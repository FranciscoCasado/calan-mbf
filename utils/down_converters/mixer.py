import spidev
import RPi.GPIO as GPIO


_WRITE = 0
_READ = 1

_default = [[0, 0, 0x022], [0, 1, 0x0ff], [0, 2, 0x1a0], [0, 3, 0x000], [0, 4, 0x31c],
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

_boards = {'a': 0, 'b': 1, 'c': 2, 'd': 3, }
_ports = {'1': 1, '2': 2, '3': 4, '4': 5, }

_set_local_addrs = [0, 0, 0x023]
_standbyMode = [0, 0, 0x026]
_rxMode = [0, 0, 0x02A]
_doutEn = [0, 14, 0x362]

_A1 = 15
_A2 = 13


def _bitmask(n):
    return int('1'*n, 2)


def _bitread(n, i):
    return int("{0:02b}".format(n)[-(i+1)])


def _message(rw, a, d):
    return (rw << 15) | ((a & _bitmask(5)) << 10) | (d & _bitmask(10))


class Mixer:
    """docstring for Mixer"""
    def __init__(self):
        global _WRITE, _READ, _default, _set_local_addrs, _A1, _A2
        global _standbyMode, _rxMode, _doutEn, _ports, _boards

        # GPIO config
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(_A1, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(_A2, GPIO.OUT, initial=GPIO.LOW)

        # SPI config
        bus = 0
        device = 0
        self.spi = spidev.SpiDev()
        self.spi.open(bus, device)
        self.spi.max_speed_hz = 1000000

        # LO parameters
        self._N = 0b01001000
        self._F = 0b10000000000000000000
        self._Flow = self._F & _bitmask(10)
        self._Fhigh = (self._F >> 10) & _bitmask(10)

    # Board actions
    def init_all(self):
        self.init_board(0)
        self.init_board(1)
        self.init_board(2)
        self.init_board(3)

    def init_board(self, board):
        self._select_board(board)
        for i in xrange(len(_default)):
            if not _default[i][0]:
                self.write_reg(_default[i])
                if _default[i+1][0]:
                    self.write_reg(_set_local_addrs)
                else:
                    self.write_reg(_default[i])
        self.write_reg(_standbyMode)
        self.write_reg(_doutEn)
        self.write_reg(15, (self.get_default(15) & ~_bitmask(7)) | self._N)
        self.write_reg(16, self._Fhigh)
        self.write_reg(17, self._Flow)
        self.write_reg(5, 1)
        self.write_reg(_rxMode)
        self.write_reg(5, 0)
        print('Done configuring '+str(board))

    def calibrate_all(self):
    	self.set_gain('a1',7,15)
    	self.set_gain('a2',7,15)
    	self.set_gain('a3',7,15)
    	self.set_gain('a4',7,15)
    	self.set_gain('b1',7,15)
    	self.set_gain('b2',7,15)
    	self.set_gain('b3',7,15)
    	self.set_gain('b4',7,15)
    	self.set_gain('c1',7,15)
    	self.set_gain('c2',7,15)
    	self.set_gain('c3',7,15)
    	self.set_gain('c4',7,15)
    	self.set_gain('d1',7,15)
    	self.set_gain('d2',7,15)
    	self.set_gain('d3',7,15)
    	self.set_gain('d4',7,15)

    def _select_board(self,board):
        assert(board < 4)
        GPIO.output(_A1, _bitread(board, 0))
        GPIO.output(_A2, _bitread(board, 1))

    def standby(self, board):
        if board == 'all':
            for i in range(4):
                self._select_board(i)
                self.write_reg(_standbyMode)
        else:
            self._select_board(board)
            self.write_reg(_standbyMode)

    def set_gain(self, channel, lna_gain=7, vga_gain=15):
        if len(channel) > 2:
            print("invalid channel")
            return
        try:
            board = _boards[channel[0]]
            port = _ports[channel[1]]
        except KeyError:
            print("invalid channel")
            return
        self._select_board(board)
        self.write_reg(6, (self.get_default(6) & _bitmask(5)) | 1 << (port+4))
        self.write_reg(1, (self.get_default(1) & ~_bitmask(8)) | lna_gain << 5 | vga_gain)

    # SPI communication
    def write_reg(self, addrs, data=None):
        if data is None:
            self.write_reg(addrs[1], addrs[2])
            return
        m = _message(_WRITE, addrs, data)
        send = [m >> 8, m & _bitmask(8)]
        self.spi.xfer2(send)

    def read_reg(self, addrs):
        m = _message(_READ, addrs, 0)
        send = [m >> 8, m & _bitmask(8)]
        read = self.spi.xfer2(send)
        return (read[0] << 8) | (read[1] & _bitmask(8))

    def get_default(self, addrs):
        for i in _default:
            if i[1] == addrs:
                return i[2]
        return -1

    def clean_gpio(self):
        GPIO.cleanup()
