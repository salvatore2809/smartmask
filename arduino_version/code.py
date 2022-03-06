import fsm_main
fsm_main.run_fsm()
'''
import time
import board
import busio
#from adafruit_circuitplayground.express import cpx

uart = busio.UART(board.TX, board.RX, baudrate=9600)
str_col=""
tzero=time.monotonic()
while True:

    data = uart.read(1)  # read a byte

    if data is not None:  # Data was received
        str_col+=data.decode()
        #output = "%0.1f\t%d\t%0.1f\r\n" % (time.monotonic(),
        #                                   cpx.light, cpx.temperature)
        #uart.write(output)         # Print to serial
        if data.decode()=='\n':
            #print(str(time.monotonic())+" "+str_col)

            if "gas" in str_col:
                gas = float(str_col[-8:-1])
                print(str(time.monotonic())+" "+str(gas))
            str_col=""

        #time.sleep(0.3)
'''
