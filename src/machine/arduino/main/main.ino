#include "message.h"
#include "pinout.h"


void serial__wait_for_data_available() {
  while(!Serial.available()) {
    delay(0.1);
  }
}

uint32_t serial__read_unit32_t() {
  uint32_t result = 0;

  serial__wait_for_data_available();
  result += (uint32_t) Serial.read();

  serial__wait_for_data_available();
  result += (uint32_t) Serial.read() << 8;

  serial__wait_for_data_available();
  result += (uint32_t) Serial.read() << 16;

  serial__wait_for_data_available();
  result += (uint32_t) Serial.read() << 24;

  return result;
}


uint8_t serial__read_unit8_t() {
  serial__wait_for_data_available();

  return Serial.read();
}

void serial__write_unit8_t(uint8_t value) {
    Serial.write(value);
}

void setup() {
  Serial.begin(9600);

  // Enable Direction and Pulse stepper motor pins as OUTPUT
  for (int i = 0; i < 3; i++) {
    pinMode(PIN_DIR[i], OUTPUT);
    pinMode(PIN_PUL[i], OUTPUT);
  }
}


/* interpret an array of move structures and actually send them to output pins of the microcontroller */
int flush_moves_buffer(struct move* moves_buffer, int moves_buffer_size) {
    for (int i = 0; i < moves_buffer_size; i++) {
        /* execute a single move: SET DIRECTION, an axis direction change */
        if (moves_buffer[i].type == SET_DIR) {
            if (moves_buffer[i].data.as_set_dir.dir_id >= 0 && moves_buffer[i].data.as_set_dir.dir_id <= 2) {
                if (moves_buffer[i].data.as_set_dir.dir_state) {
                    digitalWrite(PIN_DIR[moves_buffer[i].data.as_set_dir.dir_id], HIGH);
                } else {
                    digitalWrite(PIN_DIR[moves_buffer[i].data.as_set_dir.dir_id], LOW);
                }
            }
        /* execute a single move: THREE PWM, synchronized series of up/down ticks on each axis */
        } else if (moves_buffer[i].type == THREE_PWM) {
            /* a separation between one signal change on X axis (UP to DOWN or DOWN to UP) */
            uint32_t spacing_x =
                moves_buffer[i].data.as_three_pwm.time_microseconds /
                (moves_buffer[i].data.as_three_pwm.num_x * 2 + 1);
            /* a separation between one signal change on Y axis (UP to DOWN or DOWN to UP) */
            uint32_t spacing_y =
                moves_buffer[i].data.as_three_pwm.time_microseconds /
                (moves_buffer[i].data.as_three_pwm.num_y * 2 + 1);
            /* a separation between one signal change on Z axis (UP to DOWN or DOWN to UP) */
            uint32_t spacing_z =
                moves_buffer[i].data.as_three_pwm.time_microseconds /
                (moves_buffer[i].data.as_three_pwm.num_z * 2 + 1);

            if (spacing_x == 0 || spacing_y == 0 || spacing_z == 0) {
                return 1;
            } else {
                uint32_t next_x = spacing_x;
                uint32_t next_y = spacing_y;
                uint32_t next_z = spacing_z;

                uint32_t pul_state_x = 0;
                uint32_t pul_state_y = 0;
                uint32_t pul_state_z = 0;

                uint32_t ticks_made_x = 0;
                uint32_t ticks_made_y = 0;
                uint32_t ticks_made_z = 0;

                uint32_t time = 0;

                while (time < moves_buffer[i].data.as_three_pwm.time_microseconds) {
                    uint32_t next_iter = next_x;
                    if (next_y < next_iter) {
                        next_iter = next_y;
                    }

                    if (next_z < next_iter) {
                        next_iter = next_z;
                    }

                    delayMicroseconds(next_iter - time);
                    time = next_iter;

                    if (time == next_x) {
                        pul_state_x = 1 - pul_state_x;

                        if (pul_state_x == 0) {
                            ticks_made_x += 1;
                        }

                        if (ticks_made_x < moves_buffer[i].data.as_three_pwm.num_x) {
                            digitalWrite(PIN_PUL[0], pul_state_x);
                        }

                        next_x += spacing_x;
                    }

                    if (time == next_y) {
                        pul_state_y = 1 - pul_state_y;

                        if (pul_state_y == 0) {
                            ticks_made_y += 1;
                        }

                        if (ticks_made_y < moves_buffer[i].data.as_three_pwm.num_y) {
                            digitalWrite(PIN_PUL[1], pul_state_y);
                        }

                        next_y += spacing_y;
                    }

                    if (time == next_z) {
                        pul_state_z = 1 - pul_state_z;

                        if (pul_state_z == 0) {
                            ticks_made_z += 1;
                        }

                        if (ticks_made_z < moves_buffer[i].data.as_three_pwm.num_z) {
                            digitalWrite(PIN_PUL[2], pul_state_z);
                        }

                        next_z += spacing_z;
                    }
                }
            }
        } else {
            return 2;
        }
    }
    return 0;
}

const int MOVES_BUFFER_MAX_SIZE = 50;
move moves_buffer[MOVES_BUFFER_MAX_SIZE];
int moves_buffer_size = 0;

/* a loop that receives messages via serial port and interpretes them */
void loop() {
  serial__wait_for_data_available();
  byte value = serial__read_unit8_t();

  int result;

  switch(value) {
    case MESSAGE_PING:
      /* a PING message, that is responded to with a PONG */

      {
        serial__write_unit8_t(MESSAGE_PONG);
      }
      break;
    case MESSAGE_SET_DIR:
      /*
       * A SET DIRECTION message that schedules an axis direction change.
       *
       * After being scheduled, the messages aren't actually interpreted, but wait
       * for a FLUSH message, or end of buffer space, whichever comes first.
       */

      {
        uint32_t dir_id = serial__read_unit8_t();
        uint32_t dir_state = serial__read_unit8_t();
        if (moves_buffer_size >= MOVES_BUFFER_MAX_SIZE) {
            flush_moves_buffer(moves_buffer, moves_buffer_size);
            moves_buffer_size = 0;
        }

        moves_buffer[moves_buffer_size].type = SET_DIR;
        moves_buffer[moves_buffer_size].data.as_set_dir.dir_id = dir_id;
        moves_buffer[moves_buffer_size].data.as_set_dir.dir_state = dir_state;
        moves_buffer_size++;

        serial__write_unit8_t(MESSAGE_SET_DIR_SCHEDULED);
      }
      break;
    case MESSAGE_THREE_PWM:
      /*
       * A THREE PWM message that schedules synchronized series of up/down ticks on each axis.
       *
       * After being scheduled, the messages aren't actually interpreted, but wait
       * for a FLUSH message, or end of buffer space, whichever comes first.
       */
      {
        if (moves_buffer_size >= MOVES_BUFFER_MAX_SIZE) {
            flush_moves_buffer(moves_buffer, moves_buffer_size);
            moves_buffer_size = 0;
        }

        moves_buffer[moves_buffer_size].type = THREE_PWM;
        moves_buffer[moves_buffer_size].data.as_three_pwm.time_microseconds = serial__read_unit32_t();
        moves_buffer[moves_buffer_size].data.as_three_pwm.num_x = serial__read_unit32_t();
        moves_buffer[moves_buffer_size].data.as_three_pwm.num_y = serial__read_unit32_t();
        moves_buffer[moves_buffer_size].data.as_three_pwm.num_z = serial__read_unit32_t();
        moves_buffer_size++;

        serial__write_unit8_t(MESSAGE_THREE_PWM_SCHEDULED);
      }
      break;
    case MESSAGE_FLUSH:
      /*
       * A FLUSH messages that interpretes all moves and direction changes that have been
       * scheduled.
       */

      serial__write_unit8_t(MESSAGE_FLUSH_STARTED);
      result = flush_moves_buffer(moves_buffer, moves_buffer_size);
      moves_buffer_size = 0;

      if (result == 0) {
        serial__write_unit8_t(MESSAGE_FLUSH_FINISHED);
      } else {
        serial__write_unit8_t(MESSAGE_FLUSH_FAILED);
        serial__write_unit8_t(result & 0xff);
      }

      break;
    default:
      {
        serial__write_unit8_t(MESSAGE_UNKNOWN);
      }
  }
}
