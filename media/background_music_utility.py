import time
from pathlib import Path

import pygame

import global_constants

_mixer_initialized = False

LAB_AUDIO_TEST_BEEP_COUNT = 2
LAB_AUDIO_TEST_BEEP_GAP_SECONDS = 0.25


def ensure_mixer_initialized() -> bool:
    """Initialize pygame mixer once for the current process."""
    global _mixer_initialized
    if _mixer_initialized:
        return True
    try:
        pygame.mixer.init()
        _mixer_initialized = True
        return True
    except pygame.error:
        return False


def get_lab_audio_test_path() -> Path:
    return Path(global_constants.MUSIC_MEDIA_PATH) / global_constants.LAB_AUDIO_TEST_SOUND


def run_lab_audio_check() -> bool:
    """Play the optional lab audio test. Returns True if beeps were played."""
    return play_lab_audio_test(get_lab_audio_test_path())


def play_lab_audio_test(beep_path: str | Path) -> bool:
    """Play the lab audio test beeps. Returns True if playback started."""
    if not ensure_mixer_initialized():
        return False

    path = Path(beep_path)
    if not path.is_file():
        return False

    try:
        sound = pygame.mixer.Sound(str(path))
        duration = sound.get_length()
        for beep_index in range(LAB_AUDIO_TEST_BEEP_COUNT):
            if sound.play() is None:
                return False
            gap = (
                LAB_AUDIO_TEST_BEEP_GAP_SECONDS
                if beep_index < LAB_AUDIO_TEST_BEEP_COUNT - 1
                else 0.0
            )
            time.sleep(duration + gap)
        return True
    except (pygame.error, FileNotFoundError):
        return False


def start_background_music(background_music_path, number_of_loops=0):
    """Start background music in the game."""
    if not ensure_mixer_initialized():
        print("Background music unavailable. Skipping playback.")
        return

    try:
        pygame.mixer.music.load(background_music_path)
        pygame.mixer.music.play(loops=number_of_loops)
    except (pygame.error, FileNotFoundError):
        print("Background music unavailable. Skipping playback.")


def stop_background_music():
    """Stop the running background music."""
    try:
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
    except pygame.error:
        pass
