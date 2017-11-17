import corr
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.animation as animation
import numpy as np
from mbf.actions import PhaseCalibration


class Spectra(animation.TimedAnimation):
    def __init__(self, fpga, fig, mode, numc):
        self.letters = ['a', 'b', 'c', 'd']
        self.fpga = fpga
        self.mode = mode
        self.numc = numc
        self.channels = [None]*self.numc

        self.fig = fig
        self.axes = [None]*self.numc
        self.lines = [None]*self.numc
        self.t = np.linspace(0, 255, 256)  # needed as x domain
        for i in range(self.numc):
            self.axes[i] = self.fig.add_subplot(self.numc/4, 4, i+1)
            # axes[i].set_xlabel('N')
            # axes[i].set_ylabel(self.letters[i/4]+str(i%4+1))
            self.axes[i].set_title(mode+'[ a1 x '+self.letters[i/4]+str(i % 4+1)+' ]')
            # self.axes[i].set_title(self.letters[i])
            self.lines[i] = Line2D([], [], color='blue')
            self.axes[i].add_line(self.lines[i])
            self.axes[i].set_xlim(0, 128)
            self.axes[i].set_ylim(-2**2, 2**2)
            # self.axes[i].set_aspect('equal', 'datalim')

        plt.tight_layout()  # prevent text & graphs overlapping
        animation.TimedAnimation.__init__(self, fig, interval=50, blit=True)

    def _draw_frame(self, framedata):
        self.update_data()
        for i in range(self.numc):
            self.lines[i].set_data(self.t, np.array(self.channels[i]))

        self._drawn_artists = self.lines

    def new_frame_seq(self):
        return iter(range(1))

    def _init_draw(self):
        lines = self.lines
        for l in lines:
            l.set_data([], [])

    def read_bram(self):
        self.fpga.write_int('cal_new_acc', 1)
        self.fpga.write_int('cal_new_acc', 0)
        acc_n = 0 # self.fpga.read_uint('cal_acc_count')

        data_ab = [None] * self.numc
        ab_re = [None] * self.numc
        ab_im = [None] * self.numc
        for i in range(self.numc):
            data_ab[i] = np.fromstring(self.fpga.read('cal_probe' + str(i / 4) + '_xab_ab' + str(i % 4), 256 * 16, 0),
                                       dtype='>q') / 2.0 ** 17
            ab_re[i] = np.zeros(256)
            ab_im[i] = np.zeros(256)
            for j in range(len(data_ab[i]) / 2):
                ab_re[i][j] = data_ab[i][j * 2]
                ab_im[i][j] = data_ab[i][j * 2 + 1]

        data_pow = [None] * (self.numc/2)
        pow = [None] * self.numc
        for i in range(self.numc/2):
            data_pow[i] = np.fromstring(self.fpga.read('cal_probe' + str(i / 4) + '_xpow_s' + str((i % 2)+1), 256 * 16, 0),
                                       dtype='>q') / 2.0 ** 17
            pow[2*i+0] = np.zeros(256)
            pow[2*i+1] = np.zeros(256)
            for j in range(len(data_pow[i]) / 2):
                pow[2*i+0][j] = data_pow[i][j*2]
                pow[2*i+1][j] = data_pow[i][j*2+1]

        return ab_re, ab_im, pow, acc_n

    def update_data(self):
        data_re, data_im, data_pow, acc_n = np.array(self.read_bram())
        if self.mode == 'real':
            for i in range(self.numc):
                self.channels[i] = (data_re[i])
        elif self.mode == 'imag':
            for i in range(self.numc):
                self.channels[i] = (data_im[i])
        else:
            for i in range(self.numc):
                self.channels[i] = (data_pow[i])
