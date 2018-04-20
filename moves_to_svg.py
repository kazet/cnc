import svgwrite

import utils


def moves_to_svg(moves, pixels_per_mm=100):
    def scale_position(position):
        x, y = position
        return (pixels_per_mm * x, pixels_per_mm * y)

    margin = 10  # px
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

    for current in moves[1:]:
        dwg.add(dwg.line(last, current, stroke=svgwrite.rgb(0, 0, 0, '%')))
        last = current

    dwg.save()

    return file_name
