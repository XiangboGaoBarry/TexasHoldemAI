import unittest

import rlcard
from rlcard.agents.random_agent import RandomAgent
from rlcard.games.nolimitholdem.round import Action
from .determism_util import is_deterministic


class TestNolimitholdemEnv(unittest.TestCase):

    def test_reset_and_extract_state(self):
        env = rlcard.make('no-limit-holdem')
        state, _ = env.reset()
        self.assertEqual(state['obs'].size, 54)

    def test_is_deterministic(self):
        self.assertTrue(is_deterministic('no-limit-holdem'))

    def test_get_legal_actions(self):
        env = rlcard.make('no-limit-holdem')
        env.reset()
        legal_actions = env._get_legal_actions()
        for action in legal_actions:
            self.assertIn(action, env.actions)

    def test_decode_action(self):
        env = rlcard.make('no-limit-holdem')
        state, _ = env.reset()
        for action in state['legal_actions']:
            decoded = env._decode_action(action)
            self.assertIn(decoded, env.actions)

        decoded = env._decode_action(Action.FOLD.value)
        self.assertEqual(decoded, Action.FOLD)

        env.step(0)
        decoded = env._decode_action(1)
        self.assertEqual(decoded, Action.CHECK)

    def test_step(self):
        env = rlcard.make('no-limit-holdem')
        state, player_id = env.reset()
        self.assertEqual(player_id, env.get_player_id())
        action = state['legal_actions'][0]
        _, player_id = env.step(action)
        self.assertEqual(player_id, env.get_player_id())

    def test_step_back(self):
        env = rlcard.make('no-limit-holdem', config={'allow_step_back':True})
        _, player_id = env.reset()
        env.step(0)
        _, back_player_id = env.step_back()
        self.assertEqual(player_id, back_player_id)
        self.assertEqual(env.step_back(), False)

        env = rlcard.make('no-limit-holdem')
        with self.assertRaises(Exception):
            env.step_back()

    def test_run(self):
        env = rlcard.make('no-limit-holdem')
        agents = [RandomAgent(env.action_num) for _ in range(env.player_num)]
        env.set_agents(agents)
        trajectories, payoffs = env.run(is_training=False)
        self.assertEqual(len(trajectories), 2)
        total = 0
        for payoff in payoffs:
            total += payoff
        self.assertEqual(total, 0)

    def test_get_perfect_information(self):
        env = rlcard.make('no-limit-holdem')
        _, player_id = env.reset()
        self.assertEqual(player_id, env.get_perfect_information()['current_player'])

    def test_multiplayers(self):
        env = rlcard.make('no-limit-holdem', config={'game_player_num':5})
        player_num = env.game.get_player_num()
        self.assertEqual(player_num, 5)

    def test_config_chips(self):
        env = rlcard.make('no-limit-holdem', config={'game_player_num':5, 'chips_for_each':[100, 200, 400, 600, 900]})
        env.game.init_game()
        players = env.game.players
        chips = []
        for i in range(5):
            chips.append(players[i].remained_chips + players[i].in_chips)
        self.assertEqual(chips, [100, 200, 400, 600, 900])

if __name__ == '__main__':
    unittest.main()
