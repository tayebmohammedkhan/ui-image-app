#!/usr/bin/env python3
"""
Futuristic Photo Carousel App
A PyQt6 desktop application with a neon-styled UI for uploading photo/text pairs
and navigating through a 10-slide carousel.
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QFileDialog, QFrame, QGraphicsDropShadowEffect
)
from PyQt6.QtGui import QPixmap, QFont, QColor, QPalette, QLinearGradient, QPainter, QBrush
from PyQt6.QtCore import Qt, QSize

# Slide titles array
SLIDE_TITLES = [
    "NEURAL INTERFACE",
    "QUANTUM ANALYSIS",
    "HOLOGRAPHIC RENDER",
    "CYBER SYNTHESIS",
    "NEON MATRIX",
    "DIGITAL REALM",
    "PLASMA CORE",
    "VOID SCANNER",
    "FLUX CAPACITOR",
    "OMEGA PROTOCOL"
]

FUTURISTIC_STYLE = """
QMainWindow {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #0a0a1a, stop:0.5 #1a1a3a, stop:1 #0a0a2a);
}

QWidget#centralWidget {
    background: transparent;
}

QLabel {
    color: #00ffff;
    font-family: 'Consolas', 'Courier New', monospace;
}

QLabel#titleLabel {
    color: #00ffff;
    font-size: 28px;
    font-weight: bold;
    letter-spacing: 4px;
    padding: 10px;
}

QLabel#slideTitle {
    color: #ff00ff;
    font-size: 22px;
    font-weight: bold;
    letter-spacing: 3px;
    padding: 8px;
    border: 2px solid #ff00ff;
    border-radius: 5px;
    background: rgba(255, 0, 255, 0.1);
}

QLabel#slideCounter {
    color: #00ff88;
    font-size: 16px;
    font-weight: bold;
}

QLabel#imageLabel {
    background: rgba(0, 255, 255, 0.05);
    border: 2px solid #00ffff;
    border-radius: 10px;
    padding: 10px;
}

QLabel#uploadStatus {
    color: #ffff00;
    font-size: 14px;
    padding: 5px;
}

QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #1a1a3a, stop:0.5 #2a2a5a, stop:1 #1a1a3a);
    color: #00ffff;
    border: 2px solid #00ffff;
    border-radius: 8px;
    padding: 12px 25px;
    font-size: 14px;
    font-weight: bold;
    font-family: 'Consolas', 'Courier New', monospace;
    letter-spacing: 2px;
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #2a2a5a, stop:0.5 #4a4a8a, stop:1 #2a2a5a);
    border-color: #00ffff;
    color: #ffffff;
}

QPushButton:pressed {
    background: #00ffff;
    color: #0a0a1a;
}

QPushButton:disabled {
    background: #1a1a2a;
    border-color: #333366;
    color: #666699;
}

QPushButton#navButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #1a0a2a, stop:0.5 #3a1a5a, stop:1 #1a0a2a);
    border-color: #ff00ff;
    color: #ff00ff;
    padding: 15px 40px;
    font-size: 16px;
}

QPushButton#navButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #3a1a5a, stop:0.5 #6a3a8a, stop:1 #3a1a5a);
    color: #ffffff;
}

QPushButton#navButton:pressed {
    background: #ff00ff;
    color: #0a0a1a;
}

QPushButton#navButton:disabled {
    background: #1a1a2a;
    border-color: #442255;
    color: #664477;
}

QPushButton#uploadButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #0a1a1a, stop:0.5 #1a3a3a, stop:1 #0a1a1a);
    border-color: #00ff88;
    color: #00ff88;
}

QPushButton#uploadButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #1a3a3a, stop:0.5 #2a5a5a, stop:1 #1a3a3a);
    color: #ffffff;
}

QTextEdit {
    background: rgba(10, 10, 30, 0.8);
    color: #00ffff;
    border: 2px solid #00ffff;
    border-radius: 8px;
    padding: 10px;
    font-size: 14px;
    font-family: 'Consolas', 'Courier New', monospace;
    selection-background-color: #00ffff;
    selection-color: #0a0a1a;
}

QTextEdit:focus {
    border-color: #00ff88;
    background: rgba(10, 20, 30, 0.9);
}

QFrame#uploadFrame {
    background: rgba(0, 255, 255, 0.05);
    border: 2px solid #00ffff;
    border-radius: 15px;
    padding: 15px;
}

QFrame#carouselFrame {
    background: rgba(255, 0, 255, 0.03);
    border: 2px solid #ff00ff;
    border-radius: 15px;
    padding: 20px;
}

QFrame#contentFrame {
    background: rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(0, 255, 255, 0.3);
    border-radius: 10px;
}
"""


class GlowEffect(QGraphicsDropShadowEffect):
    """Custom glow effect for futuristic UI elements."""
    
    def __init__(self, color="#00ffff", blur=20, parent=None):
        super().__init__(parent)
        self.setBlurRadius(blur)
        self.setColor(QColor(color))
        self.setOffset(0, 0)


class FuturisticCarouselApp(QMainWindow):
    """Main application window with futuristic styling."""
    
    def __init__(self):
        super().__init__()
        self.current_slide = 0
        self.photo_path = None
        self.txt_path = None
        self.slide_texts = [""] * 10
        
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("⚡ FUTURISTIC PHOTO CAROUSEL ⚡")
        self.setMinimumSize(1200, 850)
        self.setStyleSheet(FUTURISTIC_STYLE)
        
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title_label = QLabel("◈ QUANTUM CAROUSEL INTERFACE ◈")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setGraphicsEffect(GlowEffect("#00ffff", 30))
        main_layout.addWidget(title_label)
        
        # Upload Section
        upload_frame = QFrame()
        upload_frame.setObjectName("uploadFrame")
        upload_layout = QHBoxLayout(upload_frame)
        upload_layout.setSpacing(20)
        
        # Photo upload
        photo_section = QVBoxLayout()
        self.photo_btn = QPushButton("⬆ UPLOAD RAW PHOTO")
        self.photo_btn.setObjectName("uploadButton")
        self.photo_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.photo_btn.clicked.connect(self.upload_photo)
        self.photo_btn.setGraphicsEffect(GlowEffect("#00ff88", 15))
        
        self.photo_status = QLabel("[ NO PHOTO LOADED ]")
        self.photo_status.setObjectName("uploadStatus")
        self.photo_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        photo_section.addWidget(self.photo_btn)
        photo_section.addWidget(self.photo_status)
        upload_layout.addLayout(photo_section)
        
        # Pair indicator
        pair_label = QLabel("◆━━━ PAIR ━━━◆")
        pair_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pair_label.setStyleSheet("color: #ffff00; font-size: 16px; font-weight: bold;")
        upload_layout.addWidget(pair_label)
        
        # Text file upload
        txt_section = QVBoxLayout()
        self.txt_btn = QPushButton("⬆ UPLOAD TXT FILE")
        self.txt_btn.setObjectName("uploadButton")
        self.txt_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.txt_btn.clicked.connect(self.upload_txt)
        
        self.txt_status = QLabel("[ NO TEXT FILE LOADED ]")
        self.txt_status.setObjectName("uploadStatus")
        self.txt_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        txt_section.addWidget(self.txt_btn)
        txt_section.addWidget(self.txt_status)
        upload_layout.addLayout(txt_section)
        
        main_layout.addWidget(upload_frame)
        
        # Carousel Section
        carousel_frame = QFrame()
        carousel_frame.setObjectName("carouselFrame")
        carousel_layout = QVBoxLayout(carousel_frame)
        carousel_layout.setSpacing(15)
        
        # Slide header
        header_layout = QHBoxLayout()
        
        self.slide_title = QLabel(SLIDE_TITLES[0])
        self.slide_title.setObjectName("slideTitle")
        self.slide_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.slide_title.setGraphicsEffect(GlowEffect("#ff00ff", 20))
        
        self.slide_counter = QLabel("◉ SLIDE 01 / 10 ◉")
        self.slide_counter.setObjectName("slideCounter")
        self.slide_counter.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        header_layout.addStretch()
        header_layout.addWidget(self.slide_title)
        header_layout.addStretch()
        carousel_layout.addLayout(header_layout)
        carousel_layout.addWidget(self.slide_counter, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Content area
        content_frame = QFrame()
        content_frame.setObjectName("contentFrame")
        content_layout = QHBoxLayout(content_frame)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # Image display
        self.image_label = QLabel("◈ AWAITING IMAGE DATA ◈")
        self.image_label.setObjectName("imageLabel")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(500, 400)
        self.image_label.setMaximumSize(600, 450)
        self.image_label.setScaledContents(False)
        content_layout.addWidget(self.image_label)
        
        # Text input
        text_section = QVBoxLayout()
        text_label = QLabel("▸ DATA INPUT TERMINAL ◂")
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_label.setStyleSheet("color: #00ff88; font-size: 14px; font-weight: bold; letter-spacing: 2px;")
        
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Enter data stream for this slide...")
        self.text_input.setMinimumWidth(350)
        self.text_input.textChanged.connect(self.save_current_text)
        
        text_section.addWidget(text_label)
        text_section.addWidget(self.text_input)
        content_layout.addLayout(text_section)
        
        carousel_layout.addWidget(content_frame)
        
        # Navigation
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(50)
        
        self.prev_btn = QPushButton("◀◀ PREVIOUS")
        self.prev_btn.setObjectName("navButton")
        self.prev_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.prev_btn.clicked.connect(self.prev_slide)
        self.prev_btn.setEnabled(False)
        
        # Progress indicator
        self.progress_label = QLabel(self.get_progress_bar())
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_label.setStyleSheet("color: #00ffff; font-size: 18px; letter-spacing: 3px;")
        
        self.next_btn = QPushButton("NEXT ▶▶")
        self.next_btn.setObjectName("navButton")
        self.next_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.next_btn.clicked.connect(self.next_slide)
        self.next_btn.setGraphicsEffect(GlowEffect("#ff00ff", 15))
        
        nav_layout.addStretch()
        nav_layout.addWidget(self.prev_btn)
        nav_layout.addWidget(self.progress_label)
        nav_layout.addWidget(self.next_btn)
        nav_layout.addStretch()
        
        carousel_layout.addLayout(nav_layout)
        main_layout.addWidget(carousel_frame)
        
        # Footer
        footer = QLabel("━━━ SYSTEM INITIALIZED ━━━ READY FOR INPUT ━━━")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet("color: #666699; font-size: 12px; letter-spacing: 3px;")
        main_layout.addWidget(footer)
        
    def get_progress_bar(self):
        """Generate visual progress indicator."""
        filled = "●" * (self.current_slide + 1)
        empty = "○" * (9 - self.current_slide)
        return f"[ {filled}{empty} ]"
    
    def upload_photo(self):
        """Handle raw photo file upload."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Raw Photo File",
            "",
            "Raw Images (*.raw *.cr2 *.nef *.arw *.dng *.orf *.rw2);;All Images (*.png *.jpg *.jpeg *.bmp *.gif *.tiff *.raw *.cr2 *.nef *.arw *.dng);;All Files (*.*)"
        )
        
        if file_path:
            self.photo_path = file_path
            filename = Path(file_path).name
            self.photo_status.setText(f"✓ {filename[:30]}{'...' if len(filename) > 30 else ''}")
            self.photo_status.setStyleSheet("color: #00ff88; font-size: 14px;")
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
            self.txt_status.setText(f"✓ {filename[:30]}{'...' if len(filename) > 30 else ''}")
            self.txt_status.setStyleSheet("color: #00ff88; font-size: 14px;")
            
            # Optionally load txt content into first slide
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # You could use this content as needed
            except Exception as e:
                print(f"Error reading text file: {e}")
    
    def update_image_display(self):
        """Update the image displayed in the carousel."""
        if self.photo_path:
            pixmap = QPixmap(self.photo_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    580, 430,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.image_label.setPixmap(scaled)
            else:
                self.image_label.setText("◈ RAW FORMAT - PREVIEW UNAVAILABLE ◈\n\n[Image data loaded]")
        else:
            self.image_label.setText("◈ AWAITING IMAGE DATA ◈")
    
    def save_current_text(self):
        """Save the current text input to the slides array."""
        self.slide_texts[self.current_slide] = self.text_input.toPlainText()
    
    def update_slide(self):
        """Update all slide elements for current position."""
        self.slide_title.setText(SLIDE_TITLES[self.current_slide])
        self.slide_counter.setText(f"◉ SLIDE {self.current_slide + 1:02d} / 10 ◉")
        self.progress_label.setText(self.get_progress_bar())
        
        # Load saved text for this slide
        self.text_input.blockSignals(True)
        self.text_input.setText(self.slide_texts[self.current_slide])
        self.text_input.blockSignals(False)
        
        # Update navigation buttons
        self.prev_btn.setEnabled(self.current_slide > 0)
        self.next_btn.setEnabled(self.current_slide < 9)
        
        # Update image display
        self.update_image_display()
    
    def prev_slide(self):
        """Navigate to previous slide."""
        if self.current_slide > 0:
            self.save_current_text()
            self.current_slide -= 1
            self.update_slide()
    
    def next_slide(self):
        """Navigate to next slide."""
        if self.current_slide < 9:
            self.save_current_text()
            self.current_slide += 1
            self.update_slide()


def main():
    app = QApplication(sys.argv)
    
    # Set application-wide dark palette
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(10, 10, 26))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 255, 255))
    palette.setColor(QPalette.ColorRole.Base, QColor(15, 15, 35))
    palette.setColor(QPalette.ColorRole.Text, QColor(0, 255, 255))
    app.setPalette(palette)
    
    window = FuturisticCarouselApp()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
