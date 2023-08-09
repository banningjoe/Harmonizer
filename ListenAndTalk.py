import numpy as np
import simpleaudio as sa
import threading
import pyaudio
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import aubio
import json
import time
from Test import *

# Parameters for audio recording
FORMAT = pyaudio.paFloat32
CHANNELS = 1
RATE = 44100
CHUNK = 1024

# Initialize PyAudio
p = pyaudio.PyAudio()

# Open the microphone stream
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

# Initialize Aubio pitch detection
pitch_o = aubio.pitch("default", CHUNK, CHUNK, RATE)
pitch_o.set_unit("Hz")
pitch_o.set_silence(-40)

# Initialize plot
fig, ax = plt.subplots()
line_played, = ax.plot([], [], label='Played Tone', color='blue')
line_sung, = ax.plot([], [], label='Sung Tone', color='red')
ax.set_ylim(0, 1500)
ax.set_xlim(0, 5)  # Display most recent 5 seconds
ax.legend()
ax.set_xlabel('Time (s)')
ax.set_ylabel('Frequency (Hz)')

# Initialize data for the plot
time_values = []
played_tone_freqs = []
sung_tone_freqs = []

# Create the tone array once outside of the animation
duration_ms = 1000  # Duration of the tone in milliseconds
sample_rate = 44100  # Standard audio sample rate
tone = generate_tone("E", 3, duration_ms, sample_rate)

def init():
    line_played.set_data([], [])
    line_sung.set_data([], [])
    return line_played, line_sung

# Function to update the plot with new audio data
def animate(i):
    data = stream.read(CHUNK)
    data_np = np.frombuffer(data, dtype=np.float32)
    
    # Normalize the audio data
    data_normalized = data_np / np.max(np.abs(data_np))
    
    # Perform pitch estimation using Aubio
    pitch = pitch_o(data_normalized)[0]
    
    if pitch <= 1500:  # Exclude values greater than 1500 Hz
        sung_tone_freqs.append(pitch)
        played_tone_freqs.append(tone[i % len(tone)])  # Reuse the generated tone array
        time_values.append(i / RATE)
        
        # Calculate the time range for the x-axis
        time_range = max(0, time_values[-1] - 5)  # Show most recent 5 seconds
        ax.set_xlim(time_range, time_values[-1])
        
        line_sung.set_data(time_values, sung_tone_freqs)
        line_played.set_data(time_values, played_tone_freqs)
    
    return line_played, line_sung

# Create a thread for playing the tone
def play_tone_thread():
    global tone
    duration_ms = 1000  # Duration of the tone in milliseconds
    sample_rate = 44100  # Standard audio sample rate

    tone = generate_tone("E", 3, duration_ms, sample_rate)
    play_tone((tone * 32767).astype(np.int16), sample_rate)

# Create a thread for playing the song
def play_song_thread():
    for note_info in song:
        note = note_info["note"]
        octave = note_info["octave"]
        duration = note_info["duration"]
        
        tone = generate_tone(note, octave, duration * 1000, sample_rate)
        play_tone((tone * 32767).astype(np.int16), sample_rate)
        time.sleep(duration)

# Load song from JSON
with open("song.json", "r") as json_file:
    song = json.load(json_file)

# Set up animation
ani = animation.FuncAnimation(fig, animate, init_func=init, blit=True, interval=10)

# Create and start threads
play_thread = threading.Thread(target=play_tone_thread)
song_thread = threading.Thread(target=play_song_thread)

play_thread.start()
song_thread.start()

# Show the plot
plt.show()

# Stop and close the stream
stream.stop_stream()
stream.close()

# Terminate PyAudio
p.terminate()

# Wait for the threads to finish
play_thread.join()
song_thread.join()