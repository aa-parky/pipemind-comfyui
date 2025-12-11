#!/usr/bin/env python3
"""
RPG Map Prompt Generator for z-image turbo

This script helps generate optimized prompts for creating RPG maps using
the z-image turbo model in ComfyUI. It guides users through the process
of building effective prompts based on map type and desired features.
"""

import sys
from typing import Dict, List, Optional


class MapPromptGenerator:
    """Generates optimized prompts for RPG map creation."""

    MAP_TYPES = {
        "world": "World/Continent Map",
        "regional": "Regional/Local Area Map",
        "battle": "Battle/Encounter Map",
        "dungeon": "Dungeon/Interior Map"
    }

    THEMES = {
        "high-fantasy": "High Fantasy",
        "dark-fantasy": "Dark Fantasy",
        "sci-fi": "Science Fiction",
        "cyberpunk": "Cyberpunk",
        "post-apoc": "Post-Apocalyptic",
        "horror": "Horror",
        "steampunk": "Steampunk",
        "wuxia": "Eastern/Wuxia"
    }

    def __init__(self):
        self.map_type: Optional[str] = None
        self.theme: Optional[str] = None
        self.elements: List[str] = []
        self.style: Optional[str] = None
        self.atmosphere: Optional[str] = None
        self.colors: Optional[str] = None

    def get_map_type(self) -> str:
        """Prompt user for map type."""
        print("\n=== RPG Map Prompt Generator ===\n")
        print("Map Types:")
        for key, name in self.MAP_TYPES.items():
            print(f"  {key}: {name}")

        while True:
            choice = input("\nSelect map type: ").strip().lower()
            if choice in self.MAP_TYPES:
                self.map_type = choice
                return choice
            print("Invalid choice. Please try again.")

    def get_theme(self) -> str:
        """Prompt user for theme."""
        print("\nThemes:")
        for key, name in self.THEMES.items():
            print(f"  {key}: {name}")

        while True:
            choice = input("\nSelect theme (or press Enter for custom): ").strip().lower()
            if not choice:
                custom = input("Enter custom theme: ").strip()
                self.theme = custom
                return custom
            if choice in self.THEMES:
                self.theme = choice
                return choice
            print("Invalid choice. Please try again.")

    def get_world_map_details(self) -> List[str]:
        """Get details specific to world maps."""
        print("\n--- World Map Details ---")
        elements = []

        continents = input("Describe land masses/continents: ").strip()
        if continents:
            elements.append(continents)

        geography = input("Major geography (mountains, rivers, forests): ").strip()
        if geography:
            elements.append(geography)

        political = input("Kingdoms/regions (optional): ").strip()
        if political:
            elements.append(political)

        poi = input("Points of interest (optional): ").strip()
        if poi:
            elements.append(poi)

        return elements

    def get_regional_map_details(self) -> List[str]:
        """Get details specific to regional maps."""
        print("\n--- Regional Map Details ---")
        elements = []

        center = input("Central location/settlement: ").strip()
        if center:
            elements.append(center)

        terrain = input("Surrounding terrain: ").strip()
        if terrain:
            elements.append(terrain)

        features = input("Key features (roads, buildings, landmarks): ").strip()
        if features:
            elements.append(features)

        return elements

    def get_battle_map_details(self) -> List[str]:
        """Get details specific to battle maps."""
        print("\n--- Battle Map Details ---")
        elements = []

        # Size
        size = input("Map size (e.g., 40x40 feet) [default: 40x40]: ").strip()
        if not size:
            size = "40x40 feet"
        elements.append(size)

        # Grid
        grid = input("Grid type (square/hex) [default: square]: ").strip().lower()
        if not grid or grid == "square":
            elements.append("square grid with 5-foot squares")
        else:
            elements.append("hexagonal grid")

        setting = input("Setting/environment: ").strip()
        if setting:
            elements.append(setting)

        terrain = input("Terrain features (trees, rocks, water, etc.): ").strip()
        if terrain:
            elements.append(terrain)

        cover = input("Cover elements: ").strip()
        if cover:
            elements.append(cover)

        return elements

    def get_dungeon_map_details(self) -> List[str]:
        """Get details specific to dungeon maps."""
        print("\n--- Dungeon/Interior Map Details ---")
        elements = []

        structure = input("Structure type (cave, castle, dungeon, etc.): ").strip()
        if structure:
            elements.append(structure)

        layout = input("Layout description (rooms, corridors): ").strip()
        if layout:
            elements.append(layout)

        features = input("Key features (doors, furniture, traps, etc.): ").strip()
        if features:
            elements.append(features)

        grid = input("Include grid? (y/n) [default: y]: ").strip().lower()
        if grid != 'n':
            elements.append("square grid overlay")

        return elements

    def get_style(self) -> str:
        """Prompt user for style."""
        print("\n--- Style ---")

        if self.map_type == "world":
            styles = [
                "hand-drawn on aged parchment",
                "satellite view",
                "fantasy atlas",
                "antique map style"
            ]
        elif self.map_type == "regional":
            styles = [
                "illustrated adventure map",
                "hand-drawn parchment",
                "tactical overview",
                "isometric view"
            ]
        elif self.map_type == "battle":
            styles = [
                "optimized for virtual tabletop",
                "game board style",
                "realistic terrain",
                "miniature terrain style"
            ]
        else:  # dungeon
            styles = [
                "classic dungeon style",
                "detailed floor plan",
                "isometric view",
                "old-school RPG style"
            ]

        print("\nSuggested styles:")
        for i, style in enumerate(styles, 1):
            print(f"  {i}. {style}")

        choice = input("\nSelect style number or enter custom: ").strip()

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(styles):
                self.style = styles[idx]
                return styles[idx]
        except ValueError:
            pass

        self.style = choice
        return choice

    def get_atmosphere(self) -> str:
        """Prompt user for atmosphere/mood."""
        print("\n--- Atmosphere/Mood (optional) ---")
        atmosphere = input("Describe atmosphere (e.g., ominous, bright, foggy): ").strip()
        self.atmosphere = atmosphere if atmosphere else None
        return atmosphere

    def get_colors(self) -> str:
        """Prompt user for color scheme."""
        print("\n--- Color Scheme (optional) ---")
        colors = input("Color scheme (e.g., warm earth tones, neon colors): ").strip()
        self.colors = colors if colors else None
        return colors

    def build_prompt(self) -> str:
        """Build the final optimized prompt."""
        parts = []

        # Map type and perspective
        if self.map_type == "world":
            parts.append(f"{self.theme} world map")
            parts.append("top-down view")
        elif self.map_type == "regional":
            parts.append(f"{self.theme} regional map")
            parts.append("top-down view")
        elif self.map_type == "battle":
            parts.append(f"{self.theme} battle map")
            parts.append("top-down view")
        else:  # dungeon
            parts.append(f"{self.theme} dungeon map")
            parts.append("top-down view")

        # Add elements
        parts.extend(self.elements)

        # Add style
        if self.style:
            parts.append(self.style)

        # Add atmosphere
        if self.atmosphere:
            parts.append(self.atmosphere)

        # Add colors
        if self.colors:
            parts.append(self.colors)

        # Add quality tags
        if self.map_type == "battle":
            parts.extend([
                "high contrast",
                "clear for gameplay",
                "detailed textures",
                "game-ready quality"
            ])
        elif self.map_type == "dungeon":
            parts.extend([
                "clear and readable",
                "detailed but functional",
                "high quality"
            ])
        else:
            parts.extend([
                "detailed cartography",
                "clear and readable",
                "high quality"
            ])

        # Join with commas
        prompt = ", ".join(parts)
        return prompt

    def run_interactive(self) -> str:
        """Run the interactive prompt builder."""
        self.get_map_type()
        self.get_theme()

        # Get map-specific details
        if self.map_type == "world":
            self.elements = self.get_world_map_details()
        elif self.map_type == "regional":
            self.elements = self.get_regional_map_details()
        elif self.map_type == "battle":
            self.elements = self.get_battle_map_details()
        else:  # dungeon
            self.elements = self.get_dungeon_map_details()

        self.get_style()
        self.get_atmosphere()
        self.get_colors()

        prompt = self.build_prompt()

        print("\n" + "="*80)
        print("GENERATED PROMPT:")
        print("="*80)
        print(prompt)
        print("="*80)

        return prompt

    def save_prompt(self, prompt: str, filename: str = "map_prompt.txt"):
        """Save the prompt to a file."""
        try:
            with open(filename, 'w') as f:
                f.write(prompt)
            print(f"\nPrompt saved to {filename}")
        except Exception as e:
            print(f"\nError saving prompt: {e}")


def main():
    """Main entry point."""
    generator = MapPromptGenerator()
    prompt = generator.run_interactive()

    # Ask if user wants to save
    save = input("\nSave prompt to file? (y/n): ").strip().lower()
    if save == 'y':
        filename = input("Filename [map_prompt.txt]: ").strip()
        if not filename:
            filename = "map_prompt.txt"
        generator.save_prompt(prompt, filename)

    print("\nDone! Use this prompt with z-image turbo in ComfyUI.")


if __name__ == "__main__":
    main()
