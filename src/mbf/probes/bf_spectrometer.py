import corr
import numpy as np


class BfSpectrometer:
    def __init__(self, fpga, numc):
        self.fpga = fpga
        self.numc = 2

    def find_channel(self):
        re, im, pow, acc_n = np.array(self.read())
        # print pow
        max_value = np.amax(pow[0])
        max_index = np.argmax(pow[0])
        return max_value, max_index

    def read(self):
        self.fpga.write_int('bf_new_acc', 1)
        self.fpga.write_int('bf_new_acc', 0)
        acc_n = 0  # self.fpga.read_uint('cal_acc_count')

        ab_re, ab_im = None, None
        pow = self._read_pow_bram()

        return ab_re, ab_im, pow, acc_n

    def _read_pow_bram(self):
        data_pow = [None] * (self.numc / 2)
        pow = [None] * self.numc
        for i in range(self.numc / 2):
            data_pow[i] = np.fromstring(
                self.fpga.read('bf_probe0_xpow_s' + str(i + 1), 256 * 16, 0),
                dtype='>q') / 2.0 ** 17
            pow[2 * i + 0] = np.zeros(256)
            pow[2 * i + 1] = np.zeros(256)
            for j in range(len(data_pow[i]) / 2):
                pow[2 * i + 0][j] = data_pow[i][j * 2]
                pow[2 * i + 1][j] = data_pow[i][j * 2 + 1]

        return pow
