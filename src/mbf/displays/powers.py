import corr
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.animation as animation
import numpy as np


class Powers(animation.TimedAnimation):
    def __init__(self, probe, fig):
        self.powers = np.zeros(16)+1
        self.letters = ['a', 'b', 'c', 'd']
        self.probe = probe

        # Set figure
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
        self.axes.set_title('Received power')
        self.axes.set_xlabel('Channels')
        self.axes.set_ylabel('Power [dB]')
        self.axes.set_xlim(1, 17)
        self.axes.set_ylim(-20, 5)
        self.axes.grid('on')
        # axes.set_aspect('equal', 'datalim')

        plt.tight_layout()  # prevent text & graphs overlapping

        animation.TimedAnimation.__init__(self, fig, interval=1000, blit=True)

    def _draw_frame(self, framedata):
        self.update_data()
        for i in range(16):
            self.bars[i].set_height(self.powers[i])
        self.line_mean.set_data(self.xdom_lines, self.rms_mean_dB)
        self.line_dev_sup.set_data(self.xdom_lines, self.rms_mean_dB + self.rms_dev_dB)
        self.line_dev_inf.set_data(self.xdom_lines, self.rms_mean_dB - self.rms_dev_dB)

    def new_frame_seq(self):
        return iter(range(1))

    def _init_draw(self):
        lines = [self.line_mean, self.line_dev_sup, self.line_dev_inf]
        for l in lines:
            l.set_data([], [])

    def update_data(self):
        # Retrieve data
        self.powers = 10*np.log10(self.probe.read())

        # Calculate mean and deviation
        self.rms_mean_dB = np.zeros(17) + np.mean(self.powers)
        self.rms_dev_dB = np.zeros(17) + np.std(self.powers)
