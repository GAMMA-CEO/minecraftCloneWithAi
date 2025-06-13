import pygame

class Renderer:
    def __init__(self, screen, block_size=40):
        self.screen = screen
        self.block_size = block_size

    def render(self, world, player):
        self.screen.fill((135, 206, 235))  # Sky blue background
        # Draw grid
        for x in range(world.width):
            for y in range(world.height):
                rect = pygame.Rect(x * self.block_size, y * self.block_size, self.block_size, self.block_size)
                pygame.draw.rect(self.screen, (200, 200, 200), rect, 1)
        # Draw blocks
        for block in world.blocks:
            pygame.draw.rect(
                self.screen,
                block.color,
                pygame.Rect(block.x * self.block_size, block.y * self.block_size, self.block_size, self.block_size)
            )
        # Draw player
        pygame.draw.rect(
            self.screen,
            (255, 0, 0),
            pygame.Rect(player.x * self.block_size, player.y * self.block_size, self.block_size, self.block_size)
        )

    def get_grid_pos(self, mouse_pos):
        mx, my = mouse_pos
        return mx // self.block_size, my // self.block_size