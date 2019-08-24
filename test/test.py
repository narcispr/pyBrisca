import unittest
import random
from card_utils import Stack
from brisca_utils import calculate_card_value, check_victory_hand, BriscaDeck, BriscaCard
from brisca_players import BriscaPlayerBase, BriscaPlayerSimpleAI


class CardUtilsTestCase(unittest.TestCase):
    def setUp(self):
        self.hand = Stack()
        self.hand.cards.append(BriscaCard('Oros', 1))
        self.hand.cards.append(BriscaCard('Copes', 3))
        self.hand.cards.append(BriscaCard('Espases', 10))

    def test_stack(self):
        self.assertEqual(self.hand.card_index(BriscaCard('Copes', 3)), 1, '3 Copes should be in position 1')


class BriscaUtilsTestCase(unittest.TestCase):
    def setUp(self):
        self.hand = Stack()
        self.hand.cards.append(BriscaCard('Oros', 1))
        self.hand.cards.append(BriscaCard('Copes', 3))
        self.hand.cards.append(BriscaCard('Espases', 10))
        self.victory_card = BriscaCard('Oros', 9)

    def test_set_card_points(self):
        deck = BriscaDeck()
        points = 0
        for c in deck.cards:
            points += c.points
        print("Total points in a brisca deck is {}".format(points))
        self.assertEqual(points, 120, 'A whole brisca deck must contain 120 points!')

    def test_calculate_card_value(self):
        hand_card_values = list()
        for c in self.hand.cards:
            calculate_card_value(c, self.victory_card.suit, c.suit)
            hand_card_values.append(c.value)
        self.assertEqual(hand_card_values, [35, 22, 14], 'Card values has changed!')

    def test_check_victory_hand(self):
        table = Stack()
        table.add(BriscaCard(1, 10), 'player1')
        table.add(BriscaCard(1, 1), 'player2')
        owner, card, points = check_victory_hand(table, self.victory_card.suit)
        self.assertEqual(owner, 'player2', '1 must wins over 10')
        table.add(BriscaCard(0, 2), 'player3')
        owner, card, points = check_victory_hand(table, self.victory_card.suit)
        self.assertEqual(owner, 'player3', 'Oros must wins over Copes')
        table.clear()
        table.add(BriscaCard('Copes', 4), 'player1')
        table.add(BriscaCard('Copes', 5), 'player2')
        table.add(BriscaCard('Copes', 6), 'player3')
        table.add(BriscaCard('Copes', 7), 'player4')
        owner, card, points = check_victory_hand(table, self.victory_card.suit)
        self.assertEqual(owner, 'player4', '7 must win 4, 5 and 6')
        table.clear()
        table.add(BriscaCard(int(random.random()*4), 1 + int(random.random()*12)), 'player1')
        table.add(BriscaCard(int(random.random()*4), 1 + int(random.random()*12)), 'player2')
        table.add(BriscaCard(int(random.random()*4), 1 + int(random.random()*12)), 'player3')
        table.add(BriscaCard(int(random.random()*4), 1 + int(random.random()*12)), 'player4')
        print('With trumfo = {} and table:'.format(self.victory_card))
        for c in table.cards:
            print(c)
        owner, card, points = check_victory_hand(table, self.victory_card.suit)
        print('winning card is: {}'.format(card))


class BriscaPlayerTestCase(unittest.TestCase):
    def setUp(self):
        params = dict()
        self.player = BriscaPlayerBase('player-AI', params)
        self.deck = BriscaDeck()
        self.deck.shuffle()

        params = dict()
        params['victory_suit_penalty'] = 3.5
        self.player_simple_ai = BriscaPlayerSimpleAI('player-AI-Mem', params)
        self.player_simple_ai.victory_suit = BriscaCard('Oros', 2).suit

    def test_unseen_cards(self):
        self.assertEqual(len(self.player.unseen_cards.cards), 48, 'Initially must be 48 unseen cards!')
        self.player.receive_card(self.deck.deal(1))
        self.player.receive_card(self.deck.deal(1))
        self.player.receive_card(self.deck.deal(1))
        self.assertEqual(len(self.player.unseen_cards.cards), 45, 'After receiving 1st hand must be 45 unseen cards!')
        print('Unseen cards after receiving 1st hand: {}'.format(len(self.player.unseen_cards.cards)))

    def test_brisca_player_candidates(self):
        table = Stack()
        table.add(BriscaCard('Copes', 10), 'player1')
        self.player_simple_ai.hand.add(BriscaCard('Oros', 3), self.player_simple_ai.name)
        self.player_simple_ai.hand.add(BriscaCard('Copes', 8), self.player_simple_ai.name)
        self.player_simple_ai.hand.add(BriscaCard('Copes', 12), self.player_simple_ai.name)
        self.player_simple_ai.table = table
        candidates = self.player_simple_ai.get_candidate_cards()
        self.assertEqual(len(candidates), 2, '2 cards should win current table!')

        table.add(BriscaCard('Oros', 10), 'player2')
        self.player_simple_ai.table = table
        candidates = self.player_simple_ai.get_candidate_cards()
        self.assertEqual(candidates.cards[0], BriscaCard('Oros', 3), 'Only 3 Oros wins!')

    def test_brisca_player_wining_cards(self):
        self.player_simple_ai.table.clear()
        self.player_simple_ai.unseen_cards = BriscaDeck()
        played_card = BriscaCard('Copes', 10)
        wining_cards = self.player_simple_ai.get_unseen_cards_that_win(played_card)
        self.assertEqual(len(wining_cards), 16, 'All Oros (12) plus 1, 3, 12 and 11 of copes (4) win!')

    def test_brisca_player_probability(self):
        self.player.unseen_cards.cards = [BriscaCard('Oros', 1), BriscaCard('Copes', 2), BriscaCard('Bastos', 3),
                                          BriscaCard('Oros', 4), BriscaCard('Copes', 5), BriscaCard('Bastos', 7)]
        p = self.player.probability_of_having_n_card_from_m(2, 6)
        print('Final probability: {}'.format(p))
# if __name__ == '__main__':
#     # unittest.main()
#     suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
#     unittest.TextTestRunner(verbosity=3).run(suite)
