import csv


def build_heatmap_on_image(image_path, outfile_path, data_file_path, save_only_heatmap=False):



def read_coordinates(coordinates_file_path):
    with open(coordinates_file_path) as coordinates_file:
        csv_reader = csv.reader(coordinates_file)
        return [row for row in csv_reader]
