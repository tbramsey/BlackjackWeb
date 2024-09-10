import random
import pygame
import torch
import torch.nn as nn
import torch.nn.functional as F
from enum import Enum
from collections import namedtuple
import numpy as np

class BlackjackGame():
    def __init__(self):
        self.reset_hands()
        self.reset()

    def reset_hands(self):
        self.dealer = [0] * 10
        self.player = [0] * 10
        self.player2 = [0] * 10
        self.dealer_hand = 0
        self.player_hand = 0
        self.player2_hand = 0
        self.player_ace_count = 0
        self.player2_ace_count = 0
        self.dealer_ace_count = 0
        self.canSplit = 0
        self.canDouble1 = 0
        self.canDouble2 = 0
        self.double1 = False
        self.double2 = False
        self.split = False
        self.reward = 0

    def reset(self):
        self.deck = [0] * 313
        self.balance = 1000
        self.current_card = 0
        self.bet = 10
        self.count = 0
        self.decks_remaining = 6
        self.random = random
        self.print_info = False
        self.random.seed()
        self.deal_6_decks()
        self.shuffle_deck()

    def deal_6_decks(self):
        self.deck = []
        for _ in range(6):  # 6 decks
            for i in range(1, 14):  # Cards 1 to 13
                card_value = i
                if card_value == 1:
                    card_value = 11
                elif card_value > 10:
                    card_value = 10
                self.deck.append(card_value)  # 4 of each card per deck (suit doesn't matter)

        self.deck *= 4  # As there are 4 suits

    def shuffle_deck(self):
        self.random.shuffle(self.deck)

    def count_card(self, rank):
        num_of_type = 0
        for card in self.deck:
            if card == rank:
                num_of_type += 1
        return num_of_type

    def get_state(self):
        remaining_card_counts = [self.count_card(card) for card in range(2, 12)]
        state = [
            self.player_hand,
            self.player_ace_count,
            self.player2_hand,
            self.player2_ace_count,
            self.dealer[0],
            self.dealer_ace_count,
            self.count,
            self.decks_remaining,
            int(self.canSplit),
            int(self.canDouble1),
            int(self.canDouble2)
        ]
        state.extend(remaining_card_counts)
        return np.array(state, dtype=int)

    def set_bet(self, action):
        action_to_bet = {
            4: 0,
            5: 10,
            6: 20
        }
        
        if action in action_to_bet:
            self.bet = action_to_bet[action]
        else:
            self.bet = 10

    def play_step(self, action):
        self.player_hand = sum(self.player)
        self.player_hand2 = sum(self.player2)
        self.dealer_hand = sum(self.dealer)
        self.canSplit = 1 if self.player[0] == self.player[1] and self.player[2] == 0 else 0
        self.canDouble1 = 1 if self.player[1] != 0 and self.player[2] == 0 else 0
        index1 = len([card for card in self.player if card != 0])        
        if action != 0:
            if action == 1 and self.canSplit == 1: #split
                if self.print_info:
                    print("split")
                self.split = True
                self.player2[0] = self.player[0]
                self.player2_hand = self.player2[0]
                self.player[1] = self.next_card()
                if self.player[1] == 11:
                    self.player_ace_count += 1
            elif action == 2 and self.canDouble1 == 1: #double
                if self.print_info:
                    print("double")
                self.double1 = True
                self.player[index1] = self.next_card()
                if self.player[index1] == 11:
                    self.player_ace_count += 1
                index1 += 1
                action = 0
            elif action == 3: #hit
                if self.print_info:
                    print("hit")
                self.player[index1] = self.next_card()
                if self.player[index1] == 11:
                    self.player_ace_count += 1
                index1 += 1
            self.player_hand = sum(self.player)
            if self.player_hand > 21:
                for j in range(10):
                    if self.player[j] == 11:
                        self.player[j] = 1
                        self.player_hand = sum(self.player)
                        break
            self.canDouble1 = 0
            self.canSplit = 0
            self.player_hand = sum(self.player)
        if self.print_info:
            print("stay")
        action = 0
        self.award_points()
        self.player_hand = sum(self.player)
        if self.player_hand > 21:
            for j in range(0, 9):
                if self.player[j] == 11:
                    self.player[j] = 1
        self.player_hand = sum(self.player)
        self.decks_remaining = (312 - self.current_card) // 52
        
        if action == 1 and self.canSplit == 0:
            self.reward = -1000
        if action == 2 and self.canDouble1 == 0:
            self.reward = -1000

        return self.reward, self.balance, self.decks_remaining, action

    def play_step2(self, action):
        self.player_hand = sum(self.player)
        self.player_hand2 = sum(self.player2)
        self.dealer_hand = sum(self.dealer)
        self.canSplit = 0
        index2 = len([card for card in self.player if card != 0])
        if self.player2[1] == 0:
            self.player2[1] = self.next_card()
            if self.player2[1] == 11:
                    self.player2_ace_count += 1
            self.canDouble2 = 1
        if action != 0:
            if action == 1 and self.canSplit == 1:
                if self.print_info:
                    print("split on split")
                action = 0
            if action == 2 and self.canDouble2 == 1: #double
                if self.print_info:
                    print("double on split")
                self.double2 = True
                self.player2[index2] = self.next_card()
                if self.player2[index2] == 11:
                    self.player2_ace_count += 1
                index2 += 1
                action = 0
            elif action == 3: #hit
                if self.print_info:
                    print("hit on split")
                self.player2[index2] = self.next_card()
                if self.player2[index2] == 11:
                    self.player2_ace_count += 1
                index2 += 1
            if self.player2_hand > 21:
                for j in range(10):
                    if self.player2[j] == 11:
                        self.player2[j] = 1
                        self.player2_hand -= 10
                        break
            self.canDouble2 = 0
        if self.print_info:
            print("stay")
        action = 0
        self.award_points()

        self.decks_remaining = (312 - self.current_card) // 52
        if action == 1 and self.canSplit == 0:
            self.reward = -1000
        if action == 2 and self.canDouble2 == 0:
            self.reward = -1000
        
        return self.reward, self.balance, self.decks_remaining, action

    def deal(self):
        self.decks_remaining = 6

        if self.print_info:
            print("Balance:", self.balance)

        self.decks_remaining = (312 - self.current_card) // 52

        #if self.print_info:
            #print("bet", bet)
            #print("count", self.count)

        self.dealer[0] = self.next_card()
        if self.dealer[0] == 11:
            self.dealer_ace_count += 1

        self.player[0] = self.next_card()
        if self.player[0] == 11:
            self.player_ace_count += 1
        self.player[1] = self.next_card()
        if self.player[1] == 11:
            self.player_ace_count += 1

        if self.player[0] == 1 and self.player[1] == 10 or self.player[0] == 10 and self.player[1] == 1:
            self.balance = self.change_amount(self.balance, self.bet * 1.5)
            return

        self.canDouble = 1
        if self.player[0] == self.player[1]:
            self.canSplit = 1
        self.player_hand = sum(self.player)
        self.player_hand2 = sum(self.player2)
        self.dealer_hand = sum(self.dealer)
        
    
    def evaluate(self):
        self.player_hand = sum(self.player)
        self.player_hand2 = sum(self.player2)
        self.dealer_hand = sum(self.dealer)
        if self.print_info:
            print("Dealer value:", self.dealer_hand)
            print("Player value:", self.player_hand)
            print("Player2 value:", self.player2_hand)
            print("Dealer hand:", *self.dealer)
            print("Player hand:", *self.player)
            print("Player2 hand:", *self.player2)


        
        if self.player_hand > 21:
            if self.print_info:
                print("Dealer Wins")
            if self.double1:
                self.balance = self.change_amount(self.balance, -self.bet * 2)
                self.double1 = False
            else:
                self.balance = self.change_amount(self.balance, -self.bet)
        else:
            if self.dealer_hand > 21:
                if self.print_info:
                    print("Player Wins")
                if self.double1:
                    self.balance = self.change_amount(self.balance, self.bet * 2)
                    self.double1 = False
                else:
                    self.balance = self.change_amount(self.balance, self.bet)
            else:
                if self.player_hand > self.dealer_hand:
                    if self.print_info:
                        print("Player Wins")
                    if self.double1:
                        self.balance = self.change_amount(self.balance, self.bet * 2)
                        self.double1 = False
                    else:
                        self.balance = self.change_amount(self.balance, self.bet)
                elif self.player_hand < self.dealer_hand:
                    if self.print_info:
                        print("Dealer Wins")
                    if self.double1:
                        self.balance = self.change_amount(self.balance, -self.bet * 2)
                        self.double1 = False
                    else:
                        self.balance = self.change_amount(self.balance, -self.bet)
                elif self.player_hand == self.dealer_hand:
                    self.double1 = False
                    if self.print_info:
                        print("Draw")

        if self.split:
            if self.player2_hand > 21:
                if self.print_info:
                    print("Dealer Wins second hand")
                if self.double2:
                    self.balance = self.change_amount(self.balance, -self.bet * 2)
                    self.double2 = False
                else:
                    self.balance = self.change_amount(self.balance, -self.bet)
                self.split = False
            else:
                if self.dealer_hand > 21:
                    if self.print_info:
                        print("Player Wins  second hand")
                    if self.double2:
                        self.balance = self.change_amount(self.balance, self.bet * 2)
                        self.double2 = False
                    else:
                        self.balance = self.change_amount(self.balance, self.bet)
                    self.split = False
                else:
                    if self.player2_hand > self.dealer_hand:
                        if self.print_info:
                            print("Player Wins second hand")
                        if self.double2:
                            self.balance = self.change_amount(self.balance, self.bet * 2)
                            self.double2 = False
                        else:
                            self.balance = self.change_amount(self.balance, self.bet)
                        self.split = False
                    elif self.player2_hand < self.dealer_hand:
                        if self.print_info:
                            print("Dealer Wins second hand")
                        if self.double2:
                            self.balance = self.change_amount(self.balance, -self.bet * 2)
                            self.double2 = False
                        else:
                            self.balance = self.change_amount(self.balance, -self.bet)
                        self.split = False
                    elif self.player2_hand == self.dealer_hand:
                        self.double2 = False
                        if self.print_info:
                            print("Draw second hand")
                        self.split = False
        return self.balance
    
    def dealerTurn(self):
        self.dealer[1] = self.next_card()
        if self.dealer[1] == 11:
            self.dealer_ace_count += 1
        self.player_hand = sum(self.player)
        self.player_hand2 = sum(self.player2)
        self.dealer_hand = sum(self.dealer)
        
        x = 2
        while self.dealer_hand < 17:
            self.dealer[x] = self.next_card()
            if self.dealer[x] == 11:
                self.dealer_ace_count += 1
            self.dealer_hand = sum(self.dealer)
            if self.dealer_hand > 21:
                for j in range(0, 9):
                    if self.dealer[j] == 11:
                        self.dealer[j] = 1
            x += 1
            self.dealer_hand = sum(self.dealer)

        
        self.dealer_hand = sum(self.dealer)
    
    def award_points(self):
        self.player_hand = sum(self.player)
        self.player_hand2 = sum(self.player2)
        self.dealer_hand = sum(self.dealer)
        if self.player[1] == 0:
            if self.player_hand > 21:
                if self.double1:
                    self.reward += -self.bet * 2 * 2
                else:
                    self.reward += -self.bet * 2
            else:
                if self.dealer_hand > 21:
                    if self.double1:
                        self.reward += self.bet * 2
                    else:
                        self.reward += self.bet
                else:
                    if self.player_hand > self.dealer_hand:
                        if self.double1:
                            self.reward += self.bet * 2
                        else:
                            self.reward += self.bet
                    elif self.player_hand < self.dealer_hand:
                        if self.double1:
                            self.reward += -self.bet * 2 * 2
                        else:
                            self.reward += -self.bet * 2
                    elif self.player_hand == self.dealer_hand:
                        self.reward += 0
        else:
            if self.split:
                if self.player2_hand > 21:
                    if self.double1:
                        self.reward += -self.bet * 2 * 2
                    else:
                        self.reward += -self.bet * 2
                else:
                    if self.dealer_hand > 21:
                        if self.double1:
                            self.reward += self.bet * 2
                        else:
                            self.reward += self.bet
                    else:
                        if self.player2_hand > self.dealer_hand:
                            if self.double1:
                                self.reward += self.bet * 2
                            else:
                                self.reward += self.bet
                        elif self.player2_hand < self.dealer_hand:
                            if self.double1:
                                self.reward += -self.bet * 2 * 2
                            else:
                                self.reward += -self.bet * 2
                        elif self.player2_hand == self.dealer_hand:
                            self.reward += -self.bet

    def change_amount(self, balance, bet):
        balance += bet
        return balance

    def count_cards(self, card):
        if card in [2, 3, 4, 5, 6]:
            self.count += 1
        elif card in [10, 11, 12, 13, 1]:
            self.count -= 1
        return self.count

    def next_card(self):
        card = self.deck.pop()
        self.count_cards(card)
        self.current_card += 1
        return card
