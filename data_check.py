import matplotlib
matplotlib.use('Agg')

import netCDF4 as nc
import matplotlib.pyplot as plt

filename = '/home/thebear/codes4fun/project_master/triton_gnssr_processing/data/20250107/TRITON_185832_20250107174354_CorDDM_v2.0_nc'

def plot_ddm(ddm):
    plt.figure(figsize=(8, 6))
    plt.imshow(ddm, aspect='auto', cmap='viridis')
    plt.colorbar(label='Amplitude [W]')
    plt.tight_layout()
    plt.savefig(f'/home/thebear/codes4fun/project_master/triton_gnssr_processing/figs/lole')
    plt.close()

def read_file(filename):
    dataset = nc.Dataset(filename, 'r')
    ddm = dataset.variables['DDMpower'][:]
    print(f'shape of DDMpower: {ddm.shape}')
    codeRange = dataset.variables['CodePhaseRange'][:]
    print(f'shape of CodePhaseRange: {codeRange.shape}')
    print(f'here is the CodePhaseRange variable: {codeRange}')
    prn = dataset.variables['PRN'][:]
    print(f'shape of PRN: {prn.shape}')
    print(f'here is the PRN variable: {prn}')
    chodePhaseRate= dataset.variables['CodePhaseRate'][:]
    print(f'shape of CodePhaseRate: {chodePhaseRate.shape}')
    print(f'here is the CodePhaseRate variable: {chodePhaseRate}')
    #DDMpower= dataset.variables['DDMpower'][:]
    #print(f'shape of DDMPower: {DDMpower.shape}')
    #print(f'here is the DDMPower variable: {DDMpower}')
    codePhase= dataset.variables['CodePhase'][1380:1386]
    print(codePhase)
    #codePhaseRange= dataset.variables['CodePhaseRange'][:]
    dopplerFrequency= dataset.variables['DopplerFrequency'][:]
    #dopplerRange= dataset.variables['DopplerRange'][:]  
    #clk_bias = dataset.variables['ClkBiasRate'][:]
    print(f'shape of doppler then codephase: {dopplerFrequency.shape}, {codePhase.shape}')
    #print(f'here is the DopplerFrequency variable: {dopplerFrequency}')
    #print(f'here is the DopplerRange variable: {dopplerRange}')
    #print(f'here is the CodePhase variable: {codePhase}')
    #print(f'here is the CodePhaseRange variable: {codePhaseRange}')
    #print(f'here is the ClkBiasRate variable: {clk_bias}')
    #plot_ddm(DDMpower)

read_file(filename)

"""
CodePhase
desc:The code phase delay value of 65 bin in 128 bin in code phase delay axis
type:float64
unit:chips

DopplerFrequency
desc:the real vale of Doppler Frequency need to +ClkBiasRate*f1*10^(-12) and f1=1575.42E+6
type:float64
unit:Hz

"""