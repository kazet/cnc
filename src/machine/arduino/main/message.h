#define MESSAGE_UNKNOWN 0x30
#define MESSAGE_PING 0x31
#define MESSAGE_PONG 0x32
#define MESSAGE_THREE_PWM 0x33
#define MESSAGE_THREE_PWM_SCHEDULED 0x34
#define MESSAGE_SET_DIR 0x36
#define MESSAGE_SET_DIR_SCHEDULED 0x37
#define MESSAGE_THREE_PWM_ERROR 0x38
#define MESSAGE_FLUSH 0x39
#define MESSAGE_FLUSH_STARTED 0x3a
#define MESSAGE_FLUSH_FINISHED 0x3b
#define MESSAGE_FLUSH_FAILED 0x3c

typedef uint8_t move_type;
const int SET_DIR = 0;  /* set the move direction */
const int THREE_PWM = 1;  /* send a consistent, synchronized PWM signal on all three axes */

union move_data {
    struct {
        uint32_t dir_id;  /* the axis to be set */
        uint32_t dir_state;  /* the state to be set: 1 (UP), 0 (DOWN) */
    } as_set_dir;

    struct {
        uint32_t time_microseconds; /* how long the signal should be */
        uint32_t num_x;  /* how many up/down ticks on X axis */
        uint32_t num_y;  /* how many up/down ticks on Y axis */
        uint32_t num_z;  /* how many up/down ticks on Z axis */
    } as_three_pwm;
};


struct move {
    move_type type;
    union move_data data;
};
