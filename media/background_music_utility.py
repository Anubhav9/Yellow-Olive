import pygame

def start_background_music(background_music_path, number_of_loops=0):
    """
    Utility function to start the background music in the game
    """
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(background_music_path)
        pygame.mixer.music.play(loops=number_of_loops)
    except pygame.error:
        print("Audio device not available. Skipping background music.")


def stop_background_music():
    """
    Stops the running background music
    """
    try:
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
    except pygame.error:
        pass
