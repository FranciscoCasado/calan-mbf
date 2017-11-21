import corr
import numpy as np


class CalSpectrometer:
    def __init__(self, fpga):
        self.fpga = fpga
        self.numc = 16

    def read(self):
        self.fpga.write_int('cal_new_acc', 1)
        self.fpga.write_int('cal_new_acc', 0)
        acc_n = 0  # self.fpga.read_uint('cal_acc_count')

        ab_re, ab_im = self._read_ab_bram()
        pow = self._read_pow_bram()

        return ab_re, ab_im, pow, acc_n

    def _read_ab_bram(self):
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
        return ab_re, ab_im

    def _read_pow_bram(self):
        data_pow = [None] * (self.numc / 2)
        pow = [None] * self.numc
        for i in range(self.numc / 2):
            data_pow[i] = np.fromstring(
                self.fpga.read('cal_probe' + str(i / 2) + '_xpow_s' + str((i % 2) + 1), 256 * 16, 0),
                dtype='>q') / 2.0 ** 17
            pow[2 * i + 0] = np.zeros(256)
            pow[2 * i + 1] = np.zeros(256)
            for j in range(len(data_pow[i]) / 2):
                pow[2 * i + 0][j] = data_pow[i][j * 2]
                pow[2 * i + 1][j] = data_pow[i][j * 2 + 1]

        return pow
