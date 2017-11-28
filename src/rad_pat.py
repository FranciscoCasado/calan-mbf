import logging
import sys
import time

import corr
import matplotlib.pyplot as plt
import mbf
import numpy as np

loggers = []
lh = corr.log_handlers.DebugLogHandler()
logger = logging.getLogger('192.168.1.13')
logger.addHandler(lh)
logger.setLevel(10)

ip_addr = '192.168.1.13'
fpga = corr.katcp_wrapper.FpgaClient(ip_addr, 7147, timeout=10, logger=logger)
time.sleep(1)

if fpga.is_connected():
    print 'ok\n'
else:
    print 'ERROR connecting to server %s on port %i.\n' % (ip_addr, 7147)


bf = mbf.actions.Beamformer(fpga, 5, 10)
bf.steer_beam(0, 0)

probe = mbf.probes.BfSpectrometer(fpga)


theta = range(-90, 91, 1)
phi = [0]  # range(-90, 90, 1)

value = np.zeros([len(theta), len(phi)])

bf.steer_beam(0, 0)
val, index = probe.find_channel()
print str(val)+str(index)
time.sleep(5)


for i in range(len(theta)):
    for j in range(len(phi)):
        print '['+str(theta[i])+','+str(phi[j])+'] :  ',
        bf.steer_beam(theta[i], phi[j])
        time.sleep(0.5)
        re, im, pow, acc_n = probe.read()
        data = 10*np.log10(pow[4]/(2.0**17))
        value[i][j] = data[index]
        print str(value[i][j])

plt.plot(theta, value)
plt.show()
