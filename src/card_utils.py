import random


class Card:
    suit_name = {0: 'Oros', 1: 'Copes', 2: 'Espases', 3: 'Bastos'}
    suit_index = {'Oros': 0, 'Copes': 1, 'Espases': 2, 'Bastos': 3}

    def __init__(self, suit, number, points=0):
        if isinstance(suit, int):
            self.suit = suit
        elif isinstance(suit, str) and suit in Card.suit_index:
            self.suit = Card.suit_index[suit]
        else:
            print("Invalid suit {}. Suit set to 'Oros'".format(suit))
            self.suit = 0
        self.number = number
        self.points = points
        self.value = 0
        self.wining_probability = 0

    def __str__(self):
        return '{} {}'.format(self.number, Card.suit_name[self.suit])

    def __eq__(self, other):
        if other.suit == self.suit and other.number == self.number:
            return True
        else:
            return False


class Stack:
    def __init__(self):
        self.cards = list()
        self.owner = list()

    def add(self, card, owner):
        self.cards.append(card)
        self.owner.append(owner)

    def min_points(self, victory_suit, victory_suit_penalty):
        points = list()
        for c in self.cards:
            p = c.points
            if c.suit == victory_suit:
                p += victory_suit_penalty
            points.append(p)
        return points.index(min(points)), min(points)

    def max_points(self):
        points = list()
        for c in self.cards:
            points.append(c.points)
        return points.index(max(points)), max(points)

    def clear(self):
        self.cards.clear()
        self.owner.clear()

    def card_index(self, card):
        return self.cards.index(card)

    def get(self, i):
        assert i < len(self.cards), 'Stack overflow!'
        return self.cards[i]

    def __len__(self):
        return len(self.cards)

    def __str__(self):
        ret = ''
        if len(self.owner) < len(self.cards):
            for c in self.cards:
                ret += str(c) + '\n'
        else:
            for i in range(len(self.cards)):
                ret += str(self.cards[i]) + '[' + self.owner[i] + ']\n'
        return ret


class Deck:
    def __init__(self):
        self.cards = list()
        for s in range(4):
            for n in range(1, 13):
                self.cards.append(Card(s, n))

    def __str__(self):
        ret = ''
        for c in self.cards:
            ret += str(c) + '\n'
        return ret

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self, number):
        number = min(number, len(self.cards))
        ret = self.cards[0:number]
        self.cards = self.cards[number:]
        if len(ret) == 0:
            return None
        elif len(ret) == 1:
            return ret[0]
        return ret

    def remove_card(self, card):
        try:
            idx = self.cards.index(card)
        except:
            idx = -1

        if idx >= 0:
            del self.cards[idx]
        return idx
