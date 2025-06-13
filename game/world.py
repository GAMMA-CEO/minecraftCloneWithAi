from .block import Block

class World:
    def __init__(self, width=20, height=15):
        self.width = width
        self.height = height
        self.blocks = []
        self.generate_world()

    def generate_world(self):
        self.blocks = []
        for x in range(self.width):
            for y in range(self.height):
                if y == self.height - 1:
                    block_type = 'grass'
                elif y > self.height - 4:
                    block_type = 'dirt'
                else:
                    block_type = 'stone'
                self.blocks.append(Block(x, y, block_type))

    def render(self, renderer):
        # Render the blocks in the world
        for block in self.blocks:
            block.render(renderer)

    def get_block_at(self, x, y):
        for block in self.blocks:
            if block.x == x and block.y == y:
                return block
        return None

    def add_block(self, x, y, block_type='dirt'):
        if not self.get_block_at(x, y):
            self.blocks.append(Block(x, y, block_type))

    def remove_block(self, x, y):
        self.blocks = [b for b in self.blocks if not (b.x == x and b.y == y)]

    def update(self):
        pass  # Add world logic here