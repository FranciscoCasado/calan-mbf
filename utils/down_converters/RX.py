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

def bitread(n,i):
    return int("{0:02b}".format(n)[-(i+1)])

def bitmask(n):
    return int('1'*n, 2)

def mensaje(rw, a, d):
    return ((rw<<15) | ((a & bitmask(5))<<10) | (d & bitmask(10)))

def writeReg(addrs, data = None):
    if data == None:
        writeReg(addrs[1],addrs[2])
        return
    m = mensaje(WRITE,addrs,data)
    send = [m >> 8, m & bitmask(8)]
    spi.xfer2(send)

def readReg(addrs):
    m = mensaje(READ,addrs,0)
    send = [m >> 8, m & bitmask(8)]
    read = spi.xfer2(send)
    return (read[0]<<8) | (read[1] & bitmask(8))

def obtenerDef(addrs):
    for i in default:
        if i[1] == addrs:
            return i[2]
    return -1

# Calculado en excel: https://www.maximintegrated.com/en/app-notes/index.mvp/id/6269
# LO = 5800MHz
# REF = 40 MHz
# R = 1 (divisor de REF, no se puede cambiar?)
# N -> 7 bits (0 a 127)
# F -> 20 bits (0 a 1048575)
N = 0b01001000
F = 0b10000000000000000000
Flow = F & bitmask(10);
Fhigh = (F >> 10) & bitmask(10);

setLocalAddrs = [0, 0, 0x023];
standbyMode = [0, 0, 0x026];
rxMode = [0, 0, 0x02A];
doutEn = [0, 14,0x362];

def initBoard(boardAddrs):
    assert(boardAddrs<4)
    GPIO.output(A1, bitread(boardAddrs,0))
    GPIO.output(A2, bitread(boardAddrs,1))
    for i in xrange(len(default)):
        if not default[i][0]:
            writeReg(default[i])
            if default[i+1][0]:
                writeReg(setLocalAddrs)
        else:
            writeReg(default[i])
    writeReg(standbyMode)
    writeReg(doutEn)
    writeReg(15, (obtenerDef(15) & ~bitmask(7)) | N);
    writeReg(16, Fhigh);
    writeReg(17, Flow);
    writeReg(5,1)
    writeReg(rxMode)
    writeReg(5,0)

A1 = 15
A2 = 13

GPIO.setmode(GPIO.BOARD)
spi = spidev.SpiDev()

GPIO.setup(A1, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(A2, GPIO.OUT, initial=GPIO.LOW)

# Connects to the specified SPI device, opening /dev/spidev<bus>.<device>
# pi@raspberrypi:~/python $ ls /dev/spi*
# /dev/spidev0.0  /dev/spidev0.1
bus = 0
device = 0
spi.open(bus, device)
spi.max_speed_hz = 1000000

while 1:
    GPIO.output(A1, 0)
    GPIO.output(A2, 0)
    inp=raw_input("programar?\n")
    if(inp=='q'):
        break
    initBoard(0)
    initBoard(1)
    initBoard(2)
    initBoard(3)

GPIO.cleanup()
