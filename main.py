import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QFileDialog,
    QTextEdit, QVBoxLayout, QHBoxLayout, QStackedWidget
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

SLIDE_TITLES = [
    "Exposure Check",
    "White Balance",
    "Sharpness",
    "Noise Level",
    "Highlights",
    "Shadows",
    "Color Accuracy",
    "Artifacts",
    "Cropping",
    "Final Review"
]

class Slide(QWidget):
    def __init__(self, title):
        super().__init__()
        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")

        self.image_label = QLabel("No Image Loaded")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setFixedHeight(300)
        self.image_label.setStyleSheet("border: 1px solid #ccc;")

        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Enter notes for this slide...")

        layout = QVBoxLayout()
        layout.addWidget(self.title_label)
        layout.addWidget(self.image_label)
        layout.addWidget(self.text_input)
        self.setLayout(layout)

    def set_image(self, image_path):
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            self.image_label.setPixmap(
                pixmap.scaled(
                    self.image_label.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
            )

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt Carousel App")
        self.resize(800, 600)

        self.current_index = 0

        self.upload_btn = QPushButton("Upload Photo + TXT")
        self.upload_btn.clicked.connect(self.upload_pair)

        self.stack = QStackedWidget()
        self.slides = []
        for title in SLIDE_TITLES:
            slide = Slide(title)
            self.slides.append(slide)
            self.stack.addWidget(slide)

        self.prev_btn = QPushButton("Previous")
        self.next_btn = QPushButton("Next")
        self.prev_btn.clicked.connect(self.prev_slide)
        self.next_btn.clicked.connect(self.next_slide)

        nav_layout = QHBoxLayout()
        nav_layout.addWidget(self.prev_btn)
        nav_layout.addWidget(self.next_btn)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.upload_btn)
        main_layout.addWidget(self.stack)
        main_layout.addLayout(nav_layout)
        self.setLayout(main_layout)

        self.update_nav_buttons()

    def upload_pair(self):
        image_file, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", "Images (*.jpg *.png *.jpeg *.tif *.bmp *.raw)"
        )
        if not image_file:
            return

        txt_file, _ = QFileDialog.getOpenFileName(
            self, "Select TXT File", "", "Text Files (*.txt)"
        )
        if not txt_file:
            return

        for slide in self.slides:
            slide.set_image(image_file)

    def next_slide(self):
        if self.current_index < self.stack.count() - 1:
            self.current_index += 1
            self.stack.setCurrentIndex(self.current_index)
        self.update_nav_buttons()

    def prev_slide(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.stack.setCurrentIndex(self.current_index)
        self.update_nav_buttons()

    def update_nav_buttons(self):
        self.prev_btn.setEnabled(self.current_index > 0)
        self.next_btn.setEnabled(self.current_index < self.stack.count() - 1)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
