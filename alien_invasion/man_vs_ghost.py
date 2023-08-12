import sys
from time import sleep

import pygame

from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button
from man import Man
from bullet import Bullet
from ghost import Ghost

class manvsghost:
    """Overall class to manage game assets and behavior."""
    
    def __init__(self):
        """Initialize the game and create game resources."""
        pygame.init()
        self.settings = Settings()
        
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        pygame.display.set_caption("Man VS Ghost")
        
        # Create an instance to store game statistics,
        # and create a scoreboard.
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)
                                  
        self.man = Man(self)
        self.bullets = pygame.sprite.Group()
        self.ghosts = pygame.sprite.Group()
        
        self._create_fleet()
        
        # Make the Play button.
        self.play_button = Button(self, "Play")
        
        # Set the background color.
        self.bg_color = (0, 204, 255)    
        
    def run_game(self):
        """Start the main loop for the game."""
        while True:
            self._check_events()
            
            if self.stats.game_active:
                self.man.update()
                self._update_bullets()
                self._update_ghosts()
                
            self._update_screen()
            
    def _update_bullets(self):
        """Update position of bullets and get rid of old bullets."""
        # Update bullet positions.        
        self.bullets.update()
            
        # Get rid of bullets that have disappeared.
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                    self.bullets.remove(bullet)
                    
        self._check_bullet_ghost_collisions()
        
    def _check_bullet_ghost_collisions(self):
        """Respond to bullet-ghost collisions."""
        # Remove any bullets and ghosts that have collided.                
                    
        collisions = pygame.sprite.groupcollide(self.bullets, self.ghosts, True, True)
        
        if collisions:
            for ghosts in collisions.values():
                self.stats.score += self.settings.ghost_points * len(ghosts)
            self.sb.prep_score()
        
        if not self.ghosts:
            # Destroy existing bullets and create new fleet.
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()
            
            # Increase level.
            self.stats.level += 1
            self.sb.prep_level()            
                    
    def _update_ghosts(self):
        """Check if the fleet is at an edge, then update the positions of all ghosts in the fleet."""
        self._check_fleet_edges()
        self.ghosts.update()
        
        # Look for ghost-man collisions.
        if pygame.sprite.spritecollideany(self.man, self.ghosts):
            self._man_hit()
            
        # Look for ghosts hitting the bottom of the screen.
        self._check_ghosts_bottom()    
            
    # Watch for keyboard and mouse events.
    def _check_events(self):
        """Respond to keypresses and mouse events."""        
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    self._check_keydown_events(event)
                elif event.type == pygame.KEYUP: 
                    self._check_keyup_events(event)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    self._check_play_button(mouse_pos)
                        
    def _check_play_button(self, mouse_pos):
        """Start a new game when the player clicks Play."""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
            
            # Reset the game settings.
            self.settings.initialize_dynamic_settings()
            
            # Reset the game statistics.
            self.stats.reset_stats()
            self.stats.game_active = True
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_mans()
            
            # Get rid of any remaining ghosts and bullets.
            self.ghosts.empty()
            self.bullets.empty()
            
            # Create a new fleet and center the ship.
            self._create_fleet()
            self.man.center_man()  
            
            # Hide the mouse cursor.
            pygame.mouse.set_visible(False)                 
                                     
    def _check_keydown_events(self, event):
        """Respond to keypresses."""
        if event.key == pygame.K_RIGHT:
            self.man.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.man.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()        
            
    def _check_keyup_events(self, event):
        """Respond to key releases."""
        if event.key == pygame.K_RIGHT:
            self.man.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.man.moving_left = False    
                                                                      
        # Move the man to the right.
        self.man.rect.x += 1
        
    def _fire_bullet(self):
        """Create a new bullet and add it to the bullets group."""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet (self)
            self.bullets.add(new_bullet)
            
                        
    def _update_screen(self):
        """Update images on screen, and flip to new screen."""                
        # redraw the screen during each pass through the loop.
        self.screen.fill(self.settings.bg_color)
        self.man.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.ghosts.draw(self.screen)
        
        # Draw the score information.
        self.sb.show_score() 
        
        # Draw the play button if the game is inactive. 
        if not self.stats.game_active:
            self.play_button.draw_button()           
                    
        # Make the most recently drawn screen visible.
        pygame.display.flip()
        
    def _create_fleet(self):
        """Create the fleet of ghosts."""
        # Create a ghost and find the number of ghosts in a row.
        # Spacing between each ghost is equal to one ghost width.
        ghost = Ghost(self)
        ghost_width, ghost_height = ghost.rect.size
        available_space_x = self.settings.screen_width - (2 * ghost_width)
        number_ghosts_x = available_space_x // (2 * ghost_width)
        
        # Determine the number of rows of ghosts that fit on the screen.
        man_height = self.man.rect.height
        available_space_y = (self.settings.screen_height - (3 * ghost_height) - man_height)
        number_rows = available_space_y // (2 * ghost_height)
        
        # Create the full fleet of ghosts.
        for row_number in range(number_rows):
            for ghost_number in range(number_ghosts_x):
                self._create_ghost(ghost_number, row_number)
            
    def _create_ghost(self, ghost_number, row_number):        
            """Create a ghost and place it in the row."""
            ghost = Ghost(self)
            ghost_width, ghost_height = ghost.rect.size
            ghost.x = ghost_width + 2 * ghost_width * ghost_number
            ghost.rect.x = ghost.x
            ghost.rect.y = ghost_height + 2 * ghost.rect.height * row_number
            self.ghosts.add(ghost)
            
    def _check_fleet_edges(self):
        """Respond appropriately if any ghosts have reached an edge."""
        for ghost in self.ghosts.sprites():
            if ghost.check_edges():
                self._change_fleet_direction()
                break
            
    def _change_fleet_direction(self):
        """Drop the entire fleet and change the fleet's direction."""
        for ghost in self.ghosts.sprites():
            ghost.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1
        
    def _man_hit(self):
        """Respond to the man being hit by a ghost."""
        if self.stats.mans_left > 0:
            # Decrement mans_left, and update scoreboard.
            self.stats.mans_left -= 1
            self.sb.prep_mans()
        
            # Get rid of any remaining ghosts and bullets.
            self.ghosts.empty()
            self.bullets.empty()
        
            # Create a new fleet and center the ship.
            self._create_fleet()
            self.man.center_man()
        
            # Pause 
            sleep(0.5) 
        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)
            
    def _check_ghosts_bottom(self):
        """Check if any ghosts have reached the bottom of the screen>"""
        screen_rect = self.screen.get_rect()
        for ghost in self.ghosts.sprites():
            if ghost.rect.bottom >= screen_rect.bottom:
                # Treat this the same as if the man got hit.
                self._man_hit()
                break                           
                
       
if __name__ == '__main__':
    # Make a game instance, and run the game.
    ai = manvsghost()
    ai.run_game()
    
                            