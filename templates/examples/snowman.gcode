G91
G17

# left circle
G2 X20 Y20 I0 J20
G2 X-20 Y-20 I-20 J0

# go to farthest right point of the left circle
G2 X20 Y20 I0 J20

# middle circle
G2 X15 Y15 I15 J0
G2 X-15 Y-15 I0 J-15

# go to farthest top point of the middle circle
G2 X15 Y15 I15 J0

# hand with fingers
G0 X9 Y12
G0 X0 Y5
G0 X0 Y-5
G0 X3 Y3.5
G0 X-3 Y-3.5
G0 X5 Y0
G0 X-5 Y0
G0 X-9 Y-12

# go to farthest bottom point of the middle circle
G2 X0 Y-30 I0 J-15

# hand with fingers
G0 X9 Y-12
G0 X0 Y-5
G0 X0 Y5
G0 X3 Y-3.5
G0 X-3 Y3.5
G0 X5 Y0
G0 X-5 Y0
G0 X-9 Y12

# go to farthest right point of the middle circle
G3 X15 Y15 I0 J15

# right circle
G2 X10 Y10 I10 J0
G2 X-10 Y-10 I0 J-10

