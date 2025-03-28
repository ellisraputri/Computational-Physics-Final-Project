import pygame, sys
from constant import *
from display import Display

class Simulator:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(GAME_NAME)
        self.clock = pygame.time.Clock()
        self.display = Display(self.screen)
    
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                self.display.handle_event(event)
            
            self.display.update()
            self.display.render()
            pygame.display.update()
            self.clock.tick(60)


if __name__ == "__main__":
    simulator = Simulator()
    simulator.run()
