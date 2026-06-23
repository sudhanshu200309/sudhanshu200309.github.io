#!/usr/bin/env python3
"""
Boom Shaka Laka Song Player - Display song lyrics line by line in the terminal
with timing to match the song flow
"""

import time
import os

def clear_screen():
    """Clear the terminal screen"""
    os.system('clear' if os.name == 'posix' else 'cls')

def play_song(lyrics_with_timing):
    """
    Play song lyrics word by word with proper timing
    
    Args:
        lyrics_with_timing: List of tuples (lyric_line, delay_in_seconds)
    """
    clear_screen()
    print("\n" * 2)
    print("=" * 70)
    print("🎵 BOOM SHAKA LAKA - KR$NA & Dhandha Nyoliwala 🎵".center(70))
    print("=" * 70)
    print("\n" * 2)
    
    time.sleep(2)
    
    for line, delay in lyrics_with_timing:
        if line:  # Only process non-empty lines
            words = line.split()
            word_delay = delay / len(words) if len(words) > 0 else delay
            
            for i, word in enumerate(words):
                print(f"{word}", end="", flush=True)
                time.sleep(word_delay)
                if i < len(words) - 1:
                    print(" ", end="", flush=True)
            print()  # New line after all words
        else:
            print()  # Print blank line for spacing
            time.sleep(delay)
    
    print("\n" * 2)
    print("=" * 70)
    print("Song finished! 🎵".center(70))
    print("=" * 70)

# Define the song with timing
# Format: (lyric_line, time_to_display_for_in_seconds)
# Adjust timing to match the beat of the song
# Use "" (empty string) with short delay for pauses between lines

song_lyrics = [
    # INTRO - Chorus
    ("Kare ab Boom Shaka laka, Kare Bandook Shaka laka", 2.5),
    ("Chilla rahe Boom Shaka laka, hilade room Shaka laka", 2.5),
    ("Bolo Boom Shaka laka, Kare Bandook Shaka laka", 2.5),
    ("Chilla rahe Boom Shaka laka, hilade room Shaka laka", 2.5),
    ("", 0.8),
    
    # VERSE 1: KR$NA
    ("Agar karoo baat toh wo aam baat (nahi)", 2.2),
    ("Aur ye kare buss baatein, jaise kaam kaaj nahi", 2.5),
    ("Jo bol rahe the zyada, unka naam aaj nahi", 2.3),
    ("Mujhse bhid na dubara tu koi jaan baaz ni", 2.4),
    ("", 0.5),
    
    ("Me na gayab hota bro, Just quiet, on the low", 2.3),
    ("And If I ever go, Mai Retire hora G.O.A.T", 2.4),
    ("Mujhe kheeche ye niche, The higher up I go", 2.2),
    ("Me waha se se hoo aaya, Where they fire up the stove", 2.5),
    ("", 0.5),
    
    ("Chalata me b'm, The 5 series be M", 2.0),
    ("Jo Rakti thi blocked, Kare slide in my DM", 2.2),
    ("Har subah bheje GM, Milna hai TN", 1.8),
    ("Kyunki chahiye usse chahiye more D, jaise PM", 2.3),
    ("", 0.8),
    
    # CHORUS
    ("Kare ab Boom Shaka laka, Kare Bandook Shaka laka", 2.5),
    ("Chilla rahe Boom Shaka laka, hila de room Shaka laka", 2.5),
    ("Bolo ab Boom Shaka laka, Kare Bandook Shaka laka", 2.5),
    ("Chilla rahe Boom Shaka laka, hila de room Shaka laka", 2.5),
    ("", 0.8),
    
    # VERSE 2: Dhandha Nyoliwala
    ("Jab tak khada yo chora is field PE", 2.0),
    ("Samajh le match abhi baaki hai", 1.8),
    ("Boundary se bahr ball giregi or", 1.9),
    ("Feel aani Nagasaki hai", 1.7),
    ("", 0.5),
    
    ("Dil chori ni karde loot leva ye chore", 2.3),
    ("Dila ke r daku hai", 1.6),
    ("Mai ta duniya bhuli baitha c tu menu", 2.2),
    ("Dass tan sahi Tera naa ki hai", 2.0),
    ("", 0.8),
    
    # OUTRO - Chorus
    ("Bolo ab Boom Shaka laka, Kare Bandook Shaka laka", 2.5),
    ("Chilla rahe Boom Shaka laka, hilade room Shaka laka", 2.5),
    ("", 2.0),
]

if __name__ == "__main__":
    try:
        play_song(song_lyrics)
    except KeyboardInterrupt:
        print("\n\nSong interrupted by user.")
