import math
import matplotlib.pyplot as plt
import numpy as np
import random
import shapely.affinity
from shapely.geometry import Polygon
import unittest

from python.src.mrr_calculator import get_mrr_angle_of_long_side, get_mrr_dims

# these points represent the item we are interested in
# it is 8 units long and 2 units tall
# feel free to change the values, but keep the long side on the
# x-axis and shorter side on the y-axis
base_item_points = [[-4, 1], [4, 1], [4, -1], [-4, -1]]

# number of random shapes to create in one of the tests (completely arbitrary)
# if this number is increased too much
RAND_TEST_COUNT = 20

# this variable allows the user to set how accurate the angle calculation is
# if 1, it means that 100% of the values returned by the calculator are used for comparison
# any value less than 1 corresponds to that percent accuracy
# so if the value is 0.5, that means the about half of the comparisons should fail
# the test values should fail
# this is mainly just to show off the fancy lines when the prediction is wrong
ACCURACY_FACTOR = 1


class TestBoundingBox(unittest.TestCase):

    def setUp(self):
        """
        Shared setup for each unit test
        :return:
        """
        self.pass_angles = []    # correctly calculated angles for the given test
        self.fail_angles = []    # incorrectly calculated angles
        plt.clf()                # clear any previous plots
        self.ax = plt.subplot()  # axis where angled lines will be drawn
        self.shapes = []         # shapes in each test (to check for overlap)

    def test_single(self):
        """
        Simple test of the bounding box calculator
        Create a shape, rotate it and calculate the rotation using the target function
        :return:
        """
        exp_rotation = 60
        shape = Polygon(base_item_points)
        shape = shapely.affinity.rotate(shape, exp_rotation)
        act_rotation = get_mrr_angle_of_long_side(shape)
        self.assertEqual(exp_rotation, act_rotation)

        # bonus validation to check the length and width match expected
        x_vals = np.array(base_item_points)[:, 0]
        y_vals = np.array(base_item_points)[:, 1]
        exp_length = max(x_vals) - min(x_vals)
        exp_width = max(y_vals) - min(y_vals)
        act_length, act_width = get_mrr_dims(shape)
        self.assertEqual(round(exp_length), round(act_length))
        self.assertEqual(round(exp_width), round(act_width))

    def test_hardcoded(self):
        """
        Test rotations using a set of predefined angles
        :return:
        """
        test_angles = [0, 15, 38, 45, 120, 135, 156, 179]
        for exp_rotation in test_angles:
            shape, exp_rotation = self.generate_shape(exp_rotation)
            act_rotation = get_mrr_angle_of_long_side(shape)
            act_length, act_width = get_mrr_dims(shape)
            if random.random() >= ACCURACY_FACTOR:
                act_rotation = random.randint(0, 179)

            self.plot_shape(shape, exp_rotation, act_rotation, act_length)
            self.check_rotation(exp_rotation, act_rotation)

        plt.savefig("mrr_test_hardcoded.png")
        plt.show()
        self.check_test("hardcoded angles", len(test_angles))

    def test_random(self):
        """
        Test with randomly generated rotation angles
        :return:
        """
        for i in range(RAND_TEST_COUNT):
            shape, exp_rotation = self.generate_shape()
            act_rotation = get_mrr_angle_of_long_side(shape)
            act_length, act_width = get_mrr_dims(shape)
            if random.random() >= ACCURACY_FACTOR:
                act_rotation = random.randint(0, 179)

            self.plot_shape(shape, exp_rotation, act_rotation, act_length)
            self.check_rotation(exp_rotation, act_rotation)

        plt.savefig("mrr_test_random.png")
        plt.show()
        self.check_test("randomly generated angles", RAND_TEST_COUNT)

    def generate_shape(self, rotation=None):
        """
        Generate a shape using the base item as a starting point
        The shape will be rotated around its center, randomly scaled,
        and translated to a random area (checking for overlap with other shapes)
        :param rotation: Degree to rotate around shape's center
                         If not given, a random angle will be generated
        :return: The generated shape and degrees it is rotated
        """
        # either the caller gives an expected rotation or an angle is randomly generated
        if rotation is None:
            rotation = random.randint(0, 179)

        # same random scale for x and y dirs
        scale = (random.random() + 1) * 6

        # translate to a random center
        x_off, y_off = random.randrange(-100, 100), random.randrange(-100, 100)

        # create and modify the shape
        shape = Polygon(base_item_points)
        shape = shapely.affinity.rotate(shape, rotation)
        shape = shapely.affinity.scale(shape, scale, scale)
        shape = shapely.affinity.translate(shape, x_off, y_off)

        # move the shape around the plot until it does not overlap other shapes
        shape_hit = self.check_shape_overlap(shape)
        try_count = 0
        while shape_hit:
            try_count += 1
            # translate to a random center
            x_off, y_off = random.randrange(-100, 100), random.randrange(-100, 100)
            shape = shapely.affinity.translate(shape, x_off, y_off)
            shape_hit = self.check_shape_overlap(shape)

            # after 5 failed attempts, give up and just return the shape that overlaps
            # this avoids an infinite loop if RAND_TEST_COUNT is too high
            if try_count >= 5:
                break

        # keep track of all shapes in each test
        self.shapes.append(shape)

        return shape, rotation

    def check_shape_overlap(self, shape):
        """
        Check for overlap between all shapes in the given test
        :param shape: New shape to check
        :return: True if the new shape overlaps any existing shape,
                 False if there are no overlaps (shape can be added)
        """
        for test_shape in self.shapes:
            if shape.intersects(test_shape):
                return True
        return False

    def plot_shape(self, shape, exp_rotation, act_rotation, length):
        """
        Add the shape to the shared plot, fill with a random color.
        The expected and actual (calculated) rotation values are provided.
            If they match, a white line will be drawn from center to an edge at the target angle.
            If they do not match, a black line will be
        :param shape:
        :param exp_rotation:
        :param act_rotation:
        :param length:
        :return:
        """
        box_x, box_y = shape.exterior.xy
        plt.fill(box_x, box_y, c=np.random.rand(3, ))
        line_length = length / 2
        # pass case: expected and actual match, draw a single white line at angle
        if exp_rotation == act_rotation:
            self.draw_angle_line(shape.centroid, exp_rotation, line_length, text=str(exp_rotation))
        # fail case: draw a black line at expected rotation, red line at calculated angle
        else:
            text = f"{exp_rotation} != {act_rotation}"
            self.draw_angle_line(shape.centroid, act_rotation, line_length, color='red')
            self.draw_angle_line(shape.centroid, exp_rotation, line_length, color='black', text=text)
    #
    def draw_angle_line(self, point, angle, length, color='white', text=None):
        """
        Draw a line starting at the given point extending at the given angle
        Optionally add a text label
        Based on https://stackoverflow.com/questions/28417604/plotting-a-line-from-a-coordinate-with-and-angle
        """
        # starting point
        x, y = point.x, point.y

        # find the end point
        end_x = x + length * math.cos(math.radians(angle))
        end_y = y + length * math.sin(math.radians(angle))

        # plot the points
        self.ax.plot([x, end_x], [y, end_y], c=color)

        # if text was given, add it offset from the start point
        if text:
            text_x = x - length / 2 * math.cos(math.radians(angle))
            text_y = y - length / 2 * math.sin(math.radians(angle))
            self.ax.text(text_x, text_y, text, c="black")

    def check_rotation(self, exp_rotation, act_rotation):
        """
        Compare expected vs. actual and append to pass/fail list
        :param exp_rotation:
        :param act_rotation:
        :return:
        """
        if exp_rotation == act_rotation:
            self.pass_angles.append(exp_rotation)
        else:
            print(f"Rotation failed: {exp_rotation=} != {act_rotation=}")
            self.fail_angles.append(exp_rotation)

    def check_test(self, test_name, exp_pass_count):
        """
        Verify the correct number of shape rotation calculations were hit,
        raise an exception if not
        :param test_name:
        :param exp_pass_count:
        :return:
        """
        self.assertEqual(len(self.pass_angles), exp_pass_count, f"Failed {test_name}")


if __name__ == '__main__':
    unittest.main()
