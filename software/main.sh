#!/bin/sh

NAME="$1"

STATE_DIR=/var/lib/flasher/state

# Backup and Format files are written to by the GPIO service.
BACKUP_FILE=$STATE_DIR/backup
FORMAT_FILE=$STATE_DIR/format
# Status file is read by the GPIO service (might even be a socket?)
STATUS_FILE=$STATE_DIR/status

D=/usr/lib/flasher
#D=.

if [ -f $BACKUP_FILE ]
then
	echo "Doing a backup of $DEVICE."
	echo "BACKUP" > $STATUS_FILE

	$D/backup.sh "$NAME"
fi

if [ -f $FORMAT_FILE ]
then
	echo "Formatting ${DEVICE}1 as $FS"
	echo "FORMATTING" > $STATUS_FILE

	$D/format.sh "$NAME" $(cat $FORMAT_FILE)
fi

echo "$NAME: Work done"
echo "DONE" > $STATUS_FILE
