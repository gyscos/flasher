#!/bin/sh

NAME=$1
FS=$2
DEVICE=/dev/$NAME

# TODO: find this from current state

echo Formatting ${DEVICE}1 as $FS

parted -s $DEVICE mktable gpt
parted -s $DEVICE mkpart primary $FS 0% 100%
mkfs.$FS -q -F ${DEVICE}1
