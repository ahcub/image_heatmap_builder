import sys
from glob import glob

from PyQt4 import QtGui
from os.path import join, splitext, basename


class ImageHeatMapBuilder:
    def __init__(self):
        self.main_window = None
        self.progress_bar = None
        self.pictures_dir = ''
        self.pictures_data_dir = ''
        self.output_dir = ''

    def start(self):
        app = QtGui.QApplication(sys.argv)
        self.main_window = QtGui.QWidget()
        main_layout = QtGui.QVBoxLayout()

        elements_groups = [
            self.get_selection_elements('Pictures folder', 'pictures_dir'),
            self.get_selection_elements('Data folder', 'pictures_data_dir'),
            self.get_selection_elements('Output folder', 'output_dir'),
        ]

        main_layout.addLayout(create_grid_layout(elements_groups))

        build_heatmaps_btn = QtGui.QPushButton('Build heatmaps')
        build_heatmaps_btn.clicked.connect(self.build_heatmaps)
        main_layout.addWidget(build_heatmaps_btn)

        self.progress_bar = QtGui.QProgressBar()
        self.progress_bar.setMinimum(0)
        main_layout.addWidget(self.progress_bar)

        self.main_window.setWindowTitle('Image heatmap builder')
        self.main_window.setLayout(main_layout)
        self.main_window.show()
        sys.exit(app.exec_())

    def get_selection_elements(self, label_text, property_name):
        label = QtGui.QLabel('%s:' % label_text)
        line_edit = QtGui.QLineEdit()
        button = QtGui.QPushButton('Select directory')
        button.clicked.connect(self.directory_select_callback(property_name))
        return label, line_edit, button

    def directory_select_callback(self, property_name):
        if property_name not in self.__dict__:
            raise ValueError("No %s property found in object %s" % (property_name, self))

        def callback():
            self.__dict__[property_name] = QtGui.QFileDialog().getExistingDirectory(self.main_window)

        return callback

    def build_heatmaps(self):
        # TODO: add check for valid directories
        tasks_data_sets = []
        for image_file in glob(join(self.pictures_dir, '*.png')):
            #TODO: add check for picture data exists
            data_file_name = splitext(basename(image_file))[0] + '.csv'
            data_file_path = join(self.pictures_data_dir, data_file_name)
            tasks_data_sets.append((image_file, ))


def create_grid_layout(elements_groups):
    grid_layout = QtGui.QGridLayout()
    for row_index, elements_group in enumerate(elements_groups):
        for col_index, element in enumerate(elements_group):
            grid_layout.addWidget(element, row_index, col_index)
    return grid_layout

