import sys
from glob import glob
from multiprocessing import Pool
from time import sleep

from PyQt4 import QtGui
from os.path import join, splitext, basename

from src.heatmap_utils import build_heatmap_on_image


class ImageHeatMapBuilder:
    def __init__(self):
        self.app = None
        self.main_window = None
        self.progress_bar = None
        self.pictures_dir = ''
        self.pictures_data_dir = ''
        self.output_dir = ''

    def start(self):
        self.app = QtGui.QApplication(sys.argv)
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
        sys.exit(self.app.exec_())

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
        # TODO: setup global lock for running heatmaps construction
        tasks_pool = Pool()
        tasks_registry = []
        for image_file in glob(join(self.pictures_dir, '*.png')):
            # TODO: add check for picture data exists
            # TODO: check is output directory exists
            image_file_name_base, image_file_ext = splitext(basename(image_file))
            data_file_path = join(self.pictures_data_dir, image_file_name_base + '.csv')
            output_file_path = join(self.output_dir, image_file_name_base + '_with_heatmap' + image_file_ext)
            async_result = tasks_pool.apply_async(build_heatmap_on_image, (image_file, data_file_path, output_file_path))
            tasks_registry.append((async_result, image_file))

        self.progress_bar.setMaximum(len(tasks_registry))
        errors = []
        all_tasks_done = False
        while not all_tasks_done:
            all_tasks_done = True
            not_completed_tasks = []
            for task, image_file in tasks_registry:
                if task.read():
                    try:
                        task.get()
                    except Exception as e:
                        errors.append('Failed to build heatmap for %s' % image_file)
                        # TODO: log error reason
                    else:
                        self.progress_bar.setValue(self.progress_bar.value + 1)
                else:
                    not_completed_tasks.append((task, image_file))
                    all_tasks_done = False
                self.app.processEvents()
                sleep(0.05)
            tasks_registry = not_completed_tasks


def create_grid_layout(elements_groups):
    grid_layout = QtGui.QGridLayout()
    for row_index, elements_group in enumerate(elements_groups):
        for col_index, element in enumerate(elements_group):
            grid_layout.addWidget(element, row_index, col_index)
    return grid_layout

