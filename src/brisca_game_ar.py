import time
import random
import cv2
from cv2 import aruco
import pyttsx3
from card_utils import Stack
from brisca_utils import check_victory_hand, BriscaDeck
from brisca_players import BriscaPlayerSimpleAI


def get_marker_id():
    cam = cv2.VideoCapture(0)
    num_frames = 0
    aruco_dict = cv2.aruco.getPredefinedDictionary(aruco.DICT_6X6_100)
    parameters = aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)
    card_id = -1

    while num_frames < 125:
        ret, frame = cam.read()
        if not ret:
            break
        k = cv2.waitKey(1)

        if k % 256 == 27:
            # ESC pressed
            print("Escape hit, closing...")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, rejectedImgPoints = detector.detectMarkers(gray)
        num_frames += 1
        if ids is not None:
            card_id = ids[0][0]
            break
    cam.release()
    cv2.destroyAllWindows()
    return card_id


class BriscaGameAR:
    def __init__(self, names, player_idx, player):
        assert len(names) <= 4, '2, 3 or 4 players only!'
        assert player_idx < len(names), 'Invalid players index!'

        self.players_name = names
        self.player_idx = player_idx
        self.player = player
        self.next_player = 0
        self.victory_card = None
        self.player_points = list()
        for j in range(len(names)):
            self.player_points.append(0)
        self.list_of_seen_cards = list()

        self.engine = pyttsx3.init()
        self.engine.setProperty('voice', 'calatalan')

    def announce(self, text):
        if isinstance(text, list):
            text = text[int(random.random() * len(text))]
        print(text)
        self.engine.say(text)
        self.engine.runAndWait()
        time.sleep(0.5)

    def get_card(self):
        card_id = -1
        while card_id <= 0:
            card_id = get_marker_id()
            if card_id in self.list_of_seen_cards:
                card_id = -1
            else:
                self.list_of_seen_cards.append(card_id)
        card = BriscaDeck.get_card_id(card_id)
        return card

    def player_order(self):
        order = list()
        for j in range(self.next_player, len(self.players_name)):
            order.append(j)
        for j in range(0, self.next_player):
            order.append(j)
        return order

    def game(self):
        confirmed = False
        self.announce(['Hola! Soc en {}, comencem?'.format(self.players_name[self.player_idx]),
                       'Hem dic {}, fem una brisca?'.format(self.players_name[self.player_idx]),
                       'Soc en {}, jugem a la brisca?'.format(self.players_name[self.player_idx])])
        while not confirmed:
            self.announce(["Ensenya'm el trumfo...", "De que va la partida?"])
            self.victory_card = self.get_card()
            self.announce('El trumfo és el {}?'.format(self.victory_card))
            answ = input("El trumfo es {}? (S/N)".format(self.victory_card))
            if answ == 's' or answ == 'S' or answ == 'si' or answ == 'SI' or answ == 'Si':
                confirmed = True
        self.list_of_seen_cards.pop()
        self.player.set_up(self.victory_card.suit, len(self.players_name))

        self.announce(['Reparteix-me 3 cartes, siusplau!', "Dona'm la ma inicial"])
        for j in range(3):
            self.player.receive_card(self.get_card())
            if j < 2:
                self.announce(['La següent...', 'Una més', 'Una altra...'])

        for j in range(int(48 / len(self.players_name))):
            order = self.player_order()
            table = Stack()
            for p in order:
                if p == self.player_idx:
                    idx, played_card = self.player.play(table)
                    self.announce(['Agafeu la carta en posicio {}, que és un {}.'.format(idx + 1, played_card),
                                   'Jugo la carta {} que està en posició {}'.format(played_card, idx + 1),
                                   'Agafa la carta número {} que és un {}'.format(idx + 1, played_card)])
                else:
                    self.announce(['Ensenyem la carta que vols jugar {}.'.format(self.players_name[p]),
                                   'Que jugues {}?'.format(self.players_name[p]),
                                   'Et toca {}. Que tires?'.format(self.players_name[p]),
                                   "Va {}, Ensenya'm la carta".format(self.players_name[p]),
                                   'Següent carta siusplau',
                                   '{}, vas tu.'.format(self.players_name[p]),
                                   '{}, et toca.'.format(self.players_name[p])])
                    played_card = self.get_card()
                    table.add(played_card, self.players_name[p])
                    print('El jugador {} baixa la carta {}.'.format(self.players_name[p], played_card))

            owner, card, points = check_victory_hand(table, self.victory_card.suit)
            self.next_player = self.players_name.index(owner)
            self.player_points[self.next_player] += points

            if points > 0 and owner != self.players_name[self.player_idx]:
                self.announce(["El jugador {} ha guanyat la ma i ha fet {} punts".format(owner, points),
                               "{} punts pel jugador {}".format(points, owner)])
            elif points == 0 and owner != self.players_name[self.player_idx]:
                self.announce(["Guanya el jugador {}".format(owner),
                               "Palla pel burro {}".format(owner)])
            elif owner == self.players_name[self.player_idx]:
                self.announce(["Aquesta ma per mi",
                               "Guanyo jo",
                               "{} punts per mi".format(points)])

            if j < int(48 / len(self.players_name)) - 3:
                self.announce(['Donem una carta i col·locala en posició 3',
                               'Carta siusplau',
                               "M'acosteu la meva carta siusplau?"])
                self.player.receive_card(self.get_card())

        for j, p in enumerate(self.player_points):
            print('{}: {} punts'.format(self.players_name[j], p))
        a = max(self.player_points)
        idx = self.player_points.index(a)
        if idx == self.player_idx:
            self.announce(['Us he fotut una pallisa! Ha ha ha ha!!!',
                           'Ara us he guanyat!',
                           'Aquesta partida la guanyo jo!'])
        else:
            self.announce(['Ha guanyat el jugador {}. Felicitats!'.format(self.players_name[idx]),
                           'Molt bé {}, has guanyat!'.format(self.players_name[idx]),
                           'Aquesta partica la guanya el jugador {}.'.format(self.players_name[idx]), ])


if __name__ == '__main__':
    num_players = int(input('Quats serem a més de jo? '))
    players_name = list()
    if 0 < num_players < 4:
        for i in range(num_players):
            nom = input('Nom jugador/a {}: '.format(i + 1))
            players_name.append(nom)
        nom_ai = input('Tria el meu nom: ')

        params = dict()
        params['victory_suit_penalty'] = 3.5
        p1 = BriscaPlayerSimpleAI(nom_ai, params)
        players_name.append(nom_ai)
        brisca = BriscaGameAR(players_name, len(players_name) - 1, p1)
        brisca.game()
    else:
        print('Hem de ser entre 2 i 4 jugadors!')
