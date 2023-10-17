import os
import pygame
from PIL import Image




# convert image from PIL to pygame surface image
def pil_image_to_surface(pil_image):
    return pygame.image.fromstring(pil_image.tobytes(), pil_image.size, pil_image.mode)

# returns surfaces for king in check (red outline) using pygame mask module
def outline_mask(image, outline_size):
    mask = pygame.mask.from_surface(image)

    mask_outline = mask.outline()
    i = 0

    max_width = 0
    max_height = 0

    for point in mask_outline:

        mask_outline[i] = (point[0] + outline_size[0], point[1] + outline_size[1])

        max_width = max(mask_outline[i][0], max_width)
        max_height = max(mask_outline[i][1], max_height)

        i += 1

    new_surface = pygame.Surface((max_width, max_height))

    pygame.draw.polygon(new_surface, CHECK_COLOR, mask_outline, 50)

    return new_surface



# boards
BOARD_BG = pygame.image.load(os.path.join("assets", "resources", "board background.jpg"))
NOTATION_SYSTEM = pygame.image.load(os.path.join("assets", "resources", "coordinate system.png"))

# check background
CHECK_BACKGROUND = pygame.image.load(os.path.join("assets", "resources", "check background.png"))

# pieces (standard)
preview_image = Image.open(os.path.join("assets", "resources", "pieces", "standard.png"))

# cropping of default preview picture to get individual pieces
WHITE_KING = pil_image_to_surface(preview_image.crop((1, 0, 259, 266)))
WHITE_QUEEN = pil_image_to_surface(preview_image.crop((321, 0, 607, 266)))
WHITE_BISHOP = pil_image_to_surface(preview_image.crop((669, 0, 925, 266)))
WHITE_KNIGHT = pil_image_to_surface(preview_image.crop((1003, 0, 1252, 266)))
WHITE_ROOK = pil_image_to_surface(preview_image.crop((1358, 0, 1570, 266)))
WHITE_PAWN = pil_image_to_surface(preview_image.crop((1703, 0, 1885, 266)))

BLACK_KING = pil_image_to_surface(preview_image.crop((1, 334, 259, 605)))
BLACK_QUEEN = pil_image_to_surface(preview_image.crop((321, 334, 607, 605)))
BLACK_BISHOP = pil_image_to_surface(preview_image.crop((669, 334, 926, 605)))
BLACK_KNIGHT = pil_image_to_surface(preview_image.crop((1003, 334, 1252, 605)))
BLACK_ROOK = pil_image_to_surface(preview_image.crop((1358, 334, 1570, 605)))
BLACK_PAWN = pil_image_to_surface(preview_image.crop((1703, 334, 1885, 605)))


# WHITE_KING_CHECK = outline_mask(WHITE_KING, (10, 10))
# BLACK_KING_CHECK = outline_mask(BLACK_KING, (10, 10))

# pygame.init()

# screen = pygame.display.set_mode(size=(800, 600))

# screen.blit(CHECK_BACKGROUND, (0, 0))
# screen.blit(WHITE_KING, (0, 0))

# pygame.display.flip()

# run = True

# while run:
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             pygame.quit()
#             break