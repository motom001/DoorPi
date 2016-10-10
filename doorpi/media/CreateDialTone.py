#!/usr/bin/python


# Stolen from this source - thx to FB36:
# http://code.activestate.com/recipes/578168-sound-generator-using-wav-file/

def generate_dial_tone(filename = 'dialtone.wav', volume = 50):
    # generate wav file containing sine waves
    # FB36 - 20120617
    import math, wave, array
    duration = 3 # seconds
    freq = 440 # of cycles per second (Hz) (frequency of the sine waves)
    data = array.array('h') # signed short integer (-32768 to 32767) data
    sampleRate = 44100 # of samples per second (standard)
    #sampleRate = 2048 # of samples per second (standard)
    numChan = 1 # of channels (1: mono, 2: stereo)
    dataSize = 2 # 2 bytes because of using signed short integers => bit depth = 16
    numSamplesPerCyc = int(sampleRate / freq)
    numSamples = sampleRate * duration
    for i in range(numSamples / 2):
        sample = 32767 * float(volume) / 100
        sample *= math.sin(math.pi * 2 * (i % numSamplesPerCyc) / numSamplesPerCyc)
        data.append(int(sample))
    for i in range(numSamples / 2):
        sample = 0
        data.append(int(sample))
    f = wave.open(filename, 'w')
    f.setparams((numChan, dataSize, sampleRate, numSamples, "NONE", "Uncompressed"))
    f.writeframes(data.tostring())
    f.close()

    return filename