from rlcard.games.limitholdem import Player


class NolimitholdemPlayer(Player):

    def __init__(self, player_id, init_chips, np_random):
        ''' Initilize a player.

        Args:
            player_id (int): The id of the player
            init_chips (int): The number of chips the player has initially
        '''
        super(NolimitholdemPlayer, self).__init__(player_id, np_random)
        self.remained_chips = init_chips
        # players' 5 bets each round (O:bet_amount, 1: 1 if occupied else 0)
        self.players_hist_bets = [(0, 0)] * 40

    def bet(self, chips):
        quantity = chips if chips <= self.remained_chips else self.remained_chips
        self.in_chips += quantity
        self.remained_chips -= quantity

    def get_state(self, public_cards, all_chips, legal_actions):
        ''' Encode the state for the player

        Args:
            public_cards (list): A list of public cards that seen by all the players
            all_chips (int): The chips that all players have put in

        Returns:
            (dict): The state of the player
        '''
        state = {}
        state['hand'] = [c.get_index() for c in self.hand]
        state['public_cards'] = [c.get_index() for c in public_cards]
        state['all_chips'] = all_chips
        state['my_chips'] = self.in_chips
        state['legal_actions'] = legal_actions
        state['player_id'] = self.player_id
        state['hist_bets'] = self.players_hist_bets
        return state


