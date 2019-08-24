import random
from card_utils import Stack
from brisca_utils import calculate_card_value, BriscaDeck


class BriscaPlayerBase:
    def __init__(self, name, params=None):
        self.name = name
        self.hand = Stack()
        self.points = 0
        self.params = params
        self.unseen_cards = BriscaDeck()
        self.table = Stack()
        self.num_players = 0
        self.victory_suit = None
        self.is_set_up = False

    def set_up(self, victory_suit, num_players):
        self.victory_suit = victory_suit
        self.num_players = num_players
        self.is_set_up = True

    def __str__(self):
        ret = self.name + ': \n'
        ret += str(self.hand)
        return ret

    def receive_card(self, card):
        self.hand.cards.append(card)
        self.unseen_cards.remove_card(card)

    def clear_table(self, table):
        for c in table.cards:
            self.unseen_cards.remove_card(c)

    def play(self, table):
        assert self.is_set_up, 'First set up player!'

        self.table = table
        for c in table.cards:
            self.unseen_cards.remove_card(c)

        for c in self.hand.cards:
            c.wining_probability = 0

        idx = self.select_card()

        table.add(self.hand.cards[idx], self.name)
        played_card = self.hand.cards[idx]
        del self.hand.cards[idx]
        return idx, played_card

    def select_card(self):
        print('Not implemented in Base!')
        return -1

    def get_candidate_cards(self):
        candidates = Stack()
        max_value_table = -1
        for c in self.table.cards:
            calculate_card_value(c, self.victory_suit, self.table.cards[0].suit)
            if c.value > max_value_table:
                max_value_table = c.value
        for c in self.hand.cards:
            if len(self.table) > 0:
                calculate_card_value(c, self.victory_suit, self.table.cards[0].suit)
                if c.value > max_value_table:
                    candidates.add(c, self.name)
            else:
                calculate_card_value(c, self.victory_suit, c.suit)
                candidates.add(c, self.name)
        return candidates

    def get_unseen_cards_that_win(self, card):
        suit = card.suit
        if len(self.table) > 0:
            suit = self.table.cards[0].suit
        calculate_card_value(card, self.victory_suit, suit)
        wining_cards = Stack()
        for c in self.unseen_cards.cards:
            calculate_card_value(c, self.victory_suit, suit)
            if c.value > card.value:
                wining_cards.add(c, 'unknown')
        return wining_cards

    def probability_of_having_n_card_from_m(self, n, m):
        probability = 0
        unseen = len(self.unseen_cards.cards)
        for i in range(m):
            probability += (1 - probability) * (n/unseen)
            unseen -= 1
        return probability


class BriscaPlayerHuman(BriscaPlayerBase):
    def select_card(self):
        print('Cartes jugades:')
        for c in self.table.cards:
            print(c)

        candidates = self.get_candidate_cards()
        remaining_cards = (len(self.hand) * (self.num_players - len(self.table) - 1))
        for c in candidates.cards:
            wc = self.get_unseen_cards_that_win(c)
            c.wining_probability = 1 - self.probability_of_having_n_card_from_m(len(wc), remaining_cards)

        print("Ma {}:".format(self.name))
        for i, c in enumerate(self.hand.cards):
            print('{}: {} ({}%)'.format(i, c, int(c.wining_probability * 100)))

        idx = -1
        while idx < 0 or idx >= len(self.hand.cards):
            idx = int(input("Carta a jugar: "))
        return idx


class BriscaPlayerRandom(BriscaPlayerBase):
    def select_card(self):
        idx = int(random.random() * len(self.hand.cards))
        return idx


class BriscaPlayerSimpleAI(BriscaPlayerBase):
    def select_card(self):
        # Rule of play:
        # * If first player or can not win plays the card with less points.
        # * If can win (according to current cars in the table) and there are points in table or in the 'winning card',
        #   plays the 'winning card' with more points. Otherwise plays the card with less points.
        idx = self.hand.min_points(self.victory_suit, self.params['victory_suit_penalty'])[0]
        if len(self.table.cards) > 0:
            max_value_table = -1
            points_table = 0
            candidates = Stack()
            for c in self.table.cards:
                points_table += c.points
                calculate_card_value(c, self.victory_suit, self.table.cards[0].suit)
                if c.value > max_value_table:
                    max_value_table = c.value
            for c in self.hand.cards:
                calculate_card_value(c, self.victory_suit, self.table.cards[0].suit)
                if c.value > max_value_table:
                    candidates.cards.append(c)
            if len(candidates.cards) > 0 and (points_table > 0 or candidates.max_points()[1] > 0):
                idx = self.hand.cards.index(candidates.cards[candidates.max_points()[0]])

        return idx
