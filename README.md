# pype

(in development)

*pype* is a python module for controlling organ valves through servo motors that have been attached to an arduino.

setting up *pype* for controlling the servo motor:
    1. installing pype and all dependencies on your computer
    2. connect the arduino to your computer
    3. upload the 'StandardFirmata' program (as it can be found in the standard example files or [here](https://github.com/firmata/arduino/blob/master/examples/StandardFirmata/StandardFirmata.ino))
    4. load python interpreter and use pype:

    ```python
    from pype import pipes
    from mu.mel import mel

    # defining the pitch of your pipe
    pitch = mel.SimplePitch(concert_pitch_freq=440, cents=-1200)  # a3

    # defining the arduino pin of the servo motor
    pin = 10

    # defining the actual pipe object
    my_pipe = pipes.ServoPipe(pitch, pin)

    # open the valve, so that air could enter the pipe
    my_pipe.on()

    # close the valve, so that no air could enter the pipe anymore
    my_pipe.off()

    # open the valve slowly over 3 seconds
    my_pipe.on(3)

    # infinitely open and close the valve
    my_pipe.tremolo(1)

    # stop all processes
    my_pipe.stop()
    ```
