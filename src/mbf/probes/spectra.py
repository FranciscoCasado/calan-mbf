import corr
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.animation as animation
import numpy as np


class Spectra(animation.TimedAnimation):
    def __init__(self, fpga, fig, mode):
        self.channels = [None]*16
        self.letters = ['a', 'b', 'c', 'd']
        self.fpga = fpga
        self.mode = mode

        self.t = np.linspace(0, 255, 256)  # needed as x domain

        self.fig = fig
        self.axes = [None]*16
        self.lines = [None]*16
        for i in range(16):
            self.axes[i] = self.fig.add_subplot(4, 4, i+1)
            # axes[i].set_xlabel('N')
            # axes[i].set_ylabel(self.letters[i/4]+str(i%4+1))
            self.axes[i].set_title(self.letters[i/4]+str(i % 4+1))
            # self.axes[i].set_title(self.letters[i])
            self.lines[i] = Line2D([], [], color='blue')
            self.axes[i].add_line(self.lines[i])
            self.axes[i].set_xlim(0, 128)
            self.axes[i].set_ylim(-2**1, 2**1)
            # self.axes[i].set_aspect('equal', 'datalim')

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

    def read_bram(self):
        self.fpga.write_int('call_new_acc', 1)
        self.fpga.write_int('call_new_acc', 0)
        acc_n = self.fpga.read_uint('cal_acc_count')

        data_ab = [None]*16
        ab_re = [None]*16
        ab_im = [None]*16
        for i in range(16):
            data_ab[i] = np.fromstring(self.fpga.read('xab' + str(i/4) + '_ab' + str(i%4), 256 * 16, 0),
                                       dtype='>q')/2.0**17
            ab_re[i] = np.zeros(256)
            ab_im[i] = np.zeros(256)
            for j in range(len(data_ab[i]) / 2):
                ab_re[i][j] = data_ab[i][j * 2]
                ab_im[i][j] = data_ab[i][j * 2 + 1]

            # data_pow = np.fromstring(self.fpga.read('xpow' + str(0) + '_s2', 256 * 16, 0), dtype='>Q')
        # interleave
        return ab_re, ab_im

    def update_data(self):
        data_re, data_im = np.array(self.read_bram())
        if self.mode == 'real':
            for i in range(16):
                self.channels[i] = data_re[i]
        elif self.mode == 'imag':
            for i in range(16):
                self.channels[i] = data_im[i]
