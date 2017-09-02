#!/bin/sh

NAME="$1"

BACKUP_FILE=/var/lib/flasher/state/backup
FORMAT_FILE=/var/lib/flasher/state/format

D=/usr/lib/flasher
#D=.

if [ -f $BACKUP_FILE ]
then
	$D/backup.sh "$NAME"
fi

if [ -f $FORMAT_FILE ]
then
	$D/format.sh "$NAME" $(cat $FORMAT_FILE)
fi
