import os
import pygame



pygame.mixer.init()

if False:
    # recorded move sounds
    path = os.path.join("assets", "resources", "sounds", "recorded sounds")

    MOVE_SOUND = pygame.mixer.Sound(os.path.join(path, "move.wav"))
    CAPTURE_SOUND = pygame.mixer.Sound(os.path.join(path, "capture.wav"))
    CASTLE_SOUND = pygame.mixer.Sound(os.path.join(path, "castle.wav"))
    CHECK_SOUND = MOVE_SOUND
    MATCH_END_SOUND = None

else:
    # downloaded move sounds from https://github.com/ornicar/lila/tree/master/public/sound/standard (Lichess.org)
    path = os.path.join("assets", "resources", "sounds", "downloaded sounds")

    MOVE_SOUND = pygame.mixer.Sound(os.path.join(path, "move.wav"))
    CAPTURE_SOUND = pygame.mixer.Sound(os.path.join(path, "capture.wav"))
    CASTLE_SOUND = MOVE_SOUND
    CHECK_SOUND = MOVE_SOUND
    MATCH_END_SOUND = pygame.mixer.Sound(os.path.join(path, "game end.wav"))


