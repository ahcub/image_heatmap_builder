import csv

import Image
from heatmap import Heatmap


def build_heatmap_on_image(image_path, outfile_path, data_file_path, save_only_heatmap=False):
    img = Image.open(image_path)
    hm = Heatmap()
    coordinates = read_coordinates(data_file_path)
    img_heatmap = hm.heatmap(coordinates, size=img.size, area=((0, 0), img.size))
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
