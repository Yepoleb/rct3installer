import sys
from PyQt5.QtWidgets import (QApplication, QWizard, QWizardPage, QLabel, 
    QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QFileDialog, QCheckBox,
    QProgressBar)
from PyQt5.QtCore import Qt

PROGRAM_NAME = "RollerCoaster Tycoon 3"

PAGE_INTRO = 0
PAGE_INSTALLER = 1
PAGE_PREFIX_EXISTS = 2
PAGE_CREATING_PREFIX = 3
PAGE_EXTRACTING = 4
PAGE_COPYING = 5
PAGE_DONE = 6

class InstallWizard(QWizard):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setPage(PAGE_INTRO, IntroPage())
        self.setPage(PAGE_INSTALLER, InstallerPage())
        self.setPage(PAGE_PREFIX_EXISTS, PrefixExistsPage())
        self.setPage(PAGE_CREATING_PREFIX, CreatingPrefixPage())
        self.setPage(PAGE_EXTRACTING, ExtractingPage())
        self.setPage(PAGE_COPYING, CopyingPage())
        
        self.setWindowTitle("{} Install Wizard".format(PROGRAM_NAME))
    
class IntroPage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setTitle("Introduction")
        
        intro_label = QLabel("Welcome to the installer of {}".format(PROGRAM_NAME))
        intro_label.setWordWrap(True)
        
        layout = QVBoxLayout()
        layout.addWidget(intro_label)
        self.setLayout(layout)

class InstallerPage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setTitle("Select Installer")
        #self.setSubTitle("Select the setup file you want to use to install {}".format(PROGRAM_NAME))
        label = QLabel("Select the setup file you want to use to install {}".format(PROGRAM_NAME))
        label.setWordWrap(True)
        
        self.path_edit = QLineEdit()
        path_button = QPushButton("Choose")
        
        self.registerField("installer_path", self.path_edit)
        path_button.clicked.connect(self.choose_path)
        
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(path_button)
        
        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addLayout(path_layout)
        
        self.setLayout(layout)
    
    def choose_path(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Setup File")
        if file_path:
            self.path_edit.setText(file_path)

class PrefixExistsPage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setTitle("Recreate Prefix")
        
        label = QLabel("The default prefix for this game already exists. Do you want to recreate it?")
        label.setWordWrap(True)
        
        checkbox = QCheckBox("Recreate")
        checkbox.setCheckState(Qt.Checked)
        self.registerField("recreate_prefix", checkbox)
        
        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(checkbox)
        
        self.setLayout(layout)

class CreatingPrefixPage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setTitle("Creating Prefix")
        
        label = QLabel("Creating a new prefix, please wait...")
        label.setWordWrap(True)
        
        busybar = QProgressBar()
        busybar.setMinimum(0)
        busybar.setMaximum(0)
        
        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(busybar)
        
        self.setLayout(layout)

class ExtractingPage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setTitle("Extracting Files")
        
        label = QLabel("Extracting game files, please wait...")
        label.setWordWrap(True)
        
        self.current_file = QLabel("Test file name")
        self.current_file.setWordWrap(True)
        
        self.progress = QProgressBar()
        self.progress.setValue(0)
        
        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(self.current_file)
        layout.addWidget(self.progress)
        
        self.setLayout(layout)

class CopyingPage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setTitle("Copying Files")
        
        label = QLabel("Copying game files, please wait...")
        label.setWordWrap(True)
        
        busybar = QProgressBar()
        busybar.setMinimum(0)
        busybar.setMaximum(0)

        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(busybar)
        
        self.setLayout(layout)

class DonePage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setTitle("Installation Done")
        
        label = QLabel("Installation of {} has finished. You can close this window now.")
        label.setWordWrap(True)
        
        layout = QVBoxLayout()
        layout.addWidget(label)
        
        self.setLayout(layout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    wizard = InstallWizard()
    wizard.show()
    sys.exit(app.exec_())
