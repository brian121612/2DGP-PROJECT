from pico2d import load_image

class Pannel:
    def __init__(self):
        self.image = load_image('manual.png')

    def draw(self):
        self.image.draw(1280//2, 720//2)

    def update(self):
        pass