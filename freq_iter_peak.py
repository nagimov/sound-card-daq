#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
import soundcard as sc

STEPS = 4
ITERS = 4

peak, argpeak = np.min, np.argmin  # replace with (np.max, np.argmax) for max values

# optimization
freq = {'L': np.geomspace(30, 17000, num=STEPS).tolist(), 'R': np.geomspace(30, 17000, num=STEPS).tolist()}
rms = {'L': [], 'R': []}
for n, ch in [(0, 'L'), (1, 'R')]:
    print(f'Optimizing channel {ch}')
    for f in freq[ch]:
        w = sc.play_and_record(sc.sine_wave(f))
        rms[ch].append(sc.rms(w[n]))
        print(f'f = {f:.2f} Hz, rms_{ch} = {rms[ch][-1]:.2f}')
    for i in range(ITERS):
        peak_indices = np.argwhere(rms[ch] == peak(rms[ch])).flatten()
        peak_index_left, peak_index_right = max(0, min(peak_indices) - 1), min(max(peak_indices) + 1, len(freq[ch]) - 1)
        print(f'{" "*4*i}refining peak: f_{ch} = {freq[ch][peak_indices[0]]:.2f} Hz, peak_{ch} = {peak(rms[ch]):.2f}')
        freq_fine = np.geomspace(freq[ch][peak_index_left], freq[ch][peak_index_right], num=STEPS + 2)
        freq_fine = [k for k in freq_fine[1:-1] if k not in freq[ch]]  # don't duplicate measurements
        for f in freq_fine:
            freq_pos = np.argwhere(f < np.array(freq[ch])).flatten()[0]
            w = sc.play_and_record(sc.sine_wave(f))
            rms[ch].insert(freq_pos, sc.rms(w[n]))
            freq[ch].insert(freq_pos, f)
            print(f'{" "*4*(i+1)}f = {f:.2f} Hz, rms_{ch} = {rms[ch][freq_pos]:.2f}')
    peak_indices = np.argwhere(rms[ch] == peak(rms[ch])).flatten()
    peak_freq = freq[ch][peak_indices[len(peak_indices) // 2]]
    print(f'{"    "*ITERS}final peak: f_{ch} = {peak_freq:.2f} Hz, rms_{ch} = {peak(rms[ch]):.2f}')
    freq[f'{ch}_peak'], rms[f'{ch}_peak'] = freq[ch][argpeak(rms[ch])], peak(rms[ch])
# plot
plt.figure(figsize=(9, 2))
for ch in ['L', 'R']:
    plt.plot(freq[ch], rms[ch], '.-', label=f'{ch} ch: peak @ {freq[f"{ch}_peak"]:.2f} Hz', lw=0.5, ms=3)
plt.plot([freq['L_peak'], freq['R_peak']], [rms['L_peak'], rms['R_peak']], '+', ms=7)
plt.tight_layout()
plt.legend(loc='lower left')
plt.xscale('log')
plt.savefig(__file__.replace('.py', '.png'), dpi=100)
