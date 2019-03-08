#!/bin/bash

################################################################################
# Simple script to install OpenCV 3 on Ubuntu 18.04
#	- https://opencv.org/releases.html
#
# Example:
# install_opencv.sh 1
# install_opencv.sh 2
################################################################################
OPENCV_VERSION="3.4.5"
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
	sudo apt-get install -y build-essential git cmake unzip pkg-config curl
	sudo apt-get install -y libjpeg-dev libpng-dev libtiff-dev libtbb-dev qt5-default
	sudo apt-get install -y libavcodec-dev libavformat-dev libavdevice-dev libswscale-dev
	sudo apt-get install -y libv4l-dev libdc1394-22-dev
	sudo apt-get install -y libxvidcore-dev libx264-dev
	sudo apt-get install -y libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libgstreamer-opencv1.0-0
	sudo apt-get install -y libgtk2.0-dev libgtk-3-dev
	sudo apt-get install -y libatlas-base-dev gfortran
	sudo apt-get install -y libcanberra-gtk*
	sudo apt-get install -y python3-dev python3-pip

	sudo apt-get update -y --fix-missing
done

sudo apt-get clean -y
sudo apt-get autoremove -y

################################################################################
# STEP 2
#	- Clone & unzip OpenCV packages/libraries via OpenCV archive directory
################################################################################
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
sudo pip3 install virtualenv virtualenvwrapper
sudo rm -rf ~/.cache/pip

echo -e "\n# virtualenv and virtualenvwrapper" >> $BASHRC_FILE
echo "export WORKON_HOME=$HOME/.virtualenvs" >> $BASHRC_FILE
echo "export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3" >> $BASHRC_FILE
echo -e "source /usr/local/bin/virtualenvwrapper.sh\n" >> $BASHRC_FILE
source $BASHRC_FILE

mkvirtualenv cv -p python3

[[ "$VIRTUAL_ENV" == "" ]]; INVENV=$?
if [[ "$INVENV" == "1" ]]; then

	pip3 install --upgrade numpy
	pip3 install --upgrade imutils
	pip3 install --upgrade scikit-learn
	pip3 install --upgrade matplotlib
	pip3 install --upgrade pillow
	pip3 install --upgrade tensorflow
	pip3 install --upgrade keras

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
		-D WITH_TBB=ON \
		-D WITH_LIBV4L=ON \
		-D WITH_V4L=ON \
		-D WITH_OPENGL=ON \
		-D WITH_QT=ON \
		-D WITH_FFMPEG=ON \
		-D WITH_GTK=ON \
		-D BUILD_EXAMPLES=ON ..
		# -D WITH_GSTREAMER=ON \
		# -D ENABLE_VFPV3=ON \
		# -D ENABLE_NEON=ON \
		# -D WITH_CUBLAS=ON \
		# -D WITH_CUDA=OFF \
		# -D CUDA_NVCC_FLAGS="-D_FORCE_INLINES --expt-relaxed-constexpr" ..

	make -j4
	sudo make install
	sudo ldconfig

	cd /usr/local/lib/python3.6/site-packages/cv2/python-3.6/
	sudo mv cv2.cpython-36m-x86_64-linux-gnu.so cv2.so

	cd ~/.virtualenvs/cv/lib/python3.6/site-packages/
	ln -s /usr/local/lib/python3.6/site-packages/cv2/python-3.6/cv2.so cv2.so

	cd ~/

fi
# wget https://s3-us-west-2.amazonaws.com/static.pyimagesearch.com/ball-tracking/ball-tracking.zip
# unzip ball-tracking.zip

# wget https://s3-us-west-2.amazonaws.com/static.pyimagesearch.com/opencv-yolo/yolo-object-detection.zip
# unzip yolo-object-detection.zip

# wget https://s3-us-west-2.amazonaws.com/static.pyimagesearch.com/pi-object-detection/pi-object-detection.zip
# unzip pi-object-detection.zip

# sudo modprobe bcm2835-v4l2

# sudo apt-get install openjdk-8-jdk
# echo "deb [arch=amd64] http://storage.googleapis.com/bazel-apt stable jdk1.8" | sudo tee /etc/apt/sources.list.d/bazel.list
# curl https://bazel.build/bazel-release.pub.gpg | sudo apt-key add -
# sudo apt-get update && sudo apt-get install -y bazel

# wget https://s3-us-west-2.amazonaws.com/static.pyimagesearch.com/machine-learning-python/python-machine-learning.zip
# unzip python-machine-learning.zip

# wget https://s3-us-west-2.amazonaws.com/static.pyimagesearch.com/keras-save-load/keras-save-load.zip
# unzip keras-save-load.zip

# https://www.pyimagesearch.com/2015/09/21/opencv-track-object-movement/#comment-382155
# wget https://s3-us-west-2.amazonaws.com/static.pyimagesearch.com/track-object-movement/track-object-movement.zip
# unzip track-object-movement.zip

# wget https://s3-us-west-2.amazonaws.com/static.pyimagesearch.com/keras-tutorial/keras-tutorial.zip
# unzip keras-tutorial.zip

# wget https://www.pyimagesearch.com/wp-content/uploads/2015/01/auto-canny.zip
# unzip auto-canny.zip

# wget wget https://s3-us-west-2.amazonaws.com/static.pyimagesearch.com/holistically-nested-edge-detection/holistically-nested-edge-detection.zip
# unzip holistically-nested-edge-detection.zip

# sudo reboot

# else
# 	echo -e "\ninstall_opencv.sh\n"
# 	echo -e	"HOW TO USE:\n"
# 	echo -e	"Params:"
# 	echo -e	"\t1. Expand filesystem (requires reboot)"
# 	echo -e	"\t2. After 1 is complete, proceed with installation of OpenCV\n"
# fi
