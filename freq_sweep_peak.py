#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
import soundcard as sc

peak, argpeak = np.min, np.argmin  # replace with (np.max, np.argmax) for max values

# frequency sweep
freq = np.geomspace(30, 17000, num=100)
with open(__file__.replace('.py', '.csv'), 'w') as csv:
    csv.write('freq, rms_L, rms_R\n')
    for f in freq:
        w_L, w_R = sc.play_and_record(sc.sine_wave(f))
        rms_L, rms_R = sc.rms(w_L), sc.rms(w_R)
        print(f'f = {f:.2f} Hz, rms_L = {rms_L:.2f}, rms_R = {rms_R:.2f}')
        csv.write(f'{f:.2f}, {rms_L:.2f}, {rms_R:.2f}\n')
sweep = np.genfromtxt(__file__.replace('.py', '.csv'), delimiter=',', names=True)
freq_L_peak, rms_L_peak = sweep['freq'][argpeak(sweep['rms_L'])], peak(sweep['rms_L'])
freq_R_peak, rms_R_peak = sweep['freq'][argpeak(sweep['rms_R'])], peak(sweep['rms_R'])
# plot
plt.figure(figsize=(9, 2))
plt.plot(sweep['freq'], sweep['rms_L'], '.-', label=f'L ch: peak @ {freq_L_peak:.2f} Hz', lw=0.5, ms=1)
plt.plot(sweep['freq'], sweep['rms_R'], '.-', label=f'R ch: peak @ {freq_R_peak:.2f} Hz', lw=0.5, ms=1)
plt.plot([freq_L_peak, freq_R_peak], [rms_L_peak, rms_R_peak], '+', ms=7)
plt.tight_layout()
plt.legend(loc='lower left')
plt.xscale('log')
plt.savefig(__file__.replace('.py', '.png'), dpi=100)
