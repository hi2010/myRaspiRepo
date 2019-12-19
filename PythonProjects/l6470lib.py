"""
My .

Docstring
"""


from threading import Timer  # noqa
from threading import Thread
import spidev
import time

# make all methods thread safe (more or less, problems may occur on reset device)
#                               (as in behaviour not as needed / wantet, but easy)
#                               (fixable)
from threading import Lock
myLock = Lock()

# init spi
spi = spidev.SpiDev()
spi.open(0, 0)
spi.mode = 3
# speed prbly limited by wires
# spi.max_speed_hz = 15200
# spi.max_speed_hz = 3900000
spi.max_speed_hz = 7800000  # max from testing
# spi.max_speed_hz = 15600000
# spi.max_speed_hz = 31200000
# spi.max_speed_hz = 62500000
# spi.max_speed_hz = 125000000

# ------------- register adresses ------------
# datasheet 9.1, p.: 40/41
#                   # len:
ABS_POS = 0x01      # 22
EL_POS = 0x02       # 9
MARK = 0x03         # 22
SPEED = 0x04        # 20
ACC = 0x05          # 12
DEC = 0x06          # 12
MAX_SPEED = 0x07    # 10
MIN_SPEED = 0x08    # 13
FS_SPD = 0x15       # 10
KVAL_HOLD = 0x09    # 8
KVAL_RUN = 0x0A     # 8
KVAL_ACC = 0x0B     # 8
KVAL_DEC = 0x0C     # 8
INT_SPEED = 0x0D    # 14
ST_SLP = 0x0E       # 8
FN_SLP_ACC = 0x0F   # 8
FN_SLP_DEC = 0x10   # 8
K_THERM = 0x11      # 4
ADC_OUT = 0x12      # 5
OCD_TH = 0x13       # 4
STALL_TH = 0x14     # 7
STEP_MODE = 0x16    # 8
ALARM_EN = 0x17     # 8
CONFIG = 0x18       # 16
STATUS = 0x19       # 16

# KVAL's are relative to current and power during the operation
# therefore a higher kval means higher force
# but i guess stall_th needs to be adjusted acordingly

# --------------------------------------------
#
#
#
#  reset
spi.xfer([0xC0])

#  -----------test move -----------
testMove = 0
if testMove == 1:
    #  run command, dir
    spi.xfer2([0x50])
    # speed
    spi.xfer2([0x00])
    spi.xfer2([0x31])
    spi.xfer2([0x51])

    # pause
    time.sleep(5)

    # run command, dir
    spi.xfer2([0x51])
    # speed
    spi.xfer2([0x00])
    spi.xfer2([0x31])
    spi.xfer2([0x51])

    # pause
    time.sleep(5)

    # soft stop
    spi.xfer([0xB0])

    # get status
    spi.xfer([0xE0])
    a = spi.readbytes(2)
    for i in a:
        print(i)


def getStatus():
    """
    Not sure right now, if like in datasheet or different.

    Read statusregister.
    """
    myLock.acquire()
    a = spi.xfer([0xD0])
    b = spi.readbytes(2)
    myLock.release()
    return a + b


def softStop():
    """
    Like in datasheet.

    Stops motor slower but softer.
    """
    myLock.acquire()
    spi.xfer([0xB0])
    myLock.release()


def hardStop():
    """
    Like in datasheet.

    Stops motor fast.
    """
    myLock.acquire()
    spi.xfer([0xB8])
    myLock.release()


def softHiZ():
    """
    Like in datasheet.

    Sets driver to high z mode (soft).
    """
    myLock.acquire()
    spi.xfer([0xA8])
    myLock.release()


# --------- set param get param ---------
print("param Test")
# spi.xfer(0b000param)
spi.xfer([0x14])  # set param stall th reg
spi.xfer([0x48])

# for registers with len % 8 != 0
# first x bit are ignored (of msb)


def setParam(param, val):
    """
    Write to registers.

    Param is the register address like defined at the begining of this file.
    Val is the value which is written to the register [type=list].
    Length of val needs to be right size.
    Otherwise 'strange' behaviour may occur.
    """
    myLock.acquire()
    spi.xfer([(param & 0x1F)])  # register val /param
    if len(val) > 0:
        for i in val:
            # print(i)
            spi.xfer([i])
        myLock.release()
    else:
        myLock.release()
        print("no val given")


def getParam(param, lenInBytes):
    """
    Read from registers.

    Param is the register address like defined at the begining of this file.
    LenInBytes is the expected number of bytes from the register.
    """
    res = []
    myLock.acquire()
    res += spi.xfer([(param + 0x20) & 0x3F])  # register val /param
    # print("res: ", res)
    if lenInBytes > 0:
        for i in range(lenInBytes):
            res += spi.readbytes(1)
    myLock.release()
    res[0] = res[0] + res[len(res)-1]
    res.pop()
    #  print("retres2: ", res)
    #  msb gets send first but in this case added to back, therefor reverse is
    #  necessary maybe this is faster than insert(0,x), but dunno.
    res.reverse()
    return res


def goHome():
    """
    Like in datasheet.

    Moves motor to driver home position.
    """
    myLock.acquire()
    spi.xfer([0x70])
    myLock.release()


def byteListToNum(val):
    """
    Convert list of bytes to one integer.

    val.type==list<integer(bytes)>
    """
    res = 0
    ln = len(val)
#  print("ln: ", ln)
    for i in range(ln):
        #    print("vali: ", val[i], " shiftn: ", (ln-i-1))
        res += (val[i] << (8 * (ln-i-1)))
#    print("res: ", hex(res))
    return res


def initDevice():
    """
    Initialize device, set certain register values and check if writing worked.

    These values are application specific and need to be set to fit needs.
    Other registers may need to be set for some cases.
    """
    # set param stall th reg
    assertVal = [0x2a]
    assertReg = STALL_TH
    setParam(assertReg, assertVal)
    print("Stall_TH: ", hex(byteListToNum(getParam(assertReg, len(assertVal)))))
    assert byteListToNum(getParam(assertReg, len(assertVal))) == byteListToNum(assertVal)

    # test acc reg read write
    assertVal = [0x00, 0x0F]
    assertReg = ACC
    setParam(assertReg, assertVal)
    print("ACC: ", hex(byteListToNum(getParam(assertReg, len(assertVal)))))
    assert byteListToNum(getParam(assertReg, len(assertVal))) == byteListToNum(assertVal)

    assertVal = [0x00, 0x24]
    assertReg = MAX_SPEED
    setParam(assertReg, assertVal)
    print("MaxSpeed: ", hex(byteListToNum(getParam(assertReg, len(assertVal)))))
    assert byteListToNum(getParam(assertReg, len(assertVal))) == byteListToNum(assertVal)

    assertVal = [0x4F]
    assertReg = KVAL_ACC
    setParam(assertReg, assertVal)
    print("KVAL_ACC: ", hex(byteListToNum(getParam(assertReg, len(assertVal)))))
    assert byteListToNum(getParam(assertReg, len(assertVal))) == byteListToNum(assertVal)

    assertVal = [0x4F]
    assertReg = KVAL_RUN
    setParam(assertReg, assertVal)
    print("KVAL_RUN: ", hex(byteListToNum(getParam(assertReg, len(assertVal)))))
    assert byteListToNum(getParam(assertReg, len(assertVal))) == byteListToNum(assertVal)

    assertVal = [0x4E]
    assertReg = KVAL_DEC
    setParam(assertReg, assertVal)
    print("KVAL_DEC: ", hex(byteListToNum(getParam(assertReg, len(assertVal)))))
    assert byteListToNum(getParam(assertReg, len(assertVal))) == byteListToNum(assertVal)


#  init device, so that it has a defined state.
initDevice()


def resetDevice():
    """
    Reset device and reinitialise afterwards.

    Resets device, waits for .2 seconds and initializes the device afterwards.
    This function may create problems if called in an multithread environment,
    because the motor might be moved before the device is reinitialised.
    """
    myLock.acquire()
    spi.xfer([0xC0])
    time.sleep(.2)
    myLock.release()
    initDevice()


print("register test successfull !!!")


# homing with switch
def releaseSW(Act, Dir):
    """Not yet initialised."""
    pass


def homeAxe():
    """Not yet initialised."""
    pass


# get param
a = spi.xfer([0x35])
b = spi.readbytes(1)
print("Answer to writen: ", a[0], " read byte: ", b[0], " : ", bin(a[0]), bin(b[0]))


# read status
def readStatus(printStatus=None):
    """
    Not sure right now, if like in datasheet or different.

    Read statusregister.
    """
    myLock.acquire()
    spi.xfer([0x39])
    a = spi.readbytes(2)
    myLock.release()
    if printStatus is not None:
        print("status : ", a[0], b[0], bin(a[0]), bin(b[0]))
    return a


readStatus()

# -----------------------stall test ------
# set alarm condition to stall
# error reg val
# 0x30
# stall_th in steps of 31.25 mA stall detect (7 bit) up to 4A
stallTestEnb = 0
if stallTestEnb != 0:
    time.sleep(2)
    print("Stall Test started")

    # run command, dir
    spi.xfer2([0x51])
    # speed
    spi.xfer2([0x00])
    spi.xfer2([0x51])
    spi.xfer2([0x51])

    # get status
    b = spi.xfer([0xD0])
    print("b: ", b[0])
    a = spi.readbytes(2)
    time.sleep(1)

    stat = [0xFF]
    while((stat[0] & 0x60) != 0):
        stat = readStatus()
        print("stat: ", stat[0], stat[1], " : ", bin(stat[0]), bin(stat[1]))

    # soft stop
    spi.xfer([0xB0])

    time.sleep(2)
    print("Stall Test 2 started")

    # run command, dir
    spi.xfer([0x50])
    # speed
    spi.xfer([0x00])
    spi.xfer([0x51])
    spi.xfer([0x51])

    # get status
    b = spi.xfer([0xD0])
    print("b: ", b[0])
    a = spi.readbytes(2)
    time.sleep(1)

    stat = [0xFF]
    while((stat[0] & 0x60) != 0):
        stat = readStatus()
        print("stat: ", stat[0], stat[1], " : ", bin(stat[0]), bin(stat[1]))

    # soft stop
    spi.xfer([0xB0])


def stopOnStall(maxNumOfLoops=None, printRes=None, sleepTime=0):
    """Stop the motor if stall is detected."""
    loopNum = 0
    stat = [0xFF]

    # while no error has occured loop
    while not(((stat[0] & 0x40) == 0) or ((stat[0] & 0x20) == 0)):
        stat = readStatus()

        # print for debug purposes
        if printRes is not None:
            print("stat: ", stat[0], stat[1], " : ", bin(stat[0]), bin(stat[1]))

        # break loop if maxNumOfLoops is reached
        if maxNumOfLoops is not None:
            if loopNum > maxNumOfLoops:
                print("maxNumOfLoops reahed in stopOnStall")
                return 0

        loopNum += 1
        time.sleep(sleepTime)

    hardStop()
    # not sure if needed
    time.sleep(.1)
    #  GetStatus [...] resets [...] STATUS register warning flags.
    getStatus()

    print("Stall detected exiting stopOnStall")
    return 1


def run(direction, speed):
    """
    Like in datasheet.

    Moves motor in direction at speed.
    direction 1 / 0 cw ccw or the other way round.
    speed is a 3 byte number like speed=0x123456 .
    """
    if direction == 0:
        # run command, dir
        myLock.acquire()
        spi.xfer([0x50])
    else:
        myLock.acquire()
        spi.xfer([0x51])
    # speed
    spi.xfer([(speed >> 16) & 0xFF])
    spi.xfer([(speed >> 8) & 0xFF])
    spi.xfer([speed & 0xFF])
    myLock.release()


def goTo(absPos):
    """
    Like in datasheet.

    Moves motor to driver position absPos.
    """
    myLock.acquire()
    spi.xfer([0x60])
    spi.xfer([(absPos >> 16) & 0x3F])
    spi.xfer([(absPos >> 8) & 0xFF])
    spi.xfer([absPos & 0xFF])
    myLock.release()


def move(direction, nStep):
    """
    Like in datasheet.

    Moves motor in direction for n steps.
    """
    if direction != 0:
        myLock.acquire()
        spi.xfer([0x41])
    else:
        myLock.acquire()
        spi.xfer([0x40])
    spi.xfer([(nStep >> 16) & 0x3F])
    spi.xfer([(nStep >> 8) & 0xFF])
    spi.xfer([nStep & 0xFF])
    myLock.release()

# reset
# spi.xfer([0xC0])


print("stall test finisehd")

# ------------------- Tests with multithreading ---------------------


class StallAgent(Thread):
    """
    Used for testing.

    This class may be started as thread and will detect if stall occured.
    If stall occured the motor will be stopped.
    """

    def __init__(self, checkTime, timeout, maxNumOfLoops=100):
        """Doc pass."""
        Thread.__init__(self)
        self.checkTime = checkTime
        self.spi = spi
        self.timeout = timeout
        self.maxNumOfLoops = maxNumOfLoops

    def setIsRunningFalse(self):
        """Doc pass."""
        print("is not running?")
        self.isRunning = False

    def run(self):
        """Doc pass."""
        self.isRunning = True
        # t = Timer(self.timeout, self.setIsRunningFalse)
        # t.start()
        while self.isRunning:
            print(readStatus())
            # time.sleep(self.checkTime)
            tmp = stopOnStall(sleepTime=self.checkTime)
            if tmp != 0:
                print("stallAgent detected Stall, now shuting down")
                # print("stallAgent is set to stay alive")
                self.isRunning = False


class moveAgent(Thread):
    """
    Used for testing.

    This class may be started as a thread.
    The motor wi be started every 10 seconds and moved in the other direction.
    """

    def __init__(self, width=0x050000):
        """Doc pass."""
        Thread.__init__(self)
        self.width = width

    def run(self):
        """Doc pass."""
        while True:
            print("moveAgnet running dir=1")
            move(0, self.width)
            # break
            time.sleep(10)
            print("moveAgnet running dir=0")
            move(1, self.width)
            time.sleep(10)

# run(0, 0x010000)
# move(1, 0x040000)
# stallAg = StallAgent(.2, 1000)
# stallAg.start()
# mvAg = moveAgent()
# mvAg.start()
# stallAg.terminate()
