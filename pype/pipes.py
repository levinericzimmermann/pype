import multiprocessing

from mu.mel import mel

from pype import servos


class Pipe(object):
    def __init__(self, pitch: mel.SimplePitch):
        self._pitch = pitch

    @property
    def pitch(self) -> mel.SimplePitch:
        return self._pitch


class ServoPipe(Pipe):
    def __init__(
        self,
        pitch: mel.SimplePitch,
        pin: int,
        port: str = "/dev/ttyACM0",
        # angle when the valve to the pipe is compeletely closed, so that no air is going
        # to the pipe
        closed_angle: float = 90,
        # angle when the valve to the pipe is compeletely opened, so that all air is
        # passing to the pipe
        opened_angle: float = 10,
        allowed_range_of_angles: tuple = (0, 180),
        # how long it takes to move 60 degree, depending on the particular servo motor
        # model that get used
        operating_speed: float = 0.11,
        # how many degree does the motor approximately move with each step
        move_to_grid_size: float = 0.1,
    ):
        self._closed_angle = closed_angle
        self._opened_angle = opened_angle

        super().__init__(pitch)
        self._servo = servos.Servo(
            pin,
            port,
            closed_angle,
            allowed_range_of_angles,
            operating_speed,
            move_to_grid_size,
        )

        self._servo.move_to(opened_angle, 0.25)
        self._servo.move_to(closed_angle, 0.25)

        self._process = None

    def _start(self, target, args: tuple = tuple([])) -> None:
        # first stopping all previous processes
        self.stop()
        # overwriting process variable
        self._process = multiprocessing.Process(target=target, args=args)
        # starting the new process
        self._process.start()

    def stop(self) -> None:
        """stop all movements immediately"""
        try:
            self._process.terminate()
        except AttributeError:
            pass

    def on(self, duration: float = 0) -> None:
        """completely open the valve in n seconds"""
        self._start(self._servo.move_to, (self._opened_angle, duration))

    def off(self, duration: float = 0) -> None:
        """completely close the valve in n seconds"""
        self._start(self._servo.move_to, (self._closed_angle, duration))

    def tremolo(self, duration_per_cycle: float) -> None:
        def tremolo():
            while True:
                self._servo.move_to(self._opened_angle, duration)
                self._servo.move_to(self._closed_angle, duration)

        duration = duration_per_cycle * 0.5
        self._start(tremolo)
