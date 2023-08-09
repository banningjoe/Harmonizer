import numpy as np
import simpleaudio as sa
import time

noteFrequencies = {
    "C": 32.703,
    "C#": 34.648,
    "D": 36.708,
    "D#": 38.891,
    "E": 41.203,
    "F": 43.654,
    "F#": 46.249,
    "G": 48.999,
    "G#": 51.913,
    "A": 55,
    "A#":58.27,
    "B":61.735
}

def calculate_note_frequency(note,octave):
    frequency = noteFrequencies[note]*(2**octave)
    return frequency

def generate_tone(note,octave, duration_ms, sample_rate):
    frequency = calculate_note_frequency(note,octave)
    t = np.linspace(0, duration_ms / 1000, int(sample_rate * duration_ms / 1000), False)
    tone = 0.5 * np.sin(2 * np.pi * frequency * t)
    return tone

def play_tone(audio_samples, sample_rate):
    play_obj = sa.play_buffer(audio_samples, 1, 2, sample_rate)
    play_obj.wait_done()

if __name__ == "__main__":
    duration_ms = 1000  # Duration of the tone in milliseconds
    sample_rate = 44100  # Standard audio sample rate

    tone = generate_tone("E",3, duration_ms, sample_rate)
    play_tone((tone * 32767).astype(np.int16), sample_rate)
    