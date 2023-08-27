import math
import numpy as np

# if two points have x values less than this far away from each other,
# treat the polygon as vertical (to avoid a divide by 0)
VERTICAL_THRESHOLD = 0.001


def get_mrr_angle_of_long_side(polygon):
    """
    Return the rotation of the min. rotated rectangle for the
    given shapely polygon in degrees.
    For our purposes, the object in the bounding box is longer in the
    x dir than it is wider in the y dir (at 0 degrees rotation).
    We want to know how much the long side is rotated about the polygon's center.
    """
    box = list(polygon.minimum_rotated_rectangle.exterior.coords)

    # get length of both sides or the mrr
    start_pt = box[0]
    len_side_1 = math.dist(start_pt, box[1])
    len_side_2 = math.dist(start_pt, box[3])

    # compare both sides and use the longer side as the length (side of interest)
    if len_side_1 >= len_side_2:
        end_pt = box[1]
    else:
        end_pt = box[3]

    # calculate the distances between the x and y of both points
    x_dist = start_pt[0] - end_pt[0]
    y_dist = start_pt[1] - end_pt[1]

    # if the points are effectively above each other, call it 90 degrees rotated
    # this avoids a divide by 0 error
    if abs(x_dist) <= VERTICAL_THRESHOLD:
        return 90

    # rise over run to get the slope
    slope = y_dist / x_dist

    # the magic, use the arc tan of the slope to find the
    # angle relative to the box's center
    # https://www.mathopenref.com/arctan.html
    angle_rad = math.atan(slope)
    angle_deg = np.rad2deg(angle_rad)
    # I only care about the angle to the nearest degree, your needs may vary
    angle = round(angle_deg)
    # similarly, my target object is symmetric about the y-axis,
    # so a rotation of 181 is the same as a rotation of 1
    angle = restrict_0_to_180(angle)

    return angle


def get_mrr_dims(polygon):
    """
    Return the length and width of the min. rotated rectangle of the given shapely polygon.
    The longer side will always be treated as the length, shorter side as width.
    """
    box = list(polygon.minimum_rotated_rectangle.exterior.coords)

    # get length of both sides or the mrr
    start_pt = box[0]
    len_side_1 = math.dist(start_pt, box[1])
    len_side_2 = math.dist(start_pt, box[3])

    # compare both sides and use the longer side as the length, shorter as width
    if len_side_1 >= len_side_2:
        length, width = len_side_1, len_side_2
    else:
        length, width = len_side_2, len_side_1

    return length, width

def restrict_0_to_180(degree):
    """
    Ensure the input value is restricted between 0 and 180
    :param degree:
    :return:
    """
    while degree < 0:
        degree += 180
    return degree % 180
