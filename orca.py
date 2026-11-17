# Add to top with other import statements:

from array import array

# Add to "Edit here" block, careful to not override text color cream

background = color(20, 70, 120)   # ocean blue (replaces the old background)
black = color(12, 12, 20)
white = color(245, 245, 250)
gray = color(150, 160, 175)       # saddle patch
water = color(170, 220, 255)      # spout

# Replace the draw cat method with this:

    def draw_orca(blinking, happy):
        scale = 0.70 if progress.sessions < 5 else (
            0.85 if progress.sessions < 10 else 1.0)

        def point(x, y):
            return int(120 + (x - 120) * scale), int(128 + (y - 125) * scale)

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

        # THIS DRAWS THE ORCA!
        ellipse(52, 128, 28, 13, black)                  # tail stock
        tri(46, 126, 12, 100, 28, 128, black)            # upper fluke
        tri(46, 130, 12, 156, 28, 128, black)            # lower fluke
        ellipse(120, 130, 78, 38, black)                 # body
        ellipse(125, 150, 58, 15, white)                 # belly
        tri(100, 95, 132, 95, 108, 58, black)            # dorsal fin
        ellipse(92, 106, 15, 5, gray)                    # saddle patch
        tri(142, 152, 122, 152, 128, 186, black)         # pectoral fin
        ellipse(160, 118, 14, 7, white)                  # eye patch

        # Eye (sits inside the white patch)
        if happy:
            line(156, 121, 161, 115, black)
            line(161, 115, 166, 121, black)
        elif blinking:
            line(157, 118, 167, 118, black)
        else:
            ellipse(162, 118, 3, 3, black)

        # Mouth
        line(198, 134, 174, 141, white)
        if happy:
            line(174, 141, 170, 137, white)

        if timer.phase == "BREAK":                       # Fish snack
            ellipse(212, 143, 8, 4, orange)
            tri(220, 143, 228, 138, 228, 148, orange)

        if happy:
            # Water spout from the blowhole
            line(150, 92, 150, 68, water)
            line(150, 68, 139, 60, water)
            line(150, 68, 161, 60, water)
            for x, y in ((48, 85), (190, 80), (45, 175), (196, 185)):
                canvas.hline(x - 4, y, 9, green)
                canvas.vline(x, y - 4, 9, green)
                
# Update the method call in the "While True" block (roughly around line 296)

draw_orca(blink_elapsed >= 3000, happy)


# You also will want to edit the names of the stages inside the "While True" loop :)