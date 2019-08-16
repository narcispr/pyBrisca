import unittest
from pyBriscaAR import BriscaARGame
from pyBrisca import BriscaPlayerSimpleAI, Card
import random


class BriscaARGAmeTestCase(unittest.TestCase):
    def setUp(self):
        params = dict()
        params['victory_suit_penalty'] = 3.5
        p1 = BriscaPlayerSimpleAI('Simple-AI', params)
        self.brisca = BriscaARGame(['narcís', p1.name], 1, p1)

    def test_get_card(self):
        c1 = Card(int(random.random()*2), int(random.random()*12) + 1, 0, 0)
        print('Show me the {}'.format(c1))
        c2 = self.brisca.get_card()
        print("Seen: {}".format(c2))
        self.assertEqual(c1, c2, 'This card is not the {}'.format(c1))


if __name__ == '__main__':
    unittest.main()