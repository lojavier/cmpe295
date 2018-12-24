#!/bin/bash

################################################################################
# Simple script to install OpenCV 3.4 on Raspbian Stretch OS
#	- https://opencv.org/releases.html
# 	- https://www.raspberrypi.org/downloads/raspbian/
#
# Example:
# install_opencv.sh 1
# install_opencv.sh 2
################################################################################

################################################################################
# STEP 1
# 	- Expand root filesystem
################################################################################
if [[ $1 -eq 1 ]]; then
	sudo raspi-config --expand-rootfs
	sudo reboot
	
################################################################################
# STEP 2
#	- Remove uneccessary packages/libraries
#	- Install neccesary packages/libraries for OpenCV preparation
################################################################################
elif [[ $1 -eq 2 ]]; then
	sudo apt-get purge -y wolfram-engine
	sudo apt-get purge -y libreoffice*
	sudo apt-get clean -y
	sudo apt-get autoremove -y

	sudo apt-get update -y
	sudo apt-get upgrade -y
	sudo rpi-update
	
	sudo apt-get install -y build-essential git cmake pkg-config
	sudo apt-get install -y libtbb2 libtbb-dev libjpeg-dev libjpeg8-dev  libtiff5-dev libjasper-dev libpng12-dev
	sudo apt-get install -y libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
	sudo apt-get install -y libxvidcore-dev libx264-dev
	sudo apt-get install -y libgtk2.0-dev libgtk-3-dev
	sudo apt-get install -y libcanberra-gtk*
	sudo apt-get install -y libatlas-base-dev gfortran
	sudo apt-get install -y python-dev python2.7-dev python3-dev python-numpy
	sudo apt-get install -y python-picamera python3-picamera
	
	sudo apt-get clean -y
	sudo apt-get autoremove -y

################################################################################
# STEP 3
#	- Clone & install OpenCV packages/libraries via GitHub
################################################################################
elif [[ $1 -eq 3 ]]; then

	cd ~/
	git clone -b '3.4' https://github.com/opencv/opencv.git

	cd ~/
	git clone -b '3.4' https://github.com/opencv/opencv_contrib.git

	sudo apt-get install -y python-pip python3-pip

	sudo pip install virtualenv virtualenvwrapper
	sudo rm -rf ~/.cache/pip
	sudo pip3 install virtualenv virtualenvwrapper
	sudo rm -rf ~/.cache/pip

	PROFILE=~/.profile
	echo -e "\n# virtualenv and virtualenvwrapper" >> $PROFILE
	echo "export WORKON_HOME=$HOME/.virtualenvs" >> $PROFILE
	echo "export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3" >> $PROFILE
	echo -e "source /usr/local/bin/virtualenvwrapper.sh\n" >> $PROFILE
	source $PROFILE

	mkvirtualenv cv -p python2
	source $PROFILE
	mkvirtualenv cv -p python3
	source $PROFILE
	workon cv

	pip install numpy
	pip3 install numpy

	cd ~/opencv/
	mkdir -p build
	cd build/
	cmake -D CMAKE_BUILD_TYPE=RELEASE \
	      -D CMAKE_INSTALL_PREFIX=/usr/local \
	      -D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib/modules \
	      -D ENABLE_NEON=ON \
              -D ENABLE_VFPV3=ON \
              -D BUILD_TESTS=ON \
	      -D INSTALL_C_EXAMPLES=ON \
	      -D INSTALL_PYTHON_EXAMPLES=ON \
	      -D BUILD_EXAMPLES=ON ..

	sudo sed -i 's/CONF_SWAPSIZE=100/#CONF_SWAPSIZE=100\nCONF_SWAPSIZE=1024/g' /etc/dphys-swapfile
	sudo /etc/init.d/dphys-swapfile stop
	sudo /etc/init.d/dphys-swapfile start

	make -j4
	sudo make install
	sudo ldconfig
	
	sudo sed -i 's/CONF_SWAPSIZE=1024/#CONF_SWAPSIZE=1024/g' /etc/dphys-swapfile
	sudo sed -i 's/#CONF_SWAPSIZE=100/CONF_SWAPSIZE=100/g' /etc/dphys-swapfile
	sudo /etc/init.d/dphys-swapfile stop
	sudo /etc/init.d/dphys-swapfile start

	cd ~/.virtualenvs/cv/lib/python2.7/site-packages/
	ln -s /usr/local/lib/python2.7/site-packages/cv2.so cv2.so
	
	cd /usr/local/lib/python3.5/site-packages/
	sudo mv cv2.cpython-35m-arm-linux-gnueabihf.so cv2.so
	cd ~/.virtualenvs/cv/lib/python3.5/site-packages/
	ln -s /usr/local/lib/python3.5/site-packages/cv2.so cv2.so
	
else
	echo -e "\ninstall_opencv.sh\n"
	echo -e	"HOW TO USE:\n"
	echo -e	"Params:"
	echo -e	"\t1. Expand filesystem (requires reboot)"
	echo -e	"\t2. After 1 is complete, proceed with installation of OpenCV\n"
fi
