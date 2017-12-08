import numpy as np

_letters = {'a': 0, 'b': 1, 'c': 2, 'd': 3, }
_numbers = {'1': 0, '2': 1, '3': 2, '4': 3, }


class Beamformer:
    def __init__(self, fpga, addr_x, addr_y):
        self.letters = ['a', 'b', 'c', 'd']
        self.fpga = fpga
        self.addr_x = addr_x
        self.addr_y = addr_y

    def steer_beam(self, theta, phi):

        self.fpga.write_int('bf_addr_x', self.addr_x)
        self.fpga.write_int('bf_addr_y', self.addr_y)

        v_re, v_im = self.calculate_vector(theta, phi)
        # print 'steering to:\t theta: '+str(theta)+' - phi: '+str(phi)
        for i in range(4):
            for j in range(4):
                self.fpga.write_int('bf_addr_sub', i*4+j)
                self.write_phase(v_re[i][j], v_im[i][j])

    def calculate_vector(self, theta, phi):
        # Constants
        freq = 5.81e9           # 5.81 GHz
        c = 3e8                 # speed of light (u can't beat it)
        wavelength = c / freq   # 51.72 mm
        d = wavelength / 2      # separation between array elements

        # Array element positions
        p = np.zeros([4, 4, 3])
        for i in range(4):
            for j in range(4):
                p[i][j] = np.array([d * (i - 1.5), 0, d * (j - 1.5)])

        # Direction of Arrival calculations
        theta = np.pi / 180 * (90 - theta)
        phi = np.pi / 180 * (90 - phi)
        a = np.array([-np.sin(theta) * np.cos(phi), -np.sin(theta) * np.sin(phi), -np.cos(theta)])  # DoA
        k = 2 * np.pi / wavelength * a  # wave-number vector

        # Calculate array manifold vector
        v_re = np.zeros([4, 4])
        v_im = np.zeros([4, 4])
        for i in range(4):
            for j in range(4):
                v = np.exp(-1j * np.dot(k, p[i][j]))
                v_re[i][j] = int(np.real(v) * ((1 << 17)-1))
                v_im[i][j] = int(-np.imag(v) * ((1 << 17)-1))

        return v_re, v_im

    def write_phase(self, phase_re, phase_im):

        self.fpga.write_int('bf_phase_re', phase_re)
        self.fpga.write_int('bf_phase_im', phase_im)
        self.fpga.write_int('bf_phase_we', 1)
        self.fpga.write_int('bf_phase_we', 0)
