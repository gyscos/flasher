#!/bin/sh

NAME=$1
DEVICE=/dev/$NAME

# TODO: Save on NFS? Send an email?
TARGET=/var/lib/flasher/backups/

FILENAME=$TARGET/$(date +%Y-%m-%d_%H:%M)


PARTITION=${DEVICE}1
if [ -b $PARTITION ]
then
	FS=$(eval $(blkid $DEV | awk ' { print $3 } '); echo $TYPE)
	echo "Found filesystem $FS"

	# Attempt 1: find a mountable partition, mount it and backup the content.
	MOUNT=$(mktemp -d)
	mount $PARTITION $MOUNT

	tar -C $MOUNT -cf - . | zstd > $FILENAME.tar.zst
	ls -l $MOUNT/ >> /var/log/flasher.log

	umount $PARTITION
	rmdir $MOUNT
else
	# Attempt 2: just backup the block device.
	echo 'Meh~'
	cat $DEVICE | zstd > $FILENAME.img.zst
fi

