# Add to top with other import statements:

from array import array

# Add to "Edit Here" block with colors, being careful to not get rid of the text color!
#Also keep your pink, orange, and green colors

background = color(30, 80, 75)    # marsh green (replaces the old background)
brown = color(150, 100, 55)       # fur
fur_dark = color(105, 68, 38)     # ear, fur marks
tan = color(195, 150, 95)         # belly and snout
nose = color(40, 25, 20)          # nose, eye, mouth
red = color(235, 70, 80)          # watermelon

# Replace drawCat() method with drawCapybara()

    def draw_capybara(blinking, happy):
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

        def ellipse(cx, cy, rx, ry, ink):
            x, y = point(cx, cy)
            canvas.ellipse(x, y, max(1, int(rx * scale)),
                           max(1, int(ry * scale)), ink, True)

        def tri(x1, y1, x2, y2, x3, y3, ink):
            a, b = point(x1, y1)
            c, d = point(x2, y2)
            e, f = point(x3, y3)
            canvas.poly(0, 0, array('h', [a, b, c, d, e, f]), ink, True)

        # THIS DRAWS THE CAPYBARA!
        # Legs (stubby)
        rect(52, 160, 18, 28, fur_dark)                  # back leg
        rect(78, 164, 16, 24, brown)                     # back leg (near)
        rect(118, 160, 18, 28, fur_dark)                 # front leg
        rect(138, 164, 16, 24, brown)                    # front leg (near)

        # Barrel-shaped body
        ellipse(100, 138, 64, 36, brown)
        ellipse(100, 158, 46, 12, tan)                   # belly
        for x in (60, 80, 100):                          # fur texture
            line(x, 112, x + 6, 120, fur_dark)

        # Head and big boxy snout
        ellipse(158, 118, 28, 26, brown)
        ellipse(182, 126, 20, 17, tan)
        ellipse(198, 119, 4, 6, nose)                    # nose
        line(178, 139, 194, 139, nose)                   # mouth
        if happy:
            line(194, 139, 197, 135, nose)

        # Ear
        ellipse(142, 98, 7, 6, fur_dark)

        # Eye
        if happy:
            line(160, 114, 165, 108, nose)
            line(165, 108, 170, 114, nose)
        elif blinking:
            line(161, 110, 171, 110, nose)
        else:
            ellipse(166, 110, 3, 4, nose)

        # Orange on its head
        ellipse(156, 90, 9, 9, orange)
        line(156, 81, 160, 77, green)

        if timer.phase == "BREAK":                       # Watermelon slice
            tri(196, 160, 232, 160, 214, 188, green)
            tri(201, 160, 227, 160, 214, 182, red)

        if happy:
            for x, y in ((45, 90), (200, 80), (40, 185), (210, 150)):
                canvas.hline(x - 4, y, 9, green)
                canvas.vline(x, y - 4, 9, green)
                
#Replace method call in the While True loop
                
draw_capybara(blink_elapsed >= 3000, happy)

# Optionally change the names in the While True loop to reflect whatever you wish!

# You also do not have to keep the orange - you can delete
# that block if you do not like it