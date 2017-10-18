# Conversion Down Hardware

## Software
`RX.py` programs a all four MAX2851 down-conversion boards. The script can be modified in order to change the operation frequency. This script must be in a Raspberry Pi board.

## Hardware
A 40MHz clock signal (sinusoidal) with -3dBm power is needed as a reference for the local oscillator PLL of the chip.

Addresses on the board can be changed (not recommended) by switching the DIP-switches, where the LSB-MSB correspond to 1-8 switches, respectively.
