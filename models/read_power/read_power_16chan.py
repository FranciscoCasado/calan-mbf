import corr
import logging
import matplotlib
import matplotlib.pyplot as plt
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


def plot_snap(axes):
    #matplotlib.pyplot.clf()
    snap_num = 2
    snap_name = ['snap_a','snap_b','snap_c','snap_d']

    time.sleep(1)   # be patient :)
    for i in range(0,4):
        data = get_snap(snap_name[i])
        #print(snap_name[i]+" ready")
        axes[i,0].plot(data[0])
        plt.axis([0, 100, -128, 128])
        axes[i,1].plot(data[1])
        axes[i,2].plot(data[2])
        axes[i,3].plot(data[3])
    # matplotlib.pylab.semilogy(interleave_a)
    #matplotlib.pylab.ylabel('Sample value ')
    # matplotlib.pylab.ylim(0)
    #matplotlib.pylab.grid()
    #matplotlib.pylab.xlabel('Sample Number')
    #matplotlib.pylab.xlim(0, 1024)
    #fig.canvas.draw()
    fig.canvas.manager.window.after(200, plot_snap(axes))

fpga = corr.katcp_wrapper.FpgaClient('192.168.1.13')


# set up the figure with a subplot to be plotted
# start the process
    
snap_name = ['snap_a','snap_b','snap_c','snap_d']
fig,axes = plt.subplots(4,4,'all')
print(axes)
print('Plot started.')
plt.ion()
plt.show()
while True:
    time.sleep(1)   # be patient :)
    for i in range(0,4):
        data = get_snap(snap_name[i])
        #print(snap_name[i]+" ready")
        axes[i,0].plot(data[0])
        axes[i,1].plot(data[1])
        axes[i,2].plot(data[2])
        axes[i,3].plot(data[3])
    print("ready")
