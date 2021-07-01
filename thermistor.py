#!/usr/bin/env python3

import numpy as np
import soundcard as sc

R_1 = 9.95e3
R_2 = 10.0e3
R_3 = 9.94e3
A = 2.108508173e-3
B = 0.7979204727e-4
C = 6.535076315e-7

while True:
    w_L, w_R = sc.play_and_record(sc.sine_wave())
    rms_L, rms_R = sc.rms(w_L), sc.rms(w_R)
    gain_ratio = rms_R * (R_1 + R_2) / R_2
    R_NTC = R_3 * (gain_ratio / rms_L - 1)
    T_NTC = 1 / (A + B * np.log(R_NTC) + C * np.log(R_NTC) ** 3) - 273.15
    print(f'R_NTC = {R_NTC:.1f} Ohm, T_NTC = {T_NTC:.1f} C')
