import math

print("G90")
RADIUS = 15
NUM_SIDES = 7
for i in range(NUM_SIDES):
    x = RADIUS - RADIUS * math.cos(2 * math.pi * i / NUM_SIDES)
    y = RADIUS * math.sin(2 * math.pi * i / NUM_SIDES)
    print("G0 X%0.2f Y%0.2f" % (
        x,
        y
    ))

print("G0 X0 Y0")
