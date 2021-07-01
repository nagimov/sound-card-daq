import configparser
import numpy as np
import os
import subprocess
import time
from scipy.io import wavfile

CFG_FILE = os.path.join(os.environ['HOME'], 'soundcard.cfg')
WAV_FILE_OUT = '/tmp/out.wav'
WAV_FILE_IN = '/tmp/in.wav'
SAMPLE_RATE = 44100
BIT_DEPTH = np.int16
WAV_FORMAT = 's16ne'
VOL_PLAY = 2 ** 16 - 1
DURATION_RECORD = 2
PAUSE_PRE_PLAY = 2
PAUSE_PRE_RECORD = 2
PAUSE_POST_RECORD = 2
DURATION_PLAY = DURATION_RECORD + PAUSE_PRE_RECORD + PAUSE_POST_RECORD

config = configparser.ConfigParser()
config.read(CFG_FILE)
PA_SINK = config.get('SOUNDCARD', 'PA_SINK', fallback='')
PA_SOURCE = config.get('SOUNDCARD', 'PA_SOURCE', fallback='')
VOL_RECORD = config.getint('SOUNDCARD', 'VOL_RECORD', fallback=-1)
if PA_SINK == '' or PA_SOURCE == '' or VOL_RECORD == -1:
    config['SOUNDCARD'] = {'PA_SINK': PA_SINK, 'PA_SOURCE': PA_SOURCE, 'VOL_RECORD': VOL_RECORD}
    with open(CFG_FILE, 'w') as cfg:
        config.write(cfg)
if PA_SINK == '' or PA_SOURCE == '':
    raise ValueError(f'PA_SINK or PA_SOURCE are not set! Specify PulseAudio devices in {CFG_FILE}')


def sine_wave(frequency=440):
    time_points = np.linspace(0, DURATION_PLAY, SAMPLE_RATE * DURATION_PLAY)
    return np.iinfo(BIT_DEPTH).max * np.sin(frequency * 2 * np.pi * time_points)


def white_noise():
    return np.random.uniform(np.iinfo(BIT_DEPTH).min, np.iinfo(BIT_DEPTH).max, SAMPLE_RATE * DURATION_PLAY)


def is_waveform_clipped(waveform):
    clipped_top = np.max(waveform) >= np.iinfo(BIT_DEPTH).max
    clipped_bottom = np.min(waveform) <= np.iinfo(BIT_DEPTH).min
    return clipped_top or clipped_bottom


def write_waveform(waveform):
    if os.path.exists(WAV_FILE_OUT):
        os.remove(WAV_FILE_OUT)
    wavfile.write(WAV_FILE_OUT, SAMPLE_RATE, np.hstack((waveform, waveform)).astype(BIT_DEPTH))


def play_wav():
    subprocess.Popen(['pacmd', 'set-sink-volume', PA_SINK, '0'])
    subprocess.Popen(['pacmd', 'set-sink-volume', PA_SINK, f'{int(VOL_PLAY)}'])
    subprocess.Popen(['paplay', WAV_FILE_OUT, f'--device={PA_SINK}'])


def record_wav():
    if VOL_RECORD == -1:
        raise ValueError('VOL_RECORD parameter is not set! Use gain_tune.py to configure recording gain')
    if os.path.exists(WAV_FILE_IN):
        os.remove(WAV_FILE_IN)
    subprocess.Popen(['pacmd', 'set-source-volume', PA_SOURCE, '0'])
    subprocess.Popen(['pacmd', 'set-source-volume', PA_SOURCE, f'{int(VOL_RECORD)}'])
    subprocess.Popen(
        [
            'parecord',
            f'--device={PA_SOURCE}',
            f'--rate={SAMPLE_RATE}',
            f'--format={WAV_FORMAT}',
            '--channels=2',
            f'--process-time-msec={DURATION_RECORD*1000}',
            WAV_FILE_IN,
        ]
    )


def read_waveform():
    _, waveform = wavfile.read(WAV_FILE_IN)
    return waveform


def play_and_record(waveform):
    write_waveform(waveform)
    time.sleep(PAUSE_PRE_PLAY)
    play_wav()
    time.sleep(PAUSE_PRE_RECORD)
    record_wav()
    time.sleep(DURATION_RECORD)
    subprocess.Popen(['pkill', 'parecord'])
    time.sleep(PAUSE_POST_RECORD)
    new_waveform = read_waveform()
    subprocess.Popen(['pkill', 'paplay'])
    if is_waveform_clipped(new_waveform):
        raise ValueError('Recorded waveform is clipped - reduce VOL_RECORD parameter')
    new_waveform_L = new_waveform.astype('int')[:, 0]
    new_waveform_R = new_waveform.astype('int')[:, 1]
    return new_waveform_L, new_waveform_R


def rms(waveform):
    return np.sqrt(np.mean(np.square(waveform)))
