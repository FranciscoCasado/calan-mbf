import corr
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.animation as animation
import numpy as np


class FourChannels(animation.TimedAnimation):
    def __init__(self, fpga, fig):
        self.channels = [None]*4
        self.letters = ['a', 'b', 'c', 'd']
        self.fpga = fpga

        self.t = np.linspace(0, 511, 512)  # needed as x domain

        self.fig = fig
        self.axes = [None]*4
        self.lines = [None]*4
        for i in range(4):
            self.axes[i] = self.fig.add_subplot(2, 2, i+1)
            # axes[i].set_xlabel('N')
            # axes[i].set_ylabel(self.letters[i/4]+str(i%4+1))
            self.axes[i].set_title(self.letters[i/4]+str(i % 4+1))
            self.lines[i] = Line2D([], [], color='blue')
            self.axes[i].add_line(self.lines[i])
            self.axes[i].set_xlim(0, 256)
            self.axes[i].set_ylim(0, 10)
            # self.axes[i].set_aspect('equal', 'datalim')

        plt.tight_layout()  # prevent text & graphs overlapping

        animation.TimedAnimation.__init__(self, fig, interval=100, blit=True)

    def _draw_frame(self, framedata):
        self.update_data()
        for i in range(4):
            self.lines[i].set_data(self.t, np.array(self.channels[i]))

        self._drawn_artists = self.lines

    def new_frame_seq(self):
        return iter(range(1))

    def _init_draw(self):
        lines = self.lines
        for l in lines:
            l.set_data([], [])

    def read_snap(self):
        raw_data = np.fromstring(self.fpga.snapshot_get('pfb_fft_0_snap_pfb_a', man_trig=True, man_valid=True)['data'],
                                 dtype='>i')
        channels = []
        for i in range(4):
            channels.append([])
        # interleave
        for n in range(len(raw_data)/4):
            for i in range(4):
                channels[i].append(raw_data[n * 4 + i])

        return channels

    def update_data(self):
        data = self.read_snap()
        for i in range(4):
            self.channels[i] = np.absolute(np.fft.fft(np.array(data[i])))/2.0**17
            # self.channels[i] = np.array(data[i])/2.0**17
