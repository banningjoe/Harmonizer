import math
intervals = ["Unison","Octave","Perfect Fifth","Perfect Fourth","Major Sixth","Major Third","Minor Sixth","Minor Third","Major 2nd","Minor 7th","Major 7th","Minor 2nd", "Tritone"]
interval_ratios = [1/1,2/1,3/2,4/3,5/3,5/4,8/5,6/5,9/8,16/9,15/8,16/15,7/5]
interval_ratios_below = [1/1,1/2,2/3,3/4,3/5,4/5,5/8,5/6,8/9,9/16,8/15,15/16,5/7]

Tones = {
     0: "A",
     1: "A#",
     2: "B",
     3: "C",
     4: "C#",
     5: "D",
     6: "D#",
     7: "E",
     8: "F",
     9: "F#",
     10: "G",
     11: "G#"
}

def calculate_interval_and_octave(sung_pitch, played_pitch):
        octave = math.floor(math.log2(sung_pitch/played_pitch)) 
        pitch_ratio = sung_pitch / (played_pitch*(2**octave))
        if pitch_ratio < 1:
            relative_pitches = interval_ratios_below - pitch_ratio
        else:
            relative_pitches = interval_ratios - pitch_ratio
        abs_relative_pitches = [abs(diff) for diff in relative_pitches]
        closest_interval = min(abs_relative_pitches)
        index = abs_relative_pitches.index(closest_interval)
        pitch_to_hit = played_pitch*interval_ratios[index]
        return intervals[index],pitch_to_hit - sung_pitch,octave

def calculate_sung_pitch(sung_pitch):
     semitonesFromA440 = 12*math.log2(sung_pitch/440)
     roundedTone = round(semitonesFromA440)
     roundedTone = roundedTone % 12
     tone = Tones[roundedTone]
     return tone
     