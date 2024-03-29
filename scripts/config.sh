#!/bin/sh
#
# Created on February 21, 2017
#
# @author: sgoldsmith
#
# Make sure you change this before running any script!
#
# Tested configs:
#
# x86 generic (no GPU/VPU optimizations)
#
# If you get SSSE3 - NOT AVAILABLE error add -DENABLE_SSSE3=OFF
#
# extracflag=""
# cmakeopts="-DBUILD_EXAMPLES=OFF -DBUILD_TESTS=OFF -DBUILD_PERF_TESTS=OFF -DWITH_QT=OFF -DWITH_GTK=OFF -DWITH_TBB=ON -DBUILD_TBB=ON"
#
# OpenCV 3.2 detects NEON, so we leave that out
#
# CHIP R8 - TBB build failed, so we use built in one
#
# extracflag="-mtune=cortex-a8 -mfloat-abi=hard"
# cmakeopts="-DBUILD_EXAMPLES=OFF -DBUILD_TESTS=OFF -DBUILD_PERF_TESTS=OFF -DWITH_QT=OFF -DWITH_GTK=OFF -DWITH_TBB=ON -DBUILD_TBB=OFF -DENABLE_NEON=ON"
#
# Pine64 - Carotene fails with "conflicts with asm clobber list", so we disable
#
# extra_c_flag="-mtune=cortex-a53"
# cmakeopts="-DBUILD_EXAMPLES=OFF -DBUILD_TESTS=OFF -DBUILD_PERF_TESTS=OFF -DWITH_QT=OFF -DWITH_GTK=OFF -DWITH_TBB=ON -DBUILD_TBB=ON -DWITH_CAROTENE=OFF"
#
# NanoPi Duo - Used 512MB version + swap and still ran out of memory, so use this
#
# extracflag="--param ggc-min-expand=0 --param ggc-min-heapsize=8192"
# cmakeopts="-DBUILD_EXAMPLES=OFF -DBUILD_TESTS=OFF -DBUILD_PERF_TESTS=OFF -DWITH_QT=OFF -DWITH_GTK=OFF -DWITH_TBB=ON -DBUILD_TBB=OFF -DENABLE_NEON=ON"
#
# Steven P. Goldsmith
# sgjava@gmail.com
# 

# Get architecture
arch=$(uname -m)

# Temp dir for downloads, etc.
tmpdir="$HOME/temp"

# Build home
buildhome="$HOME"

# OpenCV extra cflags
extracflag=""

# Custom cmake options
cmakeopts="-DBUILD_EXAMPLES=OFF -DBUILD_TESTS=OFF -DBUILD_PERF_TESTS=OFF -DWITH_QT=OFF -DWITH_GTK=OFF -DWITH_TBB=ON -DBUILD_TBB=ON"

# Zulu OpenJDK
# ARM 32
if [ "$arch" = "armv7l" ]; then
	javahome=/usr/lib/jvm/jdk11
else
	javahome=/usr/lib/jvm/jdk17
fi
export javahome

# Make sure we support architecture
if [ "$arch" = "i586" ] || [ "$arch" = "i686" ] || [ "$arch" = "armv7l" ] || [ "$arch" = "aarch64" ] || [ "$arch" = "x86_64" ]; then
	echo "\nArchitecture supported."
# Not supported
else
	echo "\nNo supported architectures detected!"
	exit 1
fi
