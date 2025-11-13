# Todo
# - clean up format
# - update README.md

import arcade
import view
from engine import *

window = make_window(title="Sidescroller Maker")

TILE_SIZE = 40
COIN_SCALE = TILE_SIZE / 64 - 0.05  # slightly smaller than tile
ENEMY_SCALE = TILE_SIZE / 128
PLAYER_SCALE = 80 / 92  # two tile height
X_SCALE = 0.7  # slightly smaller than tile


class Builder(arcade.Sprite):
    def __init__(
        self,
        textures: list[arcade.Texture],
    ):
        super().__init__(textures[0], PLAYER_SCALE)
        self.textures = textures


class MakerView(arcade.View):
    def __init__(self) -> None:
        super().__init__()
        self.game = make_game(window, make_player(PLAYER_SCALE))

        self.sprites = arcade.SpriteList()
        self.player = arcade.SpriteList()
        self.builder_draw = arcade.SpriteList()

        self.player.append(
            arcade.Sprite(
                arcade.load_texture("assets/images/p1_stand.png"),
                scale=PLAYER_SCALE,
                center_x=self.game.player.start_x,
                center_y=self.game.player.start_y,
            )
        )

        self.textures_indices = {
            0: "player",
            1: "platform",
            2: "enemy",
            3: "coin",
            4: "x",
        }
        textures = [
            arcade.load_texture("assets/images/p1_stand.png"),
            arcade.make_soft_square_texture(
                size=TILE_SIZE,
                color=arcade.color.YELLOW,
                center_alpha=255,
                outer_alpha=255,
            ),
            arcade.load_texture(":resources:/images/enemies/slimeBlock.png"),
            arcade.load_texture(":resources:/images/items/gold_1.png"),
            arcade.load_texture("assets/images/red_x.png"),
        ]
        self.builder = Builder(textures)
        self.builder.position = TILE_SIZE / 2, TILE_SIZE
        self.builder_draw.append(self.builder)

        self.grid = arcade.shape_list.ShapeElementList()
        for i in range(20, self.game.level_width, TILE_SIZE):
            for j in range(20, window.height, TILE_SIZE):
                square = arcade.shape_list.create_rectangle_outline(
                    center_x=i,
                    center_y=j,
                    width=TILE_SIZE,
                    height=TILE_SIZE,
                    color=(255, 255, 255, 100),
                )
                self.grid.append(square)

        self.camera = arcade.Camera2D()
        self.camera_bounds = arcade.LRBT(
            self.window.width / 2.0,
            self.game.level_width - self.window.width / 2.0,
            self.window.height / 2.0,
            self.window.height / 2.0,
        )

    def on_draw(self) -> None:
        self.camera.use()
        self.clear()
        self.grid.draw()
        self.sprites.draw()
        self.player.draw()
        self.builder_draw.draw()

    def on_update(self, delta_time) -> None:
        self.camera.position = self.builder.position
        self.camera.position = arcade.camera.grips.constrain_xy(
            self.camera.view_data, self.camera_bounds
        )

    def resolve_game_collisions(self, sprite) -> None:
        ground_overlap = arcade.check_for_collision_with_list(
            sprite, self.game.platform_list
        )
        if ground_overlap:
            self.game.platform_list.remove(ground_overlap[0])

        enemy_overlap = arcade.check_for_collision_with_list(
            sprite, self.game.enemy_list
        )
        if enemy_overlap:
            self.game.enemy_list.remove(enemy_overlap[0])

        coin_overlap = arcade.check_for_collision_with_list(sprite, self.game.coin_list)
        if coin_overlap:
            self.game.coin_list.remove(coin_overlap[0])

    def resolve_player_collision(self) -> None:
        if self.player:
            overlap = arcade.check_for_collision_with_list(self.player[0], self.sprites)
            if overlap:
                for i in range(len(overlap)):
                    self.sprites.remove(overlap[i])
                    self.resolve_game_collisions(self.game.player)

    def resolve_maker_collisions(self, sprite) -> None:
        overlap = arcade.check_for_collision_with_list(sprite, self.sprites)
        if overlap:
            self.sprites.remove(overlap[0])
            self.resolve_game_collisions(sprite)

    def on_key_press(self, symbol, modifiers) -> None:
        # start game
        if symbol == arcade.key.ENTER:
            # clone the game to keep original state safe
            game = make_game(
                window,
                make_player(
                    scale=PLAYER_SCALE,
                    start_x=self.game.player.start_x,
                    start_y=self.game.player.start_y,
                ),
            )
            for platform in self.game.platform_list:
                game.make_platform(
                    center_x=platform.center_x,
                    center_y=platform.center_y,
                    width=TILE_SIZE,
                    height=TILE_SIZE,
                )
            for enemy in self.game.enemy_list:
                game.make_enemy(
                    center_x=enemy.center_x, center_y=enemy.center_y, scale=ENEMY_SCALE
                )
            for coin in self.game.coin_list:
                game.make_coin(
                    center_x=coin.center_x, center_y=coin.center_y, scale=COIN_SCALE
                )
            run(game)

        # place build
        if symbol == arcade.key.SPACE:
            if self.textures_indices[self.builder.cur_texture_index] == "player":
                self.game.player.position = self.builder.center_x, self.builder.center_y
                self.game.player.start_x = self.builder.center_x
                self.game.player.start_y = self.builder.center_y
                self.player.remove(self.player[0])
                self.player.append(
                    arcade.Sprite(
                        arcade.load_texture("assets/images/p1_stand.png"),
                        scale=PLAYER_SCALE,
                        center_x=self.builder.center_x,
                        center_y=self.builder.center_y,
                    )
                )
                self.resolve_player_collision()
            elif self.textures_indices[self.builder.cur_texture_index] == "platform":
                platform = arcade.SpriteSolidColor(
                    width=TILE_SIZE,
                    height=TILE_SIZE,
                    center_x=self.builder.center_x,
                    center_y=self.builder.center_y,
                    color=arcade.color.YELLOW,
                )
                self.resolve_maker_collisions(platform)
                self.sprites.append(platform)
                self.resolve_player_collision()
                self.game.make_platform(
                    self.builder.center_x, self.builder.center_y, TILE_SIZE, TILE_SIZE
                )
            elif self.textures_indices[self.builder.cur_texture_index] == "enemy":
                enemy = arcade.Sprite(
                    arcade.load_texture(":resources:/images/enemies/slimeBlock.png"),
                    scale=ENEMY_SCALE,
                    center_x=self.builder.center_x,
                    center_y=self.builder.center_y,
                )
                self.resolve_maker_collisions(enemy)
                self.sprites.append(enemy)
                self.resolve_player_collision()
                self.game.make_enemy(
                    self.builder.center_x, self.builder.center_y, ENEMY_SCALE
                )
            elif self.textures_indices[self.builder.cur_texture_index] == "coin":
                coin = arcade.Sprite(
                    arcade.load_texture(":resources:/images/items/gold_1.png"),
                    scale=COIN_SCALE,
                    center_x=self.builder.center_x,
                    center_y=self.builder.center_y,
                )
                self.resolve_maker_collisions(coin)
                self.sprites.append(coin)
                self.resolve_player_collision()
                self.game.make_coin(
                    self.builder.center_x, self.builder.center_y, COIN_SCALE
                )
            elif self.textures_indices[self.builder.cur_texture_index] == "x":
                delete = arcade.Sprite(
                    arcade.load_texture("assets/images/red_x.png"),
                    center_x=self.builder.center_x,
                    center_y=self.builder.center_y,
                )
                self.resolve_maker_collisions(delete)

        # change builder build
        if symbol == arcade.key.KEY_1:
            if self.builder.cur_texture_index != 0:
                self.builder.center_y += TILE_SIZE / 2
                if self.builder.center_y == window.height:
                    self.builder.center_y -= TILE_SIZE
            self.builder.cur_texture_index = 0
            self.builder.set_texture(self.builder.cur_texture_index)
        elif symbol == arcade.key.KEY_2:
            if self.builder.cur_texture_index == 0:
                self.builder.center_y -= TILE_SIZE / 2
            self.builder.cur_texture_index = 1
            self.builder.set_texture(self.builder.cur_texture_index)
        elif symbol == arcade.key.KEY_3:
            if self.builder.cur_texture_index == 0:
                self.builder.center_y -= TILE_SIZE / 2
            self.builder.cur_texture_index = 2
            self.builder.set_texture(self.builder.cur_texture_index)
        elif symbol == arcade.key.KEY_4:
            if self.builder.cur_texture_index == 0:
                self.builder.center_y -= TILE_SIZE / 2
            self.builder.cur_texture_index = 3
            self.builder.set_texture(self.builder.cur_texture_index)
        elif symbol == arcade.key.KEY_5:
            if self.builder.cur_texture_index == 0:
                self.builder.center_y -= TILE_SIZE / 2
            self.builder.cur_texture_index = 4
            self.builder.set_texture(self.builder.cur_texture_index)

        # move builder
        if symbol == arcade.key.LEFT:
            if self.builder.center_x > TILE_SIZE:
                self.builder.center_x -= TILE_SIZE
        elif symbol == arcade.key.RIGHT:
            if self.builder.center_x < self.game.level_width - TILE_SIZE:
                self.builder.center_x += TILE_SIZE
        elif symbol == arcade.key.UP:
            if self.builder.center_y < self.window.height - TILE_SIZE:
                self.builder.center_y += TILE_SIZE
        elif symbol == arcade.key.DOWN:
            if self.builder.center_y > TILE_SIZE:
                self.builder.center_y -= TILE_SIZE

        # correct scale
        if self.textures_indices[self.builder.cur_texture_index] == "player":
            self.builder.scale = PLAYER_SCALE
        elif self.textures_indices[self.builder.cur_texture_index] == "platform":
            self.builder.scale = 1.0
        elif self.textures_indices[self.builder.cur_texture_index] == "enemy":
            self.builder.scale = ENEMY_SCALE
        elif self.textures_indices[self.builder.cur_texture_index] == "coin":
            self.builder.scale = COIN_SCALE
        elif self.textures_indices[self.builder.cur_texture_index] == "x":
            self.builder.scale = X_SCALE


view.maker_view = MakerView()
window.show_view(view.maker_view)
arcade.run()
