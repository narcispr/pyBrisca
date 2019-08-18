import random
from card_utils import Card, Stack, Deck
from brisca_utils import calculate_card_value


class BriscaPlayerBase:
    def __init__(self, name, params=None):
        self.name = name
        self.hand = Stack()
        self.points = 0
        self.params = params
        self.unseen_cards = Deck()

    def __str__(self):
        ret = self.name + ': \n'
        ret += str(self.hand)
        return ret

    def receive_card(self, card):
        self.hand.cards.append(card)
        self.unseen_cards.remove_card(card)

    def play(self, table, victory_suit=None):
        for c in table.cards:
            self.unseen_cards.remove_card(c)
        idx = self.select_card(table, victory_suit)
        table.add(self.hand.cards[idx], self.name)
        played_card = self.hand.cards[idx]
        del self.hand.cards[idx]
        assert isinstance(played_card, Card)
        return idx, played_card

    def select_card(self,table, victory_suit):
        print('Not implemented in Base!')
        return -1


class BriscaPlayerHuman(BriscaPlayerBase):
    def select_card(self, table, victory_suit):
        print('Cartes jugades:')
        for c in table.cards:
            print(c)
        print("Ma {}:".format(self.name))
        for i, c in enumerate(self.hand.cards):
            print('{}: {}'.format(i, c))
        idx = -1
        while idx < 0 or idx >= len(self.hand.cards):
            idx = int(input("Carta a jugar: "))
        return idx


class BriscaPlayerRandom(BriscaPlayerBase):
    def select_card(self, table, victory_suit):
        idx = int(random.random() * len(self.hand.cards))
        return idx


class BriscaPlayerSimpleAI(BriscaPlayerBase):
    def select_card(self, table, victory_suit):

        # Rule of play:
        # * If first player or can not win plays the card with less points.
        # * If can win (according to current cars in the table) and there are points in table or in the 'winning card',
        #   plays the 'winning card' with more points. Otherwise plays the card with less points.

        idx = self.hand.min_points(victory_suit, self.params['victory_suit_penalty'])[0]
        if len(table.cards) > 0:
            max_value_table = -1
            points_table = 0
            candidates = Stack()
            for c in table.cards:
                points_table += c.points
                calculate_card_value(c, victory_suit, table.cards[0].suit)
                if c.value > max_value_table:
                    max_value_table = c.value
            for c in self.hand.cards:
                calculate_card_value(c, victory_suit, table.cards[0].suit)
                if c.value > max_value_table:
                    candidates.cards.append(c)
            if len(candidates.cards) > 0 and (points_table > 0 or candidates.max_points()[1] > 0):
                idx = self.hand.cards.index(candidates.cards[candidates.max_points()[0]])

        return idx
