import board
import time
from adafruit_circuitplayground import cp

class Led:

    lastTimeBlink=0
    status=False
    position = 0

    def __init__(self, ledPos, brightness):
        self.lastTimeBlink = 0
        self.position = ledPos
        cp.pixels.brightness = brightness

    def blink(self, delaySec):
        currentTime = time.monotonic()
        if ((currentTime - self.lastTimeBlink) >= delaySec):
            self.lastTimeBlink = time.monotonic()
            if self.status==True:
                #cp.pixels[self.position] = (0, 255, 0)
                self.setColour((0, 255, 0))
            else:
                #cp.pixels[self.position] = (0, 0, 0)
                self.setColour((0, 0, 0))
            self.status = not(self.status)

    def setColour(self, colour = [0, 0, 0]):
        cp.pixels[self.position] = colour
