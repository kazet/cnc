def create_steps_sequence(sequence_time, max_pulse_time, num_steps, axis):
    if isinstance(num_steps, float):
        num_steps = int(num_steps)

    if num_steps == 0:
        return []

    time = 0
    sequence = []
    time_per_single_pulse = sequence_time / (num_steps * 2.0)

    for step in range(num_steps):
        if time_per_single_pulse > max_pulse_time:
            sequence.append((time, axis, 'UP'))
            time += max_pulse_time
            sequence.append((time, axis, 'DOWN'))
            time += time_per_single_pulse * 2 - max_pulse_time
        else:
            sequence.append((time, axis, 'UP'))
            time += time_per_single_pulse
            sequence.append((time, axis, 'DOWN'))
            time += time_per_single_pulse
    return sequence
        

def create_xyz_steps_sequence(step_time, max_pulse_time, num_x_steps, num_y_steps, num_z_steps):
    sequence_time = step_time * max(
        num_x_steps,
        num_y_steps,
        num_z_steps,
    )

    sequence_x = create_steps_sequence(sequence_time, max_pulse_time, num_x_steps, 'X')
    sequence_y = create_steps_sequence(sequence_time, max_pulse_time, num_y_steps, 'Y')
    sequence_z = create_steps_sequence(sequence_time, max_pulse_time, num_z_steps, 'Z')

    return sorted(
        sequence_x +
        sequence_y +
        sequence_z
    )

