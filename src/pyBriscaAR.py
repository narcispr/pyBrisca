import numpy as np
import cv2
from cv2 import aruco
import matplotlib.pyplot as plt
import matplotlib as mpl
from pyBrisca import Deck, Stack, check_victory_hand, BriscaPlayerSimpleAI, set_card_points
import pyttsx3
import time


def create_ar_markers():
    aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_100)
    fig = plt.figure()
    nx = 8
    ny = 6
    for i in range(1, nx*ny+1):
        ax = fig.add_subplot(ny,nx, i)
        img = aruco.drawMarker(aruco_dict,i, 700)
        plt.imshow(img, cmap = mpl.cm.gray, interpolation = "nearest")
        ax.axis("off")

    plt.savefig("markers.pdf")
    plt.show()


def get_image_from_webcam(frame_name):
    cam = cv2.VideoCapture(0)
    cv2.namedWindow("WebCam")

    while True:
        ret, frame = cam.read()
        cv2.imshow("WebCam", frame)
        if not ret:
            break
        k = cv2.waitKey(1)

        if k % 256 == 27:
            # ESC pressed
            print("Escape hit, closing...")
            break
        elif k % 256 == 32:
            # SPACE pressed
            cv2.imwrite(frame_name, frame)
            break

    cam.release()
    cv2.destroyAllWindows()


def ar_marker_detection(frame_name):
    frame = cv2.imread(frame_name)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_100)
    parameters = aruco.DetectorParameters_create()
    corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
    frame_markers = aruco.drawDetectedMarkers(frame.copy(), corners, ids)
    plt.figure()
    plt.imshow(frame_markers)
    for i in range(len(ids)):
        c = corners[i][0]
        plt.plot([c[:, 0].mean()], [c[:, 1].mean()], "o", label="id={0}".format(ids[i]))
    plt.legend()
    plt.show()


def get_marker_id():
    cam = cv2.VideoCapture(0)
    # cv2.namedWindow("WebCam")
    time = 0
    aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_100)
    parameters = aruco.DetectorParameters_create()
    card_id = -1

    while time < 125:
        ret, frame = cam.read()
        # cv2.imshow("WebCam", frame)
        if not ret:
            break
        k = cv2.waitKey(1)

        if k % 256 == 27:
            # ESC pressed
            print("Escape hit, closing...")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
        time += 1
        if ids is not None:
            card_id = ids[0][0]
            break
    cam.release()
    cv2.destroyAllWindows()
    return card_id


class BriscaARGame:
    def __init__(self, players_name, player_idx, player):
        assert len(players_name) <= 4, '2, 3 or 4 players only!'
        assert player_idx < len(players_name), 'Invalid players index!'

        self.players_name = players_name
        self.player_idx = player_idx
        self.player = player
        self.next_player = 0
        self.victory_card = None
        self.player_points = list()
        for i in range(len(players_name)):
            self.player_points.append(0)
        self.list_of_seen_cards = list()

        self.engine = pyttsx3.init()
        self.engine.setProperty('voice', 'catalan')

    def announce(self, text):
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
        card = Deck.get_card_id(card_id)
        set_card_points(card)
        print('Card points: {}'.format(card.points))
        return card

    def player_order(self):
        order = list()
        for i in range(self.next_player, len(self.players_name)):
            order.append(i)
        for i in range(0, self.next_player):
            order.append(i)
        return order

    def game(self):
        confirmed = False
        while not confirmed:
            self.announce("Ensenya'm el trumfo...")
            self.victory_card = self.get_card()
            self.announce('El trumfo és el {}?'.format(self.victory_card))
            answ = input("El trumfo es {}? (S/N)".format(self.victory_card))
            if answ == 's' or answ == 'S':
                confirmed = True
        self.list_of_seen_cards.pop()

        self.announce('Reparteix-me 3 cartes, siusplau!')
        for i in range(3):
            self.player.hand.cards.append(self.get_card())
            if i < 2:
                self.announce('La següent...')


        for i in range(int(48/len(self.players_name))):
            print('Ma {} de {}'.format(i, int(48/len(self.players_name))))
            order = self.player_order()
            table = Stack()
            for p in order:
                # self.announce('Es el torn del jugador {}'.format(self.players_name[p]))
                if p == self.player_idx:
                    idx, played_card = self.player.play(table, self.victory_card.suit)
                    self.announce('Agafeu la carta en posicio {}, que és un {}.'.format(idx + 1, played_card))
                else:
                    self.announce('Ensenyem la carta que vols jugar {}.'.format(self.players_name[p]))
                    played_card = self.get_card()
                    table.add(played_card, self.players_name[p])
                    print('El jugador {} baixa la carta {}.'.format(self.players_name[p], played_card))

            for c in table.cards:
                print('{} --> points: {}, value: {}'.format(c, c.points, c.value))

            owner, card, points = check_victory_hand(table, self.victory_card.suit)
            self.next_player = self.players_name.index(owner)
            self.player_points[self.next_player] += points

            if points > 0:
                self.announce("El jugador {} ha guanyat la ma i ha fet {} punts".format(owner, points))
            else:
                self.announce("El jugador {} ha guanyat la ma. Palla pel burro!".format(owner))

            if i < int(48/len(self.players_name)) - 3:
                self.announce('Donem una carta i col·locala en posició 3')
                self.player.hand.cards.append(self.get_card())

        for i, p in enumerate(self.player_points):
            print('{}: {} punts'.format(self.players_name[i], p))
        a = max(self.player_points)
        idx = self.player_points.index(a)
        if idx == self.player_idx:
            self.announce('Us he fotut una pallisa! Ha ha ha ha!!!')
        else:
            self.announce('Ha guanyat el jugador {}. Felicitats!'.format(self.players_name[idx]))

        @staticmethod
        def get_marker_id():
            cam = cv2.VideoCapture(0)
            # cv2.namedWindow("WebCam")
            time = 0
            aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_100)
            parameters = aruco.DetectorParameters_create()
            card_id = -1

            while time < 125:
                ret, frame = cam.read()
                # cv2.imshow("WebCam", frame)
                if not ret:
                    break
                k = cv2.waitKey(1)

                if k % 256 == 27:
                    # ESC pressed
                    print("Escape hit, closing...")
                    break

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
                time += 1
                if ids is not None:
                    card_id = ids[0][0]
                    break
            cam.release()
            cv2.destroyAllWindows()
            return card_id


if __name__ == '__main__':
    # create_ar_markers()
    # get_image_from_webcam('image.png')
    # ar_marker_detection('image.png')

    # print('Show card to camera')
    # card_id = get_marker_id()
    # if card_id > 0:
    #     print('Seen card: {}'.format(card_id))
    # else:
    #     print('No card seen!')

    params = dict()
    params['victory_suit_penalty'] = 3.5
    p1 = BriscaPlayerSimpleAI('Simple-AI', params)
    brisca = BriscaARGame(['narcís', p1.name, 'Lídia'], 1, p1)
    brisca.game()
