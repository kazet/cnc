import math
import svgwrite

import utils

def line_id_to_stroke(line_id):
    if line_id % 10 == 0:
        return svgwrite.rgb(50, 0, 0, '%')
    else:
        return svgwrite.rgb(70, 70, 70, '%')


def moves_to_svg(moves, tool_diameter, pixels_per_mm=20):
    def scale_position(position):
        x, y = position
        return (pixels_per_mm * x, pixels_per_mm * y)

    margin = pixels_per_mm * 2 * tool_diameter

    moves = list(map(scale_position, moves))

    min_x = min([x for (x, _) in moves])
    max_x = max([x for (x, _) in moves])
    min_y = min([y for (_, y) in moves])
    max_y = max([y for (_, y) in moves])

    last = moves[0]
    token = utils.random_token()
    file_name = 'static/%s.svg' % token
    dwg = svgwrite.Drawing(
        file_name,
        profile='tiny',
    )

    dwg.viewbox(
        min_x - margin,
        min_y - margin,
        (max_x - min_x) + 2 * margin,
        (max_y - min_y) + 2 * margin,
    )

    tool_move_fill_stroke = svgwrite.rgb(0, 0, 0, '%')
    tool_move_direction_stroke = svgwrite.rgb(0, 0, 100, '%')

    for turning_point in moves:
        dwg.add(
            dwg.circle(
                center=turning_point,
                r=tool_diameter * pixels_per_mm / 2.0,
                fill=tool_move_fill_stroke))

    for current in moves[1:]:
        dwg.add(dwg.line(last, current, stroke=tool_move_fill_stroke, stroke_width=tool_diameter * pixels_per_mm))
        dwg.add(dwg.line(last, current, stroke=tool_move_direction_stroke, stroke_width=3))
        last = current

    for line_id in range(math.floor(min_x / pixels_per_mm), math.ceil(max_x / pixels_per_mm) + 1):
        stroke = line_id_to_stroke(line_id)

        dwg.add(
            dwg.line(
                (line_id * pixels_per_mm, min_y),
                (line_id * pixels_per_mm, max_y),
                stroke=stroke))

    for line_id in range(math.floor(min_y / pixels_per_mm), math.ceil(max_y / pixels_per_mm) + 1):
        stroke = line_id_to_stroke(line_id)

        dwg.add(
            dwg.line(
                (min_x, line_id * pixels_per_mm),
                (max_x, line_id * pixels_per_mm),
                stroke=stroke))

    dwg.add(dwg.circle(center=(0, 0), r=0.5 * pixels_per_mm, fill='red'))

    dwg.save()

    return file_name
