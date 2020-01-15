def code() -> str:
    """
    Example G-code module, letter "q".

    Please simulate first, before milling.
    """
    return """
        G90
        G17
        G2 X20 Y0  I10 J0
        G2 X0 Y0 I-10 J0
        G2 X10 Y-10 I10 J0
        G0 X0 Y-10
        G0 X35 Y-10
    """
