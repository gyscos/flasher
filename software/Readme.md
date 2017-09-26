This is the software side of the flasher project.

It includes:
* A set of trigger scripts (`main.sh`, `format.sh`, `backup.sh`) that perform backup or filesystem format actions when called.
* A systemd service file (`flasher-trigger@.service`) that calls `main.sh` with the given argument (this is mostly used as a workaroung to bypass the limitations of udev).
* A udev rule (`90-flasher.rules`) to start the `flasher-trigger` service whenever a flash drive is plugged.
* A python daemon (`flasherdaemon.py`) that serves as an interface between the trigger script and the GPIO LEDs and buttons (currently only work on raspberry pi).
* A systemd service file (`flasher.service`) that runs the python daemon.

You can package everything in a `pkg` directory by running `DESTDIR=pkg/ ./install.sh`.

There is also a `PKGBUILD` and a `flasher.install`: on Archlinux, you can just run:

```
makepkg -si
sudo systemctl start flasher
```
