def code() -> str:
    """
    Example G-code module, a drawing of the number "5".

    Please simulate first, before milling.
    """
    return """
        G90
        G17
        G00 X0 Y0
        G00 X0 Y12.5
        G02 I7.5 J0 X7.5 Y20
        G00 X17.5 Y20
        G02 I0 J-7.5 X25.001 Y12.5
        G00 X25.001 Y0
        G00 X45 Y0
        G00 X45 Y20
    """
