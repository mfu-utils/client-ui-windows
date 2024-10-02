import os.path
import sys

from PySide6.QtWidgets import QWidget, QTextBrowser

from App.Core.Utils import Str
from config import VERSION_SHOW, VERSION_DETAILED, VERSION_BUILD_DATE, STATIC_LICENSE_URL
from config import STATIC_REPO_URL, STATIC_REPO_NAME, STATIC_LICENSE_NAME, RCL_PROTOCOL_VERSION
from App.Core import Filesystem
from App.Widgets.Modals.AbstractModal import AbstractModal
from App.Widgets.UIHelpers import UIHelpers
from App.helpers import config, styles, platform, lc, machine
from config import ROOT


class AboutModal(AbstractModal):
    def __init__(self, parent: QWidget = None):
        super(AboutModal, self).__init__(parent)
        self.__central_layout = UIHelpers.h_layout()
        self.setFixedSize(470, 250)
        self.setWindowTitle(lc("aboutModal.title"))

        _styles = ["aboutModal", "qMenu"]

        if platform().is_darwin():
            _styles.append("qMenuMacFix")

        self.setStyleSheet(styles(_styles))

        self.__image = UIHelpers.image('logo.png', self, (64, 64))

        self.__image_layout = UIHelpers.v_layout((0, 0, 0, 0), 0)
        self.__image_layout.addSpacing(10)
        self.__image_layout.addWidget(self.__image)
        self.__image_layout.addStretch()

        self.__central_layout.addLayout(self.__image_layout)

        self.__text = QTextBrowser(self)
        self.__text.setObjectName("AboutModalTextBrowser")
        self.__text.setOpenExternalLinks(True)
        self.__text.setText(
            Str.replace_templated(Filesystem.read_file(os.path.join(ROOT, 'assets', 'text', 'about.html')), {
                "appName": f"{config('app.name')} {VERSION_SHOW}",
                "versionTitle": lc("aboutModal.build"),
                "version": VERSION_DETAILED,
                "arch": machine().name,
                "buildDate": VERSION_BUILD_DATE,
                "licenseTitle": lc("aboutModal.license"),
                "licenseName": STATIC_LICENSE_NAME,
                "licenseUrl": STATIC_LICENSE_URL,
                "repoTitle": lc("aboutModal.repo"),
                "repoName": STATIC_REPO_NAME,
                "repoUrl": STATIC_REPO_URL,
                "pythonVersionTitle": lc("aboutModal.python_version"),
                "pythonVersion": sys.version,
                "protoTitle": lc("aboutModal.proto"),
                "rclProtoVersion": str(RCL_PROTOCOL_VERSION),
            })
        )

        self.__central_layout.addWidget(self.__text)

        self.centralWidget().setLayout(self.__central_layout)

        self._disable_all_parents()

        self.show()

        UIHelpers.to_center(self, UIHelpers.find_parent_recursive(self, "MainWindow"))
