#!/bin/sh

set -e

NAME=$1
FS=$2
DEVICE=/dev/$NAME

CMD="mkfs.$FS"
ARGS=""

case $FS in
	fat16) CMD="mkfs.fat" ;;
	fat32) CMD="mkfs.fat -F32" ;;

	ext2) ARGS="-q -F" ;;
	ext3) ARGS="-q -F" ;;
	ext4) ARGS="-q -F" ;;
	btrfs) ARGS="-q -f" ;;
	ntfs) ARGS="-q -f -F" ;;
	exfat) ;;
	*) echo "Unknown filesystem $FS" ;;
esac


# Clear the beginning of the drive, sometimes it has weird blocks
dd if=/dev/zero of=$DEVICE bs=1M count=1

parted -s $DEVICE mktable gpt
parted -s $DEVICE mkpart primary 0% 100%

eval $CMD $ARGS ${DEVICE}1
