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

        self.fpga.write_int('phase_cal_addr', letter*4+num)
        self.fpga.write_int('phase_cal_re', phase_re)
        self.fpga.write_int('phase_cal_im', phase_im)
        self.fpga.write_int('phase_cal_we', 1)
        self.fpga.write_int('phase_cal_we', 0)

    def init_phase(self):
        self.set_phase('a1', (1 << 17)-1, 0)
        self.set_phase('a2', (1 << 17)-1, 0)
        self.set_phase('a3', (1 << 17)-1, 0)
        self.set_phase('a4', (1 << 17)-1, 0)
        self.set_phase('b1', (1 << 17)-1, 0)
        self.set_phase('b2', (1 << 17)-1, 0)
        self.set_phase('b3', (1 << 17)-1, 0)
        self.set_phase('b4', (1 << 17)-1, 0)
        self.set_phase('c1', (1 << 17)-1, 0)
        self.set_phase('c2', (1 << 17)-1, 0)
        self.set_phase('c3', (1 << 17)-1, 0)
        self.set_phase('c4', (1 << 17)-1, 0)
        self.set_phase('d1', (1 << 17)-1, 0)
        self.set_phase('d2', (1 << 17)-1, 0)
        self.set_phase('d3', (1 << 17)-1, 0)
        self.set_phase('d4', (1 << 17)-1, 0)

    def calibrate(self):
        data_re, data_im, acc_n = np.array(self.read_bram())
        pcal = PhaseCalibration(self.fpga)
        print "first data"
        for i in range(16):
            ref_re = data_re[i/4][13]
            ref_im = data_im[i/4][13]
            ref_mag = np.sqrt(ref_re**2+ref_im**2)
            cal_re = data_re[i][13]
            cal_im = data_im[i][13]
            cal_mag = np.sqrt(cal_re**2+cal_im**2)
            cal_re = cal_re/cal_mag*ref_mag/cal_mag*((2.0**17)-1)
            cal_im = cal_im/cal_mag*ref_mag/cal_mag*((2.0**17)-1)
            print 'a'+str(i+1)+':  ',
            print str(int(data_re[i][13]))+'\t'+str(int(data_im[i][13]))
            print '\t'+str(int(cal_re))+'\t'+str(int(cal_im))
            pcal.set_phase(self.letters[i/4]+str((i % 4)+1), int(cal_re), int(cal_im))

    def read_bram(self):
        self.fpga.write_int('call_new_acc', 1)
        self.fpga.write_int('call_new_acc', 0)
        acc_n = self.fpga.read_uint('cal_acc_count')

        data_ab = [None] * 16
        ab_re = [None] * 16
        ab_im = [None] * 16
        for i in range(16):
            data_ab[i] = np.fromstring(self.fpga.read('xab' + str(i / 4) + '_ab' + str(i % 4), 256 * 16, 0),
                                       dtype='>q') / 2.0 ** 17
            ab_re[i] = np.zeros(256)
            ab_im[i] = np.zeros(256)
            for j in range(len(data_ab[i]) / 2):
                ab_re[i][j] = data_ab[i][j * 2]
                ab_im[i][j] = data_ab[i][j * 2 + 1]

        return ab_re, ab_im, acc_n


