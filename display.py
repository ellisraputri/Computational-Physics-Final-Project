import pygame
import numpy as np
from constant import *
from WaveSimulation import WaveSimulation

class Display:
    def __init__(self, screen):
        self.screen = screen
        self.selected_x, self.selected_y = None, None
        self.submitted = False
        self.x_text = ""
        self.y_text = ""
        
        grid_width = RIGHT_PANEL_X // 5  
        grid_height = SCREEN_HEIGHT // 5
        self.wave_sim = WaveSimulation(grid_size=(grid_width, grid_height))
        
        self.wave_scale = 1.0  
        self.color_mode = 'seismic' 

    def render(self):
        self.screen.fill(GAME_COLOR['BLUE'])
        pygame.draw.rect(self.screen, GAME_COLOR['BROWN'], 
                         (0, GROUND_Y, RIGHT_PANEL_X, SCREEN_HEIGHT - GROUND_Y))
        
        self._draw_right_panel()
        self._render_wave_sim()
        
        if self.selected_x is not None and self.selected_y is not None:
            if not self.submitted:
                pygame.draw.circle(self.screen, GAME_COLOR['WHITE'], (self.selected_x, self.selected_y), 6)
            else:
                pygame.draw.line(self.screen, GAME_COLOR['RED'], (self.selected_x - 8, self.selected_y - 8), (self.selected_x + 8, self.selected_y + 8), 4)
                pygame.draw.line(self.screen, GAME_COLOR['RED'], (self.selected_x + 8, self.selected_y - 8), (self.selected_x - 8, self.selected_y + 8), 4)


    def _draw_right_panel(self):
        font_title = pygame.font.Font(None, 32)
        font1 = pygame.font.Font(None, 24)
        
        pygame.draw.rect(self.screen, GAME_COLOR['WHITE'], 
                         (RIGHT_PANEL_X, 0, RIGHT_PANEL_WIDTH, SCREEN_HEIGHT))
        title_text = font_title.render("User Input", True, GAME_COLOR['BLACK'])
        self.screen.blit(title_text, (RIGHT_PANEL_X + 20, 20))

        coord_label = font1.render("Hypocenter Coordinates:", True, GAME_COLOR['BLACK'])
        self.screen.blit(coord_label, (RIGHT_PANEL_X + 20, 80))
        
        x_label = font1.render(f"X: {self.x_text}", True, GAME_COLOR['BLACK'])
        y_label = font1.render(f"Y: {self.y_text}", True, GAME_COLOR['BLACK'])
        self.screen.blit(x_label, (RIGHT_PANEL_X + 40, 120))
        self.screen.blit(y_label, (RIGHT_PANEL_X + 40, 150))
        
        button_text = "Reset" if self.submitted else "Start"
        button_color = GAME_COLOR['RED'] if self.submitted else GAME_COLOR['GREEN']
        pygame.draw.rect(self.screen, button_color, 
                        (RIGHT_PANEL_X + 40, 200, 200, 40))
        text = font1.render(button_text, True, GAME_COLOR['WHITE'])
        self.screen.blit(text, (RIGHT_PANEL_X + 80, 210))

    def _render_wave_sim(self):
        for i in range(self.wave_sim.nx):
            for j in range(self.wave_sim.ny):
                # Get normalized wave value (-1 to 1)
                value = self.wave_sim.u[i, j] * self.wave_scale
                value = max(-1, min(1, value))  # Clamp to [-1, 1]
                
                # Convert to color based on mode
                if self.color_mode == 'seismic':
                    # Red-blue seismic color scheme
                    if value > 0:
                        color = (255, int(255*(1-value)), int(255*(1-value)))
                    else:
                        color = (int(255*(1+value)), int(255*(1+value)), 255)
                # Draw the cell (5px per grid cell)
                pygame.draw.rect(self.screen, color, (i*5, j*5, 5, 5))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            
            if x < RIGHT_PANEL_X and y < SCREEN_HEIGHT:
                if not self.submitted:
                    self.selected_x, self.selected_y = x, y
                    self.x_text, self.y_text = str(x), str(y)
                    self.wave_sim = WaveSimulation(
                        grid_size=(RIGHT_PANEL_X//5, SCREEN_HEIGHT//5))
                    self.wave_sim.set_source(x, y)
            
            elif (RIGHT_PANEL_X + 40 <= x <= RIGHT_PANEL_X + 240 and 
                  200 <= y <= 240):
                self.submitted = not self.submitted
                if not self.submitted:
                    self.selected_x, self.selected_y = None, None
                    self.x_text, self.y_text = "", ""
                    self.wave_sim = WaveSimulation(
                        grid_size=(RIGHT_PANEL_X//5, SCREEN_HEIGHT//5))


    def update(self):
        if self.submitted:
            self.wave_sim.update_wave()