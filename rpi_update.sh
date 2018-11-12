#!/bin/sh

# raspi-config --expand-rootfs

sudo apt-get purge -y wolfram-engine
sudo apt-get purge -y libreoffice*
sudo apt-get clean -y
sudo apt-get autoremove -y

sudo apt-get update -y
sudo apt-get upgrade -y
sudo rpi-update


