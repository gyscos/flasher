## Flasher

Flasher is a service to automatically format or backup flash drives when inserted.

It is meant to be installed on a small computer board (like a Raspberry Pi Zero) with a single USB port, to easily prepare flash drives before use.

## Behaviour

Depending on the current state (using physical buttons connected to the computer), it runs the following actions whenever a flash drive is plugged:

* Backup
    * If a single partition is detected and can be mounted, make a backup of the partition content.
    * Otherwise, make a backup of the entire block device.
* Format
    * Create a new GPT partition table with a single partition
    * Format the partition with the desired filesystem.

## Hardware

Flasher is intended to be run on a computer with the following hardware connected:

* A USB socket to plug the flash drive to operate on
* A on/off switch to enable automatic action
* A button to move between modes (Backup, Format Fat32, Format NTFS, Format ext, ...)
* A bunch of LEDs to indicate current status

## How's it work?

* A daemon listen for button presses, toggle LEDs, and maintain status files.
* A udev rule waits for plugged flash drives, and starts a script (via a systemd service). This script reads the current state, and performs the corresponding actions.
