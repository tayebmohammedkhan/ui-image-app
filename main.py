import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QStackedWidget, QTextEdit, QFileDialog, QMessageBox
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

class SlidePage(QWidget):
    """
    Custom Widget representing a single slide in the carousel.
    """
    def __init__(self, title_text):
        super().__init__()
        
        # Main layout for the slide
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # 1. Title (from array)
        self.title_label = QLabel(title_text)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        self.layout.addWidget(self.title_label)

        # 2. Image Area
        self.image_label = QLabel("No Image Loaded")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("border: 2px dashed #ccc; background-color: #f0f0f0;")
        self.image_label.setMinimumHeight(300)
        self.image_label.setScaledContents(False) # We will scale pixmap manually to keep aspect ratio
        self.layout.addWidget(self.image_label)

        # 3. Text Input Box
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Text content will appear here, or type your own...")
        self.text_input.setMaximumHeight(150)
        self.layout.addWidget(self.text_input)

    def set_image(self, pixmap):
        """Sets the image for this specific slide"""
        # Scale image to fit the label height while keeping aspect ratio
        scaled_pixmap = pixmap.scaled(
            self.image_label.width(), 
            300, 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)
    
    def set_text_content(self, text):
        """Sets text for this slide"""
        self.text_input.setText(text)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Photo & Text Carousel")
        self.resize(800, 600)

        # --- Data Configuration ---
        # The titles for your 10 slides
        self.titles = [
            "1. Orientation", "2. Lighting", "3. Composition", 
            "4. Color Grade", "5. Focus", "6. Subject Matter", 
            "7. Background", "8. Editing", "9. Storytelling", "10. Final Verdict"
        ]
        
        self.slides = [] # To keep track of slide objects

        # --- Main Layout ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)

        # --- Top Bar: Upload Controls ---
        top_bar = QHBoxLayout()
        
        self.btn_upload_img = QPushButton("1. Select Photo")
        self.btn_upload_img.clicked.connect(self.upload_image)
        
        self.btn_upload_txt = QPushButton("2. Select Text File")
        self.btn_upload_txt.clicked.connect(self.upload_text)
        
        self.btn_process = QPushButton("Load Pair")
        self.btn_process.setStyleSheet("background-color: #007bff; color: white; font-weight: bold;")
        self.btn_process.clicked.connect(self.process_pair)
        self.btn_process.setEnabled(False) # Disabled until files are selected

        top_bar.addWidget(self.btn_upload_img)
        top_bar.addWidget(self.btn_upload_txt)
        top_bar.addWidget(self.btn_process)
        
        self.lbl_status = QLabel("Please upload files.")
        self.lbl_status.setStyleSheet("color: gray; margin-left: 10px;")
        
        # Add top bar to main layout
        self.main_layout.addLayout(top_bar)
        self.main_layout.addWidget(self.lbl_status)

        # --- Carousel Section (QStackedWidget) ---
        self.carousel = QStackedWidget()
        self.main_layout.addWidget(self.carousel)

        # Generate the 10 slides
        for title in self.titles:
            slide = SlidePage(title)
            self.slides.append(slide)
            self.carousel.addWidget(slide)

        # --- Bottom Bar: Navigation ---
        nav_layout = QHBoxLayout()
        
        self.btn_prev = QPushButton("Previous")
        self.btn_prev.clicked.connect(self.go_prev)
        
        self.btn_next = QPushButton("Next")
        self.btn_next.clicked.connect(self.go_next)

        nav_layout.addWidget(self.btn_prev)
        nav_layout.addStretch() # Spacer to push buttons to sides
        self.lbl_counter = QLabel(f"Slide 1 / {len(self.titles)}")
        nav_layout.addWidget(self.lbl_counter)
        nav_layout.addStretch()
        nav_layout.addWidget(self.btn_next)

        self.main_layout.addLayout(nav_layout)

        # Initialize button states
        self.update_nav_buttons()

        # Placeholders for file paths
        self.img_path = None
        self.txt_path = None

    def upload_image(self):
        # Open file dialog
        fname, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if fname:
            self.img_path = fname
            self.btn_upload_img.setText(f"Img: {os.path.basename(fname)}")
            self.check_ready()

    def upload_text(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Open Text File", "", "Text Files (*.txt)")
        if fname:
            self.txt_path = fname
            self.btn_upload_txt.setText(f"Txt: {os.path.basename(fname)}")
            self.check_ready()

    def check_ready(self):
        # Only enable Load button if both files are present
        if self.img_path and self.txt_path:
            self.btn_process.setEnabled(True)
            self.lbl_status.setText("Files selected. Click 'Load Pair' to render.")

    def process_pair(self):
        """Reads the files and populates all 10 slides"""
        try:
            # 1. Load Pixmap
            pixmap = QPixmap(self.img_path)
            if pixmap.isNull():
                raise Exception("Failed to load image format.")

            # 2. Read Text
            with open(self.txt_path, 'r', encoding='utf-8') as f:
                text_content = f.read()

            # 3. Populate Slides
            for slide in self.slides:
                slide.set_image(pixmap)
                slide.set_text_content(text_content)
            
            self.lbl_status.setText("Loaded successfully.")
            self.lbl_status.setStyleSheet("color: green;")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def go_next(self):
        current = self.carousel.currentIndex()
        if current < self.carousel.count() - 1:
            self.carousel.setCurrentIndex(current + 1)
            self.update_nav_buttons()

    def go_prev(self):
        current = self.carousel.currentIndex()
        if current > 0:
            self.carousel.setCurrentIndex(current - 1)
            self.update_nav_buttons()

    def update_nav_buttons(self):
        """Disables buttons at boundaries (0 and 10) and updates counter"""
        idx = self.carousel.currentIndex()
        total = self.carousel.count()

        self.btn_prev.setEnabled(idx > 0)
        self.btn_next.setEnabled(idx < total - 1)
        
        self.lbl_counter.setText(f"Slide {idx + 1} / {total}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
