#!/bin/bash

################################################################################
# Simple script to install OpenCV 3 on Ubuntu 18.04 OS
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
	
	sudo apt-get install -y build-essential git cmake unzip pkg-config curl
	sudo apt-get install -y libjpeg-dev libpng-dev libpng12-dev libtiff-dev libtiff5-dev
	sudo apt-get install -y libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libavdevice-dev
	sudo apt-get install -y libxvidcore-dev libx264-dev libgstreamer1.0-dev
	sudo apt-get install -y libgtk2.0-dev libgtk-3-dev
	sudo apt-get install -y libcanberra-gtk*
	sudo apt-get install -y libatlas-base-dev gfortran
	sudo apt-get install -y python3-dev python3-picamera python3-pip
	
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

	echo -e "\n# virtualenv and virtualenvwrapper" >> $BASHRC_FILE
	echo "export WORKON_HOME=$HOME/.virtualenvs" >> $BASHRC_FILE
	echo "export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3" >> $BASHRC_FILE
	echo -e "source /usr/local/bin/virtualenvwrapper.sh\n" >> $BASHRC_FILE
	source $BASHRC_FILE

	mkvirtualenv cv -p python3

# elif [[ $1 -eq 4 ]]; then

	workon cv

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
		-D ENABLE_NEON=ON \
    	-D ENABLE_VFPV3=ON \
		-D WITH_GSTREAMER=ON \
		-D WITH_FFMPEG=ON \
		-D WITH_TBB=ON \
		-D WITH_GTK=ON \
		-D WITH_LIBV4L=ON \
		-D WITH_V4L=ON \
		-D WITH_OPENGL=ON \
		-D WITH_CUBLAS=ON \
		-D WITH_QT=OFF \
		-D CUDA_NVCC_FLAGS="-D_FORCE_INLINES --expt-relaxed-constexpr" \
		-D BUILD_EXAMPLES=ON ..

	make -j4
	sudo make install
	sudo ldconfig

	cd /usr/local/lib/python3.6/site-packages/cv2/python-3.6/
	sudo mv cv2.cpython-36m-x86_64-linux-gnu.so cv2.so

	cd ~/.virtualenvs/cv/lib/python3.6/site-packages/
	ln -s /usr/local/lib/python3.6/site-packages/cv2/python-3.6/cv2.so cv2.so

	cd ~/
	wget https://s3-us-west-2.amazonaws.com/static.pyimagesearch.com/ball-tracking/ball-tracking.zip
	unzip ball-tracking.zip

	wget https://s3-us-west-2.amazonaws.com/static.pyimagesearch.com/opencv-yolo/yolo-object-detection.zip
	unzip yolo-object-detection.zip

	wget https://s3-us-west-2.amazonaws.com/static.pyimagesearch.com/pi-object-detection/pi-object-detection.zip
	unzip pi-object-detection.zip

	sudo modprobe bcm2835-v4l2

	sudo apt-get install openjdk-8-jdk
	echo "deb [arch=amd64] http://storage.googleapis.com/bazel-apt stable jdk1.8" | sudo tee /etc/apt/sources.list.d/bazel.list
	curl https://bazel.build/bazel-release.pub.gpg | sudo apt-key add -
	sudo apt-get update && sudo apt-get install -y bazel

	wget https://s3-us-west-2.amazonaws.com/static.pyimagesearch.com/machine-learning-python/python-machine-learning.zip
	unzip python-machine-learning.zip

	wget https://s3-us-west-2.amazonaws.com/static.pyimagesearch.com/keras-save-load/keras-save-load.zip
	unzip keras-save-load.zip

	wget https://s3-us-west-2.amazonaws.com/static.pyimagesearch.com/keras-tutorial/keras-tutorial.zip
	unzip keras-tutorial.zip

	sudo reboot

else
	echo -e "\ninstall_opencv.sh\n"
	echo -e	"HOW TO USE:\n"
	echo -e	"Params:"
	echo -e	"\t1. Expand filesystem (requires reboot)"
	echo -e	"\t2. After 1 is complete, proceed with installation of OpenCV\n"
fi
