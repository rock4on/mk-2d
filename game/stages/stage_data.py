"""
Defines data for all available stages.

Each stage has the following properties:
- color: Background color (R, G, B)
- floor: Y coordinate of the floor
- gravity: Gravity strength (affects jump physics)
- weather: Weather effect (can be None, "rain", "snow", "sandstorm")
"""

STAGE_DATA = {
    "dojo": {
        "color": (100, 50, 50),
        "floor": 450,
        "gravity": 0.8,
        "weather": None,
        "description": "A traditional dojo with wooden floors and hanging scrolls."
    },
    "forest": {
        "color": (40, 80, 40),
        "floor": 450,
        "gravity": 0.8,
        "weather": "rain",
        "description": "A lush forest clearing with soft ground and swaying trees."
    },
    "temple": {
        "color": (70, 70, 90),
        "floor": 450,
        "gravity": 0.8,
        "weather": None,
        "description": "An ancient stone temple with mystical energy."
    },
    "arena": {
        "color": (200, 180, 140),
        "floor": 450,
        "gravity": 0.8,
        "weather": "snow",
        "description": "A grand battle arena with stone columns and a cheering crowd."
    },
    "volcano": {
        "color": (60, 20, 20),
        "floor": 450,
        "gravity": 0.9,  # Higher gravity due to volcanic pressure
        "weather": "sandstorm",
        "description": "The edge of an active volcano with molten lava and falling ash."
    },
    "cliff": {
        "color": (100, 100, 150),
        "floor": 450,
        "gravity": 0.85,
        "weather": "rain",
        "description": "A precarious cliff edge with dangerous drops and gusting winds."
    },
    "dunes": {
        "color": (220, 200, 170),
        "floor": 450,
        "gravity": 0.75,  # Lower gravity (sand gives way)
        "weather": "sandstorm",
        "description": "Shifting desert sands that change with each battle."
    },
    "ice": {
        "color": (200, 220, 255),
        "floor": 450,
        "gravity": 0.8,
        "weather": "snow",
        "description": "A frozen lake with slippery footing and deep blue ice."
    }
}

# Default stage properties if a specific stage isn't found
DEFAULT_STAGE = {
    "color": (50, 50, 80),
    "floor": 450,
    "gravity": 0.8,
    "weather": None,
    "description": "A standard battle zone."
}
