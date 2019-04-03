#!/bin/bash

################################################################################
# Simple script to install OpenCV 4 on Ubuntu 16.04/18.04
#	- https://opencv.org/releases.html
################################################################################
OPENCV_VERSION="4.0.1"
cd ~/
BASHRC_FILE="${HOME}/.bashrc"

################################################################################
# STEP 1
#	- Remove uneccessary packages/libraries
#	- Install neccesary packages/libraries for OpenCV preparation
################################################################################
sudo apt-get purge -y wolfram-engine
sudo apt-get purge -y libreoffice*
sudo apt-get clean -y
sudo apt-get autoremove -y

sudo apt-get update -y && sudo apt-get upgrade -y
sudo apt-get update -y --fix-missing && sudo apt-get upgrade -y

sudo apt update -y && sudo apt upgrade -y
sudo apt update -y --fix-missing && sudo apt upgrade -y

if [[ 1 -eq 1 ]]; then
	sudo apt-get install -y net-tools
	sudo apt-get install -y virtualbox-guest-additions-iso
	sudo apt-get install -y virtualbox-guest-dkms
	sudo apt-get install -y virtualbox-guest-x11
fi

for ((a=0; a <= 1; a++))
do
	sudo apt-get install -y build-essential cmake unzip pkg-config
	sudo apt-get install -y libjpeg-dev libpng-dev libtiff-dev
	sudo apt-get install -y libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
	sudo apt-get install -y libxvidcore-dev libx264-dev
	sudo apt-get install -y libgtk-3-dev
	sudo apt-get install -y libatlas-base-dev gfortran
	sudo apt-get install -y python3-dev

	sudo apt-get update -y --fix-missing
done

sudo apt-get clean -y
sudo apt-get autoremove -y

################################################################################
# STEP 2
#	- Clone & unzip OpenCV packages/libraries via OpenCV archive directory
################################################################################
cd ~/
wget -O opencv.zip "https://github.com/opencv/opencv/archive/${OPENCV_VERSION}.zip"
wget -O opencv_contrib.zip "https://github.com/opencv/opencv_contrib/archive/${OPENCV_VERSION}.zip"

unzip opencv.zip
unzip opencv_contrib.zip

mv "opencv-${OPENCV_VERSION}" opencv
mv "opencv_contrib-${OPENCV_VERSION}" opencv_contrib

################################################################################
# STEP 3
#	- Setup OpenCV virtual environment
################################################################################
cd ~/
wget https://bootstrap.pypa.io/get-pip.py
sudo python3 get-pip.py
sudo pip install virtualenv virtualenvwrapper
sudo rm -rf ~/get-pip.py ~/.cache/pip

echo -e "\n# virtualenv and virtualenvwrapper" >> $BASHRC_FILE
echo "export WORKON_HOME=$HOME/.virtualenvs" >> $BASHRC_FILE
echo "export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3" >> $BASHRC_FILE
echo "source /usr/local/bin/virtualenvwrapper.sh" >> $BASHRC_FILE
source $BASHRC_FILE
export WORKON_HOME=$HOME/.virtualenvs
export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
source /usr/local/bin/virtualenvwrapper.sh

mkvirtualenv cv -p python3

[[ "$VIRTUAL_ENV" == "" ]]; INVENV=$?
if [[ "$INVENV" == "1" ]]; then

	workon cv

	pip install --upgrade numpy
	pip install --upgrade imutils

	cd ~/opencv/
	mkdir -p build
	cd build/
	cmake -D CMAKE_BUILD_TYPE=RELEASE \
		-D CMAKE_INSTALL_PREFIX=/usr/local \
		-D INSTALL_PYTHON_EXAMPLES=ON \
		-D INSTALL_C_EXAMPLES=OFF \
		-D OPENCV_ENABLE_NONFREE=ON \
		-D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib/modules \
		-D PYTHON_EXECUTABLE=~/.virtualenvs/cv/bin/python3 \
		-D BUILD_EXAMPLES=ON ..

	make -j4

	sudo make install
	sudo ldconfig

	cd /usr/local/lib/python3.6/site-packages/cv2/python-3.6/
	sudo mv cv2.cpython-36m-x86_64-linux-gnu.so cv2.so

	cd ~/.virtualenvs/cv/lib/python3.6/site-packages/
	ln -s /usr/local/lib/python3.6/site-packages/cv2/python-3.6/cv2.so cv2.so

	deactivate

	cd ~/

fi
