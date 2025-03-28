import pygame
from constant import *

class Display:
    def __init__(self, screen):
        self.screen = screen
        self.selected_x, self.selected_y = None, None
        self.submitted = False
        self.x_text = ""
        self.y_text = ""
    
    def render(self):
        font_title = pygame.font.Font(None, 32)
        font1 = pygame.font.Font(None, 24)

        self.screen.fill(GAME_COLOR['BLUE'])  # Background color
        pygame.draw.rect(self.screen, GAME_COLOR['BROWN'], (0, GROUND_Y, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_Y))
        
        # Right panel
        pygame.draw.rect(self.screen, GAME_COLOR['WHITE'], (RIGHT_PANEL_X, 0, RIGHT_PANEL_WIDTH, SCREEN_HEIGHT))
        title_text = font_title.render("User Input", True, GAME_COLOR['BLACK'])
        self.screen.blit(title_text, (RIGHT_PANEL_X + 130, 17))

        coord_label = font1.render("Choose a hypocenter:", True, GAME_COLOR['BLACK'])
        self.screen.blit(coord_label, (RIGHT_PANEL_X + 20, 80))

        x_label = font1.render("X:", True, GAME_COLOR['BLACK'])
        self.screen.blit(x_label, (RIGHT_PANEL_X + 20, 120))
        y_label = font1.render("Y:", True, GAME_COLOR['BLACK'])
        self.screen.blit(y_label, (RIGHT_PANEL_X + 120, 120))

        # Entry fields
        entry_color = GAME_COLOR['WHITE'] if self.submitted else GAME_COLOR['GRAY']
        pygame.draw.rect(self.screen, entry_color, (RIGHT_PANEL_X + 50, 115, 50, 30))
        pygame.draw.rect(self.screen, entry_color, (RIGHT_PANEL_X + 150, 115, 50, 30))
        
        x_text_render = font1.render(self.x_text, True, GAME_COLOR['BLACK'])
        y_text_render = font1.render(self.y_text, True, GAME_COLOR['BLACK'])
        self.screen.blit(x_text_render, (RIGHT_PANEL_X + 55, 120))
        self.screen.blit(y_text_render, (RIGHT_PANEL_X + 155, 120))

        # Hypocenter marker
        if self.selected_x is not None and self.selected_y is not None:
            if not self.submitted:
                pygame.draw.circle(self.screen, GAME_COLOR['WHITE'], (self.selected_x, self.selected_y), 6)
            else:
                pygame.draw.line(self.screen, GAME_COLOR['RED'], (self.selected_x - 8, self.selected_y - 8), (self.selected_x + 8, self.selected_y + 8), 4)
                pygame.draw.line(self.screen, GAME_COLOR['RED'], (self.selected_x + 8, self.selected_y - 8), (self.selected_x - 8, self.selected_y + 8), 4)

        # Submit button
        submit_text = "Cancel" if self.submitted else "Save"
        button_color = GAME_COLOR['GRAY'] if self.submitted else GAME_COLOR['GREEN']
        pygame.draw.rect(self.screen, button_color, (RIGHT_PANEL_X + 230, 115, 100, 30))
        text = font1.render(submit_text, True, GAME_COLOR['BLACK'])
        self.screen.blit(text, (RIGHT_PANEL_X + 255, 120))
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if y > GROUND_Y and x < RIGHT_PANEL_X and not self.submitted: 
                self.selected_x, self.selected_y = x, y
                self.x_text, self.y_text = str(x), str(y)

            elif RIGHT_PANEL_X + 230 <= x <= RIGHT_PANEL_X + 330 and 115 <= y <= 145:
                self.submitted = not self.submitted
                print(f"Selected: x={self.selected_x}, y={self.selected_y}")
