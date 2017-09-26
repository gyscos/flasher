#!/usr/bin/env python3
"""This daemon manages the GPIO part of the flasher service.
Currently expects to be run on a raspberry pi device."""

# TODO: add CLI arguments? Read a config file?

import time
import os
from threading import Thread
from enum import Enum
import pigpio


PIPE_DIR = "/var/run/flasher"
# PIPE_DIR = "./flasher"
PIPE_FILE = PIPE_DIR + "/status"

STATE_DIR = "/var/lib/flasher/state"
# STATE_DIR = "./state"
BACKUP_FILE = STATE_DIR + "/backup"
FORMAT_FILE = STATE_DIR + "/format"

MODE_NAMES = ["ext4", "fat32", "ntfs", "backup"]

MIN_BUTTON_DELAY = 100/1000

# Pins numbers
MODE_LED_PINS = [14, 15, 2, 3]

STATUS_LED_G_PIN = 17
STATUS_LED_R_PIN = 27

# Those are input
BUTTON_PIN = 10
TOGGLE_PIN = 9

BLINKING_TIMES = {
    0: 0.1,
    1: 0.5
    }


def main():
    "Main entry-point"
    FlasherDaemon().run()


class State(Enum):
    "Possible state for the service."

    # We're waiting for a flash drive: status LED is green.
    WAITING = 1
    # We're formatting the flash drive. LED is red.
    FORMATTING = 2
    # We're making a backup of the drive. LED is blinking red.
    BACKING = 3
    # The drive is ready to be pulled out. LED is blinking green.
    READY = 4


class StatusColor(Enum):
    "Possible color for the status LED"
    RED = 1
    GREEN = 2
    NONE = 3

    def get_rg(self):
        "Returns a tuple containing the red and green value for this color."
        if self == StatusColor.RED:
            return (1, 0)
        elif self == StatusColor.GREEN:
            return (0, 1)

        return (0, 0)


class FlasherDaemon:
    "Stores data for the daemon"

    def __init__(self):
        # Establish connection to GPIO server
        self.gpio = pigpio.pi()

        # Declare variables
        self.current_mode = 0
        self.state = State.WAITING
        self.active = 0
        self.last_event = 0
        self.blinking = False
        self.blinking_thread = None

    def cleanup(self):
        "Performs cleanup actions on exit."
        self.all_off()
        try:
            os.remove(PIPE_FILE)
        except FileNotFoundError:
            pass
        try:
            os.remove(BACKUP_FILE)
        except FileNotFoundError:
            pass
        try:
            os.remove(FORMAT_FILE)
        except FileNotFoundError:
            pass

    def all_off(self):
        "Turn everything off."
        for pin in MODE_LED_PINS:
            self.gpio.write(pin, 0)
        self.gpio.write(STATUS_LED_G_PIN, 0)
        self.gpio.write(STATUS_LED_R_PIN, 0)

    def run(self):
        "Run the main loop: listen for events"
        try:
            # Init starting modes
            self.all_off()
            self.enter_mode(0)
            self.set_active(self.gpio.read(TOGGLE_PIN))
            self.set_state(State.WAITING)

            self.gpio.set_pull_up_down(BUTTON_PIN, pigpio.PUD_UP)
            self.gpio.set_pull_up_down(TOGGLE_PIN, pigpio.PUD_UP)

            self.gpio.callback(BUTTON_PIN, pigpio.EITHER_EDGE,
                               self.on_button_press)
            self.gpio.callback(TOGGLE_PIN, pigpio.EITHER_EDGE, self.on_toggle)
            self.wait_for_input(self.on_input)
        finally:
            print("Cleaning up before exiting.")
            self.cleanup()

    @staticmethod
    def wait_for_input(on_input):
        "Listen on the PIPE for notification from the script."
        if not os.path.exists(PIPE_DIR):
            os.makedirs(PIPE_DIR)

        if os.path.exists(PIPE_FILE):
            os.remove(PIPE_FILE)

        os.mkfifo(PIPE_FILE)

        while True:
            with open(PIPE_FILE) as file:
                for line in file:
                    on_input(line.strip())

    def _debounce(self):
        """Performs a manual debouncing of input.
        Returns True if the event should be ignored."""

        # Basic manual debouncing
        now = time.time()
        if now - self.last_event < MIN_BUTTON_DELAY:
            return True
        self.last_event = now
        return False

    def on_button_press(self, _gpio, level, _tick):
        "Change the selected mode when the button is pressed."

        if self._debounce():
            return

        if level == 1:
            return

        if not self.active:
            # We're not doing anything in inactive mode.
            return

        if self.state != State.WAITING:
            # We're also not doing anything when a flash drive is plugged in.
            return

        self.leave_mode()
        self.enter_mode((self.current_mode + 1) % len(MODE_NAMES))

    def on_toggle(self, _gpio, level, _tick):
        "Enable/disable the entire operation depending on the switch."

        # Manual debouncing
        if self._debounce():
            return

        if level == 0:
            print("Now inactive")
        elif level == 1:
            print("Re-activating")
        self.set_active(level)

    def on_input(self, line):
        "Change the status LED based on notifications from the script."

        if line == 'BACKUP':
            self.set_state(State.BACKING)
        elif line == 'FORMATTING':
            self.set_state(State.FORMATTING)
        elif line == 'DONE':
            self.set_state(State.READY)
        elif line == 'GONE':
            self.set_state(State.WAITING)

    def set_active(self, active):
        "Enable or disable the trigger script."
        self.active = active
        if active:
            # Re-enable current mode
            self.enter_mode(self.current_mode)
            if self.state == State.WAITING:
                self.set_status_led(StatusColor.GREEN)
        else:
            self.leave_mode()
            # In WAITING mode, turn OFF the status LED.
            # Otherwise, leave it ON
            if self.state == State.WAITING:
                self.set_status_led(StatusColor.NONE)

    def set_status_led(self, color: StatusColor):
        "Sets the status led to the given color."
        self.blinking = False
        (red, green) = color.get_rg()

        self.gpio.write(STATUS_LED_R_PIN, red)
        self.gpio.write(STATUS_LED_G_PIN, green)

    def blink_status_led(self, color: StatusColor):
        "Sets the status led to blink in the given color."
        (red, green) = color.get_rg()
        if self.blinking_thread:
            self.blinking = False
            self.blinking_thread.join()

        self.blinking = True

        def _blink():
            led_on = 1
            while self.blinking:
                self.gpio.write(STATUS_LED_R_PIN, red * led_on)
                self.gpio.write(STATUS_LED_G_PIN, green * led_on)
                time.sleep(BLINKING_TIMES[led_on])
                led_on = 1 - led_on

            self.blinking_thread = None

        self.blinking_thread = Thread(target=_blink)
        self.blinking_thread.start()

    def enter_mode(self, mode: int):
        'Enters the given mode'
        print('Entering mode', MODE_NAMES[mode])
        self.current_mode = mode
        if self.active:
            mode_name = MODE_NAMES[mode]
            if mode_name == 'backup':
                write_backup(True)
            else:
                write_format(MODE_NAMES[mode])

            self.gpio.write(MODE_LED_PINS[mode], 1)

    def leave_mode(self):
        'Leaves the current mode'
        mode_name = MODE_NAMES[self.current_mode]
        if mode_name == 'backup':
            write_backup(False)
        else:
            write_format(False)

        self.gpio.write(MODE_LED_PINS[self.current_mode], 0)

    def set_state(self, state: State):
        'Updates the status LED to match the given state.'

        print("Changed state: ", state)
        self.state = state

        if state == State.WAITING:
            if self.active:
                self.set_status_led(StatusColor.GREEN)
            else:
                self.set_status_led(StatusColor.NONE)
        elif state == State.FORMATTING:
            self.set_status_led(StatusColor.RED)
        elif state == State.BACKING:
            self.blink_status_led(StatusColor.RED)
        elif state == State.READY:
            self.blink_status_led(StatusColor.GREEN)


def write_format(filesystem):
    "Write the desired filesystem to use when formatting"
    if filesystem:
        with open(FORMAT_FILE, 'w') as file:
            file.write(filesystem)
    else:
        try:
            os.remove(FORMAT_FILE)
        except:
            pass


def write_backup(enabled):
    "Enable or disable backing up the drive"
    if enabled:
        # Make sure the file exists
        with open(BACKUP_FILE, 'a') as file:
            file.write('')
    else:
        try:
            os.remove(BACKUP_FILE)
        except:
            pass


if __name__ == '__main__':
    main()
