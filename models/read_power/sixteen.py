import corr
import logging
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

        self.t = np.linspace(0, 1023, 1024)  # needed as x domain

        self.fig = fig
        self.axes = [None]*16
        self.lines = [None]*16
        for i in range(16):
            self.axes[i] = self.fig.add_subplot(4, 4, i+1)
            # axes[i].set_xlabel('N')
            # axes[i].set_ylabel(self.letters[i/4]+str(i%4+1))
            self.axes[i].set_title(self.letters[i/4]+str(i % 4+1))
            self.lines[i] = Line2D([], [], color='blue')
            self.axes[i].add_line(self.lines[i])
            self.axes[i].set_xlim(0, 64)
            self.axes[i].set_ylim(-128, 128)
            # axes[i].set_aspect('equal', 'datalim')

        plt.tight_layout()  # prevent text & graphs overlapping

        animation.TimedAnimation.__init__(self, fig, interval=1000, blit=True)

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

    def read_snap(self):
        raw_data = np.fromstring(self.fpga.snapshot_get('snap128_a', man_trig=True, man_valid=True)['data'], dtype='<i1')
        # Generate fake data
        # fake_t = np.linspace(0, 1023, 1024*4)
        # raw_data = np.sin(2 * np.pi * (fake_t + random.randint(-3, 3)) / 10.) * (100 + random.randint(-10, 10))

        channels = []
        for i in range(16):
            channels.append([])
        # interleave
        for n in range(1024):
            for i in range(16):
                channels[i].append(raw_data[n * 16 + i])

        return channels

    def update_data(self):
        data = self.read_snap()
        for i in range(16):
            self.channels[i] = np.array(data[i])


class Powers(animation.TimedAnimation):
    def __init__(self, fpga, fig):
        self.powers = np.zeros(16)+1
        self.letters = ['a', 'b', 'c', 'd']
        self.fpga = fpga

        self.xdom_bars = np.linspace(1, 16, 16)  # needed as x domain
        self.xdom_lines = np.linspace(1, 17, 17)
        self.rms_mean_dB = np.zeros(17)
        self.rms_dev_dB = np.zeros(17)

        self.fig = fig
        self.axes = fig.add_subplot(1, 1, 1)
        self.bars = self.axes.bar(self.xdom_bars, self.powers)
        self.line_mean = Line2D([], [], color='black')
        self.axes.add_line(self.line_mean)
        self.line_dev_sup = Line2D([], [], color='black', linestyle='dashed')
        self.axes.add_line(self.line_dev_sup)
        self.line_dev_inf = Line2D([], [], color='black', linestyle='dashed')
        self.axes.add_line(self.line_dev_inf)
        self.axes.set_title('Powers')
        self.axes.set_xlim(1, 17)
        self.axes.set_ylim(-20, 5)
        self.axes.grid('on')
        # axes.set_aspect('equal', 'datalim')

        plt.tight_layout()  # prevent text & graphs overlapping

        animation.TimedAnimation.__init__(self, fig, interval=20, blit=True)

    def _draw_frame(self, framedata):
        self.update_data()
        for i in range(16):
            self.bars[i].set_height(self.powers[i])
        self.line_mean.set_data(self.xdom_lines, self.rms_mean_dB)
        self.line_dev_sup.set_data(self.xdom_lines, self.rms_mean_dB + self.rms_dev_dB)
        self.line_dev_inf.set_data(self.xdom_lines, self.rms_mean_dB - self.rms_dev_dB)
        # self._drawn_artists = [self.line_mean, self.line_dev_sup, self.line_dev_inf]

    def new_frame_seq(self):
        return iter(range(1))

    def _init_draw(self):
        lines = [self.line_mean, self.line_dev_sup, self.line_dev_inf]
        for l in lines:
            l.set_data([], [])

    def read_regs(self):
        self.fpga.write_int('hold_data', 1)
        self.fpga.write_int('hold_data', 0)
        rms = np.array([self.fpga.read_uint('reg_a1'),
                        self.fpga.read_uint('reg_a2'),
                        self.fpga.read_uint('reg_a3'),
                        self.fpga.read_uint('reg_a4'),
                        self.fpga.read_uint('reg_b1'),
                        self.fpga.read_uint('reg_b2'),
                        self.fpga.read_uint('reg_b3'),
                        self.fpga.read_uint('reg_b4'),
                        self.fpga.read_uint('reg_c1'),
                        self.fpga.read_uint('reg_c2'),
                        self.fpga.read_uint('reg_c3'),
                        self.fpga.read_uint('reg_c4'),
                        self.fpga.read_uint('reg_d1'),
                        self.fpga.read_uint('reg_d2'),
                        self.fpga.read_uint('reg_d3'),
                        self.fpga.read_uint('reg_d4')])/(2.0**15)
        return rms

    def update_data(self):
        self.powers = np.log10(self.read_regs())*10
        self.rms_mean_dB = np.zeros(17) + np.mean(self.powers)
        self.rms_dev_dB = np.zeros(17) + np.std(self.powers)
