from machine import Pin
import time

button = Pin(14, Pin.IN, Pin.PULL_UP)
previous = -1

while True:
    current = button.value()
    if current != previous:
        if current == 0:
            print("PRESSED!")
        else:
            print("RELEASED")
        previous = current
    time.sleep_ms(50)
