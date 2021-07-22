#!/usr/bin/python3
# -*- coding: utf-8 -*-

import wave

import pcm as pcm
from pydub import AudioSegment

if __name__ == '__main__':
    aaa = AudioSegment.from_file("aaa/aaa.pcm", sample_width = 2, frame_rate = 44100, channels = 2)
    bbb = AudioSegment.from_file("aaa/bbb.pcm", sample_width = 2, frame_rate = 44100, channels = 2)
    (None + aaa + bbb).export("./aaa/ccc.mp3", format = "raw")
    # audio.export("./aaa.pcm/aaa.pcm", format = "raw")

    # with open("aaa.pcm/00a45c3d34607ff46595c7d6fe0f89de.pcm", 'rb') as pcmfile:
    #     pcmdata = pcmfile.read()
    # with wave.open("1111.wav", 'wb') as wavfile:
    #     wavfile.setparams((1, 2, 16000, 0, 'NONE', 'NONE'))
    #     wavfile.writeframes(pcmdata)
