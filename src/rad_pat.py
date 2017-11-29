import corr
import logging
import sys
import time
import matplotlib.pyplot as plt
import mbf
import numpy as np
import telegram
from time import strftime, localtime

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

'''
if fpga.is_connected():
    print 'ok\n'
else:
    print 'ERROR connecting to server %s on port %i.\n' % (ip_addr, 7147)
'''

print 'Starting measure'
datetime = strftime("%Y-%m-%d %H:%M:%S", localtime())
bot.send_message(chat_id=chat_id, text='Running new measurement...'+datetime)


bf = mbf.actions.Beamformer(fpga, 6, 11)
bf.steer_beam(0, 0)

probe = mbf.probes.BfSpectrometer(fpga, 2)

# Define range
theta = range(-60, 61, 3)
phi = range(-60, 61, 3)

value = np.zeros([len(theta), len(phi)])

bf.steer_beam(0, 0)
# val, index = probe.find_channel()
time.sleep(10)


for i in range(len(theta)):
    print '['+str(theta[i])+']'
    for j in range(len(phi)):
        # Steer beam
        bf.steer_beam(theta[i], phi[j])
        time.sleep(0.001)

        # Read spectrometer & process data
        re, im, pow, acc_n = probe.read()
        time.sleep(0.001)
        data = (pow[1]/(2.0**17))

        # dummy data # pow = np.array([[0.5]*256, [0.4]*256])
        # dummy data # data = np.exp(-((i-len(theta)/2.0)/(len(theta)))**2 - ((j-len(phi)/2.0)/(len(theta)))**2)

        data_dB = 10*np.log10(data)
        value[j][len(theta)-i-1] = data[12]


# Save results and notify
np.savez('pattern_'+datetime+'.npz', theta, phi, value)
bot.send_message(chat_id=chat_id, text='Done!... sending files')

try:
    # Plot results
    X, Y = np.meshgrid(phi, theta)
    levels = np.linspace(np.amin(value), np.amax(value), 1000)
    cmap = plt.cm.get_cmap("jet")

    plt.figure(figsize=(5, 4))
    cp = plt.imshow(value, extent=[-90, 90, -90, 90])
    plt.xlabel(r'$\phi$ [$^\circ$]', fontsize=16)
    plt.ylabel(r'$\theta$ [$^\circ$]', fontsize=16)
    plt.tight_layout()

    cbar = plt.colorbar(cp, ticks=[levels[0], levels[-1]])
    cbar.ax.set_yticklabels(["{0:.2f}".format(levels[0]), "{0:.2f}".format(levels[-1])])

    # Save figures
    plt.savefig('pattern_'+datetime+'.png')
    plt.savefig('pattern_'+datetime+'.pdf')

    # Send files
    img = open('pattern_'+datetime+'.png', 'rb')
    doc = open('pattern_'+datetime+'.pdf', 'rb')
    bot.send_photo(chat_id=chat_id, photo=img)
    bot.send_document(chat_id=chat_id, document=doc)

    # Display
    plt.show()

except FutureWarning:
    pass
