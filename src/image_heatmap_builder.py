import sys
from glob import glob
from logging import getLogger
from os.path import join, splitext, basename, isfile, isdir, dirname

from PyQt4 import QtGui

from src.heatmap_utils import build_heatmap_on_image
from src.opeational_utils import configure_file_and_stream_logger, configure_file_logger, mkpath

SLEEP_TIME = 0.05
WINDOW_HEIGHT = 200
WINDOW_WIDTH = 600

logger = getLogger()

main_log_path = join(dirname(sys.argv[0]), 'image_heatmap_builder.log')
configure_file_and_stream_logger(filename=main_log_path)
errors_log_path = join(dirname(sys.argv[0]), 'errors.log')
configure_file_logger(errors_log_path, level='ERROR')


class ImageHeatMapBuilder:
    def __init__(self):
        self.app = None
        self.main_window = None
        self.main_layout = None
        self.progress_bar = None
        self.error_dialog = None
        self.building_heatmaps = False

        self.images_dir = ''
        self.images_data_dir = ''
        self.output_dir = ''

        self.rotate_logs()

    @staticmethod
    def rotate_logs():
        open(main_log_path, 'w').close()
        open(errors_log_path, 'w').close()

    def start(self):
        self.app = QtGui.QApplication(sys.argv)
        self.main_window = QtGui.QWidget()
        self.main_window.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.main_layout = QtGui.QVBoxLayout()
        self.error_dialog = QtGui.QErrorMessage()
        elements_groups = [
            self.get_selection_elements('Images folder', 'images_dir'),
            self.get_selection_elements('Images data folder', 'images_data_dir'),
            self.get_selection_elements('Output folder', 'output_dir'),
        ]

        self.main_layout.addLayout(create_grid_layout(elements_groups))

        build_heatmaps_btn = QtGui.QPushButton('Build heatmaps')
        build_heatmaps_btn.clicked.connect(self.build_heatmaps)
        self.main_layout.addWidget(build_heatmaps_btn)

        self.progress_bar = QtGui.QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(1)
        self.progress_bar.setValue(0)
        self.main_layout.addWidget(self.progress_bar)

        self.main_window.setWindowTitle('Image heatmap builder')
        self.app.setWindowIcon(QtGui.QIcon(join(dirname(sys.argv[0]), 'heatmap_icon.png')))
        self.main_window.setLayout(self.main_layout)
        self.main_window.show()
        self.app.aboutToQuit.connect(self.cleanup_dialog_obj)
        sys.exit(self.app.exec_())

    def cleanup_dialog_obj(self):
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def get_selection_elements(self, label_text, property_name):
        label = QtGui.QLabel('%s:' % label_text)
        line_edit = QtGui.QLineEdit()
        line_edit.editingFinished.connect(self.directory_select_callback(property_name, line_edit, getter='line_edit'))
        button = QtGui.QPushButton('Select directory')
        button.clicked.connect(self.directory_select_callback(property_name, line_edit))
        return label, line_edit, button

    def directory_select_callback(self, property_name, line_edit_widget, getter='dialog'):
        if property_name not in self.__dict__:
            raise ValueError("No %s property found in object %s" % (property_name, self))

        def callback():
            if getter == 'dialog':
                directory = QtGui.QFileDialog().getExistingDirectory(self.main_window)
                line_edit_widget.setText(directory)
            else:
                directory = line_edit_widget.text()

            self.__dict__[property_name] = str(directory)
            logger.info('Setting %s to %s', property_name, self.__dict__[property_name])

        return callback

    def build_heatmaps(self):
        if not self.building_heatmaps:
            self.building_heatmaps = True
            try:
                if self.valid_directories():
                    errors = self.build_images_heatmaps()
                    if errors:
                        self.process_tasks_errors(errors)
            finally:
                self.building_heatmaps = False
        else:
            self.error_dialog.showMessage('Building heatmaps already started')

    def valid_directories(self):
        errors = []

        if not isdir(self.images_dir):
            if self.images_dir:
                errors.append('Images directory %s not found' % self.images_dir)
            else:
                errors.append('Select images directory')
        if not isdir(self.images_data_dir):
            if self.images_data_dir:
                errors.append('Data directory %s not found' % self.images_data_dir)
            else:
                errors.append('Select images data directory')

        if not self.output_dir:
            errors.append('Select output directory')

        if not errors:
            images = self.get_images()
            if images:
                for image_path in images:
                    data_file_path, _ = self.get_image_related_paths(image_path)
                    if not isfile(data_file_path):
                        errors.append('No corresponding data file found for %s. Ensure %s file exists' %
                                      (basename(image_path), data_file_path))
            else:
                errors.append('Could not found any image file')

        if errors:
            self.process_tasks_errors(errors)
            return False

        return True

    def get_images(self):
        return list(glob(join(self.images_dir, '*.png')))

    def get_image_related_paths(self, image_file):
        image_file_name_base, image_file_ext = splitext(basename(image_file))
        data_file_path = join(self.images_data_dir, image_file_name_base + '.csv')
        output_file_path = join(self.output_dir, image_file_name_base + '_with_heatmap' + image_file_ext)
        return data_file_path, output_file_path

    def build_images_heatmaps(self):
        errors = []
        mkpath(self.output_dir)
        images = self.get_images()
        self.progress_bar.setMaximum(len(images))
        for index, image_file in enumerate(images):
            data_file_path, output_file_path = self.get_image_related_paths(image_file)
            logger.info('Starting task for %s' % image_file)
            try:
                build_heatmap_on_image(image_file, data_file_path, output_file_path)
            except Exception as e:
                errors.append('Failed to build heatmap for %s. Error message: %s' % (image_file, e))
            else:
                logger.info('creation heatmap for %s is complete' % image_file)
            finally:
                self.progress_bar.setValue(index + 1)
                self.app.processEvents()
        return errors

    def process_tasks_errors(self, errors):
        error_message = 'Error occurred while creating heatmaps'
        if len(errors) > 5:
            error_message += '<br>More than 5 errors found. Check errors.log for more details'
        else:
            error_message += '<br>'
            error_message += '<br>'.join(errors)
        self.error_dialog.showMessage(error_message)
        logger.info('Error occurred while creating heatmaps')
        for err in errors:
            logger.error(err)


def create_grid_layout(elements_groups):
    grid_layout = QtGui.QGridLayout()
    for row_index, elements_group in enumerate(elements_groups):
        for col_index, element in enumerate(elements_group):
            grid_layout.addWidget(element, row_index, col_index)
    return grid_layout

# TODO: TEST PLAN
# Error messages
#   missing images dir
#   missing data dir
#   images dir is empty
#   some corresponding data is not found
#   task execution failed
#   errors are dumped into errors.log
#
# HeatMaps
#   heatmaps built properly for all images
#
