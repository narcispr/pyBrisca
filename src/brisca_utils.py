from card_utils import Deck, Card


class BriscaDeck(Deck):
    def __init__(self):
        Deck.__init__(self)
        for c in self.cards:
            set_card_points(c)

    def get_card_id(card_id):
        suit = int((card_id - 1) / 12)
        assert suit < 4, 'Invalid card id'
        number = (card_id - suit * 12)
        assert number <= 12, 'Invalid card id'
        c = Card(suit, number, 0, 0)
        set_card_points(c)
        return c


def check_victory_hand(table, victory_suit):
    points = 0
    max_value = -1
    owner = None
    card = None
    for j, c in enumerate(table.cards):
        calculate_card_value(c, victory_suit, table.cards[0].suit)
        points += c.points
        if c.value > max_value:
            owner = table.owner[j]
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
