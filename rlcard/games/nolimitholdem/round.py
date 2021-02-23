# -*- coding: utf-8 -*-
''' Implement NoLimit Texas Hold'em Round class
'''
from enum import Enum

from rlcard.games.limitholdem import PlayerStatus
import numpy as np


# change proceed_round if this get changed
class Action(Enum):

    FOLD = 0
    CHECK = 1
    CALL = 2
    RAISE_1BB = 3
    RAISE_2BB = 4
    RAISE_3BB = 5
    RAISE_5BB = 6
    RAISE_HALF_POT = 7
    RAISE_POT = 8
    RAISE_2POT = 9
    RAISE_3POT = 10
    RAISE_5POT = 11
    RAISE_7POT = 12
    RAISE_10POT = 13
    ALL_IN = 14
    # SMALL_BLIND = 7
    # BIG_BLIND = 8


class NolimitholdemRound():
    ''' Round can call other Classes' functions to keep the game running
    '''

    def __init__(self, num_players, init_raise_amount, dealer, np_random):
        ''' Initilize the round class

        Args:
            num_players (int): The number of players
            init_raise_amount (int): The min raise amount when every round starts
        '''
        self.np_random = np_random
        self.game_pointer = None
        self.num_players = num_players
        self.init_raise_amount = init_raise_amount
        self.dealer = dealer

        # Count the number without raise
        # If every player agree to not raise, the round is overr
        self.not_raise_num = 0

        # Count players that are not playing anymore (folded or all-in)
        self.not_playing_num = 0

        # Raised amount for each player
        self.raised = [0 for _ in range(self.num_players)]

    def start_new_round(self, game_pointer, raised=None):
        ''' Start a new bidding round

        Args:
            raised (list): Initialize the chips for each player

        Note: For the first round of the game, we need to setup the big/small blind
        '''
        self.game_pointer = game_pointer
        self.not_raise_num = 0
        if raised:
            self.raised = raised
        else:
            self.raised = [0 for _ in range(self.num_players)]

    def get_players_hist_bets(self):
        return self.players_hist_bets



    def proceed_round(self, players, action):
        ''' Call other Classes's functions to keep one round running

        Args:
            players (list): The list of players that play the game
            action (str/int): An legal action taken by the player

        Returns:
            (int): The game_pointer that indicates the next player
        '''
        player = players[self.game_pointer]

        bet_amount = 0


        if action == Action.CALL:
            diff = max(self.raised) - self.raised[self.game_pointer]
            self.raised[self.game_pointer] = max(self.raised)
            player.bet(chips=diff)
            bet_amount = diff
            self.not_raise_num += 1

        elif action == Action.ALL_IN:
            all_in_quantity = player.remained_chips
            self.raised[self.game_pointer] = all_in_quantity + self.raised[self.game_pointer]
            player.bet(chips=all_in_quantity)
            bet_amount = all_in_quantity
            self.not_raise_num = 1

        # needs to be changed if class Action(Enum) is changed
        elif 13 >= action.value >= 3:
            if action == Action.RAISE_1BB:
                quantity = self.init_raise_amount
            elif action == Action.RAISE_2BB:
                quantity = self.init_raise_amount * 2
            elif action == Action.RAISE_3BB:
                quantity = self.init_raise_amount * 3
            elif action == Action.RAISE_5BB:
                quantity = self.init_raise_amount * 5
            elif action == Action.RAISE_POT:
                quantity = self.dealer.pot
            elif action == Action.RAISE_HALF_POT:
                quantity = int(self.dealer.pot / 2)
            elif action == Action.RAISE_2POT:
                quantity = self.dealer.pot * 2
            elif action == Action.RAISE_3POT:
                quantity = self.dealer.pot * 3
            elif action == Action.RAISE_5POT:
                quantity = self.dealer.pot * 5
            elif action == Action.RAISE_7POT:
                quantity = self.dealer.pot * 7
            else:
                quantity = self.dealer.pot * 10
            self.raised[self.game_pointer] += quantity
            player.bet(chips=quantity)
            bet_amount = quantity
            self.not_raise_num = 1

        elif action == Action.FOLD:
            player.status = PlayerStatus.FOLDED

        elif action == Action.CHECK:
            self.not_raise_num += 1

        if player.remained_chips < 0:
            raise Exception("Player in negative stake")

        if player.remained_chips == 0 and player.status != PlayerStatus.FOLDED:
            player.status = PlayerStatus.ALLIN

        self.game_pointer = (self.game_pointer + 1) % self.num_players

        if player.status == PlayerStatus.ALLIN:
            self.not_playing_num += 1
            self.not_raise_num -= 1  # Because already counted in not_playing_num
        if player.status == PlayerStatus.FOLDED:
            self.not_playing_num += 1

        # Skip the folded players
        while players[self.game_pointer].status == PlayerStatus.FOLDED:
            self.game_pointer = (self.game_pointer + 1) % self.num_players

        return bet_amount, self.game_pointer

    def get_nolimit_legal_actions(self, players):
        ''' Obtain the legal actions for the curent player

        Args:
            players (list): The players in the game

        Returns:
           (list):  A list of legal actions
        '''

        full_actions = list(Action)
        # If the current chips are less than that of the highest one in the round, we can not check
        if self.raised[self.game_pointer] < max(self.raised):
            full_actions.remove(Action.CHECK)

        # If the current player has put in the chips that are more than others, we can not call
        if self.raised[self.game_pointer] == max(self.raised):
            full_actions.remove(Action.CALL)

        player = players[self.game_pointer]

        if Action.RAISE_HALF_POT in full_actions and \
                (int(self.dealer.pot / 2) + player.in_chips <= max(self.raised) or
                 int(self.dealer.pot / 2) > player.remained_chips):
            full_actions.remove(Action.RAISE_HALF_POT)

        if Action.RAISE_POT in full_actions and \
                (self.dealer.pot + player.in_chips <= max(self.raised) or
                 self.dealer.pot > player.remained_chips):
            full_actions.remove(Action.RAISE_POT)

        if Action.RAISE_2POT in full_actions and \
                (self.dealer.pot * 2 + player.in_chips <= max(self.raised) or
                 self.dealer.pot * 2 > player.remained_chips):
            full_actions.remove(Action.RAISE_2POT)

        if Action.RAISE_3POT in full_actions and \
                (self.dealer.pot * 3 + player.in_chips <= max(self.raised) or
                 self.dealer.pot * 3 > player.remained_chips):
            full_actions.remove(Action.RAISE_3POT)

        if Action.RAISE_5POT in full_actions and \
                (self.dealer.pot * 5 + player.in_chips <= max(self.raised) or
                 self.dealer.pot * 5 > player.remained_chips):
            full_actions.remove(Action.RAISE_5POT)

        if Action.RAISE_7POT in full_actions and \
                (self.dealer.pot * 7 + player.in_chips <= max(self.raised) or
                 self.dealer.pot * 7 > player.remained_chips):
            full_actions.remove(Action.RAISE_7POT)

        if Action.RAISE_10POT in full_actions and \
                (self.dealer.pot * 10 + player.in_chips <= max(self.raised) or
                 self.dealer.pot * 10 > player.remained_chips):
            full_actions.remove(Action.RAISE_10POT)

        if Action.RAISE_1BB in full_actions and \
                (self.init_raise_amount + player.in_chips <= max(self.raised) or
                 self.init_raise_amount > player.remained_chips):
            full_actions.remove(Action.RAISE_1BB)

        if Action.RAISE_2BB in full_actions and \
                (self.init_raise_amount * 2 + player.in_chips <= max(self.raised) or
                 self.init_raise_amount * 2 > player.remained_chips):
            full_actions.remove(Action.RAISE_2BB)

        if Action.RAISE_3BB in full_actions and \
                (self.init_raise_amount * 3 + player.in_chips <= max(self.raised) or
                 self.init_raise_amount * 3 > player.remained_chips):
            full_actions.remove(Action.RAISE_3BB)

        if Action.RAISE_5BB in full_actions and \
                (self.init_raise_amount * 5 + player.in_chips <= max(self.raised) or
                 self.init_raise_amount * 5 > player.remained_chips):
            full_actions.remove(Action.RAISE_5BB)

        # If the current player has no more chips after call, we cannot raise
        diff = max(self.raised) - self.raised[self.game_pointer]
        if diff > 0 and player.in_chips + diff >= player.remained_chips:
            return [Action.FOLD, Action.CALL]

        return full_actions

    def is_over(self):
        ''' Check whether the round is over

        Returns:
            (boolean): True if the current round is over
        '''
        if self.not_raise_num + self.not_playing_num >= self.num_players:
            return True
        return False
