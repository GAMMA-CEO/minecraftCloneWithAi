from ursina import Ursina, Button, Entity, color, scene, mouse, destroy, Sky, Text, held_keys, camera, application, invoke
from ursina.prefabs.first_person_controller import FirstPersonController
import time
from ctypes import cdll, c_char_p
import os
from ursina.shaders import lit_with_shadows_shader
from random import randint
from perlin_noise import PerlinNoise
from math import sin, pi

app = Ursina()

block_types = {
    'dirt': 'white_cube',
    'grass': 'grass',
    'stone': 'brick'
}

mode = 'build'  # Modes: 'build' or 'explore'
mode_text = Text(
    text=f'Mode: {mode.title()}',
    origin=(-.5,-.5),  # Top-left corner
    scale=1.5,
    background=True,
    position=(-.45, .45)
)

fly_enabled = False
last_space_time = 0

sky = Sky()

CHUNK_SIZE = 16
RENDER_DISTANCE = 3  # in chunks
WORLD_HEIGHT = 16

SEED = randint(0, 10000)
noise = PerlinNoise(octaves=3, seed=SEED)

class Chunk:
    def __init__(self, chunk_x, chunk_z, noise, block_types):
        self.chunk_x = chunk_x
        self.chunk_z = chunk_z
        self.voxels = {}
        self.entities = {}
        for x in range(CHUNK_SIZE):
            for z in range(CHUNK_SIZE):
                wx = chunk_x * CHUNK_SIZE + x
                wz = chunk_z * CHUNK_SIZE + z
                n = noise([wx / 20, wz / 20])
                height = int(n * (WORLD_HEIGHT // 2) + (WORLD_HEIGHT // 2))
                for y in range(-2, height):
                    if y == height - 1:
                        block_type = 'grass'
                    elif y > height - 4:
                        block_type = 'dirt'
                    else:
                        block_type = 'stone'
                    self.voxels[(x, y, z)] = block_type

    def show(self, block_types):
        for (x, y, z), block_type in self.voxels.items():
            pos = (self.chunk_x * CHUNK_SIZE + x, y, self.chunk_z * CHUNK_SIZE + z)
            if pos not in self.entities:
                self.entities[pos] = Voxel(position=pos, block_type=block_type)

    def hide(self):
        for entity in self.entities.values():
            destroy(entity)
        self.entities.clear()

chunks = {}
loaded_chunks = set()

def chunk_coords(x, z):
    return int(x // CHUNK_SIZE), int(z // CHUNK_SIZE)

def update_chunks():
    px, py, pz = first_person.position
    cx, cz = chunk_coords(px, pz)
    # Load new chunks
    for dx in range(-RENDER_DISTANCE, RENDER_DISTANCE+1):
        for dz in range(-RENDER_DISTANCE, RENDER_DISTANCE+1):
            chunk_pos = (cx + dx, cz + dz)
            if chunk_pos not in loaded_chunks:
                if chunk_pos not in chunks:
                    chunks[chunk_pos] = Chunk(chunk_pos[0], chunk_pos[1], noise, block_types)
                chunks[chunk_pos].show(block_types)  # Remove voxel_shader argument
                loaded_chunks.add(chunk_pos)
    # Unload far chunks
    to_unload = []
    for chunk_pos in loaded_chunks:
        if abs(chunk_pos[0] - cx) > RENDER_DISTANCE or abs(chunk_pos[1] - cz) > RENDER_DISTANCE:
            chunks[chunk_pos].hide()
            to_unload.append(chunk_pos)
    for chunk_pos in to_unload:
        loaded_chunks.remove(chunk_pos)

class Voxel(Button):
    def __init__(self, position=(0,0,0), block_type='grass'):
        super().__init__(
            parent=scene,
            position=position,
            model='cube',
            origin_y=0.5,
            texture=block_types.get(block_type, 'white_cube'),
            color=color.white,
            highlight_color=color.azure,
            shader=lit_with_shadows_shader  # Use GPU-accelerated shader
        )
        self.block_type = block_type
        self.default_color = color.white

    def input(self, key):
        global mode
        if self.hovered and mode == 'build':
            if key == 'left mouse down':
                Voxel(self.position + mouse.normal, player.selected_block)
            if key == 'right mouse down':
                destroy(self)

    def update(self):
        # Highlight block when hovered
        if self.hovered and mode == 'build':
            self.color = color.orange
        else:
            self.color = self.default_color

class Player(Entity):
    def __init__(self):
        super().__init__()
        self.selected_block = 'dirt'

player = Player()

first_person = FirstPersonController()
first_person.cursor.visible = True

instructions = Text(
    text='1: Dirt  2: Grass  3: Stone\nLeft Click: Place  Right Click: Remove\nWASD: Move  Mouse: Look\nDouble Space: Fly (Build Mode)',
    origin=(0,8),
    scale=1.5,
    background=True
)

cpp_fun_message = ''
def get_cpp_message(mode):
    try:
        lib_path = os.path.join(os.path.dirname(__file__), 'fun_message.dll')
        fun_lib = cdll.LoadLibrary(lib_path)
        fun_lib.get_fun_message.restype = c_char_p
        fun_lib.get_fun_message.argtypes = [c_char_p]
        return fun_lib.get_fun_message(mode.encode('utf-8')).decode('utf-8')
    except Exception as e:
        return f'C++ fun message not loaded. ({mode})'

cpp_text = Text(
    text=get_cpp_message(mode),
    origin=(-.5, 0),
    scale=1.2,
    background=True,
    position=(-.45, .38),
    color=color.yellow
)

def input(key):
    global mode, fly_enabled, last_space_time
    if key == '1':
        player.selected_block = 'dirt'
    elif key == '2':
        player.selected_block = 'grass'
    elif key == '3':
        player.selected_block = 'stone'
    elif key == 'c':
        mode = 'explore' if mode == 'build' else 'build'
        mode_text.text = f'Mode: {mode.title()}'
        cpp_text.text = get_cpp_message(mode)
        if mode == 'explore':
            fly_enabled = False
    elif key == 'space':
        now = time.time()
        if mode == 'build' and now - last_space_time < 0.3:
            fly_enabled = not fly_enabled
            if fly_enabled:
                mode_text.text = f'Mode: {mode.title()} (Fly)'
            else:
                mode_text.text = f'Mode: {mode.title()}'
        last_space_time = now
    elif key == 'tab':
        first_person.cursor.visible = not first_person.cursor.visible
        mouse.locked = not first_person.cursor.visible

from ursina import Button as UrsinaButton

game_started = False
loading = False
loading_text = None
menu_entities = []

def start_game():
    global game_started, loading, loading_text, menu_entities
    for e in menu_entities:
        destroy(e)
    menu_entities.clear()
    loading = True
    loading_text = Text(text='Loading world...', origin=(0,0), scale=2, background=True, color=color.white)
    invoke(finish_loading, delay=1.5)  # Simulate loading delay

def finish_loading():
    global game_started, loading, loading_text
    loading = False
    game_started = True
    if loading_text:
        destroy(loading_text)
        loading_text = None

# Title screen setup
menu_bg = Entity(parent=camera.ui, model='quad', scale=(2,1.2), color=color.dark_gray, z=1)
title_text = Text(text='Minecraft Clone', origin=(0,0), scale=3, y=0.2, background=True, color=color.azure)
start_btn = UrsinaButton(text='Start Game', color=color.lime, scale=(.3,.1), y=-0.1, on_click=start_game)
quit_btn = UrsinaButton(text='Quit', color=color.red, scale=(.3,.1), y=-0.25, on_click=application.quit)
menu_entities = [menu_bg, title_text, start_btn, quit_btn]

def update():
    global fly_enabled
    if not game_started:
        return
    if loading:
        return
    update_chunks()
    t = time.time() % 20
    # Animate sky color
    sky.color = color.rgb(
        int(100 + 100 * sin(t * pi / 20)),
        int(150 + 100 * sin(t * pi / 20)),
        int(255 * (0.5 + 0.5 * sin(t * pi / 20)))
    )
    if fly_enabled and mode == 'build':
        speed = 5 * time.dt
        if held_keys['left control']:
            first_person.y += speed
        if held_keys['left shift']:
            first_person.y -= speed

app.run()