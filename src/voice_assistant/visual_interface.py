import asyncio
import os
from collections import deque

import numpy as np
import pygame


class VisualInterface:
    def __init__(self, width=400, height=400):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Sketric Agent")

        # Load the app icon and create a grayscale version
        icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
        self.icon = pygame.image.load(icon_path)
        self.icon = pygame.transform.scale(self.icon, (200, 200))  # Scale to fit
        self.grayscale_icon = self.create_grayscale(self.icon)

        self.clock = pygame.time.Clock()
        self.is_active = False
        self.is_assistant_speaking = False
        self.energy_queue = deque(maxlen=50)  # Store last 50 energy values
        self.update_interval = 0.05  # Update every 50ms
        self.max_energy = 1.0  # Initial max energy value

        # Set the application icon for the dock
        pygame.display.set_icon(self.icon)

    def create_grayscale(self, image):
        """Convert an image to grayscale while preserving the alpha channel."""
        grayscale_image = pygame.Surface(image.get_size(), pygame.SRCALPHA)
        for x in range(image.get_width()):
            for y in range(image.get_height()):
                r, g, b, a = image.get_at((x, y))
                gray = int(0.3 * r + 0.59 * g + 0.11 * b)
                grayscale_image.set_at((x, y), (gray, gray, gray, a))
        return grayscale_image

    async def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False

        self.screen.fill((0, 0, 0))  # Black background

        # Determine which icon to display
        icon_to_display = (
            self.icon if self.is_active or self.is_assistant_speaking else self.grayscale_icon
        )

        # Draw the icon at the center of the screen
        icon_rect = icon_to_display.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(icon_to_display, icon_rect)

        pygame.display.flip()
        self.clock.tick(60)
        await asyncio.sleep(self.update_interval)
        return True

    def set_active(self, is_active):
        self.is_active = is_active

    def set_assistant_speaking(self, is_speaking):
        self.is_assistant_speaking = is_speaking

    def update_energy(self, energy):
        if isinstance(energy, np.ndarray):
            energy = np.mean(np.abs(energy))
        self.energy_queue.append(energy)

        # Update max_energy dynamically
        current_max = max(self.energy_queue)
        if current_max > self.max_energy:
            self.max_energy = current_max
        elif len(self.energy_queue) == self.energy_queue.maxlen:
            self.max_energy = max(self.energy_queue)

    def process_audio_data(self, audio_data: bytes):
        """Process and update audio energy for visualization."""
        audio_frame = np.frombuffer(audio_data, dtype=np.int16)
        energy = np.abs(audio_frame).mean()
        self.update_energy(energy)


async def run_visual_interface(interface):
    while True:
        if not await interface.update():
            break
