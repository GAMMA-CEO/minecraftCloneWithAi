class TextureManager:
    def __init__(self):
        self.textures = {}

    def load_texture(self, name, filepath):
        from pyglet import image
        self.textures[name] = image.load(filepath)

    def get_texture(self, name):
        return self.textures.get(name)

    def unload_texture(self, name):
        if name in self.textures:
            del self.textures[name]

    def clear_textures(self):
        self.textures.clear()