#!/bin/bash

cd ~/

if [[ 1 -eq 0 ]]; then
	sudo apt-get clean -y
	sudo apt-get autoremove -y
	sudo apt-get update -y
	sudo apt-get upgrade -y
	sudo apt-get install -y unzip
	sudo apt-get clean -y
	sudo apt-get autoremove -y
fi

USER=`whoami`
USER_DIR="/home/${USER}/"
DOWNLOAD_DIR="${USER_DIR}Downloads/"
RPI_OS_URL="https://downloads.raspberrypi.org/raspbian_latest"
# RPI_OS_URL="https://downloads.raspberrypi.org/raspbian_lite_latest"
RPI_OS_ZIP="raspbian-stretch.zip"
RPI_OS_IMG="raspbian-stretch.img"
# RPI_OS_ZIP="raspbian-stretch-lite.zip"
# RPI_OS_IMG="raspbian-stretch-lite.img"
RPI_OS_ZIP_PATH="${DOWNLOAD_DIR}${RPI_OS_ZIP}"
RPI_OS_IMG_PATH="${DOWNLOAD_DIR}${RPI_OS_IMG}"
RPI_OS_SEARCH="${DOWNLOAD_DIR}*${RPI_OS_IMG}"

DEV_SDX="/dev/sdc"
DEV_SDX1="${DEV_SDX}1"
DEV_SDX2="${DEV_SDX}2"

MEDIA_RPI_PATH="/media/${USER}/"
MEDIA_RPI_BOOT_PATH="${MEDIA_RPI_PATH}boot/"
MEDIA_RPI_ROOTFS_PATH="${MEDIA_RPI_PATH}rootfs/"

MNT_RPI_PATH="/mnt/rpi/"
MNT_RPI_BOOT_PATH="${MNT_RPI_PATH}boot/"
MNT_RPI_ROOTFS_PATH="${MNT_RPI_PATH}rootfs/"

SSH_FILE="ssh"
SSH_FILE_PATH="${MNT_RPI_BOOT_PATH}${SSH_FILE}"

TIMEZONE_FILE="timezone"
TIMEZONE_TEXT="US/Pacific"
TIMEZONE_PATH="${MNT_RPI_BOOT_PATH}${TIMEZONE_FILE}"

UTC_TIME_TEXT=`date -u +'%F %T'`
FAKE_HWCLOCK_FILE="fake-hwclock.data"
FAKE_HWCLOCK_PATH="${MNT_RPI_BOOT_PATH}${FAKE_HWCLOCK_FILE}"

SSID=$1
PSK=$2
WPA_SUPPLICANT_FILE="wpa_supplicant.conf"
WPA_SUPPLICANT_TEXT="ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\nupdate_config=1\ncountry=US\n\nnetwork={\n\tssid=\"${SSID}\"\n\tpsk=\"${PSK}\"\n}"
WPA_SUPPLICANT_PATH="${MNT_RPI_BOOT_PATH}${WPA_SUPPLICANT_FILE}"
echo -e "\n${WPA_SUPPLICANT_TEXT}"

INTERFACES=("eth0" "wlan0")
STATIC_IP_ADDRESS="192.168.2.23"
STATIC_ROUTERS="192.168.2.1"
STATIC_DOMAIN_NAME_SERVERS="192.168.2.1"

DHCPCD_FILE="dhcpcd.conf"
DHCPCD_PATH="${MNT_RPI_ROOTFS_PATH}etc/dhcpcd.conf"
DHCPCD_DATA="static ip_address=${STATIC_IP_ADDRESS}/24\nstatic routers=${STATIC_ROUTERS}\nstatic domain_name_servers=${STATIC_DOMAIN_NAME_SERVERS}\n"
echo -e "\n"
DHCPCD_TEXT=""
for i_f in ${INTERFACES[*]}; do
	DHCPCD_TEXT="${DHCPCD_TEXT}interface ${i_f}\n${DHCPCD_DATA}\n"
done
echo -e "${DHCPCD_TEXT}"

if [[ 1 -eq 0 ]]; then
	mkdir -vp $DOWNLOAD_DIR
	wget -v $RPI_OS_URL -O $RPI_OS_ZIP_PATH
	unzip $RPI_OS_ZIP_PATH -d $DOWNLOAD_DIR
	mv -vf $RPI_OS_SEARCH $RPI_OS_IMG_PATH
	echo ""
fi

sudo umount -v $MEDIA_RPI_BOOT_PATH
sudo umount -v $MEDIA_RPI_ROOTFS_PATH
sudo umount -v $MNT_RPI_BOOT_PATH
sudo umount -v $MNT_RPI_ROOTFS_PATH
sudo rm -vr $MNT_RPI_PATH
echo ""

if [[ 1 -eq 1 ]]; then
	sudo dd if=/dev/zero of=$DEV_SDX bs=1M count=1028 status=progress conv=fsync
	sudo sync
	echo ""
	sudo dd if=$RPI_OS_IMG_PATH of=$DEV_SDX bs=1M status=progress conv=fsync
	sudo sync
	echo ""
fi

sudo mkdir -vp $MNT_RPI_BOOT_PATH
sudo mkdir -vp $MNT_RPI_ROOTFS_PATH
sudo mount -vo rw $DEV_SDX1 $MNT_RPI_BOOT_PATH
sudo mount -vo rw $DEV_SDX2 $MNT_RPI_ROOTFS_PATH
echo ""

sudo touch $SSH_FILE_PATH
echo ""

sudo echo $TIMEZONE_TEXT > $TIMEZONE_FILE
sudo cp -vf $TIMEZONE_FILE $TIMEZONE_PATH
sudo rm -vf $TIMEZONE_FILE
echo ""

sudo echo $UTC_TIME_TEXT > $FAKE_HWCLOCK_FILE
sudo cp -vf $FAKE_HWCLOCK_FILE $FAKE_HWCLOCK_PATH
sudo rm -vf $FAKE_HWCLOCK_FILE
echo ""

sudo echo -e "${WPA_SUPPLICANT_TEXT}" > $WPA_SUPPLICANT_FILE
sudo cp -vf $WPA_SUPPLICANT_FILE $WPA_SUPPLICANT_PATH
sudo rm -vf $WPA_SUPPLICANT_FILE
echo ""

sudo cp -vf $DHCPCD_PATH $DHCPCD_FILE
sudo cat -v $DHCPCD_FILE > "${DHCPCD_FILE}.tmp"
sudo echo -e "${DHCPCD_TEXT}" >> "${DHCPCD_FILE}.tmp"
sudo mv -vf "${DHCPCD_FILE}.tmp" $DHCPCD_FILE
sudo cp -vf $DHCPCD_FILE $DHCPCD_PATH
sudo rm -vf $DHCPCD_FILE
echo ""

sudo umount -v $MNT_RPI_BOOT_PATH
sudo umount -v $MNT_RPI_ROOTFS_PATH
sudo rm -vr $MNT_RPI_PATH
sudo umount -v $MEDIA_RPI_BOOT_PATH
sudo umount -v $MEDIA_RPI_ROOTFS_PATH
echo ""
