import pygame


class Player:
    def __init__(self, name):
        self.name = name
        self.x = 10
        self.y = 5
        self.vy = 0
        self.on_ground = False
        self.selected_block = 'dirt'
        self.inventory = []
        self.health = 100

    def update(self, world):
        keys = pygame.key.get_pressed()
        speed = 0.15
        if keys[pygame.K_LEFT]:
            if not world.get_block_at(int(self.x - 0.2), int(self.y)):
                self.x -= speed
        if keys[pygame.K_RIGHT]:
            if not world.get_block_at(int(self.x + 1), int(self.y)):
                self.x += speed
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vy = -0.35
            self.on_ground = False
        # Gravity
        self.vy += 0.02
        new_y = self.y + self.vy
        if world.get_block_at(int(self.x), int(new_y + 1)):
            self.y = int(new_y)
            self.vy = 0
            self.on_ground = True
        else:
            self.y = new_y
            self.on_ground = False

    def interact(self, block):
        # Placeholder for interaction logic
        pass

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0

    def heal(self, amount):
        self.health += amount
        if self.health > 100:
            self.health = 100

    def add_to_inventory(self, item):
        self.inventory.append(item)

    def remove_from_inventory(self, item):
        if item in self.inventory:
            self.inventory.remove(item)

    def place_block(self, world):
        tx, ty = int(self.x), int(self.y + 1)
        if not world.get_block_at(tx, ty):
            world.add_block(tx, ty, self.selected_block)

    def remove_block(self, world):
        tx, ty = int(self.x), int(self.y + 1)
        if world.get_block_at(tx, ty):
            world.remove_block(tx, ty)