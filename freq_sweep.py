#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
import soundcard as sc

# frequency sweep
freq = np.geomspace(3, 20000, num=200)
with open(__file__.replace('.py', '.csv'), 'w') as csv:
    csv.write('freq, rms_L, rms_R\n')
    for f in freq:
        w_L, w_R = sc.play_and_record(sc.sine_wave(f))
        rms_L, rms_R = sc.rms(w_L), sc.rms(w_R)
        print(f'f = {f:.2f}, rms_L = {rms_L:.2f}, rms_R = {rms_R:.2f}')
        csv.write(f'{f:.2f}, {rms_L:.2f}, {rms_R:.2f}\n')
sweep = np.genfromtxt(__file__.replace('.py', '.csv'), delimiter=',', names=True)
# plot
plt.figure(figsize=(9, 2))
plt.plot(sweep['freq'], sweep['rms_L'], '.-', label='L ch', lw=0.5, ms=1)
plt.plot(sweep['freq'], sweep['rms_R'], '.-', label='R ch', lw=0.5, ms=1)
plt.tight_layout()
plt.legend(loc='upper left')
plt.xscale('log')
plt.savefig(__file__.replace('.py', '.png'), dpi=100)
