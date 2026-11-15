from machine import Pin, SPI
import time

cs = Pin(17, Pin.OUT, value=1)
dc = Pin(21, Pin.OUT, value=0)
reset = Pin(20, Pin.OUT, value=1)
spi = SPI(0, baudrate=10_000_000, polarity=0, phase=0,
          sck=Pin(18), mosi=Pin(19))

def command(number, data=None):
    cs.value(0)
    dc.value(0)
    spi.write(bytes([number]))
    if data is not None:
        dc.value(1)
        spi.write(data)
    cs.value(1)

reset.value(1)
time.sleep_ms(50)
reset.value(0)
time.sleep_ms(50)
reset.value(1)
time.sleep_ms(150)
command(0x01)
time.sleep_ms(150)
command(0x11)
time.sleep_ms(150)
command(0x3A, b"\x55")
command(0x36, b"\x00")
command(0x21)
command(0x13)
command(0x29)
time.sleep_ms(100)

def fill_screen(color):
    command(0x2A, b"\x00\x00\x00\xEF")
    command(0x2B, b"\x00\x00\x00\xEF")
    command(0x2C)
    pixel = bytes([color >> 8, color & 255])
    block = pixel * (240 * 10)
    cs.value(0)
    dc.value(1)
    for _ in range(24):
        spi.write(block)
    cs.value(1)

print("Screen test running. Click STOP to finish.")
while True:
    for name, value in [("RED", 0xF800), ("GREEN", 0x07E0),
                        ("BLUE", 0x001F), ("WHITE", 0xFFFF)]:
        print(name)
        fill_screen(value)
        time.sleep(2)
