#!/bin/bash

################################################################################
# Simple script to install OpenCV 4 on Raspbian Stretch OS
#	- https://opencv.org/releases.html
# 	- https://www.raspberrypi.org/downloads/raspbian/
#
# Example:
# install_opencv.sh 1
# install_opencv.sh 2
################################################################################
OPENCV_VERSION="4.0.1"
cd ~/
PROFILE_FILE="${HOME}/.profile"

################################################################################
# STEP 1
# 	- Expand root filesystem
################################################################################
# if [[ $1 -eq 1 ]]; then
# 	sudo raspi-config --expand-rootfs
# 	sudo reboot
	
################################################################################
# STEP 2
#	- Remove uneccessary packages/libraries
#	- Install neccesary packages/libraries for OpenCV preparation
################################################################################
# elif [[ $1 -eq 2 ]]; then
	sudo apt-get purge -y wolfram-engine
	sudo apt-get purge -y libreoffice*
	sudo apt-get clean -y
	sudo apt-get autoremove -y

	sudo apt-get update -y
	sudo apt-get upgrade -y
	sudo rpi-update
	
	sudo apt-get install -y build-essential git cmake unzip pkg-config
	sudo apt-get install -y libjpeg-dev libpng-dev libtiff-dev
	sudo apt-get install -y libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
	sudo apt-get install -y libxvidcore-dev libx264-dev
	sudo apt-get install -y libgtk-3-dev
	sudo apt-get install -y libcanberra-gtk*
	sudo apt-get install -y libatlas-base-dev gfortran
	sudo apt-get install -y python3-dev python3-picamera python3-pip

	sudo modprobe bcm2835-v4l2
	
	sudo apt-get clean -y
	sudo apt-get autoremove -y

################################################################################
# STEP 3
#	- Clone & install OpenCV packages/libraries via GitHub
################################################################################
# elif [[ $1 -eq 3 ]]; then

	wget -O opencv.zip "https://github.com/opencv/opencv/archive/${OPENCV_VERSION}.zip"
	wget -O opencv_contrib.zip "https://github.com/opencv/opencv_contrib/archive/${OPENCV_VERSION}.zip"
	
	unzip opencv.zip
	unzip opencv_contrib.zip

	mv "opencv-${OPENCV_VERSION}" opencv
	mv "opencv_contrib-${OPENCV_VERSION}" opencv_contrib

	sudo pip3 install virtualenv virtualenvwrapper
	sudo rm -rf ~/.cache/pip

	echo -e "\n# virtualenv and virtualenvwrapper" >> $PROFILE_FILE
	echo "export WORKON_HOME=$HOME/.virtualenvs" >> $PROFILE_FILE
	echo "export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3" >> $PROFILE_FILE
	echo -e "source /usr/local/bin/virtualenvwrapper.sh\n" >> $PROFILE_FILE
	source $PROFILE_FILE

	mkvirtualenv cv -p python3

# elif [[ $1 -eq 4 ]]; then

	workon cv

	pip3 install numpy
	pip3 install dropbox
	pip3 install imutils
	pip3 install "picamera[array]"

	cd ~/opencv/
	mkdir -p build
	cd build/
	cmake -D CMAKE_BUILD_TYPE=RELEASE \
	      -D CMAKE_INSTALL_PREFIX=/usr/local \
	      -D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib/modules \
	      -D ENABLE_NEON=ON \
          -D ENABLE_VFPV3=ON \
          -D BUILD_TESTS=OFF \
          -D OPENCV_ENABLE_NONFREE=ON \
	      -D INSTALL_C_EXAMPLES=OFF \
	      -D INSTALL_PYTHON_EXAMPLES=OFF \
	      -D BUILD_EXAMPLES=OFF ..

	sudo sed -i 's/CONF_SWAPSIZE=100/#CONF_SWAPSIZE=100\nCONF_SWAPSIZE=2048/g' /etc/dphys-swapfile
	sudo /etc/init.d/dphys-swapfile stop
	sudo /etc/init.d/dphys-swapfile start

	make -j1
	sudo make install
	sudo ldconfig
	
	sudo sed -i 's/CONF_SWAPSIZE=2048/#CONF_SWAPSIZE=2048/g' /etc/dphys-swapfile
	sudo sed -i 's/#CONF_SWAPSIZE=100/CONF_SWAPSIZE=100/g' /etc/dphys-swapfile
	sudo /etc/init.d/dphys-swapfile stop
	sudo /etc/init.d/dphys-swapfile start

	cd ~/.virtualenvs/cv/lib/python3.5/site-packages/
	ln -s /usr/local/lib/python3.5/site-packages/cv2 cv2
	cd ~/

	wget https://s3-us-west-2.amazonaws.com/static.pyimagesearch.com/ball-tracking/ball-tracking.zip
	unzip ball-tracking.zip

	sudo modprobe bcm2835-v4l2

	sudo reboot

else
	echo -e "\ninstall_opencv.sh\n"
	echo -e	"HOW TO USE:\n"
	echo -e	"Params:"
	echo -e	"\t1. Expand filesystem (requires reboot)"
	echo -e	"\t2. After 1 is complete, proceed with installation of OpenCV\n"
fi
