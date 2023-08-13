from ConvertSongToPitch import *
from PlayPitches import *
audio_file = "DTTIA_Vocals.wav"
chunk_size = 1024
recording_sampling_rate = 44100  # Same as your voice recording

# Load the audio file and extract pitch
pitch_data = load_audio_and_extract_pitch(audio_file, chunk_size, recording_sampling_rate)

play_pitches_as_tones(pitch_data,duration = 1)



