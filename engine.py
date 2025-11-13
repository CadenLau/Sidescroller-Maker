import os
import arcade
import random
import view

bg_star_color = (255, 255, 255, 95)
fg_star_color = [
    arcade.color.WHITE,
    arcade.color.BABY_BLUE,
    arcade.color.AQUA,
    arcade.color.BUFF,
    arcade.color.ALIZARIN_CRIMSON,
]


def create_starfield(
    width,
    height,
    batch: arcade.shape_list.ShapeElementList,
    color=bg_star_color,
    random_color=False,
):
    for i in range(200):
        x = random.randint(0, width)
        y = random.randint(0, height)
        w = random.randint(1, 3)
        h = random.randint(1, 3)
        if random_color:
            color = random.choice(fg_star_color)
        star = arcade.shape_list.create_rectangle_filled(x, y, w, h, color)
        batch.append(star)


CAMERA_PAN_SPEED = 0.3
FONT_SIZE = 16


class Player(arcade.Sprite):
    def __init__(
        self,
        animations: dict[str, list[arcade.Texture]],
        scale,
        jumps,
        jump_speed,
        movement_speed,
        start_x,
        start_y,
    ):
        super().__init__(animations["idle"][0])
        self.animations = animations
        self.textures = animations["idle"]
        self.scale_factor = scale
        self.scale = scale
        self.jumps = jumps
        self.jump_speed = jump_speed
        self.movement_speed = movement_speed
        self.start_x = start_x
        self.start_y = start_y

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
                (self.center_x, self.center_y),
                (self.scale_factor, self.scale_factor),
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
            self.scale_x = -self.scale_factor
            if self.state != "duck":  # can't move while ducking
                self.change_x = -self.movement_speed
                if not self.state in ("jump", "fall"):
                    self.set_state("walk")
        if self.key_pressed["right"] and (
            self.last_key_pressed == "right" or not self.key_pressed["left"]
        ):
            self.scale_x = self.scale_factor
            if self.state != "duck":  # can't move while ducking
                self.change_x = self.movement_speed
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
                self.change_y = self.jump_speed
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


def make_player(
    scale=1.0, start_x=100, start_y=200, jumps=2, jump_speed=20, movement_speed=8
) -> Player:
    """Precondition: jumps > 0."""
    walk = []
    for filename in sorted(os.listdir("assets/images/walk")):
        walk.append(arcade.load_texture(f"assets/images/walk/{filename}"))
    # walk = arcade.load_spritesheet("assets/images/p1_walk.png").get_texture_grid(size=(72, 97), columns=3, count=11)
    # ^^^ p1_walk.png doesn't have the images in an even grid ^^^
    animations = {
        "idle": [arcade.load_texture("assets/images/p1_stand.png")],
        "walk": walk,
        "duck": [arcade.load_texture("assets/images/p1_duck.png")],
        "jump": [arcade.load_texture("assets/images/p1_jump.png")],
        "fall": [arcade.load_texture("assets/images/p1_fall.png")],
    }
    player = Player(
        animations, scale, jumps, jump_speed, movement_speed, start_x, start_y
    )
    player.position = start_x, start_y
    return player


class GameView(arcade.View):
    def __init__(
        self,
        window: arcade.Window,
        level_width,
        parallax_scroll,
        player: Player,
        gravity,
    ) -> None:
        super().__init__()
        self.window = window
        self.level_width = level_width
        self.parallax_scroll = parallax_scroll
        self.gravity = gravity

        if self.parallax_scroll:
            self.fg_star_speed = 0.6
            self.bg_star_speed = 0.8

            self.fg_stars = arcade.shape_list.ShapeElementList()
            create_starfield(
                self.level_width, window.height, self.fg_stars, random_color=True
            )

            self.bg_stars = arcade.shape_list.ShapeElementList()
            create_starfield(self.level_width, window.height, self.bg_stars)

        self.player = player
        self.sprites = arcade.SpriteList()
        self.sprites.append(self.player)

        self.platform_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()

        self.physics_engine = None

        self.left_edge = self.player.width / 2.0
        self.right_edge = level_width - self.player.width / 2.0

        self.camera = arcade.Camera2D()
        self.camera_bounds = arcade.LRBT(
            self.window.width / 2.0,
            self.level_width - self.window.width / 2.0,
            self.window.height / 2.0,
            self.window.height / 2.0,
        )

        self.collected_coins = 0
        self.total_coins = 0
        self.coins_text = arcade.Text(
            f"coins collected: {self.collected_coins} / {self.total_coins}",
            10,
            window.height - 25,
            arcade.color.WHITE,
            FONT_SIZE,
            align="left",
        )

        self.enemies_defeated = 0
        self.total_enemies = 0
        self.enemies_text = arcade.Text(
            f"enemies defeated: {self.enemies_defeated} / {self.total_enemies}",
            10,
            window.height - 50,
            arcade.color.WHITE,
            FONT_SIZE,
            align="left",
        )

        self.death_count = 0
        self.death_text = arcade.Text(
            f"death count: {self.death_count}",
            10,
            window.height - 75,
            arcade.color.WHITE,
            FONT_SIZE,
            align="left",
        )

    def on_draw(self) -> None:
        self.camera.use()
        self.clear()
        if self.parallax_scroll:
            self.bg_stars.draw()
            self.fg_stars.draw()
        self.sprites.draw()
        self.platform_list.draw()
        self.enemy_list.draw()
        self.coin_list.draw()
        self.coins_text.draw()
        self.enemies_text.draw()
        self.death_text.draw()

    def on_update(self, delta_time) -> None:
        self.player.update(delta_time)
        self.physics_engine.update()

        self.player.center_x = arcade.math.clamp(
            self.player.center_x, self.left_edge, self.right_edge
        )
        # check if player fell off screen
        if self.player.center_y < -self.player.height / 2:
            self.player.position = self.player.start_x, self.player.start_y
            self.player.change_x = 0
            self.player.change_y = 0
            self.death_count += 1
            self.death_text.text = f"death count: {self.death_count}"

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
                if (
                    self.player.time_since_ground >= (1 / self.window._update_rate) / 9
                ):  # slower transition to walk/idle animations in return for removing infinite jump bug
                    if abs(self.player.change_x) > 0:
                        self.player.set_state("walk")
                    else:
                        self.player.set_state("idle")
                    self.player.on_ground = True
                    self.player.time_since_ground = 0
                else:
                    self.player.time_since_ground += 1

        if self.enemy_list:
            enemy_hit = arcade.check_for_collision_with_list(
                self.player, self.enemy_list
            )
            if enemy_hit:
                if not self.player.attacking:
                    self.player.position = self.player.start_x, self.player.start_y
                    self.death_count += 1
                    self.death_text.text = f"death count: {self.death_count}"
                else:
                    self.enemy_list.remove(enemy_hit[0])
                    self.enemies_defeated += 1
                    self.enemies_text.text = f"enemies defeated: {self.enemies_defeated} / {self.total_enemies}"

        if self.coin_list:
            coin_hit = arcade.check_for_collision_with_list(self.player, self.coin_list)
            if coin_hit:
                self.coin_list.remove(coin_hit[0])
                self.collected_coins += 1
                self.coins_text.text = (
                    f"coins collected: {self.collected_coins} / {self.total_coins}"
                )

        # save old position for parallax scrolling
        old_position = self.camera.position
        self.pan_camera_to_player(CAMERA_PAN_SPEED)
        self.move_text_with_camera()
        if self.parallax_scroll:
            self.scroll_background(old_position)

    def move_text_with_camera(self) -> None:
        self.coins_text.x = self.camera.center_left.x + 10
        self.enemies_text.x = self.camera.center_left.x + 10
        self.death_text.x = self.camera.center_left.x + 10

    def scroll_background(self, old_position) -> None:
        position_difference = self.camera.position - old_position
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
        if symbol == arcade.key.ESCAPE:
            if view.maker_view != None:
                self.window.show_view(view.maker_view)
        self.player.on_key_press(symbol, self.physics_engine)

    def on_key_release(self, symbol, modifiers) -> None:
        self.player.on_key_release(symbol, self.physics_engine)

    def setup_physics(self) -> None:
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player, self.platform_list, gravity_constant=self.gravity
        )
        if self.player.jumps > 1:
            self.physics_engine.enable_multi_jump(self.player.jumps)

    def make_enemy(self, center_x, center_y, scale=0.5) -> None:
        self.enemy_list.append(
            arcade.Sprite(
                ":resources:/images/enemies/slimeBlock.png", scale, center_x, center_y
            )
        )
        self.total_enemies += 1
        self.enemies_text.text = (
            f"enemies defeated: {self.enemies_defeated} / {self.total_enemies}"
        )

    def make_coin(self, center_x, center_y, scale=0.7) -> None:
        self.coin_list.append(
            arcade.Sprite(
                ":resources:/images/items/gold_1.png",
                scale,
                center_x,
                center_y,
            )
        )
        self.total_coins += 1
        self.coins_text.text = (
            f"coins collected: {self.collected_coins} / {self.total_coins}"
        )

    def make_platform(self, center_x, center_y, width=300, height=40) -> None:
        self.platform_list.append(
            arcade.SpriteSolidColor(
                width=width,
                height=height,
                center_x=center_x,
                center_y=center_y,
                color=arcade.color.YELLOW,
            )
        )

    def make_ground(self) -> None:
        self.make_platform(
            width=self.window.width * 2, center_x=self.window.width, center_y=20
        )


def make_window(width=800, height=600, title="Sidescroller Engine") -> arcade.Window:
    return arcade.Window(width, height, title)


def make_game(
    window: arcade.Window = None,
    player: Player = None,
    level_width=None,
    parallax_scroll=True,
    gravity=1.0,
) -> GameView:
    if window == None:
        window = make_window()
    if player == None:
        player = make_player()
    if level_width == None:
        level_width = window.width * 2
    return GameView(window, level_width, parallax_scroll, player, gravity)


def run(game: GameView) -> None:
    game.setup_physics()
    game.window.show_view(game)
    arcade.run()
