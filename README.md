# Calan Multi-BeamFormer

The Calan-MBF project aims to build a platform for multiple-beamforming applications, based on [CASPER](https://www.google.com) hardware.

## Requirements & Libraries
The core software for development is Matlab 2013a and  Xilinx ISE 14.7, running in a Ubuntu 12.04 machine (newer versions are also apt, but this is the OS we use at the lab).

Some other softwares needed are Ruby 1.9.1 (*with RubyGems*) and Python 2.7.

Important libraries can be obtained/installed as follows:
1. CASPER `mlib_devel`:
Open a terminal and execute these commands
  ```bash
  git clone https://github.com/FranciscoCasado/mlib_devel.git
  ```
  This repo is a fork from [casper-astro](https://github.com/casper-astro/mlib_devel) (0c3f334) with downgraded pcores in order to compile and *work* with test files (detailed later).

2. Missing `pcores`:
As as the CASPER [toolflow settings page](https://casper.berkeley.edu/wiki/MSSGE_Setup_with_Xilinx_14.x_and_Matlab_2012b) says, there are some *tweaks to be able to compile*. The most important is to download the compressed folder that has the missing `pcores` from Xilinx. Extract the files to `mlib_devel/xps_base/XPS_ROACH2_base/pcores`.

3. Set local environment variables:
In the `mlib_devel` folder, there is the file `startsg`, which can be run from a terminal and opens matlab and loads the necessary CASPER libraries. This file requieres de definition of at least three environment variables that can be written into another file (created by each user) named `startsg.local`:
  ```
  MATLAB_PATH=/usr/local/MATLAB/R2013a/
  XILINX_PLATFORM=lin64
  XILINX_PATH=/opt/Xilinx/14.7/ISE_DS
  ```
 Replace the correct Matlab and Xilinx version numbers in each path. Also verify that these are the actual installation felder paths.

4. CASPER `corr` library: install it via pip
  ```bash
  pip install corr
  ```
  This python library includes `katcp`, which is required to stablish communication between your PC and a ROACH2.

5. Ruby files for testing - *by [davidm](https://github.com/david-macmahon)*

  ```bash
  gem install --source http://astro.berkeley.edu/~davidm/gems adc16
  git clone git://github.com/david-macmahon/casper_adc16.git
  gem install pgplot
  gem install --source http://astro.berkeley.edu/~davidm/gems pgplotter
  gem install gsl
  ```
If `gsl` installation fails, [this page](https://coderwall.com/p/jk--aw/ruby-gsl-error-failed-to-build-gem-native-extension) should help.

## Hardware
A [ROACH2 rev2](https://casper.berkeley.edu/wiki/ROACH2) and an [ADC16x250-8 coax rev 2](https://casper.berkeley.edu/wiki/ADC16x250-8_coax_rev_2) (single ended SMB input).

## Test the hardware

The `utilities` folder contains the source written by davidm and a simulink model `adc16_1brd_200_rev2a.slx`, with its respective .bof file.

1. Power up the ROACH2 and connect it to the local network (same as your PC). Connect the clock source to the ADC16 board (at the lab we have a Valon Synthesizer) and plug the ADC16 inputs to some RF signal. Make sure the clock source supplies 6 dBm (valon_synth lvl. 4) and the RF signal of each input is near 0 dBm.
2. On your PC, open an iPython session to upload the .bof file to the ROACH2 with katcp. In a terminal, type `$ ipython` and enter the following commands:
  ```python
  In [1]: import corr
  In [2]: fpga = corr.katcp_wrapper.FpgaClient('ROACH2_ip_address')
  In [3]: fpga.upload_bof('utilities/adc16_test/model/adc16_1brd_200_rev2a.bof', 60000)
  ```
  The number 60000 in the third line corresponds to the port that the file transfer will use, as the default katcp 7147 is already in use. Any number greater than 10000 should also work.
  To check that the .bof arrived, type
  ```python
  In [4]: fpga.listbof()
  ```
3. Open another terminal and execute the shell script `adc16_test`. This script runs two ruby routines that turn ADC boards on, calibrates all channels (A,B,C,D) and then plots a snapshot of every signal. These routines can be run individually from the terminal:
  ```bash
  cd utils/adc16_test/src/bin
  ruby1.9.1 ./adc16_init.rb --demux 1 ROACH2_ip_address adc16_1brd_200_rev2a.bof
  ruby1.9.1 ./adc16_plot_chans.rb ROACH2_ip_address
  ```
  Note that the .bof file name does not contain the path, as it is the copy uploaded to the ROACH2.

## Calibration Process

Current state of the project is tuning the analog gain of the down-converters and. After that, phase calibrations must be performed in order to achieve coherent signals.

### Amplitude Calibration

The down-converters (MAX2851) have programmable analog gain adjustment. In order to monitor the amplitude while changing the gain, a simple model and python scripts are available in the `models/read_power` folder. The model consists of snapshots and power integrators; the python script is permanently reading the data and displaying them in two figures: _RMS_-power and snapshots of everysignal.

To run this script, the user must have programmed the ROACH2 and calibrated the ADC board. This can be done automatically by running the shell script `adc16_test`. After that, the python script can be run:
  ```bash
  ./adc16_test
  python read_power_16chan.py
  ```

