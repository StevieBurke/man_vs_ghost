import pygame
from pygame.sprite import Sprite

class Man(Sprite):
    """A class the manage the 'man' main character."""
    
    def __init__(self, ai_game):
        """Initialize the man and set his starting position."""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.screen_rect = ai_game.screen.get_rect()
        
        # Load the man's image and get its rect.
        self.image = pygame.image.load('images/man.bmp')
        self.rect = self.image.get_rect()
        
        # Set the man's starting point at the bottom center of the screen.
        self.rect.midbottom = self.screen_rect.midbottom
        
        # Store a decimal value for the man's horizontal position. 
        self.x = float(self.rect.x)
        
        # Movement flags
        self.moving_right = False
        self.moving_left = False
        
    def update(self):
        """Update the man's position based on the movement flags."""
        # Update the man's x value, not the rect.
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.x += self.settings.man_speed    
        if self.moving_left and self.rect.left > 0:
            self.x -= self.settings.man_speed
            
        # Update rect object from self.x.
        self.rect.x = self.x    
            
    def blitme(self):
        """Draw the man at its current location."""
        self.screen.blit(self.image, self.rect)
        
    def center_man(self):
        """Center the man on the screen."""
        self.rect.midbottom = self.screen_rect.midbottom
        self.x = float(self.rect.x)     
           