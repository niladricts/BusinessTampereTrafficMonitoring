#!/bin/bash

# Safer bash scripting, see: https://explainshell.com/explain?cmd=set+-euxo+pipefail
set -euxo pipefail

### Update package lists, -qq suppresses output
sudo apt update -y -qq

### Install some general tools
sudo apt install -y software-properties-common git wget -qq


## OpenCV
sudo apt install -y libopencv-dev -qq


## CUDA / cuDNN
if ! dpkg -l libcudnn8; then
    # pre-installation steps
    sudo apt-get install linux-headers-$(uname -r) gcc

    OS=ubuntu2004
    cudnn_version=8.1.1.33
    wget -q "https://developer.download.nvidia.com/compute/cuda/repos/${OS}/x86_64/cuda-${OS}.pin"
    sudo mv "cuda-${OS}.pin" "/etc/apt/preferences.d/cuda-repository-pin-600"
    sudo apt-key adv --fetch-keys "https://developer.download.nvidia.com/compute/cuda/repos/${OS}/x86_64/7fa2af80.pub"
    sudo add-apt-repository "deb https://developer.download.nvidia.com/compute/cuda/repos/${OS}/x86_64/ /"
    sudo apt-get update
    sudo apt-get install --no-install-recommends \
        cuda-11-2 \
        libcudnn8=${cudnn_version}-1+cuda11.2 -qq \
        libcudnn8-dev=${cudnn_version}-1+cuda11.2 -qq
fi


### Python installation check

echo "Checking python installation..."
if python3 -c 'import sys; exit(sys.version_info.major != 3 or sys.version_info.minor < 9)'; then
    echo "Python 3.9+ already installed."
else
    sudo add-apt-repository -y ppa:deadsnakes/ppa
    sudo apt install -y python3.9 python3.9-dev python3.9-venv -qq
    echo "Installed Python 3.9."
fi


### Create virtual environment & install required Python packages inside
python3.9 -m venv env
env/bin/pip install -r requirements.txt


# Download weights for machine learning
test -f yolov4.weights || wget -q "https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v3_optimal/yolov4.weights"

if ! test -f yolov4.h5; then
    # activate virtual environment to have access to convert-darknet-weights
    source env/bin/activate
    # convert weights to tensorflow format
    convert-darknet-weights yolov4.weights -o yolov4.h5
fi
