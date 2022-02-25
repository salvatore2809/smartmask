import smart_mask as sm
import time
from adafruit_circuitplayground import cp
import led




INIT_STATE = 0
IDLE_STATE = 1
ERROR_STATE = 2
REC_STATE = 3

#setup
state = INIT_STATE
if state == INIT_STATE:
    #try:
    #recFile = File(time.monotonic(),"sensor_data")
    smart_mask = sm.Smart_mask()
    state = IDLE_STATE
    #except:
    #    state = ERROR_STATE



recLed = led.Led( ledPos = 9 , brightness = 0.05)
fsmStateLed = led.Led( ledPos = 5 , brightness = 0.05)
logFinished = False
forcedClosure = False

while True:

    if state == IDLE_STATE:
        #time.sleep(0.2)
        fsmStateLed.setColour(colour = [0,255,0])
        smart_mask.breath_monitor_service(0.1)
        if cp.button_a:
            state = REC_STATE

    if state == ERROR_STATE:
        time.sleep(0.2)
        fsmStateLed.setColour(colour = [255,0,0])
        #dead state

    if state == REC_STATE:

        recLed.blink(0.5)

        if cp.button_b:
            cp.play_tone(3440, 0.1)
            forcedClosure = True

        #try:
            #logFinished = myFile.logSensors(0, 300, forcedClosure)
        #logFinished = recFile.logSensorsNoDelay(forcedClosure)
        #except:
        #    state = ERROR_STATE

        smart_mask.breath_monitor_service(0.1)
        logFinished = smart_mask.log_sensors_on_file(0.1, forcedClosure)


        if logFinished:
            cp.play_tone(3440, 0.1)
            logFinished = False
            forcedClosure = False
            state = IDLE_STATE


