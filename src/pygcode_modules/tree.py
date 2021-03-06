def code() -> str:
    """
    Example G-code module, a tree.

    Please simulate first, before milling.
    """
    return """
        G91
        G0 X13 Y13
        G0 X6 Y6
        G0 X4 Y4
        G0 X-4 Y-4
        G0 X-4 Y4
        G0 X4 Y-4
        G0 X-6 Y-6
        G0 X-6 Y6
        G0 X4 Y4
        G0 X-4 Y-4
        G0 X-4 Y4
        G0 X4 Y-4
        G0 X6 Y-6
        G0 X-13 Y-13
        G0 X-13 Y13
        G0 X6 Y6
        G0 X4 Y4
        G0 X-4 Y-4
        G0 X-4 Y4
        G0 X4 Y-4
        G0 X-6 Y-6
        G0 X-6 Y6
        G0 X4 Y4
        G0 X-4 Y-4
        G0 X-4 Y4
        G0 X4 Y-4
        G0 X6 Y-6
    """
