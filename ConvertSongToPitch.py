import numpy as np
import aubio
import librosa

def load_audio_and_extract_pitch(audio_file, chunk_size, sampling_rate):
    try:
        p = aubio.pitch("yinfft", chunk_size, chunk_size, sampling_rate)
        p.set_unit("midi")
    except RuntimeError:
        # If yinfft doesn't work, try the default algorithm
        p = aubio.pitch("default", chunk_size, chunk_size, sampling_rate)
        p.set_unit("midi")
    
    audio_data, _ = librosa.load(audio_file, sr=sampling_rate)
    
    pitches = []
    for i in range(0, len(audio_data), chunk_size):
        chunk = audio_data[i:i+chunk_size]
        pitch = p(chunk)[0]
        if pitch != 0:  # Ignore unvoiced segments
            pitches.append(pitch)
    
    return pitches

if __name__ == "__main__":
    # Parameters for pitch extraction
    audio_file = "your_audio.wav"
    chunk_size = 1024
    recording_sampling_rate = 44100  # Same as your voice recording
    
    # Load the audio file and extract pitch
    pitch_data = load_audio_and_extract_pitch(audio_file, chunk_size, recording_sampling_rate)
    
    # Print the extracted pitch data
    for pitch in pitch_data:
        print("Pitch:", pitch)