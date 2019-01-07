def code():
    return """
        G91 G17
        G0 X0 Y10
        G0 X5 Y0
        G2 X10 Y0 I5 J0
        G2 X-10 Y0 I-5 J0
        G2 X10 Y0 I5 J0
        G0 X10 Y0
        G2 X10 Y0 I5 J0
        G2 X-10 Y0 I-5 J0
        G2 X10 Y0 I5 J0
        G0 X5 Y0
        G0 X0 Y-10
        G0 X-40 Y0
        G0 X5 Y0
        G0 X5 Y-10
        G0 X20 Y0
        G0 X5 Y10
    """
