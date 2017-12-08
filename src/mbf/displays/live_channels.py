import corr
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.animation as animation
import numpy as np


class LiveChannels(animation.TimedAnimation):
    def __init__(self, fpga, fig):
        self.channels = [None]*16
        self.letters = ['a', 'b', 'c', 'd']
        self.fpga = fpga

        # Build figures
        self.t = np.linspace(0, 1023, 1024)  # needed as x domain
        self.fig = fig
        self.axes = [None]*16
        self.lines = [None]*16
        for i in range(16):
            self.axes[i] = self.fig.add_subplot(4, 4, i+1)
            self.axes[i].set_title(self.letters[i/4]+str(i % 4+1))
            self.lines[i] = Line2D([], [], color='blue')
            self.axes[i].add_line(self.lines[i])
            self.axes[i].set_xlim(0, 64)
            self.axes[i].set_ylim(-128, 128)

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
        raw_data = np.fromstring(self.fpga.snapshot_get('snap_adc_a', man_trig=True, man_valid=True)['data'], dtype='<i1')

        channels = []
        for i in range(16):
            channels.append([])

        # Interleave signals
        for n in range(1024):
            for i in range(16):
                channels[i].append(raw_data[n * 16 + i])

        return channels

    def update_data(self):
        data = self.read_snap()
        for i in range(16):
            self.channels[i] = np.array(data[i])
