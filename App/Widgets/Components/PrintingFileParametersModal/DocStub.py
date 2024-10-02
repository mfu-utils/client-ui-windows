from PySide6.QtWidgets import QLabel, QWidget

from App.Widgets.Components.DrawableWidget import DrawableWidget
from App.Widgets.UIHelpers import UIHelpers


class DocStub(DrawableWidget):
    def __init__(self, message: str, parent: QWidget = None):
        super(DocStub, self).__init__(parent)

        self.setObjectName("PrintingFileParameterNoViewWidget")

        self.__no_view_layout = UIHelpers.v_layout((0, 0, 0, 0), 10)

        self.__no_view_layout.addStretch()

        self.__no_view_image_layout = UIHelpers.h_layout((0, 0, 0, 0), 0)
        self.__no_view_image_layout.addStretch()
        self.__no_view_image = UIHelpers.image('no_view_64x64@2x.png')
        self.__no_view_image.setObjectName("PrintingFileParameterNoViewImage")
        self.__no_view_image_layout.addWidget(self.__no_view_image)
        self.__no_view_image_layout.addStretch()
        self.__no_view_layout.addLayout(self.__no_view_image_layout)

        self.__no_view_label_layout = UIHelpers.h_layout((0, 0, 0, 0), 0)
        self.__no_view_label_layout.addStretch()
        self.__no_view_label = QLabel(message, self)
        self.__no_view_label.setObjectName("PrintingFileParameterNoViewLabel")
        self.__no_view_label_layout.addWidget(self.__no_view_label)
        self.__no_view_label_layout.addStretch()
        self.__no_view_layout.addLayout(self.__no_view_label_layout)

        self.__no_view_layout.addStretch()

        self.setLayout(self.__no_view_layout)
