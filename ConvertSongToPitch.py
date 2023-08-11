import aubio

x = aubio.source("Radiohead - Creep.wav")
for frame in x:
    print(frame)