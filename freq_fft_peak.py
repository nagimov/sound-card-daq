#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
import soundcard as sc

peak, argpeak = np.min, np.argmin  # replace with (np.max, np.argmax) for max values

# fft peak
freq_bins = np.geomspace(30, 17000, 300)
freq_bins_cent = [np.mean([lo, hi]) for lo, hi in zip(freq_bins[:-1], freq_bins[1:])]
w_L, w_R = sc.play_and_record(sc.white_noise())
freq = np.fft.rfftfreq(len(w_L), 1 / sc.SAMPLE_RATE)
fft_L, fft_R = np.abs(np.fft.rfft(w_L)), np.abs(np.fft.rfft(w_R))
fft_L_bins = [np.mean(fft_L[np.where((freq > lo) & (freq <= hi))]) for lo, hi in zip(freq_bins[:-1], freq_bins[1:])]
fft_R_bins = [np.mean(fft_R[np.where((freq > lo) & (freq <= hi))]) for lo, hi in zip(freq_bins[:-1], freq_bins[1:])]
freq_L_peak, fft_L_peak = freq_bins_cent[argpeak(fft_L_bins)], peak(fft_L_bins)
freq_R_peak, fft_R_peak = freq_bins_cent[argpeak(fft_R_bins)], peak(fft_R_bins)
print(f'peaks: f_L = {freq_L_peak:.2f} Hz, f_R = {freq_R_peak:.2f} Hz')
# plot
scale = 0.01
plt.figure(figsize=(9, 2))
plt.plot(freq_bins_cent, np.array(fft_L_bins) * scale, '.-', label=f'L ch: peak @ {freq_L_peak:.2f} Hz', lw=0.5, ms=1)
plt.plot(freq_bins_cent, np.array(fft_R_bins) * scale, '.-', label=f'R ch: peak @ {freq_R_peak:.2f} Hz', lw=0.5, ms=1)
plt.plot([freq_L_peak, freq_R_peak], [fft_L_peak * scale, fft_R_peak * scale], '+', ms=7)
plt.tight_layout()
plt.legend(loc='lower left')
plt.xscale('log')
plt.savefig(__file__.replace('.py', '.png'), dpi=100)
