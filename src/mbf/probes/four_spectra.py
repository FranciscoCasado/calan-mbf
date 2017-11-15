import corr
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.animation as animation
import numpy as np

from mbf.actions import PhaseCalibration


class FourSpectra(animation.TimedAnimation):
    def __init__(self, fpga, fig, mode):
        self.channels = [None]*4
        self.letters = ['a', 'b', 'c', 'd']
        self.fpga = fpga
        self.mode = mode

        self.t = np.linspace(0, 255, 256)  # needed as x domain

        self.fig = fig
        self.axes = [None]*4
        self.lines = [None]*4
        for i in range(4):
            self.axes[i] = self.fig.add_subplot(4, 1, i+1)
            # axes[i].set_xlabel('N')
            # axes[i].set_ylabel(self.letters[i/4]+str(i%4+1))
            self.axes[i].set_title(self.letters[i/4]+str(i % 4+1)+' '+mode)
            # self.axes[i].set_title(self.letters[i])
            self.lines[i] = Line2D([], [], color='blue')
            self.axes[i].add_line(self.lines[i])
            self.axes[i].set_xlim(0, 128)
            self.axes[i].set_ylim(-2**1, 2**1)
            # self.axes[i].set_aspect('equal', 'datalim')

        plt.tight_layout()  # prevent text & graphs overlapping
        #self.fpga.write_int('phase_re_0', 1 << 17)
        #self.fpga.write_int('phase_im_0', 0 << 17)

        # Calibration
        if self.mode == 'real':
            data_re, data_im, acc_n = np.array(self.read_bram())
            pcal = PhaseCalibration(fpga)
            pcal.init_phase()

            ref_re = data_re[0][13]
            ref_im = data_im[0][13]
            ref_mag = np.sqrt(ref_re**2+ref_im**2)
            print "first data"
            for i in range(4):
                cal_re = data_re[i][13]
                cal_im = data_im[i][13]
                cal_mag = np.sqrt(cal_re**2+cal_im**2)
                cal_re = -cal_re/cal_mag*ref_mag/cal_mag*2.0**17
                cal_im = -cal_im/cal_mag*ref_mag/cal_mag*2.0**17
                print 'a'+str(i+1)+':  ',
                print str(int(data_re[i][13]))+'\t'+str(int(data_im[i][13]))
                print '\t'+str(int(cal_re))+'\t'+str(int(cal_im))
                pcal.set_phase('a'+str(i+1), cal_re, cal_im)

        animation.TimedAnimation.__init__(self, fig, interval=50, blit=True)

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

    def read_bram(self):
        if self.mode == 'real':
            self.fpga.write_int('call_new_acc', 1)
            self.fpga.write_int('call_new_acc', 0)
        acc_n = self.fpga.read_uint('cal_acc_count')

        data_ab = [None]*4
        ab_re = [None]*4
        ab_im = [None]*4
        for i in range(4):
            data_ab[i] = np.fromstring(self.fpga.read('xab' + str(i/4) + '_ab' + str(i%4), 256 * 16, 0),
                                       dtype='>q')
            ab_re[i] = np.zeros(256)
            ab_im[i] = np.zeros(256)
            for j in range(len(data_ab[i]) / 2):
                ab_re[i][j] = data_ab[i][j * 2]
                ab_im[i][j] = data_ab[i][j * 2 + 1]

            # data_pow = np.fromstring(self.fpga.read('xpow' + str(0) + '_s2', 256 * 16, 0), dtype='>Q')
        # interleave
        return ab_re, ab_im, acc_n

    def update_data(self):
        data_re, data_im, acc_n = np.array(self.read_bram())
        if self.mode == 'real':
            # print("     ")
            for i in range(4):
                # print str(data_re[i][13])+'\t'+str(data_im[i][13])
                self.channels[i] = data_re[i]/2.0**17
        elif self.mode == 'imag':
            for i in range(4):
                self.channels[i] = data_im[i]/2.0**17
