##
##  AR.Drone2.0 Python controller
## by Team EXCALIBUR
## (use at your own risk)
##

import socket
import sys, tty, termios

def getChar():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def setBits( lst ):
    """
    set the bits in lst to 1.
    also set bits 18, 20, 22, 24, and 28 to one (since they should always be set)
    all other bits will be 0
    """
    res = 0
    for b in lst + [18,20,22,24,28]:
        res |= (1 << b)
    return res


def sendCommand( cmd ):
    global address
    global seqno
    global s
    print "DEBUG: Sending:  '%s'" % cmd.strip()
    s.sendto(cmd,address)
    seqno += 1


def reset():
    global seqno
    seqno = 1
    sendCommand("AT*FTRIM=%d\r" % seqno )


def takeoff():
    global seqno
    sendCommand("AT*FTRIM=%d\r" % seqno )
    takeoff_cmd = setBits([9])
    for i in xrange(1,25):
        sendCommand("AT*REF=%d,%d\r" % (seqno,takeoff_cmd))


def land():
    global seqno
    land_cmd = setBits([])
    for i in xrange(1,25):
        sendCommand("AT*REF=%d,%d\r" % (seqno,land_cmd))
    seqno += 1

def move(ch):
    # Pitch
    # W - forward
    # S - back

    # Roll
    # A - left
    # D - right

    # Gaz
    # up
    # down

    # Yaw
    # left
    # right
    global seqno
    move_cmd = setBits([0])
    roll = setRoll(ch)
    pitch = setPitch(ch)
    gaz = setGaz(ch)
    yaw = setYaw(ch)
    for i in xrange(1,25):
        sendCommand("AT*PCMD=%d,%d,%d,%d,%d,%d\r" % (seqno,move_cmd,roll,pitch,gaz,yaw))

    pass

def setRoll(ch):
    # left/right
    if ch == 'a':
        return -1082130432
    if ch == 'd':
        return 1065353216
    return 0

def setPitch(ch):
    # front/back
    if ch == 'w':
        return -1082130432
    if ch == 's':
        return 1065353216
    return 0

def setGaz(ch):
    # up/down spped
    if ch == 'j':
        return -1082130432
    if ch == 'u':
        return 1065353216
    return 0

def setYaw(ch):
    #angular speed
    if ch == 'h':
        return -1082130432
    if ch == 'k':
        return 1065353216
    return 0

def toggleEmergencyMode():
    global seqno
    shutdown_cmd = setBits([8])
    sendCommand("AT*REF=%d,%d\r" % (seqno,shutdown_cmd))

def printUsage():
    print "\n\n"
    print "Keyboard commands:"
    print "\tq       - quit"
    print "\tt       - takeoff"
    print "\tl       - land"
    print "\t(space) - emergency shutoff"



print """
NOTE:  This program assumes you are already connected to the
       drone's WiFi network.
"""

address = ('192.168.1.1',5556)
seqno = 1
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("", 5554))


while True:
    printUsage()
    ch = getChar()
    if ch == 'q':
        exit(0)
    elif ch == 't':
        takeoff()
    elif ch == 'l':
        land()
    elif ch == ' ':
        reset()
        toggleEmergencyMode()
    #elif ch in ['w', 's', 'a', 'd', 'u','h', 'j', 'k'] :
        pass#move(ch)
    else:
        print "Invalid command!"
