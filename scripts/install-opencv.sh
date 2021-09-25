#!/bin/sh
#
# Created on January 31, 2017
#
# @author: sgoldsmith
#
# Install OpenCV
#
# This should work on other ARM based systems with similar architecture and
# Ubuntu/Debian as well.
#
# Steven P. Goldsmith
# sgjava@gmail.com
# 

# Get start time
dateformat="+%a %b %-eth %Y %I:%M:%S %p %Z"
starttime=$(date "$dateformat")
starttimesec=$(date +%s)

# Get current directory
curdir=$(cd `dirname $0` && pwd)

# Source config file
. "$curdir"/config.sh

opencvhome="$buildhome/opencv"
contribhome="$buildhome/opencv_contrib"

# stdout and stderr for commands logged
logfile="$curdir/install-opencv.log"
rm -f $logfile

# Simple logger
log(){
	timestamp=$(date +"%m-%d-%Y %k:%M:%S")
	echo "$timestamp $1"
	echo "$timestamp $1" >> $logfile 2>&1
}

# Remove temp dir
log "Removing temp dir $tmpdir"
rm -rf "$tmpdir" >> $logfile 2>&1
mkdir -p "$tmpdir" >> $logfile 2>&1

# Uninstall OpenCV if it exists
if [ -d "$opencvhome" ]; then
	log "Uninstalling OpenCV"
	cd "$opencvhome/build" >> $logfile 2>&1
	sudo -E make uninstall >> $logfile 2>&1
	log "Removing $opencvhome"
	sudo -E rm -rf "$opencvhome" >> $logfile 2>&1
	log "Removing $contribhome"
	sudo -E rm -rf "$contribhome" >> $logfile 2>&1
fi

log "Installing OpenCV dependenices..."
# Install build tools
sudo -E apt-get -y install build-essential checkinstall pkg-config cmake yasm doxygen >> $logfile 2>&1

# Install media I/O libraries 
sudo -E apt-get -y install libpng-dev libtiff5-dev >> $logfile 2>&1

# Install video I/O libraries, support for Firewire video cameras and video streaming libraries
sudo -E apt-get -y install libdc1394-22-dev libavcodec-dev libavformat-dev libswscale-dev libavresample-dev libx264-dev libx265-dev libv4l-dev >> $logfile 2>&1

# Install the Python 3 development environment and the Python Numerical library
sudo -E apt-get -y install python3-dev python3-numpy >> $logfile 2>&1

# Install the parallel code processing and linear algebra library
sudo -E apt-get -y install opencl-headers libtbb2 libtbb-dev libeigen3-dev libatlas-base-dev >> $logfile 2>&1

# Fork or you get "The folder you are executing pip from can no longer be found."
(sudo -E apt-get -y install python3-pip >> $logfile 2>&1)
sudo -H pip3 install pygments  2>&1

cd "$buildhome" >> $logfile 2>&1
log "Cloning opencv..."
git clone --depth 1 https://github.com/Itseez/opencv.git >> $logfile 2>&1
#git clone -b 3.4 --depth 1 https://github.com/Itseez/opencv.git >> $logfile 2>&1
log "Cloning opencv_contrib..."
git clone --depth 1 https://github.com/Itseez/opencv_contrib.git >> $logfile 2>&1

# Compile OpenCV
log "Compile OpenCV..."
# Make sure root picks up JAVA_HOME for this process
export JAVA_HOME=$javahome
log "JAVA_HOME = $JAVA_HOME"
cd "$opencvhome"
mkdir build
cd build

log "Patch OpenCVCompilerOptions.cmake to apply cflags pre cmake"
sed -e "/set(OPENCV_EXTRA_C_FLAGS \"\")/c\set(OPENCV_EXTRA_C_FLAGS \"${extra_c_flag}\")" -i "$opencvhome/cmake/OpenCVCompilerOptions.cmake"
sed -e "/set(OPENCV_EXTRA_CXX_FLAGS \"\")/c\set(OPENCV_EXTRA_CXX_FLAGS \"${extra_c_flag}\")" -i "$opencvhome/cmake/OpenCVCompilerOptions.cmake"
export CFLAGS="$extra_c_flag"
export CXXFLAGS="$extra_c_flag"
log "CMake..."
# ARM 32, x86
if [ "$arch" = "i586" ] || [ "$arch" = "i686" ] || [ "$arch" = "armv7l" ]; then
	jpeglib="/opt/libjpeg-turbo/lib32/libjpeg.a"
# ARM 64, x86_64
elif [ "$arch" = "aarch64" ] || [ "$arch" = "x86_64" ]; then
	jpeglib="/opt/libjpeg-turbo/lib64/libjpeg.a"
fi
# Make any changes in config.sh cmakeopts for extra options
cmake -DOPENCV_EXTRA_MODULES_PATH=$contribhome/modules -DCMAKE_BUILD_TYPE=RELEASE -DCMAKE_INSTALL_PREFIX=/usr/local -DEXTRA_C_FLAGS=$extra_c_flag -DEXTRA_CXX_FLAGS=$extra_c_flag -DWITH_JPEG=ON -DBUILD_JPEG=OFF -DJPEG_INCLUDE_DIR=/opt/libjpeg-turbo/include -DJPEG_LIBRARY=$jpeglib $cmakeopts .. >> $logfile 2>&1
log "Make..."
sudo -E sh -c 'make -j$(getconf _NPROCESSORS_ONLN) && make install && echo "/usr/local/lib" > /etc/ld.so.conf.d/opencv.conf && ldconfig' >> $logfile 2>&1

# Clean up
log "Removing $tmpdir"
rm -rf "$tmpdir" 

# Get end time
endtime=$(date "$dateformat")
endtimesec=$(date +%s)

# Show elapsed time
elapsedtimesec=$(expr $endtimesec - $starttimesec)
ds=$((elapsedtimesec % 60))
dm=$(((elapsedtimesec / 60) % 60))
dh=$((elapsedtimesec / 3600))
displaytime=$(printf "%02d:%02d:%02d" $dh $dm $ds)
log "Elapsed time: $displaytime"
