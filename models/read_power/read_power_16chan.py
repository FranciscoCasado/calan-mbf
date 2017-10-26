import corr
import logging
import matplotlib
import struct
import sys
import time
import pylab
import numpy


def get_snap(snap_name):
    raw_data = numpy.fromstring(fpga.snapshot_get(snap_name, man_trig=True, man_valid=True)['data'], dtype='<i1')
    chan_1 = []
    chan_2 = []
    chan_3 = []
    chan_4 = []
    # interleave
    for i in xrange(0,65536):
        chan_1.append(raw_data[i*4])
        chan_2.append(raw_data[i*4+1])
        chan_3.append(raw_data[i*4+2])
        chan_4.append(raw_data[i*4+3])
    return [chan_1, chan_2, chan_3, chan_4]


def plot_snap():
    matplotlib.pyplot.clf()
    snap_num = 2
    snap_name = ['snap_a','snap_b','snap_c','snap_d']

    for i in range(0,4):
        data = get_snap(snap_name[i])
        matplotlib.pylab.plot(data[0])
        matplotlib.pylab.plot(data[1])
        matplotlib.pylab.plot(data[2])
        matplotlib.pylab.plot(data[3])
    # matplotlib.pylab.semilogy(interleave_a)
    matplotlib.pylab.ylabel('Sample value ')
    # matplotlib.pylab.ylim(0)
    matplotlib.pylab.grid()
    matplotlib.pylab.xlabel('Sample Number')
    matplotlib.pylab.xlim(0, 1024)
    fig.canvas.draw()
    # fig.canvas.manager.window.after(500, plot_snap)

fpga = corr.katcp_wrapper.FpgaClient('192.168.1.13')


# set up the figure with a subplot to be plotted
fig = matplotlib.pyplot.figure()
ax = fig.add_subplot(1, 1, 1)

# start the process
fig.canvas.manager.window.after(100, plot_snap)
print 'Plot started.'
matplotlib.pyplot.show()
