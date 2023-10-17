import pygame

pygame.init()

screen = pygame.display.set_mode(size=(800, 600))

surface = pygame.Surface((500, 300))
surface.fill((255, 0, 0))

surface1 = pygame.Surface((400, 300))
surface1.fill((255, 0, 255))


screen.blits(blit_sequence=[(surface, (50, 50)), (surface1, (screen.get_rect().center))])
screen.render("kokot", (255, 255, 0))

pygame.display.flip()

run = True

while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            break