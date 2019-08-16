import random


class Card:
    suit_name = {0: 'Oros', 1: 'Copes', 2: 'Espases', 3: 'Bastos'}

    def __init__(self, suit, number, points, value):
        self.suit = suit
        self.number = number
        self.points = points
        self.value = value

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

    def __str__(self):
        ret = ''
        if len(self.owner) < len(self.cards):
            for c in self.cards:
                ret += str(c) + '\n'
        else:
            for i in len(self.cards):
                ret += str(self.cards[i]) + '[' + self.owner[i] + ']\n'
        return ret


class Deck:
    def __init__(self):
        self.cards = list()
        for s in range(4):
            for n in range(1, 13):
                self.cards.append(Card(s, n, 0, 0))

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

    @staticmethod
    def get_card_id(id):
        suit = int((id - 1)/12)
        assert suit < 4, 'Invalid card id'
        number = (id - suit*12)
        assert number <= 12, 'Invalid card id'
        return Card(suit, number, 0, 0)


class BriscaPlayerBase:
    def __init__(self, name, params=None):
        self.name = name
        self.hand = Stack()
        self.points = 0
        self.params = params

    def __str__(self):
        ret = self.name + ': \n'
        ret += str(self.hand)
        return ret

    def play(self, table, victory_suit=None):
        print('Not implemented in player {}'.format(self.name))


class BriscaPlayerHuman(BriscaPlayerBase):
    def play(self, table, victory_suit=None):
        print('Cartes jugades:')
        for c in table.cards:
            print(c)
        print("Ma {}:".format(self.name))
        for i, c in enumerate(self.hand.cards):
            print('{}: {}'.format(i, c))
        idx = -1
        while idx < 0 or idx >= len(self.hand.cards):
            idx = int(input("Carta a jugar: "))
        table.add(self.hand.cards[idx], self.name)
        del self.hand.cards[idx]


class BriscaPlayerRandom(BriscaPlayerBase):
    def play(self, table, victory_suit=None):
        idx = int(random.random() * len(self.hand.cards))
        print('Jugador {}: baixa {}'.format(self.name, self.hand.cards[idx]))
        table.add(self.hand.cards[idx], self.name)
        del self.hand.cards[idx]


class BriscaPlayerSimpleAI(BriscaPlayerBase):
    def play(self, table, victory_suit=None):

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
            if len(candidates.cards) > 0 and (points_table > 0  or candidates.max_points()[1] > 0):
                idx = self.hand.cards.index(candidates.cards[candidates.max_points()[0]])

        # print('Jugador {}: baixa {}'.format(self.name, self.hand.cards[idx]))
        table.add(self.hand.cards[idx], self.name)
        played_card = self.hand.cards[idx]
        del self.hand.cards[idx]
        return idx, played_card


class BriscaGame:
    def __init__(self, players):
        assert len(players) > 0, "Almenys 1 jugador!"
        assert len(players) <= 4, "Maxim 4 jugadors!"
        self.num_players = len(players)
        self.players = players
        self.next_player = 0
        self.deck = Deck()
        for c in self.deck.cards:
            self.set_card_points(c)
        self.deck.shuffle()
        self.central_card = self.deck.cards[-1]
        print('Trumfo: {}'.format(self.central_card))
        for p in self.players:
            p.hand = Stack()
            p.hand.cards = self.deck.deal(3)

    def player_order(self):
        order = list()
        for i in range(self.next_player, len(self.players)):
            order.append(i)
        for i in range(0, self.next_player):
            order.append(i)
        return order

    def round(self):
        table = Stack()
        for p in self.player_order():
            self.players[p].play(table, self.central_card.suit)

        owner, card, points = check_victory_hand(table, self.central_card.suit)

        for i, p in enumerate(self.players):
            if p.name == owner:
                p.points += points
                self.next_player = i
        for i in self.player_order():
            new_card = self.deck.deal(1)
            if new_card is not None:
                self.players[i].hand.cards.append(new_card)

    def game(self):
        while len(self.players[0].hand.cards) > 0:
            self.round()
        max_points = -1
        winner = None
        for i, p in enumerate(self.players):
            if p.points > max_points:
                max_points = p.points
                winner = p.name
                winner_idx = i

        print('El guanyador es el jugador {}: {} amb {} punts.'.format(winner_idx, winner, max_points))
        return winner_idx, max_points

    def __str__(self):
        ret = 'Carta central: ' + str(self.central_card) + '\n'

        for p in self.players:
            ret += 'Ma: {}\n{}'.format(p.name, str(p.hand))

        return ret


def check_victory_hand(table, victory_suit):
    print('Victory suit: {}'.format(victory_suit))
    points = 0
    max_value = -1
    owner = None
    card = None
    for i, c in enumerate(table.cards):
        calculate_card_value(c, victory_suit, table.cards[0].suit)
        points += c.points
        if c.value > max_value:
            owner = table.owner[i]
            card = c
            max_value = c.value
    print('La carta guanyadora es {} de {}\n\n'.format(card, owner))
    return owner, card, points


def calculate_card_value(card, victory_suit, hand_suit=None):
    if hand_suit is None:
        hand_suit = card.suit
    if card.suit == victory_suit:
        card.value = card.points + 24
    elif card.suit == hand_suit:
        card.value = card.points + 12
    if card.number == 4:
        card.value += 0.1
    if card.number == 5:
        card.value += 0.2
    if card.number == 6:
        card.value += 0.3
    if card.number == 7:
        card.value += 0.4
    if card.number == 8:
        card.value += 0.5
    if card.number == 9:
        card.value += 0.6


def set_card_points(card):
    if card.number == 1:
        card.points = 11
    elif card.number == 2:
        card.points = 0
    elif card.number == 3:
        card.points = 10
    elif card.number == 4:
        card.points = 0
    elif card.number == 5:
        card.points = 0
    elif card.number == 6:
        card.points = 0
    elif card.number == 7:
        card.points = 0
    elif card.number == 8:
        card.points = 0
    elif card.number == 9:
        card.points = 0
    elif card.number == 10:
        card.points = 2
    elif card.number == 11:
        card.points = 3
    elif card.number == 12:
        card.points = 4

if __name__ == '__main__':

    total_points = [0, 0]
    for i in range(10000):
        p0 = BriscaPlayerHuman('Lidia')
        params = dict()
        params['victory_suit_penalty'] = 0
        p1 = BriscaPlayerSimpleAI('Simple-AI_1', params)
        params['victory_suit_penalty'] = 3.5
        p2 = BriscaPlayerSimpleAI('Simple-AI_2', params)
        p3 = BriscaPlayerRandom('Random')

        players = [p2, p3]
        # random.shuffle(players)
        brisca = BriscaGame(players)
        result = brisca.game()

        total_points[result[0]] += 1

    for i, p in enumerate(total_points):
       print('Player {}: {} points'.format(i, p))

# victory_suit_penalty --> amb 2 jugadors millor posar 3.5 amb 4 jugadors no ho tinc clar...