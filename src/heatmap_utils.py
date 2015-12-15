import csv

import sys
from logging import getLogger

from PIL import Image, ImageFilter
from heatmap import Heatmap
from os.path import dirname, join

logger = getLogger()


def build_heatmap_on_image(image_path, data_file_path, outfile_path, heatmap_settings=None, save_only_heatmap=False):
    if heatmap_settings is None:
        heatmap_settings = {}
    img = Image.open(image_path)
    img.load()
    if heatmap_settings.get('monochrome_image'):
        img = img.convert('L')
    img = img.convert('RGBA')

    coordinates = convert_y_coordinate(read_coordinates(data_file_path), img.size[1])
    if 'single_point_exclude_radius' in heatmap_settings:
        coordinates = filter_single_dots_with_radius(coordinates, heatmap_settings['single_point_exclude_radius'],
                                                     heatmap_settings['required_near_points_in_radius'])

    dotsize = heatmap_settings.get('dotsize', 70)
    hm = Heatmap(libpath=join(dirname(sys.argv[0]), 'cHeatmap-x86.dll'))
    img_heatmap = hm.heatmap(coordinates, size=img.size, area=((0, 0), img.size), dotsize=dotsize, opacity=150)
    img_heatmap = img_heatmap.filter(ImageFilter.GaussianBlur(3))
    if save_only_heatmap:
        img_heatmap.save(outfile_path)
    else:
        out_file = Image.alpha_composite(img, img_heatmap)
        out_file.save(outfile_path)


def read_coordinates(coordinates_file_path):
    with open(coordinates_file_path) as coordinates_file:
        csv_reader = csv.reader(coordinates_file)
        result = []
        for row in csv_reader:
            x, y = row
            result.append((int(x), int(y)))
        return result


def convert_y_coordinate(coordinates_set, image_height):
    return [(x, image_height - y) for x, y in coordinates_set]


def filter_single_dots_with_radius(coordinates, radius, required_amount):
    result = []
    for coord in coordinates:
        near_dots_within_circle = [dot for dot in coordinates if is_dot_in_circle(dot, coord, radius)]
        logger.debug('Dots within a circle %s', near_dots_within_circle)
        if len(near_dots_within_circle) >= required_amount:
            result.append(coord)
    return result


def is_dot_in_circle(dot, circle_centre, radius):
    is_in_circle = (((dot[0] - circle_centre[0]) ** 2) + ((dot[1] - circle_centre[1]) ** 2)) <= radius ** 2
    if is_in_circle:
        logger.debug('Dot %s is inside circle with center in %s and with radius %s', dot, circle_centre, radius)
    else:
        logger.debug('Dot %s is filtered for circle with center in %s and with radius %s', dot, circle_centre, radius)
    return is_in_circle
