# -*- coding: utf-8 -*-
"""
Created on Tue Aug 23 16:09:00 2022

@author: berksma1
"""

import numpy as np
import adi
import matplotlib.pyplot as plt
import pulse_train_io_module as pulse_io

## INPUTS: bit rate, broadcast frequency, pulse train to transmit, which SDR,
##         which figures to plot, whether fidelity check desired
sample_rate = 1e6 # Hz
center_freq = 915e6 # Hz

tx_data = np.load('test_vec.npy')
tx_length = 5000

sdr_ip = "ip:192.168.2.2"

plot_rx_pulse_train = True
plot_rx_samples = True
plot_fft = True
check_fid = True

## CODE:

tx_pulse_train = tx_data[:tx_length] #change this line to input/truncate pulse train
num_periods = 1
bits_per_period = 4
num_samps = len(tx_pulse_train)*num_periods*bits_per_period # number of samples per call to rx()

sdr = adi.Pluto(sdr_ip)
sdr.sample_rate = int(sample_rate)

# Config Tx
sdr.tx_rf_bandwidth = int(sample_rate) # filter cutoff, just set it to the same as sample rate
sdr.tx_lo = int(center_freq)
sdr.tx_hardwaregain_chan0 = -50 # Increase to increase tx power, valid range is -90 to 0 dB

# Config Rx
sdr.rx_lo = int(center_freq)
sdr.rx_rf_bandwidth = int(sample_rate)
sdr.rx_buffer_size = num_samps
sdr.gain_control_mode_chan0 = 'manual'
sdr.rx_hardwaregain_chan0 = 70.0 # dB, increase to increase the receive gain, but be careful not to saturate the ADC

# Create transmit waveform (defined by function in pulse train module)
samples = pulse_io.pulse_train_to_tx(tx_pulse_train,num_periods,bits_per_period)
samples *= 2**14 # The PlutoSDR expects samples to be between -2^14 and +2^14, not -1 and +1 like some SDRs

# Start the transmitter
sdr.tx_cyclic_buffer = True # Enable cyclic buffers
sdr.tx(samples) # start transmitting

# Clear buffer just to be safe
for i in range(10):
    raw_data = sdr.rx()

# Receive samples
rx_samples = sdr.rx()

# Stop transmitting
sdr.tx_destroy_buffer()

# Calculate power spectral density (frequency domain version of signal)
psd = np.abs(np.fft.fftshift(np.fft.fft(rx_samples)))**2
psd_dB = 10*np.log10(psd)
f = np.linspace(sample_rate/-2, sample_rate/2, len(psd))

# Plot received samples in time domain. Toggle commenting out real, imag, abs
if plot_rx_samples:
    plt.figure()
    #plt.plot(np.real(rx_samples))#[:1000]))
    #plt.plot(np.imag(rx_samples))#[:1000]))
    plt.plot(np.abs(rx_samples))#[:1000]))
    plt.xlabel("Time")

# Plot processed received pulse train
rx_pulse_train = pulse_io.rx_to_pulse_train(rx_samples,num_periods,bits_per_period)

if plot_rx_pulse_train:
    plt.figure()
    plt.plot(rx_pulse_train)#[:2500]))
    plt.xlabel("Pulse Index")

#Plot freq domain
if plot_fft:
    plt.figure()
    plt.plot(f/1e6, psd_dB)
    plt.xlabel("Frequency [MHz]")
    plt.ylabel("PSD")
    plt.show()

# Verify fidelity of pulse train transmission
if check_fid:
    fidelity_check = pulse_io.check_fidelity(tx_pulse_train, rx_pulse_train)
    if fidelity_check:
        print('Success! Perfect Transmission!')
    else:
        print('Uh oh. Something was lost in translation.')
