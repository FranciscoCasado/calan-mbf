import corr
import logging
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.animation as animation
import struct
import sys
import time
import pylab
import numpy as np
import random

class SixteenChannelsLive(animation.TimedAnimation):
    def __init__(self, fpga):
        self.channels = [None]*16
        self.letters = ['a', 'b', 'c', 'd']
        self.fpga = fpga

        self.t = np.linspace(0, 1023, 1024) #needed for fake data

        fig = plt.figure()
        axes = [None]*16
        self.lines = [None]*16
        for i in range(16):
            axes[i] = fig.add_subplot(4,4,i+1)
            # axes[i].set_xlabel('N')
            # axes[i].set_ylabel(self.letters[i/4]+str(i%4+1))
            axes[i].set_title(self.letters[i/4]+str(i%4+1))
            self.lines[i] = Line2D([], [], color='blue')
            axes[i].add_line(self.lines[i])
            axes[i].set_xlim(0, 64)
            axes[i].set_ylim(-128, 128)
            #axes[i].set_aspect('equal', 'datalim')

        plt.tight_layout()  # prevent text & graphs overlapping

        animation.TimedAnimation.__init__(self, fig, interval=50, blit=True)

    def _draw_frame(self, framedata):
        self.update_data()
        for i in range(16):
            self.lines[i].set_data(self.t, np.array(self.channels[i]))

        self._drawn_artists = self.lines

    def new_frame_seq(self):
        return iter(range(1))

    def _init_draw(self):
        lines = self.lines
        for l in lines:
            l.set_data([], [])

    def read_snap(self,snap_name):
        # raw_data = numpy.fromstring(self.fpga.snapshot_get(snap_name, man_trig=True, man_valid=True)['data'], dtype='<i1')
        # generate fake data
        fake_t = np.linspace(0, 1023, 1024*4)
        raw_data = np.sin(2 * np.pi * (fake_t + random.randint(-3, 3)) / 10.) * (100 + random.randint(-10, 10))


        sub_chan_1 = []
        sub_chan_2 = []
        sub_chan_3 = []
        sub_chan_4 = []
        # interleave
        for i in range(1024):
            sub_chan_1.append(raw_data[i * 4])
            sub_chan_2.append(raw_data[i * 4 + 1])
            sub_chan_3.append(raw_data[i * 4 + 2])
            sub_chan_4.append(raw_data[i * 4 + 3])

        return [sub_chan_1, sub_chan_2, sub_chan_3, sub_chan_4]

    def update_data(self):
        for i in range(4):
            data = self.read_snap('snap_'+self.letters[i])
            self.channels[i*4+0] = data[0]
            #print(i*4+0)
            self.channels[i*4+1] = data[1]
            #print(i*4+1)
            self.channels[i*4+2] = data[2]
            #print(i*4+2)
            self.channels[i*4+3] = data[3]
            #print(i*4+3)



#fpga = corr.katcp_wrapper.FpgaClient('192.168.1.13')
fpga = 'not_an_fpga (for now)'

# set up the figure with a subplot to be plotted
# start the process
ani = SixteenChannelsLive(fpga)
# ani.save('test_sub.mp4')
plt.show()
