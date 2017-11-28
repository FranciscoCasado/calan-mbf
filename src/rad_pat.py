import logging
import sys
import time

import corr
import matplotlib.pyplot as plt
import mbf
import numpy as np

import telegram
from time import gmtime, strftime




loggers = []
lh = corr.log_handlers.DebugLogHandler()
logger = logging.getLogger('192.168.1.13')
logger.addHandler(lh)
logger.setLevel(10)

bot = telegram.Bot('468799235:AAFTHYgMC1JqlSaYW1ZgpgZHMTyZ58Cc2H4')
chat_id = 179065133

ip_addr = '192.168.1.13'
fpga = corr.katcp_wrapper.FpgaClient(ip_addr, 7147, timeout=10, logger=logger)
time.sleep(1)

if fpga.is_connected():
    print 'ok\n'
else:
    print 'ERROR connecting to server %s on port %i.\n' % (ip_addr, 7147)


print 'Starting measure',
print strftime("%Y-%m-%d %H:%M:%S", gmtime())

bot.send_message(chat_id=chat_id, text='Beamformers...')
bf = mbf.actions.Beamformer(fpga, 6, 11)
bf.steer_beam(0, 0)

probe = mbf.probes.BfSpectrometer(fpga, 2)


theta = range(-50, 51, 5)
phi = range(-50, 51, 5)

value = np.zeros([len(theta), len(phi)])

bf.steer_beam(0, 0)
val, index = probe.find_channel()
print str(val)+str(index)
time.sleep(1)


for i in range(len(theta)):
    print '['+str(theta[i])+']'
    for j in range(len(phi)):
        bf.steer_beam(theta[i], phi[j])
        # time.sleep(0.001)
        re, im, pow, acc_n = probe.read()
        data = (pow[1]/(2.0**17))
        data_dB = 10*np.log10(data)
        value[i][j] = data[index]
        # print str(value[i][j])

# plt.plot(theta, value)
# plt.title('phi='+str(phi[0]))
# plt.xlabel('theta [deg]')
# plt.ylabel('Power [dB]')
plt.imshow(value)
plt.xlabel('theta')
plt.ylabel('phi')
bot.send_message(chat_id=chat_id, text='Measure ready')
plt.show()
