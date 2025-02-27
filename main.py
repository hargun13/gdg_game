from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random

app = Ursina()
mouse.visible = False

# Load Sounds
npc_appear_sound = Audio('assets/scare_sound.mp3', autoplay=False)
footstep_sound = Audio('assets/footstep.mp3', autoplay=False, loop=False)
jumpscare_sound = Audio('assets/jumpscare.mp3', autoplay=False)

# Jumpscare Screen (Hidden by Default)
jumpscare_image = Entity(
    model='quad',
    texture='assets/jumpscare_image.jpg',  # Scary face image
    scale=(2, 1),
    color=color.white,
    enabled=False  # Start disabled
)

# Corridor Setup
class CorridorSegment(Entity):
    def __init__(self, z_offset):
        super().__init__()
        self.z_offset = z_offset
        self.create_corridor()

    def create_corridor(self):
        self.floor = Entity(model='cube', position=(0, 0, self.z_offset), scale=(10, 1, 20), color=color.gray, collider='box')
        self.ceiling = Entity(model='cube', position=(0, 10, self.z_offset), scale=(10, 1, 20), color=color.gray, collider='box')
        self.left_wall = Entity(model='cube', position=(-5, 5, self.z_offset), scale=(1, 10, 20), collider='box', texture='assets/wall.jpg')
        self.right_wall = Entity(model='cube', position=(5, 5, self.z_offset), scale=(1, 10, 20), collider='box', texture='assets/wall.jpg')

    def flicker_effect(self):
        """Makes textures flicker randomly"""
        if random.random() < 0.02:
            new_texture = 'assets/wall_glitch.jpg' if random.random() < 0.5 else 'assets/wall.jpg'
            self.left_wall.texture = new_texture
            self.right_wall.texture = new_texture

# Generate corridor
corridor_segments = [CorridorSegment(i * 20) for i in range(-2, 3)]

# Player
player = FirstPersonController()
player.cursor.visible = False
player.gravity = 0.5
player.speed = 10

# NPC Class (Creepy Effects)
class NPC(Entity):
    def __init__(self):
        super().__init__(position=(random.choice([-2, 2]), 0, random.randint(10, 30)), collider='box')
        self.model = Entity(model='assets/npc.glb', parent=self, scale=1.5)
        self.visible = False
        self.timer = 0
        self.active = False
        self.speed = 1
        self.flicker_timer = 0

    def update_behavior(self):
        if self.active:
            self.timer += time.dt
            self.flicker_timer += time.dt

            # Move NPC towards the player
            direction = (player.position - self.position).normalized()
            self.position += direction * self.speed * time.dt

            # Flicker effect
            if self.flicker_timer > random.uniform(0.2, 1.0):
                self.visible = not self.visible
                self.flicker_timer = 0

            # Jumpscare if NPC is too close
            if distance(self.position, player.position) < 1.5:
                trigger_jumpscare()

            # NPC disappears after a while
            if self.timer > random.randint(5, 10):
                self.hide_npc()

    def show_npc(self):
        """NPC appears at a random location"""
        self.position = (random.choice([-2, 2]), 0, player.z + random.randint(10, 30))
        self.visible = True
        self.active = True
        self.timer = 0
        self.flicker_timer = 0
        npc_appear_sound.play()
        print("NPC appeared!")

    def hide_npc(self):
        """Hides the NPC"""
        self.visible = False
        self.active = False
        print("NPC disappeared!")

npc = NPC()

# Trigger Jumpscare
def trigger_jumpscare():
    print("Jumpscare triggered!")
    jumpscare_sound.play()
    jumpscare_image.enabled = True
    invoke(reset_game, delay=2)  # Reset after 2 seconds

# Reset Game
def reset_game():
    print("Resetting game...")
    player.position = Vec3(0, 1, 0)  # Reset player
    npc.hide_npc()
    jumpscare_image.enabled = False

# Update function
def update():
    global corridor_segments

    # Move corridor segments forward to create infinite loop
    for segment in corridor_segments:
        if player.z - segment.z_offset > 30:
            segment.z_offset += 100
            segment.floor.z = segment.z_offset
            segment.ceiling.z = segment.z_offset
            segment.left_wall.z = segment.z_offset
            segment.right_wall.z = segment.z_offset

        # Flickering effect on walls
        segment.flicker_effect()

    # NPC behavior update
    if not npc.active and random.random() < 0.01:
        npc.show_npc()

    npc.update_behavior()

    # Footstep sound
    if held_keys['w'] or held_keys['a'] or held_keys['s'] or held_keys['d']:
        if not footstep_sound.playing:
            footstep_sound.play()

app.run()
