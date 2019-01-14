def code():
    return """
        G91 G17
        G0 Y10 X-10
        G0 Y0 X-5
        G0 Y5 X0
        G0 Y0 X5
        G0 Y0 X-5
        G0 Y-5 X0
        G3 Y-5 X5 J0 I5
        G0 Y0 X5
        G0 Y5 X0
        G3 Y5 X-5 J0 I-5
        G0 Y-5 X0
        G0 Y-10 X10
        G0 Y0 X-5
        G0 Y-15 X-15
        G0 Y0 X5
        G0 Y5 X0
        G0 Y0 X-5
        G0 Y-5 X0
        G0 Y5 X0
        G2 Y5 X5 J0 I5
        G0 Y0 X5
        G0 Y-5 X0
        G2 Y-5 X-5 J0 I-5
        G0 Y5 X0
        G0 Y10 X10
        G0 Y0 X-30
        G3 Y0 X-10 J0 I-5
        G3 Y0 X10 J0 I5

        G0 Y0 X5
        G3 Y5 X5 J5 I0
        G3 Y10 X-10 J0 I-10
        G3 Y-5 X-5 J-5 I0
        G0 Y-5 X0

        G0 Y5 X0
        G3 Y5 X-5 J0 I-5
        G3 Y-10 X-10 J-10 I0
        G3 Y-5 X5 J0 I5
        G0 Y0 X5

        G0 Y0 X-5
        G3 Y-5 X-5 J-5 I0
        G3 Y-10 X10 J0 I10
        G3 Y5 X5 J5 I0
        G0 Y5 X0

        G0 Y-5 X0
        G3 Y-5 X5 J0 I5
        G3 Y10 X10 J10 I0
        G3 Y5 X-5 J0 I-5
        G0 Y0 X-5
    """
