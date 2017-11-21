_letters = {'a': 0, 'b': 1, 'c': 2, 'd': 3, }
_numbers = {'1': 0, '2': 1, '3': 2, '4': 3, }


class Beamformer:
    def __init__(self, fpga, addr_x, addr_y):
        self.letters = ['a', 'b', 'c', 'd']
        self.fpga = fpga
        self.addr_x = addr_x
        self.addr_y = addr_y

    def steer_beam(self, theta, phi):
        v_re = [1 << 1]*16
        v_im = [1 << 1]*16

        self.fpga.write_int('bfx_addr', self.addr_x)
        self.fpga.write_int('bfy_addr', self.addr_y)

        for i in range(16):
            self.fpga.write_int('bfsub_addr', i)
            self.write_phase(v_re[i], v_im[i])

    def write_phase(self, phase_re, phase_im):

        self.fpga.write_int('bf_phase_re', phase_re)
        self.fpga.write_int('bf_phase_im', phase_im)
        self.fpga.write_int('bf_phase_we', 1)
        self.fpga.write_int('bf_phase_we', 0)
