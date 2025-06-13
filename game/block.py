class Block:
    COLORS = {
        'dirt': (139, 69, 19),
        'grass': (34, 139, 34),
        'stone': (120, 120, 120)
    }

    def __init__(self, x, y, block_type='dirt'):
        self.x = x
        self.y = y
        self.block_type = block_type
        self.color = Block.COLORS.get(block_type, (139, 69, 19))

    def update(self):
        pass  # Placeholder for future block behavior updates