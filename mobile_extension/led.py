import RPi.GPIO as GPIO
import time
import logging
from threading import Thread

logger = logging.getLogger(__name__)


class Led(Thread):
    def __init__(self, channel_blue: int, channel_green: int, channel_red: int):
        Thread.__init__(self)
        # GPIO BOARD pin
        self.P_BLUE = channel_blue
        self.P_GREEN = channel_green
        self.P_RED = channel_red
        self.fPWM = 50  # Hz (not higher with software PWM)
        self.pwmR = None
        self.pwmG = None
        self.pwmB = None
        self.colour = 0  # 0: off, 1: blue; 2: green, 3 = red, 4 = success, 5 = failure
        self.fade = True
        self.init_leds()

    def run(self):
        while True:
            if self.colour == 0:
                self.leds_off()

            if self.fade:
                if self.colour == 1:
                    self.fade_blue()
                if self.colour == 2:
                    self.fade_green()
                if self.colour == 3:
                    self.fade_red()
            else:
                if self.colour == 4:
                    self.indicate_successful()
                if self.colour == 5:
                    self.indicate_failure()

    def init_leds(self):
        self.colour = 0  # off
        GPIO.setup(self.P_RED, GPIO.OUT)
        GPIO.setup(self.P_GREEN, GPIO.OUT)
        GPIO.setup(self.P_BLUE, GPIO.OUT)
        self.pwmR = GPIO.PWM(self.P_RED, self.fPWM)
        self.pwmG = GPIO.PWM(self.P_GREEN, self.fPWM)
        self.pwmB = GPIO.PWM(self.P_BLUE, self.fPWM)
        self.pwmR.start(0)
        self.pwmG.start(0)
        self.pwmB.start(0)

    def setColor(self, r, g, b):
        self.pwmR.ChangeDutyCycle(int(r / 255 * 100))
        self.pwmG.ChangeDutyCycle(int(g / 255 * 100))
        self.pwmB.ChangeDutyCycle(int(b / 255 * 100))

    def set_blue(self):
        self.colour = 1
        self.fade = True

    def set_green(self):
        self.colour = 2
        self.fade = True

    def set_red(self):
        self.colour = 3
        self.fade = True

    def set_success(self):
        self.fade = False
        self.colour = 4

    def set_failure(self):
        self.fade = False
        self.colour = 5

    def set_off(self):
        self.colour = 0
        self.fade = True

    def fade_green(self):
        for i in range(0, 10, 1):
            self.setColor(0, i, 0)
            time.sleep(.01)
        for i in range(10, 0, -1):
            self.setColor(0, i, 0)
            time.sleep(.01)

    def fade_blue(self):
        for i in range(0, 10, 1):
            self.setColor(0, 0, i)
            time.sleep(.01)
        for i in range(10, 0, -1):
            self.setColor(0, 0, i)
            time.sleep(.01)

    def fade_red(self):
        for i in range(0, 10, 1):
            self.setColor(i, 0, 0)
            time.sleep(.01)
        for i in range(10, 0, -1):
            self.setColor(i, 0, 0)
            time.sleep(.01)

    def leds_off(self):
        self.setColor(0, 0, 0)
        time.sleep(0.1)

    def indicate_successful(self):
        time.sleep(0.2)
        self.setColor(0, 50, 0)
        time.sleep(0.2)
        self.setColor(0, 0, 0)
        time.sleep(0.2)

    def indicate_failure(self):
        time.sleep(0.2)
        self.setColor(50, 0, 0)
        time.sleep(0.2)
        self.setColor(0, 0, 0)
        time.sleep(0.1)
