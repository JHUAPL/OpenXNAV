# -*- coding: utf-8 -*-
"""
Execute hardware demo for OpenXNAV SDRs.

Check connectivity of individual SDRs, then connectivity between the two,
then transmit desired data between them.

Created on Wed Jun  7 15:44:59 2023

@author: berksma1
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import sdr_io

import  tkinter as tk
from tkinter import filedialog


def check_indiv_connectivity(sdr1,sdr2,sample_rate,center_freq,
                             plot_rx_pulse_train = True,plot_rx_samples = True,
                             plot_fft = True,check_fid = True):
    '''
    Check connectivity and transmission fidelity of individual SDR(s).

    Parameters
    ----------
    sdr1 : str
        IP address of first SDR.
    sdr2 : str
        IP address of second SDR.
    sample_rate : int
        Sampling frequency of the signal.
    center_freq : int
        Transmission frequency of SDR.
    plot_rx_pulse_train : bool, optional
        Specify whether you want to generate a plot of the received pulse 
        sequence. The default is True.
    plot_rx_samples : bool, optional
        Specify whether you want to generate a plot of the received 
        non-processed sinusoidal waveform. The default is True.
    plot_fft : bool, optional
        Specify whether you want to plot the Fourier transform of the received 
        waveform. The default is True.
    check_fid : bool, optional
        Specify whether you want to compare the transmitted and received pulse 
        sequences for transmission fidelity. The default is True.

    Returns
    -------
    None.

    '''
    # Check that both SDRs can transmit and receive data to themselves
    tx_data = np.load('test_vec.npy')
    tx_length = 5000
    
    sdr_io.sdr_tx_rx(sample_rate,center_freq,
                     sdr1,sdr1,
                     tx_data,tx_length,
                     False,False, False, False)
    
    sdr_io.sdr_tx_rx(sample_rate,center_freq,
                     sdr2,sdr2,
                     tx_data,tx_length,
                     False,False, False, False)
    
    # Prompt user to connect SDRs together before transmitting between them
    cont = input('Now that you have verified both SDRs can transmit and '
                 'receive data to and from your PC, connect the Tx port of the'
                 ' "X-RAY EMITTER" SDR to the Rx port of the "X_RAY DETECTOR" '
                 'SDR. Press Enter when ready to proceed.')
    
    # Now that SDRs are connected, check connectivity and transmission fidelity
    sdr_io.sdr_tx_rx(sample_rate,center_freq,
                 sdr1,sdr2,
                 tx_data,tx_length,
                 plot_rx_pulse_train,plot_rx_samples,plot_fft,check_fid)
    
def transmit_data(sdr1,sdr2,sample_rate,center_freq,
                  tx_data_name,tx_length,
                  plot_rx_pulse_train = True,plot_rx_samples = True,
                  plot_fft = True,check_fid = True):
    '''
    After generating a pulse train from the OpenXNAV software, transmit it from 
    the "Emitter" SDR to the "Detector" SDR

    Parameters
    ----------
    sdr1 : str
        IP address of first SDR.
    sdr2 : str
        IP address of second SDR.
    sample_rate : int
        Sampling frequency of the signal.
    center_freq : int
        Transmission frequency of SDR.
    tx_data_name : str
        filename for pulse sequence to be transmitted.
    tx_length : int
        length (in sample points) of desired pulse train.
    plot_rx_pulse_train : bool, optional
        Specify whether you want to generate a plot of the received pulse 
        sequence. The default is True.
    plot_rx_samples : bool, optional
        Specify whether you want to generate a plot of the received 
        non-processed sinusoidal waveform. The default is True.
    plot_fft : bool, optional
        Specify whether you want to plot the Fourier transform of the received 
        waveform. The default is True.
    check_fid : bool, optional
        Specify whether you want to compare the transmitted and received pulse 
        sequences for transmission fidelity. The default is True.

    Returns
    -------
    None.

    '''
    tx_data = np.load(tx_data_name)
    tx_data = tx_data[:tx_length]
    
    plt.plot(tx_data)
    plt.title('Transmitted data')
    plt.show()
    
    print("Received data:")
    sdr_io.sdr_tx_rx(sample_rate,center_freq,
                 sdr1,sdr2,
                 tx_data,tx_length,
                 plot_rx_pulse_train,plot_rx_samples,plot_fft,check_fid)

def main():
    # Get SDR IP address(es)
    sdr1 = input('Enter IP address of '\
                 'first '\
                 'SDR: ')
    sdr2 = input('Enter IP address of second SDR: ')
    
    # Ping SDR(s) in command prompt, prompt user whether they wish to proceed
    os.system('ping '+sdr1)
    os.system('ping '+sdr2)
    
    cont = input('SDR ping tests complete. Continue? [y/n] ')
    if cont == 'n' or cont == 'N' or cont == '':
        return
    
    # Define SDR signal parameters
    sample_rate = 1e6 # Hz
    center_freq = 915e6 # Hz
    
    check_indiv_connectivity(sdr1, sdr2, sample_rate, center_freq,
                             plot_rx_pulse_train = True,plot_rx_samples = True,
                             plot_fft = True,check_fid = True)
    
    cont = input('SDR connectivity check complete. '
                 'Continue with transmission? [y/n] ')
    if cont == 'n' or cont == 'N' or cont == '':
        return
    
    # Define raw data to be transmitted
    root = tk.Tk()
    tx_data_name = filedialog.askopenfilename()
    root.destroy()
    
    tx_length = int(input('Enter desired length of pulse sequence: '))
    
    transmit_data(sdr1, sdr2, sample_rate, center_freq, 
                  tx_data_name, tx_length,
                  plot_rx_pulse_train = True,plot_rx_samples = True,
                  plot_fft = True,check_fid = True)

main()
    
