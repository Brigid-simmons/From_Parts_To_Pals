"""Pico 2 W + 240x240 ST7789 + button on GP14.
Save a copy on the Pico as main.py for automatic startup.
TEST_MODE uses its own saved progress. Change to False for real sessions.
No calendar clock, internet, external libraries, or extra wiring required.
"""
from machine import Pin, SPI
import framebuf
import time
import json
import os

# Change ONLY True to False after completing the short tests.
TEST_MODE = True
# EDIT ME! (Change FOCUS_MS, BREAK_MS, or LONG_BREAK_MS to match your study preferences)
FOCUS_MS = 10_000 if TEST_MODE else 25 * 60 * 1000
BREAK_MS = 5_000 if TEST_MODE else 5 * 60 * 1000
LONG_BREAK_MS = 8_000 if TEST_MODE else 15 * 60 * 1000
SAVE_PREFIX = "buddy_test" if TEST_MODE else "buddy_real"


# Don't worry about the classes - these just serve as blueprints to keep our program
# functioning correctly :)
class Progress:
    # Alternate two files: an interrupted write leaves the previous one intact.
    def __init__(self, prefix):
        self.prefix = prefix
        self.sessions = 0
        self.seq = 0
        self.slot = 1
        self.warning = ""
        valid = []
        damaged = False
        for slot in (0, 1):
            path = "%s_%d.json" % (prefix, slot)
            try:
                with open(path) as file:
                    record = json.load(file)
                count = record["sessions"]
                seq = record["seq"]
                if (record["version"] != 1 or type(count) is not int
                        or type(seq) is not int or count < 0 or seq < 0
                        or record["check"] != (count ^ seq ^ 0x51CA)):
                    raise ValueError("Invalid progress record")
                valid.append((seq, count, slot))
            except OSError as error:
                if error.args and error.args[0] != 2:
                    damaged = True
            except (ValueError, KeyError, TypeError):
                damaged = True
        if valid:
            self.seq, self.sessions, self.slot = max(valid)
        elif damaged:
            self.warning = "Save unreadable: check Shell"
            print("Progress files unreadable; starting at zero.")
        if damaged and valid:
            print("Recovered progress from the other save file.")

    def save(self):
        next_seq = self.seq + 1
        next_slot = 1 - self.slot
        record = {"version": 1, "sessions": self.sessions,
                  "seq": next_seq,
                  "check": self.sessions ^ next_seq ^ 0x51CA}
        try:
            with open("%s_%d.json" % (self.prefix, next_slot), "w") as file:
                json.dump(record, file)
            if hasattr(os, "sync"):
                os.sync()
            self.seq = next_seq
            self.slot = next_slot
            self.warning = ""
            return True
        except OSError as error:
            self.warning = "SAVE FAILED: check Shell"
            print("SAVE FAILED:", error)
            return False


class Timer:
    def __init__(self, progress):
        self.progress = progress
        self.phase = "FOCUS"
        self.state = "READY"
        self.remaining = FOCUS_MS
        self.long_break = False

    def advance(self, milliseconds):
        if self.state != "RUNNING":
            return
        self.remaining = max(0, self.remaining - milliseconds)
        if self.remaining == 0:
            self.state = "DONE"
            if self.phase == "FOCUS":
                self.progress.sessions += 1
                self.progress.save()
                print("Focus complete. Total:", self.progress.sessions)
            else:
                print("Break complete. Press for the next focus session.")

    def press(self):
        if self.state in ("READY", "PAUSED"):
            self.state = "RUNNING"
        elif self.state == "RUNNING":
            self.state = "PAUSED"
        elif self.phase == "FOCUS":
            self.phase = "BREAK"
            self.long_break = self.progress.sessions % 4 == 0
            self.remaining = LONG_BREAK_MS if self.long_break else BREAK_MS
            self.state = "RUNNING"
        else:
            self.phase = "FOCUS"
            self.remaining = FOCUS_MS
            self.state = "RUNNING"


def run():
    # This is run() function, which puts all our previous classes together to form the program
    progress = Progress(SAVE_PREFIX)
    timer = Timer(progress)
    cs = Pin(17, Pin.OUT, value=1)
    dc = Pin(21, Pin.OUT, value=0)
    reset = Pin(20, Pin.OUT, value=1)
    button = Pin(14, Pin.IN, Pin.PULL_UP)
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

    # Allow power to settle during a cold USB startup.
    time.sleep_ms(250)
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

    buffer = bytearray(240 * 240 * 2)
    canvas = framebuf.FrameBuffer(buffer, 240, 240, framebuf.RGB565)

    def color(r, g, b):
        value = ((r & 248) << 8) | ((g & 252) << 3) | (b >> 3)
        return ((value & 255) << 8) | (value >> 8)
    
    # EDIT HERE
    # Change colors to whatever you'd like!
    background = color(25, 30, 45)
    orange = color(245, 155, 45)
    stripe = color(175, 85, 20)
    pink = color(255, 155, 170)
    dark = color(35, 25, 20)
    cream = color(255, 235, 200) # text color
    green = color(120, 230, 140)

    def text(message, y, ink=cream):
        canvas.text(message, (240 - len(message) * 8) // 2, y, ink)

    def show():
        command(0x2A, b"\x00\x00\x00\xEF")
        command(0x2B, b"\x00\x00\x00\xEF")
        command(0x2C)
        cs.value(0)
        dc.value(1)
        spi.write(buffer)
        cs.value(1)

    def draw_cat(blinking, happy):
        scale = 0.70 if progress.sessions < 5 else (
            0.85 if progress.sessions < 10 else 1.0)

        def point(x, y):
            return int(120 + (x - 120) * scale), int(128 + (y - 125) * scale)

        def rect(x, y, w, h, ink):
            x, y = point(x, y)
            canvas.fill_rect(x, y, max(1, int(w * scale)),
                             max(1, int(h * scale)), ink)

        def line(x1, y1, x2, y2, ink):
            x1, y1 = point(x1, y1)
            x2, y2 = point(x2, y2)
            canvas.line(x1, y1, x2, y2, ink)
        
        # THIS DRAWS THE CAT!
        rect(151, 149, 29, 13, orange)
        rect(171, 125, 13, 35, orange)
        rect(171, 132, 13, 6, stripe)
        rect(89, 139, 64, 43, orange)
        rect(80, 174, 33, 13, orange)
        rect(130, 174, 33, 13, orange)
        for row in range(28):
            rect(76, 62 + row, row + 1, 2, orange)
            rect(163 - row, 62 + row, row + 1, 2, orange)
        for row in range(16):
            rect(81, 70 + row, row + 1, 2, pink)
            rect(158 - row, 70 + row, row + 1, 2, pink)
        rect(76, 88, 88, 61, orange)
        rect(108, 88, 6, 15, stripe)
        rect(124, 88, 6, 15, stripe)
        if happy:
            for x in (94, 134):
                line(x, 116, x + 6, 110, dark)
                line(x + 6, 110, x + 12, 116, dark)
        elif blinking:
            rect(94, 113, 12, 3, dark)
            rect(134, 113, 12, 3, dark)
        else:
            rect(97, 108, 6, 12, dark)
            rect(137, 108, 6, 12, dark)
        rect(117, 124, 8, 5, pink)
        line(121, 129, 121, 135, dark)
        line(115, 135, 121, 135, dark)
        line(122, 135, 128, 135, dark)
        for y in (125, 134):
            line(65, y, 85, y, cream)
            line(154, y, 174, y, cream)
        if timer.phase == "BREAK":
            rect(106, 163, 25, 10, pink)  # Food bowl
        if happy:
            for x, y in ((48, 85), (190, 80), (45, 155), (196, 165)):
                canvas.hline(x - 4, y, 9, green)
                canvas.vline(x, y - 4, 9, green)

    now = time.ticks_ms()
    last_tick = now
    last_draw = time.ticks_add(now, -200)
    blink_start = now
    changed_at = now
    raw_button = button.value()
    stable_button = raw_button
    print("TEST MODE" if TEST_MODE else "REAL POMODORO MODE")
    print("Loaded completed focus sessions:", progress.sessions)
    print("Press: start / pause / resume / next phase.")

    while True:
        now = time.ticks_ms()
        elapsed = time.ticks_diff(now, last_tick)
        last_tick = now
        timer.advance(elapsed)

        reading = button.value()
        if reading != raw_button:
            raw_button = reading
            changed_at = now
        if time.ticks_diff(now, changed_at) >= 40:
            if stable_button != raw_button:
                stable_button = raw_button
                if stable_button == 0:
                    timer.press()

        blink_elapsed = time.ticks_diff(now, blink_start)
        if blink_elapsed >= 3200:
            blink_start = now
            blink_elapsed = 0
        if time.ticks_diff(now, last_draw) >= 150:
            last_draw = now
            canvas.fill(background)
            count = progress.sessions
            stage = "KITTEN" if count < 5 else ("YOUNG CAT" if count < 10 else "ADULT CAT")
            text("%s - %d focus" % (stage, count), 8)
            label = "LONG BREAK" if timer.phase == "BREAK" and timer.long_break else timer.phase
            if TEST_MODE:
                label = "TEST " + label
            text(label, 25)
            seconds = (timer.remaining + 999) // 1000
            text("%02d:%02d" % (seconds // 60, seconds % 60), 42)
            happy = timer.phase == "FOCUS" and timer.state == "DONE"
            draw_cat(blink_elapsed >= 3000, happy)

            if timer.state == "DONE":
                if timer.phase == "FOCUS":
                    message = "Fed! Press for break"
                else:
                    message = "Press for next focus"
            elif timer.state == "PAUSED":
                message = "Paused: press to resume"
            elif timer.state == "READY":
                message = "Hungry? Press to focus" if count == 0 else "Press to start focus"
            else:
                message = "Resting: press to pause" if timer.phase == "BREAK" else "Focusing: press to pause"
            text(message, 206, green if happy else cream)
            if progress.warning:
                text(progress.warning, 224, pink)
            elif count < 10:
                text("Next growth: %d/5" % (count % 5), 224)
            else:
                text("All grown! Keep focusing", 224)
            show()
        time.sleep_ms(10)


if __name__ == "__main__":
    run()
