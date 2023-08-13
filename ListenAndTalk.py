import numpy as np
import simpleaudio as sa
import threading
import pyaudio
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import aubio
import json
import time
from ToneGenerator import *
import math
from DetectHarmony import *
from ResizeYAxis import *
from ConvertSongToPitch import *

# Parameters for audio recording
FORMAT = pyaudio.paFloat32
CHANNELS = 1
RATE = 44100
CHUNK = 1024

RealSong = False



# Initialize data for the rolling average
error_window = []
error_window_size = 10  # Adjust this window size as needed

# Initialize threshold for error
error_threshold = 10  # Adjust this threshold as needed

# Create the tone array once outside of the animation
duration_ms = 1000  # Duration of the tone in milliseconds
sample_rate = 44100  # Standard audio sample rate

Default_Size_Of_Y_Axis = 500
DynamicSizing = False


five_second_value_conversion = 0.0046 #conversion of time to some arbitrary value. This determines the length of the signal.

amplitude_threshold = 0.00001  # Adjust this threshold as needed

intervals = ["Unison","Octave","Perfect Fifth","Perfect Fourth","Major Sixth","Major Third","Minor Sixth","Minor Third","Major 2nd","Minor 7th","Major 7th","Minor 2nd", "Tritone"]
interval_ratios = [1/1,2/1,3/2,4/3,5/3,5/4,8/5,6/5,9/8,16/9,15/8,16/15,7/5]
interval_ratios_below = [1/1,1/2,2/3,3/4,3/5,4/5,5/8,5/6,8/9,9/16,8/15,15/16,5/7]

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
ax.set_ylim(0, 500)
ax.set_xlim(0, 5)  # Display most recent 5 seconds
ax.legend()
ax.set_xlabel('Time (s)')
ax.set_ylabel('Frequency (Hz)')

# Initialize data for the plot
time_values = []
played_tone_freqs = []
sung_tone_freqs = []

if RealSong:
    SongPitches = load_audio_and_extract_pitch("DTTIA_Vocals.wav",CHUNK,sample_rate)

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
    
    # Calculate the current error
    if sung_tone_freqs and sung_tone_freqs[-1] is not None:
        current_error = abs(pitch - sung_tone_freqs[-1])
    else:
        current_error = 0.0

    # Update the error window
    error_window.append(current_error)
    if len(error_window) > error_window_size:
        error_window.pop(0)
    
    # Calculate the rolling average of the error
    rolling_average_error = np.mean(error_window)
    
    if np.max(np.abs(data_np)) > amplitude_threshold and rolling_average_error < error_threshold:
        sung_tone_freqs.append(pitch)
    else:
        sung_tone_freqs.append(None)  # Append None for no singing
    
    if RealSong:
        played_tone_freqs.append(SongPitches[i])

    else:
        if current_frequency is not None:
            played_tone_freqs.append(current_frequency)  # Reuse the generated tone array
        else:
            played_tone_freqs.append(None)

    time_values.append(i / RATE)
    
    # Remove old data points that are outside the time range
    while time_values[-1] - time_values[0] > five_second_value_conversion:
        time_values.pop(0)
        sung_tone_freqs.pop(0)
        played_tone_freqs.pop(0)
    
    # Update x-axis limits based on the most recent time value
    ax.set_xlim(time_values[0], time_values[-1])
    line_sung.set_data(time_values, sung_tone_freqs)
    line_played.set_data(time_values, played_tone_freqs)

    if sung_tone_freqs[-1] != 0 and sung_tone_freqs[-1] is not None:
        ResizeYAxis(Default_Size_Of_Y_Axis, sung_tone_freqs[-1], ax, DynamicSizing)

    if sung_tone_freqs[-1] != 0 and sung_tone_freqs[-1] is not None and played_tone_freqs[-1] is not None:
        interval, diff, octave = calculate_interval_and_octave(sung_tone_freqs[-1],played_tone_freqs[-1])
        semitonesFromA440 = calculate_sung_pitch(sung_tone_freqs[-1])
        print(interval + ", Difference of: " + str(diff) + " hz, Octave: " + str(octave), "Sung Pitch: " + str(semitonesFromA440))

    return line_played, line_sung

# Create a thread for playing the tone
def play_tone_thread():
    global tone
    duration_ms = 1000  # Duration of the tone in milliseconds
    sample_rate = 44100  # Standard audio sample rate

    play_tone((tone * 32767).astype(np.int16), sample_rate)

# Create a thread for playing the song
def play_song_thread():
    for note_info in song:
        note = note_info["note"]
        octave = note_info["octave"]
        duration = note_info["duration"]
        global current_frequency
        current_frequency = calculate_note_frequency(note,octave)
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