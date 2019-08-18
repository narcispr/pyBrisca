import unittest
import sys
from card_utils import Deck, Stack, Card
from brisca_utils import set_card_points, calculate_card_value, check_victory_hand
from brisca_players import BriscaPlayerBase


class BriscaUtilsTestCase(unittest.TestCase):
    def setUp(self):
        self.hand = Stack()
        self.hand.cards.append(Card(0, 1))
        self.hand.cards.append(Card(1, 3))
        self.hand.cards.append(Card(2, 10))
        self.victory_card = Card(0, 9, 0, 0)

    def test_set_card_points(self):
        deck = Deck()
        points = 0
        for c in deck.cards:
            set_card_points(c)
            points += c.points
        print("Total points in a brisca deck is {}".format(points))
        self.assertEqual(points, 120, 'A whole brisca deck must contain 120 points!')

    def test_calculate_card_value(self):
        hand_card_values = list()
        for c in self.hand.cards:
            set_card_points(c)
            calculate_card_value(c, self.victory_card.suit)
            hand_card_values.append(c.value)
        self.assertEqual(hand_card_values, [35, 22, 14], 'Card values has changed!')

    def test_check_victory_hand(self):
        table = Stack()
        table.add(Card(1, 10, 2), 'player1')
        table.add(Card(1, 1, 11), 'player2')
        owner, card, points = check_victory_hand(table, self.victory_card.suit)
        self.assertEqual(owner, 'player2', '1 must wins over 10')
        table.add(Card(0, 2, 0), 'player3')
        owner, card, points = check_victory_hand(table, self.victory_card.suit)
        self.assertEqual(owner, 'player3', 'Oros must wins over Copes')


class BriscaPlayerTestCase(unittest.TestCase):
    def setUp(self):
        params = dict()
        self.player = BriscaPlayerBase('player-AI', params)
        self.deck = Deck()
        self.deck.shuffle()

    def test_unseen_cards(self):
        self.assertEqual(len(self.player.unseen_cards.cards), 48, 'Initially must be 48 unseen cards!')
        self.player.receive_card(self.deck.deal(1))
        self.player.receive_card(self.deck.deal(1))
        self.player.receive_card(self.deck.deal(1))
        self.assertEqual(len(self.player.unseen_cards.cards), 45, 'After receiving 1st hand must be 45 unseen cards!')
        print('Unseen cards after receiving 1st hand: {}'.format(len(self.player.unseen_cards.cards)))

if __name__ == '__main__':
    # unittest.main()
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    unittest.TextTestRunner(verbosity=3).run(suite)