import logging
import sys
import time

import corr
import matplotlib.pyplot as plt
import mbf

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

bitstream = 'read_power_16chan_2017_Oct_30_1556.bof'
katcp_port = 7147

def exit_fail():
    print 'FAILURE DETECTED. Log entries:\n', lh.printMessages()
    try:
        fpga.stop()
    except:
        pass
    raise
    exit()


def exit_clean():
    try:
        fpga.stop()
    except:
        pass
    exit()

# Main
if __name__ == '__main__':
    from optparse import OptionParser

    p = OptionParser()
    p.set_usage('read_power_16chan.py [options]')
    p.set_description(__doc__)
    p.add_option("-i", '--roach_ip', dest='roach', type='str', default='192.168.1.13')
    # p.add_option('-l', '--acc_len', dest='acc_len', type='int', default=2 * (2 ** 28) / 2048,
    #              help='Set the number of vectors to accumulate between dumps. default is 2*(2^28)/2048, or just under 2 seconds.')
    # p.add_option('-g', '--gain', dest='gain', type='int', default=2**17,
    #              help='Set the digital gain (6bit quantisation scalar). Default is 2*17 (least number for not loosing less-significant bits)')
    p.add_option('-s', '--skip', dest='skip', action='store_false', default=True,
                 help='Skip reprogramming the FPGA and configuring EQ.')
    p.add_option('-b', '--bof', dest='boffile', type='str', default=bitstream,
                 help='Specify the bof file to load')
    p.add_option('-p', '--power_bars', dest='power_bars', action='store_true', default=False,
                 help='Skip reprogramming the FPGA and configuring EQ.')
    p.add_option('-c', '--channels', dest='channels', action='store_true', default=False,
                 help='Skip reprogramming the FPGA and configuring EQ.')
    opts, args = p.parse_args(sys.argv[1:])


try:
    loggers = []
    lh = corr.log_handlers.DebugLogHandler()
    logger = logging.getLogger(opts.roach)
    logger.addHandler(lh)
    logger.setLevel(10)

    print('Connecting to server %s on port %i... ' % (opts.roach, katcp_port)),
    fpga = corr.katcp_wrapper.FpgaClient(opts.roach, katcp_port, timeout=10, logger=logger)
    time.sleep(1)

    if fpga.is_connected():
        print 'ok\n'
    else:
        print 'ERROR connecting to server %s on port %i.\n' % (opts.roach, katcp_port)
        exit_fail()

    print '------------------------'
    print 'Programming FPGA with %s...' % bitstream,
    if not opts.skip:
        fpga.progdev(bitstream)
        print 'done'
    else:
        print 'Skipped.'

    print 'Configuring Quantizers...',
    fpga.write_int('cal_gain', 2**17)
    fpga.write_int('cal_acc_len', 2**12)
    fpga.write_int('bf_gain', 2**17)
    fpga.write_int('bf_acc_len', 2**12)
    print 'done'

    print 'Resetting counters...',
    fpga.write_int('cal_cnt_rst', 1)
    fpga.write_int('cal_cnt_rst', 0)
    fpga.write_int('bf_cnt_rst', 1)
    fpga.write_int('bf_cnt_rst', 0)
    print 'done'

    print 'Setting Initial Phase Calibration...'
    pcal = mbf.actions.PhaseCalibration(fpga)
    pcal.init_phase()
    pcal.calibrate()
    print 'done'

    print 'Setting Beamformer...',
    bf0 = mbf.actions.Beamformer(fpga, 5, 10)
    bf0.steer_beam(0, 0)
    bf1 = mbf.actions.Beamformer(fpga, 6, 11)
    bf1.steer_beam(0, 0)
    print 'done'

    if opts.power_bars & (not opts.channels):
        powers = mbf.displays.Powers(fpga, plt.figure())
    elif (not opts.power_bars) & opts.channels:
        channels = (fpga, plt.figure())
    else:
        # powers = mbf.displays.Powers(mbf.probes.PowerIntegrator(fpga), plt.figure())
        # channels = mbf.displays.LiveChannels(fpga, plt.figure())
        # spectra_real = mbf.displays.Spectra(fpga, plt.figure(), mode='real', numc=4)
        # spectra_imag = mbf.displays.Spectra(fpga, plt.figure(), mode='imag', numc=4)
        spectra_pow = mbf.displays.Spectra(mbf.probes.CalSpectrometer(fpga, numc=4), plt.figure(), mode='pow', scale='dB')
        bf_spectra = mbf.displays.Spectra(mbf.probes.BfSpectrometer(fpga, numc=2), plt.figure(), mode='pow', scale='dB')

    plt.show()


except KeyboardInterrupt:
    exit_clean()

exit_clean()
