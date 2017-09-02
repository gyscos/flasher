#!/bin/sh

NAME=$1
DEVICE=/dev/$1

echo "Doing a backup of $DEVICE."

TARGET=/var/lib/flasher/backups/

# Attempt 1: find a mountable partition, mount it and backup the content.
PARTITION=${DEVICE}1
MOUNT=$(mktemp -d)
mount $PARTITION $MOUNT

FILENAME=$(date +%Y-%m-%d_%H:%M)
tar -C $MOUNT -cf - . | zstd > $TARGET/$FILENAME.tar.zst
ls -l $MOUNT/ >> /var/log/flasher.log

umount $PARTITION
rmdir $MOUNT

exit 0


# Attempt 2: just backup the block device.
echo Meh~
