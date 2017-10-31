import corr
import logging
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.animation as animation
import struct
import sys
import pylab
import numpy as np
import random

class LiveChannels(animation.TimedAnimation):
    def __init__(self, fpga, fig):
        self.channels = [None]*16
        self.letters = ['a', 'b', 'c', 'd']
        self.fpga = fpga

        self.t = np.linspace(0, 1023, 1024) #needed as x domain

        self.fig = fig
        self.axes = [None]*16
        self.lines = [None]*16
        for i in range(16):
            self.axes[i] = self.fig.add_subplot(4, 4, i+1)
            # axes[i].set_xlabel('N')
            # axes[i].set_ylabel(self.letters[i/4]+str(i%4+1))
            self.axes[i].set_title(self.letters[i/4]+str(i%4+1))
            self.lines[i] = Line2D([], [], color='blue')
            self.axes[i].add_line(self.lines[i])
            self.axes[i].set_xlim(0, 64)
            self.axes[i].set_ylim(-128, 128)
            #axes[i].set_aspect('equal', 'datalim')

        plt.tight_layout()  # prevent text & graphs overlapping

        animation.TimedAnimation.__init__(self, fig, interval=10, blit=True)

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

    def read_snap(self, snap_name):
        raw_data = np.fromstring(self.fpga.snapshot_get(snap_name, man_trig=True, man_valid=True)['data'], dtype='<i1')
        # generate fake data
        #fake_t = np.linspace(0, 1023, 1024*4)
        #raw_data = np.sin(2 * np.pi * (fake_t + random.randint(-3, 3)) / 10.) * (100 + random.randint(-10, 10))


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

class Powers(animation.TimedAnimation):
    def __init__(self, fpga, fig):
        self.powers = np.zeros(16)+1
        self.letters = ['a', 'b', 'c', 'd']
        self.fpga = fpga

        self.t = np.linspace(1, 16, 16) # needed as x domain

        self.fig = fig
        self.axes = fig.add_subplot(1, 1, 1)
        self.axes.set_title('Powers')
        self.axes.set_xlim(1, 16)
        self.axes.set_ylim(-20, 5)
        self.axes.grid('on')
        # axes.set_aspect('equal', 'datalim')

        plt.tight_layout()  # prevent text & graphs overlapping

        animation.TimedAnimation.__init__(self, fig, interval=20, blit=True)

    def _draw_frame(self, framedata):
        self.update_data()
        # self.line.set_data(self.t, np.array(self.powers))
        self.axes.clear()
        self.axes.set_ylim(-20, 5)
        self.axes.grid('on')
        self.axes.bar(self.t, self.powers)
        # self._drawn_artists = [self.line]

    def new_frame_seq(self):
        return iter(range(1))

    def _init_draw(self):
        self.axes.bar(self.t, self.powers)

    def read_regs(self):
        self.fpga.write_int('hold_data', 1)
        self.fpga.write_int('hold_data', 0)
        rms_a1 = self.fpga.read_uint('reg_a1')/2.0**15
        rms_a2 = self.fpga.read_uint('reg_a2')/2.0**15
        rms_a3 = self.fpga.read_uint('reg_a3')/2.0**15
        rms_a4 = self.fpga.read_uint('reg_a4')/2.0**15
        rms_b1 = self.fpga.read_uint('reg_b1')/2.0**15
        rms_b2 = self.fpga.read_uint('reg_b2')/2.0**15
        rms_b3 = self.fpga.read_uint('reg_b3')/2.0**15
        rms_b4 = self.fpga.read_uint('reg_b4')/2.0**15
        rms_c1 = self.fpga.read_uint('reg_c1')/2.0**15
        rms_c2 = self.fpga.read_uint('reg_c2')/2.0**15
        rms_c3 = self.fpga.read_uint('reg_c3')/2.0**15
        rms_c4 = self.fpga.read_uint('reg_c4')/2.0**15
        rms_d1 = self.fpga.read_uint('reg_d1')/2.0**15
        rms_d2 = self.fpga.read_uint('reg_d2')/2.0**15
        rms_d3 = self.fpga.read_uint('reg_d3')/2.0**15
        rms_d4 = self.fpga.read_uint('reg_d4')/2.0**15

        return [rms_a1, rms_a2, rms_a3, rms_a4,
               rms_b1, rms_b2, rms_b3, rms_b4,
               rms_c1, rms_c2, rms_c3, rms_c4,
               rms_d1, rms_d2, rms_d3, rms_d4]

    def update_data(self):
        #print("******")
        self.powers = np.log10(np.array(self.read_regs()))*10
        #print(self.powers)
