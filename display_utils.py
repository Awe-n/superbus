#!/usr/bin/env python3
"""
Display Utilities Module
Shared utilities for the e-Paper display
"""

import os
import logging
from PIL import Image, ImageFont

# =============================================================================
# FONT LOADING
# =============================================================================

def load_fonts(picdir=None):
    """Load fonts with adjusted sizes for display"""
    try:
        font_header = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 24)
        font_stop = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
        font_huge = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 32)
        font_large = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)
        font_small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 11)
        font_welcome = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 30)
        font_time = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 28)
        font_date = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 20)
        logging.info("✓ Fonts loaded!")
        return font_header, font_stop, font_huge, font_large, font_small, font_welcome, font_time, font_date
    except Exception as e:
        logging.warning(f"Could not load DejaVu fonts: {e}")
        try:
            if picdir:
                font_path = os.path.join(picdir, 'Font.ttc')
                font_header = ImageFont.truetype(font_path, 24)
                font_stop = ImageFont.truetype(font_path, 14)
                font_huge = ImageFont.truetype(font_path, 32)
                font_large = ImageFont.truetype(font_path, 16)
                font_small = ImageFont.truetype(font_path, 11)
                font_welcome = ImageFont.truetype(font_path, 30)
                font_time = ImageFont.truetype(font_path, 28)
                font_date = ImageFont.truetype(font_path, 20)
                logging.info("✓ Fallback fonts loaded!")
                return font_header, font_stop, font_huge, font_large, font_small, font_welcome, font_time, font_date
        except Exception as e2:
            logging.warning(f"Could not load fallback fonts: {e2}")
        
        # Last resort: default fonts
        default = ImageFont.load_default()
        logging.warning("⚠ Using default fonts")
        return default, default, default, default, default, default, default, default

# =============================================================================
# BLANK SCREEN
# =============================================================================

def create_blank_screen(epd):
    """Create a blank white screen"""
    image = Image.new('1', (epd.height, epd.width), 255)
    return image
