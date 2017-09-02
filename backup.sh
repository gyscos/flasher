#!/bin/sh

NAME=$1
DEVICE=/dev/$1

echo "Doing a backup of $DEVICE."

# TODO: Save on NFS? Send an email?
TARGET=/var/lib/flasher/backups/

FILENAME=$TARGET/$(date +%Y-%m-%d_%H:%M)


PARTITION=${DEVICE}1
if [ -b $PARTITION ]
then
	# Attempt 1: find a mountable partition, mount it and backup the content.
	MOUNT=$(mktemp -d)
	mount $PARTITION $MOUNT

	tar -C $MOUNT -cf - . | zstd > $FILENAME.tar.zst
	ls -l $MOUNT/ >> /var/log/flasher.log

	umount $PARTITION
	rmdir $MOUNT
else
	# Attempt 2: just backup the block device.
	echo Meh~
	cat $DEVICE | zstd > $FILENAME.img.zst
fi

