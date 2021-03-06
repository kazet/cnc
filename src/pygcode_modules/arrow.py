def code() -> str:
    """
    Example G-code module, an arrow.

    Please simulate first, before milling.
    """
    return ("""
        G91
        G0 X0 Y2
        G0 X0 Y-4
        G0 X0 Y2
        G0 X-20 Y0
        G0 X40 Y0
        G0 X-5 Y-5
        G0 X5 Y5
        G0 X-5 Y5
        G0 X5 Y-5
    """)
