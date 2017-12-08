import numpy as np


class PowerIntegrator:
    def __init__(self, fpga):
        self.fpga = fpga

    def read(self):
        # Self-explanatory
        self.fpga.write_int('hold_data', 1)
        self.fpga.write_int('hold_data', 0)
        rms = np.array([self.fpga.read_uint('power_adc_a1'),
                        self.fpga.read_uint('power_adc_a2'),
                        self.fpga.read_uint('power_adc_a3'),
                        self.fpga.read_uint('power_adc_a4'),
                        self.fpga.read_uint('power_adc_b1'),
                        self.fpga.read_uint('power_adc_b2'),
                        self.fpga.read_uint('power_adc_b3'),
                        self.fpga.read_uint('power_adc_b4'),
                        self.fpga.read_uint('power_adc_c1'),
                        self.fpga.read_uint('power_adc_c2'),
                        self.fpga.read_uint('power_adc_c3'),
                        self.fpga.read_uint('power_adc_c4'),
                        self.fpga.read_uint('power_adc_d1'),
                        self.fpga.read_uint('power_adc_d2'),
                        self.fpga.read_uint('power_adc_d3'),
                        self.fpga.read_uint('power_adc_d4')])/(2.0**15)
        return rms
