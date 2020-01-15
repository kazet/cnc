def code() -> str:
    """
    Example G-code module, a 40mm circle.

    Please simulate first, before milling.
    """
    return """
        G90
        G17
        G2 X0 Y40 I0 J20
        G2 X0 Y0 I0 J-20
    """
