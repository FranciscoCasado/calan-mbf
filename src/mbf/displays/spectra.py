import corr
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.animation as animation
import numpy as np


class Spectra(animation.TimedAnimation):
    def __init__(self, probe, fig, mode, scale):
        self.letters = ['a', 'b', 'c', 'd']
        self.probe = probe
        self.mode = mode
        self.numc = self.probe.numc
        self.scale = scale
        _sp_rows = {1: 1,
                    4: 1,
                    16: 4,
                    2: 1,
                    6: 2}
        _sp_columns = {1: 1,
                       4: 4,
                       16: 4,
                       2: 2,
                       6: 3}
        self.channels = [None]*self.numc

        self.fig = fig
        self.axes = [None]*self.numc
        self.lines = [None]*self.numc
        self.t = np.linspace(0, 255, 256)  # needed as x domain
        for i in range(self.numc):
            self.axes[i] = self.fig.add_subplot(_sp_rows[self.numc], _sp_columns[self.numc], i+1)
            # axes[i].set_xlabel('N')
            # axes[i].set_ylabel(self.letters[i/4]+str(i%4+1))
            self.axes[i].set_title(mode+'[ a1 x '+self.letters[i/4]+str(i % 4+1)+' ]')
            # self.axes[i].set_title(self.letters[i])
            self.lines[i] = Line2D([], [], color='blue')
            self.axes[i].add_line(self.lines[i])
            self.axes[i].set_xlim(0, 63)
            if self.scale == 'dB':
                self.axes[i].set_ylim(-80, 10)
            else:
                self.axes[i].set_ylim(-4, 4)
            self.axes[i].grid('on')
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

    def update_data(self):
        data_re, data_im, data_pow, acc_n = np.array(self.probe.read())
        if self.scale == 'dB':
            for i in range(self.numc):
                data_pow[i] = 10*np.log10(data_pow[i]/(2.0**17))

        if self.mode == 'real':
            for i in range(self.numc):
                self.channels[i] = data_re[i]
        elif self.mode == 'imag':
            for i in range(self.numc):
                self.channels[i] = data_im[i]
        else:
            for i in range(self.numc):
                self.channels[i] = data_pow[i]
