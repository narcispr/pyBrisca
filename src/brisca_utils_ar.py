from cv2 import aruco
import matplotlib.pyplot as plt
import matplotlib as mpl


def create_ar_markers():
    aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_100)
    fig = plt.figure()
    nx = 8
    ny = 6
    for i in range(1, nx*ny+1):
        ax = fig.add_subplot(ny,nx, i)
        img = aruco.drawMarker(aruco_dict,i, 700)
        plt.imshow(img, cmap=mpl.cm.gray, interpolation="nearest")
        ax.axis("off")

    plt.savefig("markers.pdf")
    plt.show()
