#!/usr/bin/python3
# -*- coding: utf-8 -*-

import wave
from glob import glob

import pcm as pcm
from pydub import AudioSegment

if __name__ == '__main__':
    # files = glob("test/*")
    aaa = AudioSegment.from_file("pcm/4ee59654dd66c24b301c8ef6f66ebfa1")
    # bbb = AudioSegment.from_file("pcm/04f21d1a0704fae06d9d15b15ac75799")
    # ddd = AudioSegment.from_file("pcm/4f863fb7fa811de9d661dc4cbef97c2c")
    # print((bbb + aaa + ddd).duration_seconds)
    print(aaa.duration_seconds)
    (aaa).export("./test/ccc.mp3", format("mp3"))
    # (bbb + aaa + ddd).export("./test/ccc.mp3", format("mp3"))
    # aaa = AudioSegment.from_file("test/aaa", sample_width = 1, frame_rate = 22050, channels = 2)  # bbb = AudioSegment.from_file("aaa/bbb", sample_width = 1, frame_rate = 22050, channels = 2)  # (aaa + bbb).export("./aaa/ccc.mp3", format = "raw")  # audio.export("./aaa/aaa", format = "raw")

    # with open("aaa/00a45c3d34607ff46595c7d6fe0f89de.pcm", 'rb') as pcmfile:  #     pcmdata = pcmfile.read()  # with wave.open("1111.wav", 'wb') as wavfile:  #     wavfile.setparams((1, 2, 16000, 0, 'NONE', 'NONE'))  #     wavfile.writeframes(pcmdata)
