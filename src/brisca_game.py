from card_utils import Stack
from brisca_utils import check_victory_hand, BriscaDeck
from brisca_players import BriscaPlayerSimpleAI, BriscaPlayerHuman, BriscaPlayerRandom


class BriscaGame:
    def __init__(self, players_list):
        assert len(players_list) > 1, "At least 2 player!"
        assert len(players_list) <= 4, "Maximum 4 players!"
        self.num_players = len(players_list)
        self.players = players_list
        self.next_player = 0
        self.deck = BriscaDeck()
        self.deck.shuffle()
        self.central_card = self.deck.cards[-1]
        print('Trumfo: {}'.format(self.central_card))
        for player in self.players:
            player.set_up(self.central_card.suit, len(players_list))
            player.hand = Stack()
            hand = self.deck.deal(3)
            for c in hand:
                player.receive_card(c)

    def player_order(self):
        order = list()
        for j in range(self.next_player, len(self.players)):
            order.append(j)
        for j in range(0, self.next_player):
            order.append(j)
        return order

    def round(self):
        table = Stack()
        for v, player_idx in enumerate(self.player_order()):
            idx, played_card = self.players[player_idx].play(table)
            print('Jugador {}: baixa {}'.format(self.players[player_idx].name, played_card))

        owner, card, points = check_victory_hand(table, self.central_card.suit)

        for j, player in enumerate(self.players):
            player.clear_table(table)
            if player.name == owner:
                player.points += points
                self.next_player = j
        for j in self.player_order():
            new_card = self.deck.deal(1)
            if new_card is not None:
                self.players[j].receive_card(new_card)

    def game(self):
        # Play rounds
        while len(self.players[0].hand) > 0:
            self.round()

        # Check winner
        max_points = -1
        winner_idx = -1
        winner = None
        for j, player in enumerate(self.players):
            if player.points > max_points:
                max_points = player.points
                winner = player.name
                winner_idx = j
        print('El guanyador es el jugador {}: {} amb {} punts.'.format(winner_idx, winner, max_points))
        return winner_idx, max_points

    def __str__(self):
        ret = 'Carta central: ' + str(self.central_card) + '\n'
        for player in self.players:
            ret += 'Ma: {}\n{}'.format(player.name, str(player.hand))

        return ret


if __name__ == '__main__':
    params = dict()
    params['victory_suit_penalty'] = 3.5
    # victory_suit_penalty --> amb 2 jugadors millor posar 3.5 amb 4 jugadors no ho tinc clar...
    p1 = BriscaPlayerSimpleAI('Simple-AI_1', params)
    p2 = BriscaPlayerSimpleAI('Simple-AI_2', params)

    players = [p1, p2]
    brisca = BriscaGame(players)
    result = brisca.game()
