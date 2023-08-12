class GameStats:
    """Track statistics for Man VS Ghost."""
    
    def __init__(self, ai_game):
        """Initialize statistics."""
        self.settings = ai_game.settings 
        self.reset_stats()
        
        # Start Man VS Ghost in an inactive state.
        self.game_active = False
        
        # High score should never be reset.
        self.high_score = 0
        
    def reset_stats(self):
        """Initialize statistics that can change during the game."""
        self.mans_left = self.settings.man_limit
        self.score = 0
        self.level = 1
             