import sys
import time

from PyQt4 import QtGui, QtCore


def main():
    app = QtGui.QApplication(sys.argv)

    main_window = QtGui.QWidget()

    main_layout = QtGui.QVBoxLayout()

    elements_groups = [
        get_selection_elements('Pictures folder'),
        get_selection_elements('Data folder'),
        get_selection_elements('Output folder'),
    ]

    main_layout.addLayout(create_grid_layout(elements_groups))

    build_heatmaps_btn = QtGui.QPushButton('Build heatmaps')
    main_layout.addWidget(build_heatmaps_btn)
    progress_bar = QtGui.QProgressBar()
    progress_bar.setMinimum(1)
    progress_bar.setMaximum(100)
    main_layout.addWidget(progress_bar)
    main_window.setWindowTitle('Image heatmap builder')
    main_window.setLayout(main_layout)
    main_window.show()
    def loop():
        for i in range(2, 100):
            progress_bar.setValue(i)
            app.processEvents()
            time.sleep(0.05)
    QtCore.QTimer().singleShot(0, loop)


    sys.exit(app.exec_())
    # directory = QtGui.QFileDialog().getExistingDirectory(main_window)


def get_selection_elements(label_text):
    label = QtGui.QLabel('%s:' % label_text)
    line_edit = QtGui.QLineEdit()
    button = QtGui.QPushButton('Select directory')
    return label, line_edit, button


def create_grid_layout(elements_groups):
    grid_layout = QtGui.QGridLayout()
    for row_index, elements_group in enumerate(elements_groups):
        for col_index, element in enumerate(elements_group):
            grid_layout.addWidget(element, row_index, col_index)
    return grid_layout

if __name__ == '__main__':
    main()
