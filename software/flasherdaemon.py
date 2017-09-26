#!/usr/bin/env python3
"""This daemon manages the GPIO part of the flasher service."""

import time
import os
from enum import Enum
import pigpio


#PIPE_DIR = "/var/run/flasher"
PIPE_DIR = "./flasher"
PIPE_FILE = PIPE_DIR + "/status"

STATE_DIR = "/var/lib/flasher/state"
BACKUP_FILE = STATE_DIR + "/backup"
FORMAT_FILE = STATE_DIR + "/format"

FORMATS = ["ext4", "fat32", "ntfs"]

MIN_BUTTON_DELAY = 5/1000

# Pins numbers
LED_FORMATS = [14, 15, 2]

LED_BACKUP = 3

LED_STATUS_R = 27
LED_STATUS_G = 22

# Those are input
BUTTON = 24
TOGGLE = 10

class State(Enum):
    "Possible state for the service."

    # We're OFF: status LED is OFF
    INACTIVE = 1
    # We're waiting for a flash drive: status LED is green.
    WAITING = 2
    # We're formatting the flash drive. LED is red.
    FORMATTING = 3
    # We're making a backup of the drive. LED is blinking red.
    BACKING = 4
    # The drive is ready to be pulled out. LED is blinking green.
    READY = 5


def main():
    "Main entry-point"
    pi = pigpio.pi('flash.local')

    # First, set up communication channels.

    # Input: create a unix domain socket to receive status change
    wait_for_input = make_input()

    # Then, run the main loop: 2 possible sources of event.
    current_fs = 0
    write_format(FORMATS[current_fs])
    pi.write(LED_FORMATS[current_fs], 1)

    state = State.WAITING

    def set_filesystem(new_fs):
        "Sets the filesystem to the given value."
        nonlocal current_fs

        if current_fs:
            pi.write(LED_FORMATS[current_fs], 0)

        current_fs = new_fs

        if current_fs:
            print("Now using " + FORMATS[current_fs])
            pi.write(LED_FORMATS[current_fs], 1)
            write_format(FORMATS[current_fs])
        else:
            write_format(False)


    # Source 1: a GPIO event should trigger an action (change mode, ON/OFF)
    last_press = 0
    def on_button_press(_gpio, _level, _tick):
        "Change the selected filesystem when the button is pressed."
        nonlocal last_press
        # Basic manual debouncing
        now = time.time()
        if now - last_press < MIN_BUTTON_DELAY:
            return

        last_press = now
        set_filesystem((current_fs + 1) % len(FORMATS))


    last_toggle = 0
    def on_toggle(_gpio, level, _tick):
        "Enable/disable the entire operation depending on the switch."
        nonlocal state
        nonlocal last_toggle

        now = time.time()
        if now - last_press < MIN_BUTTON_DELAY:
            return

        last_toggle = now

        if level == 0:
            state = State.INACTIVE
            # Disable everything.
            write_backup(False)
            set_filesystem(False)
            print("Now inactive")

        elif level == 1:
            print("Re-activating")
            state = State.WAITING
            # Re-set the formatting mode
            set_filesystem(current_fs)

    pi.callback(BUTTON, pigpio.FALLING_EDGE, on_button_press)
    pi.callback(TOGGLE, pigpio.EITHER_EDGE, on_toggle)

    # Source 2: the trigger service notifies us of a change of status.
    def on_input(line):
        "Change the status LED based on notifications from the script."
        nonlocal state

        if line == 'BACKUP':
            state = State.BACKING
        elif line == 'FORMATTING':
            state = State.FORMATTING
        elif line == 'DONE':
            state = State.READY
        elif line == 'GONE':
            state = State.WAITING
        print(line)

    print("Waiting for input now")
    wait_for_input(on_input)


def make_input():
    "Create the input unix socket"
    # Make parent directory if necessary
    if not os.path.exists(PIPE_DIR):
        os.makedirs(PIPE_DIR)

    os.mkfifo(PIPE_FILE)

    def loop(on_input):
        "Listen for input and run the given function on it"
        try:
            while True:
                with open(PIPE_FILE) as file:
                    for line in file:
                        on_input(line.strip())
        finally:
            os.remove(PIPE_FILE)

    return loop



def write_format(filesystem):
    "Write the desired filesystem to use when formatting"
    if filesystem:
        with open(FORMAT_FILE, 'w') as file:
            file.write(filesystem)
    else:
        os.remove(FORMAT_FILE)

def write_backup(enabled):
    "Enable or disable backing up the drive"
    if enabled:
        # Make sure the file exists
        with open(BACKUP_FILE, 'a') as _:
            pass
    else:
        os.remove(BACKUP_FILE)


if __name__ == '__main__':
    main()
