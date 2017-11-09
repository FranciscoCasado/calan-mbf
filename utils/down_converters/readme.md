# Down-Conversion Hardware

The ROACH2 and the adc16 borad have a bandwidth upto ~120 MHz, so the information carried by a 5.8 GHz must be down-converted. This process is performed by four circuit boards that include a MAX2851 chip, each one capable of down-converting upto 5 independent channels. As the project only need 16 signals, only four channels of each board are used.

## Hardware settings
Every down-conversion board includes an 8DIP-switch and a combinational logic that allows physical address setting. Since there are only 4 boards in use, the address have been set succesively as:
	- A: 00 000000
	- B: 01 000000
	- C: 10 000000
	- D: 11 000000
where the left bit corresponds to the number 1 labeled on the switch and the right bit (all 0) corresponds to the number 8 labeled on the switch.

Boards must be mounted in the distribution PCB, which conects every communication line from a Raspberry Pi 3 and power supply lines.

A 40MHz clock signal (sinusoidal) with -3dBm power is needed as a reference for the local oscillator PLL of the chip.

## Control Software
The file `mixer.py` provides a class that controls all four down-conversion boards. This class implements initialization of all main address registers on the chip, with their default values, and an aplitude calibration routine, wich changes the `vga_gain` of some channels.

The file `init_mixers.py` executes the initialization and calibration, using the described library
