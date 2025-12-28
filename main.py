#!/usr/bin/env python3
"""
ISP Pipeline Photo Carousel App
A PyQt6 desktop application with integrated ISP (Image Signal Processing) pipeline
for RAW image processing with metadata parsing and parameter controls.
"""

import sys
import re
import struct
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
import numpy as np

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QFileDialog, QFrame, QSizePolicy,
    QDoubleSpinBox, QSpinBox, QComboBox, QSlider, QScrollArea,
    QGroupBox, QGridLayout, QLineEdit, QCheckBox
)
from PyQt6.QtGui import QPixmap, QImage, QColor, QPalette
from PyQt6.QtCore import Qt, QTimer

# Slide titles - ISP Pipeline stages
SLIDE_TITLES = [
    "Raw Interpretation",
    "Black Level Correction",
    "Demosaic",
    "White Balance",
    "Lens Shading Correction",
    "GTM Curve / LUT",
    "Exposure Compensation",
    "Gamma Correction",
    "Color Correction",
    "Output Preview"
]

# Bayer pattern types
BAYER_PATTERNS = {
    0: "RGGB",
    1: "GRBG",
    2: "GBRG",
    3: "BGGR"
}

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

QLabel#paramLabel {
    font-size: 13px;
    color: #495057;
    min-width: 140px;
}

QLabel#valueLabel {
    font-size: 13px;
    color: #228be6;
    font-weight: 500;
}

QLabel#fileName {
    font-size: 13px;
    color: #495057;
}

QLabel#metaKey {
    font-size: 12px;
    color: #868e96;
}

QLabel#metaValue {
    font-size: 12px;
    color: #495057;
    font-weight: 500;
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

QPushButton#applyButton {
    background-color: #40c057;
    color: white;
    border: none;
    padding: 8px 16px;
}

QPushButton#applyButton:hover {
    background-color: #37b24d;
}

QPushButton#resetButton {
    background-color: #fa5252;
    color: white;
    border: none;
    padding: 8px 16px;
}

QPushButton#resetButton:hover {
    background-color: #f03e3e;
}

QPushButton#navButton:disabled {
    background-color: #f8f9fa;
    color: #adb5bd;
    border-color: #e9ecef;
}

QSpinBox, QDoubleSpinBox, QComboBox, QLineEdit {
    background-color: #ffffff;
    border: 1px solid #dee2e6;
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 13px;
    min-width: 100px;
}

QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus, QLineEdit:focus {
    border-color: #228be6;
}

QSlider::groove:horizontal {
    height: 6px;
    background: #e9ecef;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #228be6;
    width: 16px;
    height: 16px;
    margin: -5px 0;
    border-radius: 8px;
}

QSlider::sub-page:horizontal {
    background: #228be6;
    border-radius: 3px;
}

QGroupBox {
    font-size: 13px;
    font-weight: 600;
    color: #495057;
    border: 1px solid #e9ecef;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 12px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 8px;
}

QScrollArea {
    border: none;
    background: transparent;
}

QFrame#uploadCard {
    background-color: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 8px;
}

QFrame#divider {
    background-color: #e9ecef;
}

QFrame#paramPanel {
    background-color: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 8px;
}

QCheckBox {
    font-size: 13px;
    color: #495057;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid #dee2e6;
}

QCheckBox::indicator:checked {
    background-color: #228be6;
    border-color: #228be6;
}
"""


@dataclass
class RawMetadata:
    """Parsed metadata from the text file."""
    shot_meta_revision_ver: int = 0
    frame_meta_ver: int = 0
    frame_meta_revision_ver: int = 0
    dump_time: int = 0
    camera_id: str = ""
    sensor_name: str = ""
    product_name: str = ""
    device_state: int = 0
    flash_status: int = 0
    bpp: int = 10
    packed: int = 0
    bayer_type: int = 0
    dynamic_shot_mode: int = 0
    extra_fields: Dict[str, Any] = field(default_factory=dict)


@dataclass 
class ISPParameters:
    """ISP pipeline parameters for each stage."""
    # Raw Interpretation
    width: int = 4000
    height: int = 3000
    bpp: int = 10
    bayer_pattern: int = 0
    packed: bool = False
    
    # Black Level
    black_level_r: int = 64
    black_level_gr: int = 64
    black_level_gb: int = 64
    black_level_b: int = 64
    
    # Demosaic
    demosaic_method: str = "Bilinear"
    edge_threshold: float = 0.1
    
    # White Balance
    wb_r_gain: float = 1.0
    wb_g_gain: float = 1.0
    wb_b_gain: float = 1.0
    auto_wb: bool = False
    
    # Lens Shading
    lsc_enabled: bool = True
    lsc_strength: float = 1.0
    lsc_center_x: float = 0.5
    lsc_center_y: float = 0.5
    
    # GTM / LUT
    gtm_enabled: bool = True
    gtm_strength: float = 1.0
    gtm_contrast: float = 1.0
    lut_file: str = ""
    
    # Exposure Compensation
    exposure_ev: float = 0.0
    highlight_recovery: float = 0.0
    shadow_recovery: float = 0.0
    
    # Gamma Correction
    gamma_value: float = 2.2
    gamma_enabled: bool = True
    
    # Color Correction
    saturation: float = 1.0
    hue_shift: float = 0.0
    ccm_enabled: bool = False


class MetadataParser:
    """Parser for RAW image metadata text files."""
    
    @staticmethod
    def parse(content: str) -> RawMetadata:
        metadata = RawMetadata()
        
        # Clean and split content
        lines = content.replace(',', '\n').split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or ':' not in line:
                continue
                
            key, value = line.split(':', 1)
            key = key.strip().lower()
            value = value.strip()
            
            try:
                if 'shotmetarevisionver' in key:
                    metadata.shot_meta_revision_ver = int(value)
                elif 'framemetaver' in key and 'revision' not in key:
                    metadata.frame_meta_ver = int(value)
                elif 'framemetarevisionver' in key:
                    metadata.frame_meta_revision_ver = int(value)
                elif 'dump' in key and 'time' in key:
                    metadata.dump_time = int(value)
                elif 'cameraid' in key:
                    metadata.camera_id = value
                elif 'sensorname' in key:
                    metadata.sensor_name = value
                elif 'productname' in key:
                    metadata.product_name = value
                elif 'devicestate' in key:
                    metadata.device_state = int(value)
                elif 'flashstatus' in key:
                    metadata.flash_status = int(value)
                elif 'bpp' in key:
                    metadata.bpp = int(value)
                elif 'packed' in key:
                    metadata.packed = int(value)
                elif 'bayertype' in key:
                    metadata.bayer_type = int(value)
                elif 'dynamicshotmode' in key:
                    metadata.dynamic_shot_mode = int(value)
                else:
                    metadata.extra_fields[key] = value
            except ValueError:
                metadata.extra_fields[key] = value
                
        return metadata


class ISPProcessor:
    """Image Signal Processing pipeline."""
    
    def __init__(self):
        self.raw_data: Optional[np.ndarray] = None
        self.processed_stages: Dict[int, np.ndarray] = {}
        
    def load_raw(self, file_path: str, params: ISPParameters) -> Optional[np.ndarray]:
        """Load and interpret RAW file."""
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            # Calculate expected size
            if params.packed:
                # 10-bit packed: 4 pixels in 5 bytes
                expected_bytes = (params.width * params.height * params.bpp) // 8
            else:
                # Unpacked: 16-bit per pixel
                expected_bytes = params.width * params.height * 2
            
            # Try to interpret the data
            if params.packed and params.bpp == 10:
                self.raw_data = self._unpack_10bit(data, params.width, params.height)
            else:
                # Assume 16-bit unpacked
                self.raw_data = np.frombuffer(data[:expected_bytes], dtype=np.uint16)
                if len(self.raw_data) >= params.width * params.height:
                    self.raw_data = self.raw_data[:params.width * params.height]
                    self.raw_data = self.raw_data.reshape((params.height, params.width))
                else:
                    # Fallback: create placeholder
                    self.raw_data = self._create_placeholder(params.width, params.height)
            
            return self.raw_data
            
        except Exception as e:
            print(f"Error loading RAW: {e}")
            self.raw_data = self._create_placeholder(params.width, params.height)
            return self.raw_data
    
    def _create_placeholder(self, width: int, height: int) -> np.ndarray:
        """Create a test pattern for visualization."""
        y, x = np.ogrid[:height, :width]
        pattern = ((x // 100 + y // 100) % 2) * 512 + 256
        return pattern.astype(np.uint16)
    
    def _unpack_10bit(self, data: bytes, width: int, height: int) -> np.ndarray:
        """Unpack 10-bit packed data."""
        # Simplified unpacking - 4 pixels in 5 bytes
        total_pixels = width * height
        output = np.zeros(total_pixels, dtype=np.uint16)
        
        idx = 0
        for i in range(0, min(len(data) - 4, (total_pixels * 5) // 4), 5):
            if idx + 4 > total_pixels:
                break
            b0, b1, b2, b3, b4 = data[i:i+5]
            output[idx] = ((b0 << 2) | (b4 & 0x03)) & 0x3FF
            output[idx+1] = ((b1 << 2) | ((b4 >> 2) & 0x03)) & 0x3FF
            output[idx+2] = ((b2 << 2) | ((b4 >> 4) & 0x03)) & 0x3FF
            output[idx+3] = ((b3 << 2) | ((b4 >> 6) & 0x03)) & 0x3FF
            idx += 4
            
        return output.reshape((height, width))
    
    def apply_black_level(self, image: np.ndarray, params: ISPParameters) -> np.ndarray:
        """Apply black level correction."""
        result = image.astype(np.float32)
        h, w = result.shape[:2]
        
        # Apply per-channel black level based on Bayer pattern
        pattern = BAYER_PATTERNS.get(params.bayer_pattern, "RGGB")
        
        for y in range(2):
            for x in range(2):
                channel = pattern[y * 2 + x]
                if channel == 'R':
                    bl = params.black_level_r
                elif channel == 'B':
                    bl = params.black_level_b
                else:  # G
                    bl = params.black_level_gr if x == 1 else params.black_level_gb
                
                result[y::2, x::2] = np.maximum(0, result[y::2, x::2] - bl)
        
        return result
    
    def demosaic(self, image: np.ndarray, params: ISPParameters) -> np.ndarray:
        """Demosaic Bayer pattern to RGB."""
        h, w = image.shape
        rgb = np.zeros((h, w, 3), dtype=np.float32)
        
        pattern = BAYER_PATTERNS.get(params.bayer_pattern, "RGGB")
        
        # Simple bilinear demosaic
        for y in range(2):
            for x in range(2):
                channel = pattern[y * 2 + x]
                if channel == 'R':
                    rgb[y::2, x::2, 0] = image[y::2, x::2]
                elif channel == 'B':
                    rgb[y::2, x::2, 2] = image[y::2, x::2]
                else:
                    rgb[y::2, x::2, 1] = image[y::2, x::2]
        
        # Interpolate missing values (simplified)
        from scipy import ndimage
        for c in range(3):
            mask = rgb[:, :, c] == 0
            if np.any(mask):
                rgb[:, :, c] = ndimage.generic_filter(
                    rgb[:, :, c], 
                    lambda x: np.mean(x[x > 0]) if np.any(x > 0) else 0,
                    size=3
                )
        
        return rgb
    
    def apply_white_balance(self, image: np.ndarray, params: ISPParameters) -> np.ndarray:
        """Apply white balance gains."""
        result = image.copy()
        
        if params.auto_wb:
            # Simple gray world assumption
            means = np.mean(result, axis=(0, 1))
            gray = np.mean(means)
            gains = gray / (means + 1e-6)
        else:
            gains = np.array([params.wb_r_gain, params.wb_g_gain, params.wb_b_gain])
        
        result *= gains
        return result
    
    def apply_lens_shading(self, image: np.ndarray, params: ISPParameters) -> np.ndarray:
        """Apply lens shading correction."""
        if not params.lsc_enabled:
            return image
            
        h, w = image.shape[:2]
        y, x = np.ogrid[:h, :w]
        
        # Calculate distance from center
        cx = w * params.lsc_center_x
        cy = h * params.lsc_center_y
        
        dist = np.sqrt((x - cx)**2 + (y - cy)**2)
        max_dist = np.sqrt(cx**2 + cy**2)
        
        # Vignette correction (inverse of typical vignette)
        correction = 1.0 + params.lsc_strength * (dist / max_dist) ** 2
        
        if len(image.shape) == 3:
            correction = correction[:, :, np.newaxis]
        
        return image * correction
    
    def apply_gtm(self, image: np.ndarray, params: ISPParameters) -> np.ndarray:
        """Apply global tone mapping."""
        if not params.gtm_enabled:
            return image
            
        # Normalize
        max_val = image.max() if image.max() > 0 else 1
        result = image / max_val
        
        # Apply contrast
        result = ((result - 0.5) * params.gtm_contrast + 0.5)
        
        # Apply strength (simple S-curve)
        if params.gtm_strength != 1.0:
            result = result ** (1.0 / params.gtm_strength)
        
        return np.clip(result * max_val, 0, max_val)
    
    def apply_exposure(self, image: np.ndarray, params: ISPParameters) -> np.ndarray:
        """Apply exposure compensation."""
        # EV adjustment
        ev_multiplier = 2 ** params.exposure_ev
        result = image * ev_multiplier
        
        # Highlight recovery (compress highlights)
        if params.highlight_recovery > 0:
            max_val = result.max() if result.max() > 0 else 1
            threshold = max_val * 0.8
            mask = result > threshold
            result[mask] = threshold + (result[mask] - threshold) * (1 - params.highlight_recovery * 0.5)
        
        # Shadow recovery (lift shadows)
        if params.shadow_recovery > 0:
            max_val = result.max() if result.max() > 0 else 1
            threshold = max_val * 0.2
            mask = result < threshold
            result[mask] = result[mask] * (1 + params.shadow_recovery)
        
        return result
    
    def apply_gamma(self, image: np.ndarray, params: ISPParameters) -> np.ndarray:
        """Apply gamma correction."""
        if not params.gamma_enabled:
            return image
            
        max_val = image.max() if image.max() > 0 else 1
        normalized = image / max_val
        corrected = np.power(normalized, 1.0 / params.gamma_value)
        return corrected * max_val
    
    def apply_color_correction(self, image: np.ndarray, params: ISPParameters) -> np.ndarray:
        """Apply color correction (saturation, hue)."""
        if len(image.shape) != 3:
            return image
            
        # Convert to HSV-like for saturation adjustment
        result = image.copy()
        
        # Simple saturation adjustment
        gray = np.mean(result, axis=2, keepdims=True)
        result = gray + (result - gray) * params.saturation
        
        return np.clip(result, 0, result.max())
    
    def process_stage(self, stage: int, params: ISPParameters) -> np.ndarray:
        """Process a specific ISP stage."""
        if self.raw_data is None:
            return self._create_placeholder(params.width, params.height)
        
        # Process sequentially up to the requested stage
        image = self.raw_data.astype(np.float32)
        
        if stage >= 1:  # Black Level
            image = self.apply_black_level(self.raw_data, params)
        
        if stage >= 2:  # Demosaic
            try:
                image = self.demosaic(image if stage > 1 else self.apply_black_level(self.raw_data, params), params)
            except ImportError:
                # Fallback without scipy
                h, w = image.shape if len(image.shape) == 2 else image.shape[:2]
                if len(image.shape) == 2:
                    image = np.stack([image, image, image], axis=-1)
        
        if stage >= 3:  # White Balance
            image = self.apply_white_balance(image, params)
        
        if stage >= 4:  # Lens Shading
            image = self.apply_lens_shading(image, params)
        
        if stage >= 5:  # GTM
            image = self.apply_gtm(image, params)
        
        if stage >= 6:  # Exposure
            image = self.apply_exposure(image, params)
        
        if stage >= 7:  # Gamma
            image = self.apply_gamma(image, params)
        
        if stage >= 8:  # Color Correction
            image = self.apply_color_correction(image, params)
        
        self.processed_stages[stage] = image
        return image
    
    def to_qimage(self, image: np.ndarray) -> QImage:
        """Convert numpy array to QImage."""
        if image is None:
            return QImage()
        
        # Normalize to 8-bit
        if image.max() > 0:
            normalized = (image / image.max() * 255).astype(np.uint8)
        else:
            normalized = np.zeros_like(image, dtype=np.uint8)
        
        if len(normalized.shape) == 2:
            # Grayscale
            h, w = normalized.shape
            return QImage(normalized.data, w, h, w, QImage.Format.Format_Grayscale8)
        else:
            # RGB
            h, w, c = normalized.shape
            if c == 3:
                # Convert RGB to RGBA
                rgba = np.zeros((h, w, 4), dtype=np.uint8)
                rgba[:, :, :3] = normalized
                rgba[:, :, 3] = 255
                return QImage(rgba.data, w, h, w * 4, QImage.Format.Format_RGBA8888)
        
        return QImage()


class ParameterPanel(QScrollArea):
    """Scrollable panel for ISP parameters."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setObjectName("paramPanel")
        
        self.container = QWidget()
        self.layout = QVBoxLayout(self.container)
        self.layout.setSpacing(12)
        self.layout.setContentsMargins(16, 16, 16, 16)
        
        self.setWidget(self.container)
        self.widgets: Dict[str, QWidget] = {}
        
    def clear(self):
        """Clear all parameter widgets."""
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.widgets.clear()
    
    def add_metadata_display(self, metadata: RawMetadata):
        """Add metadata display section."""
        group = QGroupBox("Parsed Metadata")
        grid = QGridLayout(group)
        grid.setSpacing(8)
        
        meta_items = [
            ("Sensor", metadata.sensor_name),
            ("Product", metadata.product_name),
            ("Camera ID", metadata.camera_id),
            ("BPP", str(metadata.bpp)),
            ("Bayer Type", BAYER_PATTERNS.get(metadata.bayer_type, str(metadata.bayer_type))),
            ("Packed", "Yes" if metadata.packed else "No"),
            ("Frame Meta Ver", str(metadata.frame_meta_ver)),
            ("Flash Status", "On" if metadata.flash_status else "Off"),
        ]
        
        for i, (key, value) in enumerate(meta_items):
            key_label = QLabel(key + ":")
            key_label.setObjectName("metaKey")
            value_label = QLabel(value)
            value_label.setObjectName("metaValue")
            grid.addWidget(key_label, i // 2, (i % 2) * 2)
            grid.addWidget(value_label, i // 2, (i % 2) * 2 + 1)
        
        self.layout.addWidget(group)
    
    def add_spin_param(self, label: str, key: str, value: int, 
                       min_val: int = 0, max_val: int = 1023) -> QSpinBox:
        """Add integer parameter with spinbox."""
        row = QHBoxLayout()
        
        lbl = QLabel(label)
        lbl.setObjectName("paramLabel")
        row.addWidget(lbl)
        
        spin = QSpinBox()
        spin.setRange(min_val, max_val)
        spin.setValue(value)
        row.addWidget(spin)
        
        self.layout.addLayout(row)
        self.widgets[key] = spin
        return spin
    
    def add_double_param(self, label: str, key: str, value: float,
                         min_val: float = 0.0, max_val: float = 10.0,
                         step: float = 0.1, decimals: int = 2) -> QDoubleSpinBox:
        """Add float parameter with double spinbox."""
        row = QHBoxLayout()
        
        lbl = QLabel(label)
        lbl.setObjectName("paramLabel")
        row.addWidget(lbl)
        
        spin = QDoubleSpinBox()
        spin.setRange(min_val, max_val)
        spin.setSingleStep(step)
        spin.setDecimals(decimals)
        spin.setValue(value)
        row.addWidget(spin)
        
        self.layout.addLayout(row)
        self.widgets[key] = spin
        return spin
    
    def add_slider_param(self, label: str, key: str, value: float,
                         min_val: float = 0.0, max_val: float = 1.0) -> QSlider:
        """Add slider parameter."""
        container = QVBoxLayout()
        
        header = QHBoxLayout()
        lbl = QLabel(label)
        lbl.setObjectName("paramLabel")
        header.addWidget(lbl)
        
        value_lbl = QLabel(f"{value:.2f}")
        value_lbl.setObjectName("valueLabel")
        header.addWidget(value_lbl)
        header.addStretch()
        
        container.addLayout(header)
        
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(0, 100)
        slider.setValue(int((value - min_val) / (max_val - min_val) * 100))
        
        def update_label(v):
            actual = min_val + (v / 100) * (max_val - min_val)
            value_lbl.setText(f"{actual:.2f}")
        
        slider.valueChanged.connect(update_label)
        container.addWidget(slider)
        
        self.layout.addLayout(container)
        self.widgets[key] = slider
        self.widgets[key + "_range"] = (min_val, max_val)
        return slider
    
    def add_combo_param(self, label: str, key: str, options: List[str], 
                        current: str = "") -> QComboBox:
        """Add dropdown parameter."""
        row = QHBoxLayout()
        
        lbl = QLabel(label)
        lbl.setObjectName("paramLabel")
        row.addWidget(lbl)
        
        combo = QComboBox()
        combo.addItems(options)
        if current in options:
            combo.setCurrentText(current)
        row.addWidget(combo)
        
        self.layout.addLayout(row)
        self.widgets[key] = combo
        return combo
    
    def add_checkbox_param(self, label: str, key: str, checked: bool = False) -> QCheckBox:
        """Add checkbox parameter."""
        cb = QCheckBox(label)
        cb.setChecked(checked)
        self.layout.addWidget(cb)
        self.widgets[key] = cb
        return cb
    
    def add_section_header(self, title: str):
        """Add a section header."""
        lbl = QLabel(title)
        lbl.setObjectName("sectionLabel")
        lbl.setStyleSheet("margin-top: 8px;")
        self.layout.addWidget(lbl)
    
    def add_stretch(self):
        """Add stretch to push content up."""
        self.layout.addStretch()
    
    def get_slider_value(self, key: str) -> float:
        """Get actual value from slider."""
        slider = self.widgets.get(key)
        range_key = key + "_range"
        if slider and range_key in self.widgets:
            min_val, max_val = self.widgets[range_key]
            return min_val + (slider.value() / 100) * (max_val - min_val)
        return 0.0


class ISPCarouselApp(QMainWindow):
    """Main application window with ISP pipeline."""
    
    def __init__(self):
        super().__init__()
        self.current_slide = 0
        self.photo_path = None
        self.txt_path = None
        self.metadata = RawMetadata()
        self.params = ISPParameters()
        self.processor = ISPProcessor()
        self.progress_dots = []
        
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("ISP Pipeline - Photo Processor")
        self.setMinimumSize(1200, 800)
        self.setStyleSheet(CLEAN_STYLE)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(32, 24, 32, 24)
        
        # Header
        header = QHBoxLayout()
        title = QLabel("ISP Pipeline")
        title.setObjectName("appTitle")
        header.addWidget(title)
        header.addStretch()
        main_layout.addLayout(header)
        
        # Upload Section
        upload_section = QHBoxLayout()
        upload_section.setSpacing(16)
        
        photo_card = self.create_upload_card("RAW Image", "RAW, CR2, NEF, ARW, DNG", self.upload_photo, "photo")
        upload_section.addWidget(photo_card)
        
        txt_card = self.create_upload_card("Metadata File", "TXT", self.upload_txt, "txt")
        upload_section.addWidget(txt_card)
        
        main_layout.addLayout(upload_section)
        
        # Divider
        divider = QFrame()
        divider.setObjectName("divider")
        divider.setFixedHeight(1)
        main_layout.addWidget(divider)
        
        # Slide header
        slide_header = QHBoxLayout()
        self.slide_title = QLabel(SLIDE_TITLES[0])
        self.slide_title.setObjectName("slideTitle")
        self.slide_counter = QLabel("1 of 10")
        self.slide_counter.setObjectName("slideCounter")
        slide_header.addWidget(self.slide_title)
        slide_header.addStretch()
        slide_header.addWidget(self.slide_counter)
        main_layout.addLayout(slide_header)
        
        # Content area
        content_layout = QHBoxLayout()
        content_layout.setSpacing(24)
        
        # Image display
        self.image_label = QLabel("Upload RAW image to begin")
        self.image_label.setObjectName("imageLabel")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(500, 380)
        self.image_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        content_layout.addWidget(self.image_label, stretch=3)
        
        # Parameter panel
        self.param_panel = ParameterPanel()
        self.param_panel.setMinimumWidth(320)
        self.param_panel.setMaximumWidth(380)
        content_layout.addWidget(self.param_panel, stretch=2)
        
        main_layout.addLayout(content_layout, stretch=1)
        
        # Action buttons
        action_layout = QHBoxLayout()
        action_layout.addStretch()
        
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.setObjectName("resetButton")
        self.reset_btn.clicked.connect(self.reset_current_stage)
        action_layout.addWidget(self.reset_btn)
        
        self.apply_btn = QPushButton("Apply")
        self.apply_btn.setObjectName("applyButton")
        self.apply_btn.clicked.connect(self.apply_current_stage)
        action_layout.addWidget(self.apply_btn)
        
        action_layout.addStretch()
        main_layout.addLayout(action_layout)
        
        # Navigation
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(16)
        
        self.prev_btn = QPushButton("← Previous")
        self.prev_btn.setObjectName("navButton")
        self.prev_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.prev_btn.clicked.connect(self.prev_slide)
        self.prev_btn.setEnabled(False)
        
        progress_container = QHBoxLayout()
        progress_container.setSpacing(8)
        progress_container.addStretch()
        
        for i in range(10):
            dot = QFrame()
            dot.setObjectName("progressDot")
            dot.setFixedSize(8, 8)
            dot.setStyleSheet("background-color: #228be6; border-radius: 4px;" if i == 0 else "background-color: #dee2e6; border-radius: 4px;")
            self.progress_dots.append(dot)
            progress_container.addWidget(dot)
        
        progress_container.addStretch()
        
        self.next_btn = QPushButton("Next →")
        self.next_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.next_btn.clicked.connect(self.next_slide)
        self.next_btn.setStyleSheet("""
            QPushButton {
                background-color: #228be6; color: white; border: none;
                border-radius: 6px; padding: 12px 32px; font-size: 14px; font-weight: 500;
            }
            QPushButton:hover { background-color: #1c7ed6; }
            QPushButton:disabled { background-color: #adb5bd; }
        """)
        
        nav_layout.addWidget(self.prev_btn)
        nav_layout.addLayout(progress_container, stretch=1)
        nav_layout.addWidget(self.next_btn)
        
        main_layout.addLayout(nav_layout)
        
        # Initialize first slide
        self.update_parameter_panel()
    
    def create_upload_card(self, title, formats, callback, card_type):
        """Create upload card."""
        card = QFrame()
        card.setObjectName("uploadCard")
        card.setFixedHeight(90)
        
        layout = QHBoxLayout(card)
        layout.setContentsMargins(20, 14, 20, 14)
        layout.setSpacing(16)
        
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
        
        btn = QPushButton("Choose File")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(callback)
        layout.addWidget(btn)
        
        return card
    
    def upload_photo(self):
        """Handle photo upload."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select RAW Image", "",
            "RAW Images (*.raw *.cr2 *.nef *.arw *.dng *.orf *.rw2);;All Files (*.*)"
        )
        
        if file_path:
            self.photo_path = file_path
            filename = Path(file_path).name
            self.photo_filename.setText(filename[:35] + "..." if len(filename) > 35 else filename)
            self.photo_filename.setStyleSheet("color: #228be6; font-size: 13px;")
            
            # Load and process
            self.processor.load_raw(file_path, self.params)
            self.update_image_display()
    
    def upload_txt(self):
        """Handle metadata file upload."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Metadata File", "",
            "Text Files (*.txt);;All Files (*.*)"
        )
        
        if file_path:
            self.txt_path = file_path
            filename = Path(file_path).name
            self.txt_filename.setText(filename[:35] + "..." if len(filename) > 35 else filename)
            self.txt_filename.setStyleSheet("color: #228be6; font-size: 13px;")
            
            # Parse metadata
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.metadata = MetadataParser.parse(content)
                
                # Update ISP params from metadata
                self.params.bpp = self.metadata.bpp
                self.params.bayer_pattern = self.metadata.bayer_type
                self.params.packed = bool(self.metadata.packed)
                
                # Refresh panel
                self.update_parameter_panel()
                
            except Exception as e:
                print(f"Error parsing metadata: {e}")
    
    def update_parameter_panel(self):
        """Update parameter panel for current slide."""
        self.param_panel.clear()
        
        # Add metadata if available
        if self.metadata.sensor_name:
            self.param_panel.add_metadata_display(self.metadata)
        
        stage = self.current_slide
        
        if stage == 0:  # Raw Interpretation
            self.param_panel.add_section_header("RAW FORMAT")
            self.param_panel.add_spin_param("Width", "width", self.params.width, 1, 10000)
            self.param_panel.add_spin_param("Height", "height", self.params.height, 1, 10000)
            self.param_panel.add_spin_param("Bits Per Pixel", "bpp", self.params.bpp, 8, 16)
            self.param_panel.add_combo_param("Bayer Pattern", "bayer_pattern", 
                                             ["RGGB", "GRBG", "GBRG", "BGGR"],
                                             BAYER_PATTERNS.get(self.params.bayer_pattern, "RGGB"))
            self.param_panel.add_checkbox_param("Packed Format", "packed", self.params.packed)
            
        elif stage == 1:  # Black Level
            self.param_panel.add_section_header("BLACK LEVEL CORRECTION")
            self.param_panel.add_spin_param("Black Level R", "bl_r", self.params.black_level_r, 0, 1023)
            self.param_panel.add_spin_param("Black Level Gr", "bl_gr", self.params.black_level_gr, 0, 1023)
            self.param_panel.add_spin_param("Black Level Gb", "bl_gb", self.params.black_level_gb, 0, 1023)
            self.param_panel.add_spin_param("Black Level B", "bl_b", self.params.black_level_b, 0, 1023)
            
        elif stage == 2:  # Demosaic
            self.param_panel.add_section_header("DEMOSAICING")
            self.param_panel.add_combo_param("Method", "demosaic_method",
                                             ["Bilinear", "VNG", "AHD", "DCB"],
                                             self.params.demosaic_method)
            self.param_panel.add_slider_param("Edge Threshold", "edge_threshold", 
                                              self.params.edge_threshold, 0.0, 1.0)
            
        elif stage == 3:  # White Balance
            self.param_panel.add_section_header("WHITE BALANCE")
            self.param_panel.add_checkbox_param("Auto White Balance", "auto_wb", self.params.auto_wb)
            self.param_panel.add_slider_param("R Gain", "wb_r", self.params.wb_r_gain, 0.5, 3.0)
            self.param_panel.add_slider_param("G Gain", "wb_g", self.params.wb_g_gain, 0.5, 3.0)
            self.param_panel.add_slider_param("B Gain", "wb_b", self.params.wb_b_gain, 0.5, 3.0)
            
        elif stage == 4:  # Lens Shading
            self.param_panel.add_section_header("LENS SHADING CORRECTION")
            self.param_panel.add_checkbox_param("Enable LSC", "lsc_enabled", self.params.lsc_enabled)
            self.param_panel.add_slider_param("Strength", "lsc_strength", self.params.lsc_strength, 0.0, 2.0)
            self.param_panel.add_slider_param("Center X", "lsc_cx", self.params.lsc_center_x, 0.0, 1.0)
            self.param_panel.add_slider_param("Center Y", "lsc_cy", self.params.lsc_center_y, 0.0, 1.0)
            
        elif stage == 5:  # GTM / LUT
            self.param_panel.add_section_header("GLOBAL TONE MAPPING")
            self.param_panel.add_checkbox_param("Enable GTM", "gtm_enabled", self.params.gtm_enabled)
            self.param_panel.add_slider_param("Strength", "gtm_strength", self.params.gtm_strength, 0.5, 2.0)
            self.param_panel.add_slider_param("Contrast", "gtm_contrast", self.params.gtm_contrast, 0.5, 2.0)
            self.param_panel.add_section_header("LUT")
            # LUT file selector would go here
            
        elif stage == 6:  # Exposure
            self.param_panel.add_section_header("EXPOSURE COMPENSATION")
            self.param_panel.add_slider_param("EV Adjustment", "exposure_ev", self.params.exposure_ev, -3.0, 3.0)
            self.param_panel.add_slider_param("Highlight Recovery", "highlight_rec", 
                                              self.params.highlight_recovery, 0.0, 1.0)
            self.param_panel.add_slider_param("Shadow Recovery", "shadow_rec",
                                              self.params.shadow_recovery, 0.0, 1.0)
            
        elif stage == 7:  # Gamma
            self.param_panel.add_section_header("GAMMA CORRECTION")
            self.param_panel.add_checkbox_param("Enable Gamma", "gamma_enabled", self.params.gamma_enabled)
            self.param_panel.add_slider_param("Gamma Value", "gamma", self.params.gamma_value, 1.0, 3.0)
            
        elif stage == 8:  # Color Correction
            self.param_panel.add_section_header("COLOR CORRECTION")
            self.param_panel.add_slider_param("Saturation", "saturation", self.params.saturation, 0.0, 2.0)
            self.param_panel.add_slider_param("Hue Shift", "hue_shift", self.params.hue_shift, -1.0, 1.0)
            self.param_panel.add_checkbox_param("Enable CCM", "ccm_enabled", self.params.ccm_enabled)
            
        elif stage == 9:  # Output Preview
            self.param_panel.add_section_header("FINAL OUTPUT")
            # Summary of all applied settings
            summary = QLabel("All ISP stages applied.\nImage ready for export.")
            summary.setStyleSheet("color: #495057; font-size: 13px; padding: 12px;")
            summary.setWordWrap(True)
            self.param_panel.layout.addWidget(summary)
        
        self.param_panel.add_stretch()
    
    def apply_current_stage(self):
        """Apply current stage parameters."""
        stage = self.current_slide
        
        # Read values from panel
        widgets = self.param_panel.widgets
        
        if stage == 0:
            if "width" in widgets:
                self.params.width = widgets["width"].value()
            if "height" in widgets:
                self.params.height = widgets["height"].value()
            if "bpp" in widgets:
                self.params.bpp = widgets["bpp"].value()
            if "bayer_pattern" in widgets:
                pattern = widgets["bayer_pattern"].currentText()
                self.params.bayer_pattern = list(BAYER_PATTERNS.values()).index(pattern)
            if "packed" in widgets:
                self.params.packed = widgets["packed"].isChecked()
                
        elif stage == 1:
            if "bl_r" in widgets:
                self.params.black_level_r = widgets["bl_r"].value()
            if "bl_gr" in widgets:
                self.params.black_level_gr = widgets["bl_gr"].value()
            if "bl_gb" in widgets:
                self.params.black_level_gb = widgets["bl_gb"].value()
            if "bl_b" in widgets:
                self.params.black_level_b = widgets["bl_b"].value()
                
        elif stage == 2:
            if "demosaic_method" in widgets:
                self.params.demosaic_method = widgets["demosaic_method"].currentText()
            if "edge_threshold" in widgets:
                self.params.edge_threshold = self.param_panel.get_slider_value("edge_threshold")
                
        elif stage == 3:
            if "auto_wb" in widgets:
                self.params.auto_wb = widgets["auto_wb"].isChecked()
            if "wb_r" in widgets:
                self.params.wb_r_gain = self.param_panel.get_slider_value("wb_r")
            if "wb_g" in widgets:
                self.params.wb_g_gain = self.param_panel.get_slider_value("wb_g")
            if "wb_b" in widgets:
                self.params.wb_b_gain = self.param_panel.get_slider_value("wb_b")
                
        elif stage == 4:
            if "lsc_enabled" in widgets:
                self.params.lsc_enabled = widgets["lsc_enabled"].isChecked()
            if "lsc_strength" in widgets:
                self.params.lsc_strength = self.param_panel.get_slider_value("lsc_strength")
            if "lsc_cx" in widgets:
                self.params.lsc_center_x = self.param_panel.get_slider_value("lsc_cx")
            if "lsc_cy" in widgets:
                self.params.lsc_center_y = self.param_panel.get_slider_value("lsc_cy")
                
        elif stage == 5:
            if "gtm_enabled" in widgets:
                self.params.gtm_enabled = widgets["gtm_enabled"].isChecked()
            if "gtm_strength" in widgets:
                self.params.gtm_strength = self.param_panel.get_slider_value("gtm_strength")
            if "gtm_contrast" in widgets:
                self.params.gtm_contrast = self.param_panel.get_slider_value("gtm_contrast")
                
        elif stage == 6:
            if "exposure_ev" in widgets:
                self.params.exposure_ev = self.param_panel.get_slider_value("exposure_ev")
            if "highlight_rec" in widgets:
                self.params.highlight_recovery = self.param_panel.get_slider_value("highlight_rec")
            if "shadow_rec" in widgets:
                self.params.shadow_recovery = self.param_panel.get_slider_value("shadow_rec")
                
        elif stage == 7:
            if "gamma_enabled" in widgets:
                self.params.gamma_enabled = widgets["gamma_enabled"].isChecked()
            if "gamma" in widgets:
                self.params.gamma_value = self.param_panel.get_slider_value("gamma")
                
        elif stage == 8:
            if "saturation" in widgets:
                self.params.saturation = self.param_panel.get_slider_value("saturation")
            if "hue_shift" in widgets:
                self.params.hue_shift = self.param_panel.get_slider_value("hue_shift")
            if "ccm_enabled" in widgets:
                self.params.ccm_enabled = widgets["ccm_enabled"].isChecked()
        
        self.update_image_display()
    
    def reset_current_stage(self):
        """Reset current stage to defaults."""
        stage = self.current_slide
        
        if stage == 0:
            self.params.width = 4000
            self.params.height = 3000
            self.params.bpp = 10
            self.params.bayer_pattern = 0
            self.params.packed = False
        elif stage == 1:
            self.params.black_level_r = 64
            self.params.black_level_gr = 64
            self.params.black_level_gb = 64
            self.params.black_level_b = 64
        elif stage == 2:
            self.params.demosaic_method = "Bilinear"
            self.params.edge_threshold = 0.1
        elif stage == 3:
            self.params.wb_r_gain = 1.0
            self.params.wb_g_gain = 1.0
            self.params.wb_b_gain = 1.0
            self.params.auto_wb = False
        elif stage == 4:
            self.params.lsc_enabled = True
            self.params.lsc_strength = 1.0
            self.params.lsc_center_x = 0.5
            self.params.lsc_center_y = 0.5
        elif stage == 5:
            self.params.gtm_enabled = True
            self.params.gtm_strength = 1.0
            self.params.gtm_contrast = 1.0
        elif stage == 6:
            self.params.exposure_ev = 0.0
            self.params.highlight_recovery = 0.0
            self.params.shadow_recovery = 0.0
        elif stage == 7:
            self.params.gamma_enabled = True
            self.params.gamma_value = 2.2
        elif stage == 8:
            self.params.saturation = 1.0
            self.params.hue_shift = 0.0
            self.params.ccm_enabled = False
        
        self.update_parameter_panel()
        self.update_image_display()
    
    def update_image_display(self):
        """Update image with current ISP stage processing."""
        if self.processor.raw_data is None:
            return
        
        try:
            # Process up to current stage
            processed = self.processor.process_stage(self.current_slide, self.params)
            
            # Convert to QImage
            qimage = self.processor.to_qimage(processed)
            
            if not qimage.isNull():
                pixmap = QPixmap.fromImage(qimage)
                scaled = pixmap.scaled(
                    self.image_label.width() - 20,
                    self.image_label.height() - 20,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.image_label.setPixmap(scaled)
            else:
                self.image_label.setText("Processing...")
                
        except Exception as e:
            self.image_label.setText(f"Error: {str(e)[:50]}")
    
    def update_progress_dots(self):
        """Update progress indicators."""
        for i, dot in enumerate(self.progress_dots):
            if i == self.current_slide:
                dot.setStyleSheet("background-color: #228be6; border-radius: 4px;")
            elif i < self.current_slide:
                dot.setStyleSheet("background-color: #40c057; border-radius: 4px;")
            else:
                dot.setStyleSheet("background-color: #dee2e6; border-radius: 4px;")
    
    def update_slide(self):
        """Update current slide display."""
        self.slide_title.setText(SLIDE_TITLES[self.current_slide])
        self.slide_counter.setText(f"{self.current_slide + 1} of 10")
        
        self.prev_btn.setEnabled(self.current_slide > 0)
        self.next_btn.setEnabled(self.current_slide < 9)
        
        self.update_progress_dots()
        self.update_parameter_panel()
        self.update_image_display()
    
    def prev_slide(self):
        """Go to previous slide."""
        if self.current_slide > 0:
            self.apply_current_stage()
            self.current_slide -= 1
            self.update_slide()
    
    def next_slide(self):
        """Go to next slide."""
        if self.current_slide < 9:
            self.apply_current_stage()
            self.current_slide += 1
            self.update_slide()
    
    def resizeEvent(self, event):
        """Handle window resize."""
        super().resizeEvent(event)
        if self.processor.raw_data is not None:
            QTimer.singleShot(100, self.update_image_display)


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(26, 26, 26))
    app.setPalette(palette)
    
    window = ISPCarouselApp()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
