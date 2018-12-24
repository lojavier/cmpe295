#!/bin/bash
# https://www.pyimagesearch.com/2018/09/26/install-opencv-4-on-your-raspberry-pi/

# raspi-config --expand-rootfs

USER=`whoami`
USER_DIR="/home/${USER}/"
PROFILE_FILE="${USER_DIR}.profile"

sudo apt-get purge -y wolfram-engine
sudo apt-get purge -y libreoffice*
sudo apt-get clean -y
sudo apt-get autoremove -y

sudo apt-get update -y
sudo apt-get upgrade -y
sudo rpi-update

# sudo apt-get install -y busybox
sudo apt-get install -y build-essential git cmake unzip pkg-config
sudo apt-get install -y libtbb2 libtbb-dev libjpeg-dev libjpeg8-dev libjasper-dev
sudo apt-get install -y libtiff-dev libtiff5-dev
sudo apt-get install -y libpng-dev libpng12-dev
sudo apt-get install -y libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
sudo apt-get install -y libxvidcore-dev libx264-dev
sudo apt-get install -y libgtk2.0-dev libgtk-3-dev
sudo apt-get install -y libcanberra-gtk*
sudo apt-get install -y libatlas-base-dev gfortran
sudo apt-get install -y libhdf5-dev libhdf5-serial-dev
sudo apt-get install -y libqtwebkit4 libqt4-test libqtgui4
sudo apt-get install -y libilmbase-dev libopenexr-dev libgstreamer1.0-dev
sudo apt-get install -y python3-dev python3-pip python3-pyqt5 python3-picamera

sudo pip3 install --upgrade pip
sudo pip3 install virtualenv virtualenvwrapper
sudo pip3 install opencv-contrib-python
sudo pip3 install imutils
sudo pip3 install "picamera[array]"

# sudo pip3 install opencv-contrib-python-headless
# sudo pip3 install opencv-python
# sudo pip3 install opencv-python-headless

echo -e "\n# virtualenv and virtualenvwrapper" >> $PROFILE_FILE
echo -e "export WORKON_HOME=$HOME/.virtualenvs" >> $PROFILE_FILE
echo -e "export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3" >> $PROFILE_FILE
echo -e "source /usr/local/bin/virtualenvwrapper.sh\n" >> $PROFILE_FILE
source $PROFILE_FILE

mkvirtualenv cv -p python3
workon cv
sudo apt-get install -y libjasper-dev
pip3 install opencv-contrib-python
pip3 install imutils
pip3 install numpy
pip3 install "picamera[array]"
deactivate cv

sudo apt-get autoremove -y
sudo apt-get clean -y
