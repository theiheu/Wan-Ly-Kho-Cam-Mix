#!/usr/bin/env python3
"""
Test script to simulate 1366x768 screen resolution for responsive design testing
"""

import sys
import os
from unittest.mock import Mock, patch

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QRect
from PyQt5.QtGui import QScreen

def create_mock_screen_1366x768():
    """Create a mock screen object for 1366x768 resolution"""
    mock_screen = Mock(spec=QScreen)
    mock_screen.geometry.return_value = QRect(0, 0, 1366, 768)
    mock_screen.logicalDotsPerInch.return_value = 96
    return mock_screen

def test_responsive_calculations():
    """Test responsive calculations for 1366x768"""
    print("=== TESTING RESPONSIVE DESIGN FOR 1366x768 ===\n")
    
    # Mock the screen
    mock_screen = create_mock_screen_1366x768()
    
    with patch('PyQt5.QtWidgets.QApplication.primaryScreen', return_value=mock_screen):
        # Import and create app instance
        from main import ChickenFarmApp
        
        app = QApplication(sys.argv)
        
        # Create main window instance
        window = ChickenFarmApp()
        
        # Test calculations
        print("SCREEN DETECTION:")
        print(f"  Resolution: {window.screen_width}x{window.screen_height}")
        print(f"  Category: {'Small' if window.is_small_screen else 'Medium' if window.is_medium_screen else 'Large'}")
        print(f"  Scale Factor: {window.scale_factor:.3f}")
        
        print("\nDIALOG SIZING:")
        dialog_w, dialog_h = window.get_responsive_dialog_size()
        print(f"  Dialog Size: {dialog_w}x{dialog_h}")
        print(f"  Width Ratio: {window.responsive_dialog_width_ratio:.2f}")
        print(f"  Height Ratio: {window.responsive_dialog_height_ratio:.2f}")
        
        print("\nFONT SCALING:")
        print(f"  Base 16px → {window.get_responsive_font_size(16)}px")
        print(f"  Base 17px → {window.get_responsive_font_size(17)}px")
        print(f"  Base 14px → {window.get_responsive_font_size(14)}px")
        
        print("\nROW HEIGHT SCALING:")
        print(f"  Base 70px → {window.get_responsive_row_height(70)}px")
        print(f"  Base 65px → {window.get_responsive_row_height(65)}px")
        print(f"  Base 50px → {window.get_responsive_row_height(50)}px")
        
        print("\nTABLE HEIGHT SCALING:")
        print(f"  Base 500px → {window.get_responsive_table_height(500)}px")
        print(f"  Base 400px → {window.get_responsive_table_height(400)}px")
        print(f"  Base 300px → {window.get_responsive_table_height(300)}px")
        
        print("\nMAIN WINDOW SIZING:")
        print(f"  Window Size: {window.width()}x{window.height()}")
        print(f"  Position: ({window.x()}, {window.y()})")
        
        # Test CSS generation
        print("\nCSS GENERATION TEST:")
        css = window.get_responsive_table_css()
        print("  CSS generated successfully ✓")
        
        # Extract key values from CSS
        import re
        font_size_match = re.search(r'font-size: (\d+)px', css)
        min_height_match = re.search(r'min-height: (\d+)px', css)
        
        if font_size_match:
            print(f"  CSS Font Size: {font_size_match.group(1)}px")
        if min_height_match:
            print(f"  CSS Min Height: {min_height_match.group(1)}px")
        
        print("\n=== EXPECTED VALUES FOR 1366x768 ===")
        print("  Screen Category: Medium")
        print("  Scale Factor: ~0.71 (clamped to 0.85)")
        print("  Dialog Size: ~1161x629 (85% x 82%)")
        print("  Font 16px → ~14px (clamped)")
        print("  Row 70px → ~60px (clamped)")
        print("  Table 500px → ~425px (85%)")
        
        print("\n=== TEST COMPLETED ===")
        
        app.quit()

if __name__ == "__main__":
    test_responsive_calculations()
