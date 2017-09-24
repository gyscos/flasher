#!/bin/sh
cd $(dirname "$0")
mkdir -p "$PREFIX/usr/lib/systemd/system"
mkdir -p "$PREFIX/etc/udev/rules.d"
mkdir -p "$PREFIX/usr/lib/flasher"
mkdir -p "$PREFIX/usr/bin"
mkdir -p "$PREFIX/var/lib/flasher/backups"
mkdir -p "$PREFIX/var/lib/flasher/state"

cp flasher-trigger@.service "$PREFIX/usr/lib/systemd/system/"
cp 90-flasher.rules "$PREFIX/etc/udev/rules.d/"

cp backup.sh "$PREFIX/usr/lib/flasher/"
cp format.sh "$PREFIX/usr/lib/flasher/"

cp main.sh "$PREFIX/usr/bin/flasher"
