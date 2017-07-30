# Calan Multi-BeamFormer

The Calan-MBF project aims to build a platform for multiple-beamforming applications, based on [CASPER](https://www.google.com) hardware.

## Requirements & Libraries
The core software for development is Matlab 2013a and  Xilinx ISE 14.7, running in a Ubuntu 12.04 machine (newer versions are also apt, but this is the OS we use at the lab).

Some other softwares needed are Ruby 1.9.1 (*with RubyGems*) and Python 2.7.

Important libraries can be obtained/installed as follows:
1. CASPER `mlib_devel`:
Open a terminal and execute these commands
    ```bash
    $ git clone http://astro.berkeley.edu/~davidm/mlib_devel.git
    $ gem install --source http://astro.berkeley.edu/~davidm/gems adc16
    $ git clone git://github.com/david-macmahon/casper_adc16.git
    ```
Note that adc16 libs have been written by [davidm](https://github.com/david-macmahon). To perform tests with these, some extra ruby libs are needed:
  ```bash
  $ git clone http://astro.berkeley.edu/~davidm/mlib_devel.git
  $ gem install --source http://astro.berkeley.edu/~davidm/gems adc16
  $ git clone git://github.com/david-macmahon/casper_adc16.git
  ```

2. CASPER `corr` library: install it via pip
    ```bash
      $ pip install corr
    ```

3. Missing `pcores`:
As as the CASPER [toolflow settings page](https://casper.berkeley.edu/wiki/MSSGE_Setup_with_Xilinx_14.x_and_Matlab_2012b) says, there are some *tweaks to be able to compile*. The most important is to download the compressed folder that has the missing `pcores` from Xilinx. Extract the files to `mlib_devel/xps_base/XPS_ROACH2_base/pcores`.


## Hardware
A [ROACH2 rev2](https://casper.berkeley.edu/wiki/ROACH2) and an [ADC16x250-8 coax rev 2](https://casper.berkeley.edu/wiki/ADC16x250-8_coax_rev_2) (single ended SMB input).

## Test the hardware

The `utilities` folder contains the source written by davidm and a simulink model `adc16_1brd_200_rev2a.slx`, with its respective .bof file.

1. Power up the ROACH2 and connect it to the local network (same as your PC).
2. Open an iPython session to upload the .bof file to the ROACH2 with katcp. In a terminal, type:
  ```python
      $ ipython
      In [1]: import corr
      In [2]: fpga = corr.katcp_wrapper.FpgaClient('ROACH2_ip_address')
      In [3]: fpga.upload_bof('utilities/adc16_test/model/adc16_1brd_200_rev2a.bof', 60000)
  ```
  The number in the third line corresponds to the port that the file transfer will use, as the default katcp 7147 is already in use.
  To check that the .bof arrived, type
  ```python
    In [4]: fpga.listbof()
  ```
3. Open another terminal and execute the ruby init script in the `utilities/adc16_test/src/bin` folder:
  ```bash
  $ cd utilities/src/bin
  $ ruby1.9.1 ./adc16_init.rb --demux 1 ROACH2_ip_address adc16_1brd_200_rev2a.bof
  ```
  Note that the .bof file name does not contain the path, as it is the copy uploaded to the ROACH2.

4. Run the histogram scripts
```bash
  $ ruby1.9.1 ./adc16_plot_chans.rb -H ROACH2_ip_address
```