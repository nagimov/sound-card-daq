#!/usr/bin/env python3

import configparser
import numpy as np
import soundcard as sc
import subprocess
import time

MARGIN = 0.75
STEPS_TOTAL = 5

step = 0
lo, hi = 0, 65535
while True:
    vol_current = int((hi + lo) / 2)
    sc.VOL_RECORD = vol_current
    try:
        w_L, w_R = sc.play_and_record(sc.sine_wave())
        rms_L, rms_R = sc.rms(w_L), sc.rms(w_R)
        lo = vol_current
        step += 1
        print(f'no clipping detected at VOL_RECORD = {vol_current}, rms_L = {rms_L:.2f}, rms_R = {rms_R:.2f}')
    except ValueError:
        hi = vol_current
        print(f'clipping detected at VOL_RECORD = {vol_current}')
    if step > STEPS_TOTAL:
        vol_current = int(sc.VOL_RECORD * MARGIN)
        sc.config['SOUNDCARD']['VOL_RECORD'] = str(vol_current)
        with open(sc.CFG_FILE, 'w') as cfg:
            sc.config.write(cfg)
        print(f'VOL_RECORD value {vol_current} saved to {sc.CFG_FILE}')
        break
