# Todo
# - upload to Git
# - upgrade to engine

import os
import arcade
import random

bg_star_color = (255, 255, 255, 95)
fg_star_color = [
    arcade.color.WHITE,
    arcade.color.BABY_BLUE,
    arcade.color.AQUA,
    arcade.color.BUFF,
    arcade.color.ALIZARIN_CRIMSON,
]


def create_starfield(
    batch: arcade.shape_list.ShapeElementList, color=bg_star_color, random_color=False
):
    for i in range(200):
        x = random.randint(0, 1600)
        y = random.randint(0, 600)
        w = random.randint(1, 3)
        h = random.randint(1, 3)
        if random_color:
            color = random.choice(fg_star_color)
        star = arcade.shape_list.create_rectangle_filled(x, y, w, h, color)
        batch.append(star)


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRAVITY = 1.0
MOVEMENT_SPEED = 8
JUMP_SPEED = 20
JUMPS = 2
CAMERA_PAN_SPEED = 0.3

window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, "Sidecroller Demo")


class Player(arcade.Sprite):
    def __init__(self, animations: dict[str, list[arcade.Texture]]):
        super().__init__(animations["idle"][0])
        self.animations = animations
        self.textures = animations["idle"]

        self.state = "idle"  # 'idle', 'walk', 'jump', 'fall', 'duck'
        self.on_ground = True
        self.time_since_ground = 0
        self.time_elapsed = 0
        self.frame_rate = 0.1
        # track key presses for horizontal movement + duck after jump
        self.key_pressed = {"left": False, "right": False, "down": False}
        self.last_key_pressed = None

        self.attacking = False
        self.attack_time = 0

    def set_state(self, new_state):
        if self.state != new_state:
            self.state = new_state
            self.textures = self.animations[new_state]
            self.cur_texture_index = 0
            self.set_texture(self.cur_texture_index)
            self.hit_box = arcade.hitbox.HitBox(
                self.texture.hit_box_points,
                (self.center_x, self.bottom + self.texture.height / 2.0),
            )

    def update(self, delta_time=1 / 60, *args, **kwargs) -> None:
        self.time_elapsed += delta_time
        if self.time_elapsed > self.frame_rate:
            if self.cur_texture_index < len(self.textures):
                self.cur_texture_index = (self.cur_texture_index + 1) % len(
                    self.textures
                )
                self.set_texture(self.cur_texture_index)

        if self.key_pressed["down"]:
            # duck only on ground
            if self.on_ground:
                self.change_x = 0
                self.set_state("duck")
        else:
            if self.state == "duck" and self.on_ground:
                self.set_state("idle")

        # horizontal movement based on which key was pressed last if both keys are pressed
        if self.key_pressed["left"] and (
            self.last_key_pressed == "left" or not self.key_pressed["right"]
        ):
            self.scale_x = -1.0
            if self.state != "duck":  # can't move while ducking
                self.change_x = -MOVEMENT_SPEED
                if not self.state in ("jump", "fall"):
                    self.set_state("walk")
        if self.key_pressed["right"] and (
            self.last_key_pressed == "right" or not self.key_pressed["left"]
        ):
            self.scale_x = 1.0
            if self.state != "duck":  # can't move while ducking
                self.change_x = MOVEMENT_SPEED
                if not self.state in ("jump", "fall"):
                    self.set_state("walk")

        if not self.key_pressed["left"] and not self.key_pressed["right"]:
            self.change_x = 0
            if self.state not in ("jump", "duck", "fall"):
                self.set_state("idle")

        if self.attacking:
            if self.attack_time < 30:
                self.attack_time += 1
            else:
                self.attacking = False
                self.attack_time = 0
                self.color = 255, 255, 255, 255

    def on_key_press(self, symbol, engine: arcade.PhysicsEnginePlatformer) -> None:
        if symbol == arcade.key.UP:
            # can jump from ground or duck
            if engine.can_jump():
                self.change_y = JUMP_SPEED
                self.set_state("jump")
                engine.increment_jump_counter()
                self.on_ground = False
        if symbol == arcade.key.DOWN:
            self.key_pressed["down"] = True
        if symbol == arcade.key.LEFT:
            self.key_pressed["left"] = True
            self.last_key_pressed = "left"
        if symbol == arcade.key.RIGHT:
            self.key_pressed["right"] = True
            self.last_key_pressed = "right"
        if symbol == arcade.key.SPACE and not self.attacking:
            self.attacking = True
            self.color = arcade.color.RED

    def on_key_release(self, symbol, engine: arcade.PhysicsEnginePlatformer) -> None:
        if symbol == arcade.key.LEFT:
            self.key_pressed["left"] = False
        if symbol == arcade.key.RIGHT:
            self.key_pressed["right"] = False
        if symbol == arcade.key.DOWN:
            self.key_pressed["down"] = False


class GameView(arcade.View):
    def __init__(self) -> None:
        super().__init__()
        self.fg_star_speed = 0.6
        self.bg_star_speed = 0.8

        self.fg_stars = arcade.shape_list.ShapeElementList()
        create_starfield(self.fg_stars, random_color=True)

        self.bg_stars = arcade.shape_list.ShapeElementList()
        create_starfield(self.bg_stars)

        self.start_x = SCREEN_WIDTH // 2
        self.start_y = 100
        self.sprites = arcade.SpriteList()
        walk = []
        for filename in sorted(os.listdir("assets/images/walk")):
            walk.append(arcade.load_texture("assets/images/walk" + "/" + filename))
        # walk = arcade.load_spritesheet("assets/images/p1_walk.png").get_texture_grid(size=(72, 97), columns=3, count=11)
        # ^^^ p1_walk.png doesn't have the images in an even grid ^^^
        animations = {
            "idle": [arcade.load_texture("assets/images/p1_stand.png")],
            "walk": walk,
            "duck": [arcade.load_texture("assets/images/p1_duck.png")],
            "jump": [arcade.load_texture("assets/images/p1_jump.png")],
            "fall": [arcade.load_texture("assets/images/p1_fall.png")],
        }
        self.player = Player(animations)
        self.player.position = self.start_x, self.start_y
        self.sprites.append(self.player)

        self.ground_list = arcade.SpriteList()
        ground = arcade.SpriteSolidColor(
            width=SCREEN_WIDTH * 2,
            height=40,
            center_x=SCREEN_WIDTH,
            center_y=20,
            color=arcade.color.YELLOW,
        )
        floor1 = arcade.SpriteSolidColor(
            width=300, height=40, center_x=600, center_y=200, color=arcade.color.YELLOW
        )
        floor2 = arcade.SpriteSolidColor(
            width=300, height=40, center_x=1200, center_y=300, color=arcade.color.YELLOW
        )
        self.ground_list.append(ground)
        self.ground_list.append(floor1)
        self.ground_list.append(floor2)

        self.enemy_list = arcade.SpriteList()
        enemy1 = arcade.Sprite(
            ":resources:/images/enemies/slimeBlock.png",
            scale=0.5,
            center_x=1500,
            center_y=72,
        )
        enemy2 = arcade.Sprite(
            ":resources:/images/enemies/slimeBlock.png",
            scale=0.5,
            center_x=900,
            center_y=72,
        )
        self.enemy_list.append(enemy1)
        self.enemy_list.append(enemy2)

        self.coin_list = arcade.SpriteList()
        coin1 = arcade.Sprite(
            ":resources:/images/items/gold_1.png",
            scale=0.7,
            center_x=enemy1.center_x + 60,
            center_y=72,
        )
        coin2 = arcade.Sprite(
            ":resources:/images/items/gold_1.png",
            scale=0.7,
            center_x=floor2.center_x + 100,
            center_y=floor2.center_y + 52,
        )
        self.coin_list.append(coin1)
        self.coin_list.append(coin2)

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player, self.ground_list, gravity_constant=GRAVITY
        )
        self.physics_engine.enable_multi_jump(JUMPS)

        self.left_edge = self.player.width / 2.0
        self.right_edge = ground.width - self.player.width / 2.0

        self.camera = arcade.Camera2D()
        self.camera_bounds = arcade.LRBT(
            SCREEN_WIDTH / 2.0,
            3.0 * SCREEN_WIDTH / 2.0,
            SCREEN_HEIGHT / 2.0,
            SCREEN_HEIGHT / 2.0,
        )

    def on_draw(self) -> None:
        self.camera.use()
        self.clear()
        self.bg_stars.draw()
        self.fg_stars.draw()
        self.sprites.draw()
        self.ground_list.draw()
        self.enemy_list.draw()
        self.coin_list.draw()
        # self.sprites.draw_hit_boxes(arcade.color.WHITE)
        # self.enemy_list.draw_hit_boxes(arcade.color.WHITE)
        # self.coin_list.draw_hit_boxes(arcade.color.WHITE)

    def on_update(self, delta_time) -> None:
        self.player.update(delta_time)
        self.physics_engine.update()

        self.player.center_x = arcade.math.clamp(
            self.player.center_x, self.left_edge, self.right_edge
        )

        # check for falling
        if (
            self.player.on_ground
            and self.player.change_y < 0
            and self.player.state == "walk"
        ):
            self.player.set_state("fall")
            self.player.on_ground = False
            self.physics_engine.jumps_since_ground = 1
        # check if player is on ground properly
        if not self.player.on_ground:
            if self.player.state in ("jump", "fall") and self.player.change_y == 0:
                if self.player.time_since_ground >= 2:
                    if abs(self.player.change_x) > 0:
                        self.player.set_state("walk")
                    else:
                        self.player.set_state("idle")
                    self.player.on_ground = True
                    self.player.time_since_ground = 0
                else:
                    self.player.time_since_ground += 1

        enemy_hit = arcade.check_for_collision_with_list(self.player, self.enemy_list)
        if enemy_hit:
            if not self.player.attacking:
                self.player.position = self.start_x, self.start_y
            else:
                self.enemy_list.remove(enemy_hit[0])

        coin_hit = arcade.check_for_collision_with_list(self.player, self.coin_list)
        if coin_hit:
            self.coin_list.remove(coin_hit[0])

        # save old position for parallax scrolling
        old_postion = self.camera.position
        self.pan_camera_to_player(CAMERA_PAN_SPEED)
        self.parallax_scroll(old_postion)

    def parallax_scroll(self, old_postion) -> None:
        position_difference = self.camera.position - old_postion
        self.fg_stars.center_x += position_difference.x * self.fg_star_speed
        self.bg_stars.center_x += position_difference.x * self.bg_star_speed

    def pan_camera_to_player(self, panning_fraction: float = 1.0) -> None:
        self.camera.position = arcade.math.smerp_2d(
            self.camera.position,
            self.player.position,
            self.window.delta_time,
            panning_fraction,
        )
        self.camera.position = arcade.camera.grips.constrain_xy(
            self.camera.view_data, self.camera_bounds
        )

    def on_key_press(self, symbol, modifiers) -> None:
        self.player.on_key_press(symbol, self.physics_engine)

    def on_key_release(self, symbol, modifiers) -> None:
        self.player.on_key_release(symbol, self.physics_engine)


game = GameView()
window.show_view(game)
arcade.run()
