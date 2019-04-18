from random import shuffle
import sys
import logging
import numpy as np

from monopoly.player import Player
import config
from monopoly.game import Game

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)


class Arena(object):
    def __init__(self, n_games=100, n_rounds=100, verbose=0):
        self.n_games = n_games
        self.n_rounds = n_rounds
        self.verbose = verbose

    def fight(self, agent, opponent, agent_id='rl', opp_id='opp'):

        if self.verbose == 0:
            config.verbose = {key: False for key in config.verbose}
            config.verbose['stats'] = True
        if self.verbose == 1:
            config.verbose = {key: True for key in config.verbose}

        win_stats = {agent_id: 0, opp_id: 0}
        full_games_counter = 0

        for n_game in range(self.n_games):

            if config.verbose['game_start']:
                logger.info('----------------STARTING GAME {}----------------\n\n'.format(n_game))

            players = []
            players.append(Player(policy=agent, player_id=agent_id))
            players.append(Player(policy=opponent, player_id=opp_id))
            shuffle(players)

            game = Game(players=players)

            for player in players:
                player.set_game(game)

            for n_round in range(self.n_rounds):
                if config.verbose['round']:
                    logger.info('-----------ROUND {}-----------\n\n'.format(n_round))

                # TODO: change this, don't like three completely the same conditional statements
                if not game.is_game_active():  # stopping rounds loop
                    break

                game.update_round()

                for player in game.players:
                    if config.verbose['player']:
                        logger.info('-----------PLAYER idx={}, id={}-----------\n\n'.format(player.index, player.id))

                    if player.is_bankrupt:  # must change it. do it two times because some players can go bankrupt when must pay bank interest
                        game.remove_player(player)  # other player's mortgaged spaces
                        break

                    if not game.is_game_active():  # stopping players loop
                        break

                    game.pass_dice()

                    while True:
                        if config.verbose['player_properties']:
                            player.show()

                        if not game.is_game_active():  # stopping players loop
                            break

                        if n_round != 0:
                            player.optional_actions()

                        game.dice.roll()

                        if player.is_in_jail():
                            stay_in_jail = player.jail_strategy(dice=game.dice)
                            if stay_in_jail:
                                player.optional_actions()
                                break

                        if game.dice.double_counter == 3:
                            player.go_to_jail()
                            break

                        player.move(game.dice.roll_sum)

                        if player.position == 30:
                            player.go_to_jail()  # the same here
                            break

                        # TODO: add card go to jail

                        space = game.board[player.position]

                        player.act(space)

                        if player.is_bankrupt:
                            game.remove_player(player)
                            break

                        if game.dice.double:
                            continue

                        if config.verbose['player_properties']:
                            player.show()

                        break


            if game.players_left != 1:
                leaderboard = game.get_leaderboard()
                win_stats[str(leaderboard[0].id)] += 1

                if config.verbose['not_full_game_result']:
                    for i, player in enumerate(leaderboard):
                        print('Player {} is on the {} place. Total wealth {}'.format(player.id, i + 1, player.total_wealth))
                        player.show()
                    if len(game.lost_players) != 0:
                        for i, player in enumerate(game.lost_players):
                            print('Player {} is on the {} place'.format(player.id, i + 1 + len(leaderboard)))
                            player.show()
            else:
                win_stats[str(game.players[0].id)] += 1
                full_games_counter += 1

                if config.verbose['full_game_result']:
                    print('Player {} is on the 1 place'.format(game.players[0].id))
                    game.players[0].show()
                    for i, player in enumerate(game.lost_players):
                        print('Player {} is on the {} place '.format(player.id, i + 2))
                        player.show()


        winrate_return = 0
        if config.verbose['stats']:
            for key in win_stats:
                winrate = np.round(win_stats[key] / self.n_games * 100, 3)
                print('----------Player {} won {} / {}'.format(key, win_stats[key], self.n_games))
                print('-------------Win rate is {} %'.format(winrate))
                if key == agent_id:
                    winrate_return = winrate

        print('---Full games {} / {}'.format(full_games_counter, self.n_games))

        return winrate_return
