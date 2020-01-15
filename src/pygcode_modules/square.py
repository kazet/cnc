def code():
    """
    Example G-code module, a square.

    Please simulate first, before milling.
    """
    return """
        G91
        G0 X20 Y0
        G0 X0 Y20
        G0 X-20 Y0
        G0 X0 Y-20
    """
