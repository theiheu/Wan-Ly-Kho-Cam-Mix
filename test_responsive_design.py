#!/usr/bin/env python3
"""
Test script để verify responsive design system
"""

import sys
import os

# Setup environment
project_root = os.path.dirname(os.path.abspath(__file__))
os.chdir(project_root)
sys.path.insert(0, project_root)

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QRect
from src.main import ChickenFarmApp

def test_responsive_design():
    """Test responsive design với các screen resolutions khác nhau"""
    
    print("=" * 80)
    print("COMPREHENSIVE RESPONSIVE DESIGN VERIFICATION")
    print("=" * 80)
    
    # Test cases cho các screen resolutions khác nhau
    test_cases = [
        # Small screens (width < 1366px) - Should use 0.10 scale factor
        {"name": "Small Screen 1024x768", "width": 1024, "height": 768, "expected_scale": "0.08-0.12"},
        {"name": "Small Screen 1280x720", "width": 1280, "height": 720, "expected_scale": "0.08-0.12"},
        {"name": "Small Screen 1280x1024", "width": 1280, "height": 1024, "expected_scale": "0.08-0.12"},
        
        # 1366x768 resolution - Should use 0.30 scale factor
        {"name": "1366x768 Resolution", "width": 1366, "height": 768, "expected_scale": "0.25-0.35"},
        
        # Medium screens (1366 < width ≤ 1600px) - Should use 0.75-1.0 scale factor
        {"name": "Medium Screen 1440x900", "width": 1440, "height": 900, "expected_scale": "0.75-1.0"},
        {"name": "Medium Screen 1600x900", "width": 1600, "height": 900, "expected_scale": "0.75-1.0"},
        
        # Large screens (width > 1600px) - Should use 0.8-1.5 scale factor
        {"name": "Large Screen 1920x1080", "width": 1920, "height": 1080, "expected_scale": "0.8-1.5"},
        {"name": "Large Screen 2560x1440", "width": 2560, "height": 1440, "expected_scale": "0.8-1.5"},
    ]
    
    app = QApplication(sys.argv)
    
    for i, test_case in enumerate(test_cases):
        print(f"\n{i+1}. Testing {test_case['name']}")
        print("-" * 60)
        
        # Simulate screen geometry
        screen = app.primaryScreen()
        original_geometry = screen.geometry()
        
        # Create test geometry
        test_geometry = QRect(0, 0, test_case['width'], test_case['height'])
        
        # Create ChickenFarmApp instance
        try:
            # Monkey patch screen geometry for testing
            def mock_geometry():
                return test_geometry
            
            screen.geometry = mock_geometry
            
            # Create app instance
            window = ChickenFarmApp()
            
            # Verify scale factor
            actual_scale = window.scale_factor
            print(f"Screen Resolution: {test_case['width']}x{test_case['height']}")
            print(f"Expected Scale Range: {test_case['expected_scale']}")
            print(f"Actual Scale Factor: {actual_scale:.3f}")
            
            # Verify screen category
            if window.is_small_screen:
                category = "Small"
            elif window.is_medium_screen:
                category = "Medium"
            else:
                category = "Large"
            print(f"Screen Category: {category}")
            
            # Verify dialog ratios
            print(f"Dialog Ratios: {window.responsive_dialog_width_ratio:.2f}w x {window.responsive_dialog_height_ratio:.2f}h")
            
            # Test responsive methods
            font_12px = window.get_responsive_font_size(12)
            row_30px = window.get_responsive_row_height(30)
            table_500px = window.get_responsive_table_height(500)
            
            print(f"Font Size: 12px → {font_12px}px")
            print(f"Row Height: 30px → {row_30px}px")
            print(f"Table Height: 500px → {table_500px}px")
            
            # Verify scale factor is in expected range
            expected_ranges = {
                "0.08-0.12": (0.08, 0.12),
                "0.25-0.35": (0.25, 0.35),
                "0.75-1.0": (0.75, 1.0),
                "0.8-1.5": (0.8, 1.5)
            }
            
            min_scale, max_scale = expected_ranges[test_case['expected_scale']]
            if min_scale <= actual_scale <= max_scale:
                print("✅ Scale factor is within expected range")
            else:
                print("❌ Scale factor is outside expected range")
            
            # Clean up
            window.close()
            
        except Exception as e:
            print(f"❌ Error testing {test_case['name']}: {e}")
        
        # Restore original geometry
        screen.geometry = lambda: original_geometry
    
    print("\n" + "=" * 80)
    print("VERIFICATION COMPLETE")
    print("=" * 80)
    
    app.quit()

if __name__ == "__main__":
    test_responsive_design()
