import math

def code(radius=35, hole_spacing=8, hole_radius=1.75, safe_height=5):
    """
    This example drills a filled, circular pattern consisting of small holes.
    
    Arguments:
        radius: circle radius
        hole_spacing: the distance between hole centers
        hole_radius: hole radius
        safe_height: the Z height to move the tool up when moving, not drilling
    """

    result = """
    G17
    G91
    G0 Z%f
    """ % safe_height

    last_hole_center_x = 0
    last_hole_center_y = 0

    half_num_rows_columns = int(1.0 * radius / hole_spacing + 1.0)

    for column in range(-half_num_rows_columns, half_num_rows_columns + 1):
        for row in range(-half_num_rows_columns, half_num_rows_columns + 1):
            hole_center_x = column * hole_spacing
            hole_center_y = row * hole_spacing
            __import__('sys').stderr.write('%d %d %d %d %d\n' % (column, row, hole_center_x, hole_center_y, radius))

            if math.sqrt(hole_center_x ** 2 + hole_center_y ** 2) > radius:
                continue
        
            result += "G0 X%d Y0\n" % (
                hole_center_x - last_hole_center_x,
            )
        
            result += "G0 X0 Y%d\n" % (
                hole_center_y - last_hole_center_y,
            )
        
            result += (
                "G0 X-%f\n" % (hole_radius) +
                "G1 Z-%f\n" % safe_height +
                "G2 X%f I%f J0\n" % (hole_radius * 2, hole_radius) +
                "G2 X-%f I-%f J0\n" % (hole_radius * 2, hole_radius) +
                "G1 Z%f\n" % safe_height +
                "G0 X%f\n" % (hole_radius)
            )
        
            last_hole_center_x = hole_center_x
            last_hole_center_y = hole_center_y

    return result
