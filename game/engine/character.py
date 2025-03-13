class Character:
    def __init__(self, is_player1=True):
        # Core properties remain the same
        self.position = (0, 0)
        self.velocity = [0, 0]
        self.health = 100
        # ...existing properties...
        
        # New animation system
        self.sprite_sheets = {}  # Character can use sprites
        self.animation_data = {} # Animation timing data
        self.current_frame = 0
        self.animation_speed_multiplier = 1.0
        
        # Customization options
        self.color_scheme = "default"
        self.available_color_schemes = {}
        self.outfit_variant = "default"
        self.available_outfits = {}
        
        # Character-specific sounds
        self.sound_effects = {}
        
        # Call initialization methods that subclasses will override
        self._init_animations()
        self._init_customization()
        self._init_sounds()
    
    # Methods that subclasses must implement
    def _init_animations(self):
        """Initialize animation data - must be implemented by subclass"""
        pass
        
    def _init_customization(self):
        """Initialize customization options - must be implemented by subclass"""
        pass
        
    def _init_sounds(self):
        """Initialize sound effects - must be implemented by subclass"""
        pass
        
    # New methods for animations
    def set_color_scheme(self, scheme_name):
        """Apply a color scheme by name"""
        if scheme_name in self.available_color_schemes:
            self.color_scheme = scheme_name
    
    def set_outfit(self, outfit_name):
        """Apply an outfit variant by name"""
        if outfit_name in self.available_outfits:
            self.outfit_variant = outfit_name