def code() -> str:
    """
    Example G-code module, a drawing of a crocodile.

    Please simulate first, before milling.
    """
    return """
        G91
        G17
        G3 X20 Y0 I10 J0
        G0 X40 Y0
        G3 X6 Y0 I3 J0
        G0 X0 Y3
        G3 X-3 Y3 I-3 J0
        G0 X-40 Y0
        G2 X0 Y6 I0 J3
        G0 X40 Y0
        G3 X0 Y6 I0 J3
        G0 X-40 Y5
        G0 X-10 Y10
    """
