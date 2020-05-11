"""servos offers an interface for controlling motors that has been attached to an Arduino.

"""

import multiprocessing
import numpy as np
import logging
import time

import pyfirmata


class Servo(object):
    # safety delay after changing the servos angle in case no particular number has been
    # defined by the user
    _safety_delay = 0.0005

    # how many seconds it takes until pyFirmata and Arduino have been synchronized
    _synchronization_time = 3

    def __init__(
        self,
        pin: int,
        port: str = "/dev/ttyACM0",
        start_angle: float = 0,
        allowed_range_of_angles: tuple = (0, 180),
        # how long it takes to move 60 degree, depending on the particular servo motor
        # model that get used
        operating_speed: float = 0.11,
        # how many degree does the motor approximately move with each step
        move_to_grid_size: float = 0.1,
    ):
        self._allowed_range_of_angles = allowed_range_of_angles
        self._board = pyfirmata.Arduino(port)
        self._pin = pin
        self._operating_speed = operating_speed
        self._operating_speed_per_degree = self._operating_speed / 60
        self._move_to_grid_size = move_to_grid_size

        # Set mode of the pin n as SERVO
        self._board.digital[pin].mode = pyfirmata.SERVO

        logging.info("synchronizing pyFirmata and Arduiono...")
        # Need to give some time to pyFirmata and Arduino to synchronize
        time.sleep(self._synchronization_time)

        self._last_position = multiprocessing.Value("f", start_angle)

        # move to start angle
        self._set_angle(start_angle)

    @property
    def board(self) -> pyfirmata.Arduino:
        return self._board

    @property
    def pin(self) -> int:
        return self._pin

    @property
    def last_position(self) -> float:
        return self._last_position.value

    @last_position.setter
    def last_position(self, value: float) -> None:
        self._last_position.value = value

    @property
    def operating_speed(self) -> float:
        return self._operating_speed

    def _is_angle_in_allowed_range(self, angle: float) -> None:
        try:
            tests = (
                angle >= self._allowed_range_of_angles[0],
                angle <= self._allowed_range_of_angles[1],
            )
            assert all(tests)

        except AssertionError:
            msg = "Angle has to be in between {} and not {}!".format(
                self._allowed_range_of_angles, angle
            )
            raise ValueError(msg)

    def _set_angle(self, angle: float, sleep_duration: float = None) -> None:
        if not sleep_duration:
            sleep_duration = self._safety_delay

        # check if angle is in allowed range
        self._is_angle_in_allowed_range(angle)
        self.board.digital[self.pin].write(angle)
        self.last_position = angle
        time.sleep(sleep_duration)

    def move_to(self, angle: float, duration: float) -> None:
        if angle != self.last_position:
            degree2move = angle - self.last_position
            estimated_duration = abs(degree2move * self._operating_speed_per_degree)
            if estimated_duration > duration:
                msg = "Servo motor is too slow to reach angle '{}' in '{}' ".format(
                    angle, duration
                )
                msg += "seconds from angle '{}'. Estimated duration is '{}'.".format(
                    self.last_position, estimated_duration
                )
                logging.warning(msg)
                self._set_angle(angle)

            elif estimated_duration == duration:
                self._set_angle(angle)

            else:
                step_size = degree2move / round(degree2move / self._move_to_grid_size)
                n_steps = abs(int(degree2move / step_size))
                step_duration = duration / n_steps

                for angle in np.linspace(
                    self.last_position, angle, n_steps, dtype=float
                ):
                    self._set_angle(angle, step_duration)
