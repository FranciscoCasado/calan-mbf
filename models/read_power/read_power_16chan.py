import corr
import matplotlib.pyplot as plt
import sixteen

fpga = corr.katcp_wrapper.FpgaClient('192.168.1.13')

# start the process
powers = sixteen.Powers(fpga, plt.figure())
channels = sixteen.LiveChannels(fpga, plt.figure())
plt.show()
