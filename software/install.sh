#!/bin/sh
cd $(dirname "$0")
mkdir -p "$DESTDIR/usr/lib/systemd/system"
mkdir -p "$DESTDIR/etc/udev/rules.d"
mkdir -p "$DESTDIR/usr/lib/flasher"
mkdir -p "$DESTDIR/usr/bin"
mkdir -p "$DESTDIR/var/lib/flasher/backups"
mkdir -p "$DESTDIR/var/lib/flasher/state"

cp flasher-trigger@.service "$DESTDIR/usr/lib/systemd/system/"
cp flasher.service "$DESTDIR/usr/lib/systemd/system"

cp 90-flasher.rules "$DESTDIR/etc/udev/rules.d/"

cp backup.sh "$DESTDIR/usr/lib/flasher/"
cp format.sh "$DESTDIR/usr/lib/flasher/"
cp flasherdaemon.py "$DESTDIR/usr/lib/flasher/"

cp main.sh "$DESTDIR/usr/bin/flasher"
