from engine import *

window = make_window(title="Sidecroller Demo")

game = make_game(window)

game.make_ground()

game.make_platform(600, 200)
game.make_platform(1200, 300)

game.make_enemy(1500, 72)
game.make_enemy(900, 72)

game.make_coin(1560, 72)
game.make_coin(1300, 352)

run(game)
