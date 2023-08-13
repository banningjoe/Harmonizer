import simpleaudio as sa
import numpy as np
import time

def play_pitches_as_tones(pitch_list, duration, sampling_rate=44100):
    tones = []
    
    for pitch in pitch_list:
        frequency = 440 * 2 ** ((pitch - 69) / 12)  # MIDI to frequency conversion
        t = np.linspace(0, duration, int(sampling_rate * duration), False)
        tone = 0.3 * np.sin(2 * np.pi * frequency * t)
        tones.append(tone)
    
    combined_tones = np.concatenate(tones)
    audio_data = (32767 * combined_tones).astype(np.int16)
    
    play_obj = sa.play_buffer(audio_data, 1, 2, sampling_rate)
    play_obj.wait_done()

if __name__ == "__main__":
    # Example list of MIDI pitches
    pitch_list = [60, 62, 64, 65, 67, 69, 71, 72]
    
    duration = 0.5  # Duration of each tone in seconds
    
    play_pitches_as_tones(pitch_list, duration)