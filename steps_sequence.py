def create_steps_sequence(num_steps, axis):
    if isinstance(num_steps, float):
        num_steps = int(num_steps)

    if num_steps == 0:
        return []

    sequence = []
    for step in range(num_steps):
        sequence.append((step * 1.0 / num_steps, axis))
    return sequence
        

def create_xyz_steps_sequence( num_x_steps, num_y_steps, num_z_steps):
    sequence_x = create_steps_sequence(num_x_steps, 'X')
    sequence_y = create_steps_sequence(num_y_steps, 'Y')
    sequence_z = create_steps_sequence(num_z_steps, 'Z')

    return sorted(
        sequence_x +
        sequence_y +
        sequence_z
    )

