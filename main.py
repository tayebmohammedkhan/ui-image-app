#!/usr/bin/env python3
"""
Photo Carousel App
A clean, minimal PyQt6 desktop application for uploading photo/text pairs
and navigating through a 10-slide carousel.
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QFileDialog, QFrame, QSizePolicy
)
from PyQt6.QtGui import QPixmap, QFont, QColor, QPalette
from PyQt6.QtCore import Qt

# Slide titles
SLIDE_TITLES = [
    "Overview",
    "Background",
    "Analysis",
    "Key Findings",
    "Details",
    "Comparison",
    "Results",
    "Discussion",
    "Summary",
    "Conclusion"
]

CLEAN_STYLE = """
QMainWindow, QWidget {
    background-color: #ffffff;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

QLabel {
    color: #1a1a1a;
}

QLabel#appTitle {
    font-size: 20px;
    font-weight: 600;
    color: #1a1a1a;
    padding: 8px 0;
}

QLabel#slideTitle {
    font-size: 24px;
    font-weight: 600;
    color: #1a1a1a;
}

QLabel#slideCounter {
    font-size: 13px;
    color: #666666;
}

QLabel#imageLabel {
    background-color: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 8px;
}

QLabel#uploadHint {
    font-size: 13px;
    color: #868e96;
}

QLabel#sectionLabel {
    font-size: 12px;
    font-weight: 600;
    color: #868e96;
    text-transform: uppercase;
    letter-spacing: 1px;
}

QLabel#fileName {
    font-size: 13px;
    color: #495057;
}

QPushButton {
    background-color: #f8f9fa;
    color: #495057;
    border: 1px solid #dee2e6;
    border-radius: 6px;
    padding: 10px 20px;
    font-size: 14px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #e9ecef;
    border-color: #ced4da;
}

QPushButton:pressed {
    background-color: #dee2e6;
}

QPushButton#primaryButton {
    background-color: #228be6;
    color: white;
    border: none;
}

QPushButton#primaryButton:hover {
    background-color: #1c7ed6;
}

QPushButton#primaryButton:pressed {
    background-color: #1971c2;
}

QPushButton#primaryButton:disabled {
    background-color: #adb5bd;
}

QPushButton#navButton {
    padding: 12px 32px;
    font-size: 14px;
    font-weight: 500;
}

QPushButton#navButton:disabled {
    background-color: #f8f9fa;
    color: #adb5bd;
    border-color: #e9ecef;
}

QTextEdit {
    background-color: #ffffff;
    color: #1a1a1a;
    border: 1px solid #dee2e6;
    border-radius: 6px;
    padding: 12px;
    font-size: 14px;
    line-height: 1.5;
}

QTextEdit:focus {
    border-color: #228be6;
}

QFrame#uploadCard {
    background-color: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 8px;
}

QFrame#divider {
    background-color: #e9ecef;
}

QFrame#progressDot {
    border-radius: 4px;
}
"""


class PhotoCarouselApp(QMainWindow):
    """Main application window with clean, minimal design."""
    
    def __init__(self):
        super().__init__()
        self.current_slide = 0
        self.photo_path = None
        self.txt_path = None
        self.slide_texts = [""] * 10
        self.progress_dots = []
        
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Photo Carousel")
        self.setMinimumSize(1000, 700)
        self.setStyleSheet(CLEAN_STYLE)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(24)
        main_layout.setContentsMargins(40, 32, 40, 32)
        
        # Header
        header = QHBoxLayout()
        title = QLabel("Photo Carousel")
        title.setObjectName("appTitle")
        header.addWidget(title)
        header.addStretch()
        main_layout.addLayout(header)
        
        # Upload Section
        upload_section = QHBoxLayout()
        upload_section.setSpacing(16)
        
        # Photo upload card
        photo_card = self.create_upload_card(
            "Photo",
            "RAW, CR2, NEF, PNG, JPG",
            self.upload_photo,
            "photo"
        )
        upload_section.addWidget(photo_card)
        
        # Text file upload card
        txt_card = self.create_upload_card(
            "Text File",
            "TXT",
            self.upload_txt,
            "txt"
        )
        upload_section.addWidget(txt_card)
        
        main_layout.addLayout(upload_section)
        
        # Divider
        divider = QFrame()
        divider.setObjectName("divider")
        divider.setFixedHeight(1)
        main_layout.addWidget(divider)
        
        # Carousel Section
        carousel_layout = QVBoxLayout()
        carousel_layout.setSpacing(16)
        
        # Slide header
        slide_header = QHBoxLayout()
        
        self.slide_title = QLabel(SLIDE_TITLES[0])
        self.slide_title.setObjectName("slideTitle")
        
        self.slide_counter = QLabel("1 of 10")
        self.slide_counter.setObjectName("slideCounter")
        
        slide_header.addWidget(self.slide_title)
        slide_header.addStretch()
        slide_header.addWidget(self.slide_counter)
        carousel_layout.addLayout(slide_header)
        
        # Content area
        content_layout = QHBoxLayout()
        content_layout.setSpacing(24)
        
        # Image display
        image_container = QVBoxLayout()
        self.image_label = QLabel("No image uploaded")
        self.image_label.setObjectName("imageLabel")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(420, 320)
        self.image_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        image_container.addWidget(self.image_label)
        content_layout.addLayout(image_container, stretch=1)
        
        # Text input section
        text_section = QVBoxLayout()
        text_section.setSpacing(8)
        
        text_label = QLabel("Notes")
        text_label.setObjectName("sectionLabel")
        text_section.addWidget(text_label)
        
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Add notes for this slide...")
        self.text_input.setMinimumWidth(300)
        self.text_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.text_input.textChanged.connect(self.save_current_text)
        text_section.addWidget(self.text_input)
        
        content_layout.addLayout(text_section, stretch=1)
        carousel_layout.addLayout(content_layout)
        
        main_layout.addLayout(carousel_layout, stretch=1)
        
        # Navigation
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(16)
        
        self.prev_btn = QPushButton("← Previous")
        self.prev_btn.setObjectName("navButton")
        self.prev_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.prev_btn.clicked.connect(self.prev_slide)
        self.prev_btn.setEnabled(False)
        
        # Progress dots
        progress_container = QHBoxLayout()
        progress_container.setSpacing(8)
        progress_container.addStretch()
        
        for i in range(10):
            dot = QFrame()
            dot.setObjectName("progressDot")
            dot.setFixedSize(8, 8)
            if i == 0:
                dot.setStyleSheet("background-color: #228be6; border-radius: 4px;")
            else:
                dot.setStyleSheet("background-color: #dee2e6; border-radius: 4px;")
            self.progress_dots.append(dot)
            progress_container.addWidget(dot)
        
        progress_container.addStretch()
        
        self.next_btn = QPushButton("Next →")
        self.next_btn.setObjectName("navButton")
        self.next_btn.setObjectName("primaryButton")
        self.next_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.next_btn.clicked.connect(self.next_slide)
        self.next_btn.setStyleSheet("""
            QPushButton {
                background-color: #228be6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 32px;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover { background-color: #1c7ed6; }
            QPushButton:pressed { background-color: #1971c2; }
            QPushButton:disabled { background-color: #adb5bd; }
        """)
        
        nav_layout.addWidget(self.prev_btn)
        nav_layout.addLayout(progress_container, stretch=1)
        nav_layout.addWidget(self.next_btn)
        
        main_layout.addLayout(nav_layout)
    
    def create_upload_card(self, title, formats, callback, card_type):
        """Create a minimal upload card."""
        card = QFrame()
        card.setObjectName("uploadCard")
        card.setFixedHeight(100)
        
        layout = QHBoxLayout(card)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(16)
        
        # Info section
        info = QVBoxLayout()
        info.setSpacing(4)
        
        label = QLabel(title)
        label.setObjectName("sectionLabel")
        info.addWidget(label)
        
        if card_type == "photo":
            self.photo_filename = QLabel("No file selected")
            self.photo_filename.setObjectName("fileName")
            info.addWidget(self.photo_filename)
        else:
            self.txt_filename = QLabel("No file selected")
            self.txt_filename.setObjectName("fileName")
            info.addWidget(self.txt_filename)
        
        hint = QLabel(formats)
        hint.setObjectName("uploadHint")
        info.addWidget(hint)
        
        layout.addLayout(info)
        layout.addStretch()
        
        # Upload button
        btn = QPushButton("Choose File")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(callback)
        layout.addWidget(btn)
        
        return card
    
    def upload_photo(self):
        """Handle photo file upload."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Photo",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif *.tiff *.raw *.cr2 *.nef *.arw *.dng *.orf *.rw2);;All Files (*.*)"
        )
        
        if file_path:
            self.photo_path = file_path
            filename = Path(file_path).name
            display_name = filename if len(filename) <= 35 else filename[:32] + "..."
            self.photo_filename.setText(display_name)
            self.photo_filename.setStyleSheet("color: #228be6; font-size: 13px;")
            self.update_image_display()
            
    def upload_txt(self):
        """Handle text file upload."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Text File",
            "",
            "Text Files (*.txt);;All Files (*.*)"
        )
        
        if file_path:
            self.txt_path = file_path
            filename = Path(file_path).name
            display_name = filename if len(filename) <= 35 else filename[:32] + "..."
            self.txt_filename.setText(display_name)
            self.txt_filename.setStyleSheet("color: #228be6; font-size: 13px;")
    
    def update_image_display(self):
        """Update the displayed image."""
        if self.photo_path:
            pixmap = QPixmap(self.photo_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    self.image_label.width() - 20,
                    self.image_label.height() - 20,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.image_label.setPixmap(scaled)
            else:
                self.image_label.setText("Preview not available\n(RAW format)")
        else:
            self.image_label.setText("No image uploaded")
    
    def save_current_text(self):
        """Save current text input."""
        self.slide_texts[self.current_slide] = self.text_input.toPlainText()
    
    def update_progress_dots(self):
        """Update progress dot indicators."""
        for i, dot in enumerate(self.progress_dots):
            if i == self.current_slide:
                dot.setStyleSheet("background-color: #228be6; border-radius: 4px;")
            else:
                dot.setStyleSheet("background-color: #dee2e6; border-radius: 4px;")
    
    def update_slide(self):
        """Update slide display."""
        self.slide_title.setText(SLIDE_TITLES[self.current_slide])
        self.slide_counter.setText(f"{self.current_slide + 1} of 10")
        
        self.text_input.blockSignals(True)
        self.text_input.setText(self.slide_texts[self.current_slide])
        self.text_input.blockSignals(False)
        
        self.prev_btn.setEnabled(self.current_slide > 0)
        self.next_btn.setEnabled(self.current_slide < 9)
        
        self.update_progress_dots()
        self.update_image_display()
    
    def prev_slide(self):
        """Go to previous slide."""
        if self.current_slide > 0:
            self.save_current_text()
            self.current_slide -= 1
            self.update_slide()
    
    def next_slide(self):
        """Go to next slide."""
        if self.current_slide < 9:
            self.save_current_text()
            self.current_slide += 1
            self.update_slide()
    
    def resizeEvent(self, event):
        """Handle window resize."""
        super().resizeEvent(event)
        self.update_image_display()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(26, 26, 26))
    palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Text, QColor(26, 26, 26))
    app.setPalette(palette)
    
    window = PhotoCarouselApp()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
