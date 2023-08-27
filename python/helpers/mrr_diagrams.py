from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt
import numpy as np
import shapely.affinity
from shapely.geometry import Polygon


def show_mrr():
    """
    Draw a rectangle rotated 45 degrees about its center
    Label all points and length/width
    Draw a bounding box and MRR around the rectangle
    :return:
    """
    plt.axis('off')
    fig, ax = plt.subplots()
    ax.axhline(y=0, color='k', alpha=0.25)
    ax.axvline(x=0, color='k', alpha=0.25)

    shape_rotation = 45
    base_item_points = [[-4, 1], [4, 1], [4, -1], [-4, -1]]

    shape = Polygon(base_item_points)
    shape = shapely.affinity.rotate(shape, shape_rotation)

    box_x, box_y = shape.exterior.xy
    plt.fill(box_x, box_y, c="gray")

    # regular bounding box
    bbox = shape.bounds
    bbox_x, bbox_y = bbox[0], bbox[1]
    width, height = (bbox[2] - bbox_x), (bbox[3] - bbox_y)
    currentAxis = plt.gca()
    currentAxis.add_patch(Rectangle((bbox_x, bbox_y), width, height, fill=None, alpha=1, color="green", linewidth=2))
    plt.text(-3, 3, "Bounding Box", c="green")

    # minimum rotated rectangle
    mrr_x, mrr_y = shape.minimum_rotated_rectangle.exterior.coords.xy
    plt.plot(mrr_x, mrr_y, color="red", linewidth=2)
    plt.text(-3, 2, "Minimum Rotated Rectangle", c="red")

    # plot the points
    ax.plot([0, 2.8], [0, 2.8], c="black", alpha=0.75)
    ax.plot([0, 2.8], [0, 0], c="black", alpha=0.75)
    ax.plot([2.8, 2.8], [0, 2.8], c="black", alpha=0.75)
    plt.text(1, 0.5, r'$\theta=45$', c="black")

    plt.show()

def label_diagram():
    plt.clf()
    fig, ax = plt.subplots()
    ax.axhline(y=0, color='k', alpha=0.25)
    ax.axvline(x=0, color='k', alpha=0.25)

    shape_rotation = 45
    base_item_points = [[-4, 1], [4, 1], [4, -1], [-4, -1]]

    shape = Polygon(base_item_points)
    shape = shapely.affinity.rotate(shape, shape_rotation)

    box = list(shape.minimum_rotated_rectangle.exterior.coords)
    print(f"MRR {box}")

    box_x, box_y = shape.exterior.xy
    plt.fill(box_x, box_y, c="gray")

    # label the length and width
    ax.plot([box[0][0], box[3][0]], [box[0][1], box[3][1]], c="green", linewidth=2)
    ax.annotate("length", (-2, 1), color="green")

    ax.plot([box[0][0], box[1][0]], [box[0][1], box[1][1]], c="red", linewidth=2)
    ax.annotate("width", (-3.5, -3.5), color="red")

    x = np.array(box)[:, 0]
    y = np.array(box)[:, 1]
    labels = ["box[0],box[4]", "box[1]", "box[2]", "box[3]"]
    ax.scatter(x, y)

    for i, txt in enumerate(labels):
        ax.annotate(txt, (x[i], y[i]))

    plt.show()


if __name__ == '__main__':
    show_mrr()
    label_diagram()
