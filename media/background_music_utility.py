import pygame

def start_background_music(background_music_path,number_of_loops=0):
    """
    Utility function to start the background music in the game
    :param background_music_path: Path to the background music
    :param number_of_loops: Number of times, the background music needs to be played
    :return: None
    """
    pygame.mixer.init()
    pygame.mixer.music.load(background_music_path)
    pygame.mixer.music.play(loops=number_of_loops)

def stop_background_music():
    """
    Stops the running background music
    :return: None
    """
    pygame.mixer.music.stop()
    pygame.mixer.music.unload()
