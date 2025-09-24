---
layout: post
title: Installing Gromacs for local Molecular Dynamics simulation
date: 2025-09-24 12:19 +0200
categories: [Projects, Homemade ML, Life Science]
tags: [data science, machine learning, self-hosted, molecular dynamics, simulation]

---
{% assign image_path = "/assets/images/projects/homemade_ml/getting_started_with_local_md_simulation/" %}



## Table of contents
  - [Table of contents](#table-of-contents)
  - [Background](#background)
  - [Getting the last version of C and C++ compilers](#getting-the-last-version-of-c-and-c-compilers)
  - [Installing cmake](#installing-cmake)
  - [Installing Cuda tool kit (and also the driver)](#installing-cuda-tool-kit-and-also-the-driver)
    - [Get the toolkit installer](#get-the-toolkit-installer)
  - [Getting the last version of Gromacs](#getting-the-last-version-of-gromacs)
  - [Building Gromacs](#building-gromacs)




## Background


That might sound surprising, but something I never really had the time to do (at least at home), was to get my hands dirty with Molecular dynamics (MD) simulation. Thus after having set up a new ssd and reinstalled a ubuntu based OS twice (don't ask about this story) on my desktop, I thought it might be the right time to dig into the MD topic.

Obviously running local MD simulation is probably not good for any setup, luckily, my beast still have a 3070 RTX GPU, nothing's impressive but that also forces us to deal with all the GPU acceleration part.

According to [wikipedia](https://en.wikipedia.org/wiki/Molecular_dynamics), MD simulation is:
> "a computer simulation method for studying the physical movements of atoms and molecules, allowing us to observe the motion of the particles over time. The atoms and molecules are allowed to interact for a fixed period, giving a view of the dynamic evolution of the system. In the most common version, the trajectories of atoms and molecules are determined by numerically solving Newton's equations of motion for a system of interacting particles, where forces between the particles and potential energy are defined by molecular mechanics force fields."

Basically it allows to simulate the behavior of atoms and molecules over time, which is useful for understanding the properties of materials, biological systems, and chemical reactions. Futhermore, MD simulation is widely used in various fields such as drug discovery, materials science, and biophysics. Thanks to the advancements in data science and machine learning, MD simulation can be enhanced by using techniques such as deep learning to predict the behavior of complex systems, or to optimize the parameters of the simulation. So much to be excited about this topic!


Gromacs is a widely used open-source software package for performing molecular dynamics simulations. Most of the time, Gromacs is installed on HPC clusters and most Life Science researchers will never have to install it through their life. But Eh, we all know I like doing such stuff.

[Gromacs installation guide](https://manual.gromacs.org/current/install-guide/index.html) is.. complete, maybe too much. But we can divide it step by step. Please note, I am installing everything on a kde neon 64 bits (ubuntu based) system.

## Getting the last version of C and C++ compilers

We're probably already good there, but let's make sure we have the last version of gcc and g++ installed:

```bash
sudo apt update
sudo apt install build-essential
```

## Installing cmake


```bash
sudo apt install cmake
```

We can then check the version:

```bash
cmake --version
```
I personally have version 3.30.5

## Installing Cuda tool kit (and also the driver)

For some reason, I always struggle to install my cuda tool kit properly. Probably because, there's so many ways out there on how to do it and everybody seems to have their own preferences.

From my point of view, I want:
- to have the toolkit 13.0 (latest as of today)
- to have the nvidia driver installed
- to do it through the package manager (apt), so it can be updated easily

Most of the tutorials I saw recommends to go through a full apt approach and install the toolkit from there. However, for me this results in a cuda version 12.04, which is not what I want.

So here's how I do it:

### Get the toolkit installer:

I go to the [cuda toolkit download section](https://developer.nvidia.com/cuda-downloads) and select:
- Operating System: Linux
- Architecture: x86_64
- Distribution: Ubuntu
- Version: 24.04
- Installer Type: deb (network)

It gives me the url to get the deb file, that I can download and install:

\bold{You should probably check the website to get the last version of the deb file}

```bash
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update
sudo apt-get -y install cuda-toolkit-13-0
```
That should normally gives us the nvcc compiler and the cuda toolkit. If you are like me nvcc --version won't work right away, because the path to cuda is not set. We can add it to our .bashrc file (nano ~/.bashrc):

and we had the following lines at the end of the file:

```bash
export PATH=/usr/local/cuda-13.0/bin${PATH:+:${PATH}}
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/usr/local/cuda/lib64
```

Then we can source the .bashrc file:

```bash
source ~/.bashrc
```
that should do the trick for nvcc.

We can check if Cuda is installed by running:

```bash
nvcc --version
```
or

```bash
nvidia-smi
```

While we are here, we can also installed the nvidia driver. My secure boot is disable, so I had no issue using the nvidia driver from the apt repository:

```bash
sudo apt-get install -y cuda-drivers
```


## Getting the last version of Gromacs

We have to download the source code from their [download section](https://manual.gromacs.org/current/download.html). I got the https link which gave me gromacs-2025-3.tar.gz

We can then extract it:

```bash
tar -xvzf gromacs-2025-3.tar.gz
cd gromacs-2025-3

```
## Building Gromacs

We can now create a build directory and run cmake.

There's a buch of option that I would like to setup for my installation, let's review them

-DCMAKE_C_COMPILER = gcc # specify the C and C++ compilers to use
-DCMAKE_CXX_COMPILER = g++ # specify the C and C++ compilers to use
-DGMX_GPU=CUDA # enable GPU acceleration using CUDA
-DGMX_BUILD_OWN_FFTW=ON # To let Gromacs build its own FFTW (Fast Fourier Transform library) 



And that should be it for the configuration part, let's run cmake:

```bash
mkdir build
cd build
cmake .. -DCMAKE_C_COMPILER=gcc -DCMAKE_CXX_COMPILER=g++ -DGMX_GPU=CUDA -DGMX_BUILD_OWN_FFTW=ON 
```

If at any step cmake fails, check the error message. delete the build directory, recreate it and run cmake again after fixing the issue.

Then we can compile Gromacs using make, and install it:

To fasten the compilation, we can use the -j flag followed by the number of cores we want to use. I have a 16 cores CPU, so I will use -j16. It will probably take some time, depending on how many cores you use.

```bash
make -j16
make check
sudo make install
```ls

Finally, we need to source the Gromacs binary to use it:

```bash
source /usr/local/gromacs/bin/GMXRC
```

And that's it, we can now check if Gromacs is installed properly by running:

```bash
gmx --version
```