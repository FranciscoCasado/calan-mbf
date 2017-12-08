import corr
import numpy as np


_letters = {'a': 0, 'b': 1, 'c': 2, 'd': 3, }
_numbers = {'1': 0, '2': 1, '3': 2, '4': 3, }


class PhaseCalibration:
    def __init__(self, fpga):
        self.letters = ['a', 'b', 'c', 'd']
        self.fpga = fpga

    def set_phase(self, addr, phase_re, phase_im):
        try:
            letter = _letters[addr[0]]
            num = _numbers[addr[1]]
        except KeyError:
            print("invalid channel")
            return

        self.fpga.write_int('cal_phase_addr', letter*4+num)
        self.fpga.write_int('cal_phase_re', phase_re)
        self.fpga.write_int('cal_phase_im', phase_im)
        self.fpga.write_int('cal_phase_we', 1)
        self.fpga.write_int('cal_phase_we', 0)

    def init_phase(self):
        self.set_phase('a1', (1 << 16), (1 << 16))
        self.set_phase('a2', (1 << 16), (1 << 16))
        self.set_phase('a3', (1 << 16), (1 << 16))
        self.set_phase('a4', (1 << 16), (1 << 16))
        self.set_phase('b1', (1 << 16), (1 << 16))
        self.set_phase('b2', (1 << 16), (1 << 16))
        self.set_phase('b3', (1 << 16), (1 << 16))
        self.set_phase('b4', (1 << 16), (1 << 16))
        self.set_phase('c1', (1 << 16), (1 << 16))
        self.set_phase('c2', (1 << 16), (1 << 16))
        self.set_phase('c3', (1 << 16), (1 << 16))
        self.set_phase('c4', (1 << 16), (1 << 16))
        self.set_phase('d1', (1 << 16), (1 << 16))
        self.set_phase('d2', (1 << 16), (1 << 16))
        self.set_phase('d3', (1 << 16), (1 << 16))
        self.set_phase('d4', (1 << 16), (1 << 16))

    def calibrate(self):
        # Retrieve spectrometer data
        data_re, data_im, data_pow, acc_n = np.array(self._read_bram())

        # Retrieve data from signal a1
        ref_re = np.sum(data_re[0][12:15])
        ref_im = np.sum(data_im[0][12:15])
        ref_mag = np.sqrt(ref_re**2 + ref_im**2)
        # Obs: average channels 12:15 is the lazy solution for not-cheking that the source is set to 5.81 GHz

        for i in range(16):
            # Retrieve data from signal i (a2,...,d4)
            pre_re = np.sum(data_re[i][12:15])
            pre_im = np.sum(data_im[i][12:15])
            pre_mag = np.sqrt(pre_re**2 + pre_im**2)

            # Normalize calibration values to match signal a1 amplitude
            cal_re = pre_re/pre_mag*ref_mag/pre_mag*(1 << 16)
            cal_im = pre_im/pre_mag*ref_mag/pre_mag*(1 << 16)

            print self.letters[i/4] + str((i % 4)+1) + ':  ',
            print str(int(data_re[i][13]))+'\t'+str(int(data_im[i][13]))
            print '\t \t'+str(int(cal_re))+'\t'+str(int(cal_im))

            # Set phase
            self.set_phase(self.letters[i/4]+str((i % 4)+1), int(cal_re), int(cal_im))

    def _read_bram(self):
        self.fpga.write_int('cal_new_acc', 1)
        self.fpga.write_int('cal_new_acc', 0)
        acc_n = self.fpga.read_uint('acc_control_acc_count')

        data_ab = [None] * 16
        ab_re = [None] * 16
        ab_im = [None] * 16

        # Interleaving multiplication
        for i in range(16):
            data_ab[i] = np.fromstring(self.fpga.read('cal_probe' + str(i / 4) + '_xab_ab' + str(i % 4), 256 * 16, 0),
                                       dtype='>q')
            ab_re[i] = np.zeros(256)
            ab_im[i] = np.zeros(256)
            for j in range(len(data_ab[i]) / 2):
                ab_re[i][j] = data_ab[i][j * 2]
                ab_im[i][j] = data_ab[i][j * 2 + 1]

        data_pow = [None] * 16
        pow = [None] * 16

        # Interleaving powers
        for i in range(16/2):
            data_pow[i] = np.fromstring(self.fpga.read('cal_probe' + str(i / 4) + '_xpow_s' + str((i % 2)+1), 256 * 16, 0),
                                       dtype='>q')
            pow[2*i+0] = np.zeros(256)
            pow[2*i+1] = np.zeros(256)
            for j in range(len(data_pow[i]) / 2):
                pow[2*i+0][j] = data_pow[i][j*2]
                pow[2*i+1][j] = data_pow[i][j*2+1]

        return ab_re, ab_im, pow, acc_n

