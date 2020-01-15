def code() -> str:
    """
    Example G-code module, letter "x".

    Please simulate first, before milling.
    """
    return """
        G91
        F60
        G0 X-3 Y-3
        G0 X3 Y3
        G0 X3 Y-3
        G0 X-3 Y3
        G0 X3 Y3
        G0 X-3 Y-3
        G0 X-3 Y3
        G0 X3 Y-3
    """
