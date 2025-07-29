#!/usr/bin/env python3
"""
Simple test để verify responsive design
"""

import sys
import os

# Setup environment
project_root = os.path.dirname(os.path.abspath(__file__))
os.chdir(project_root)
sys.path.insert(0, project_root)

print("Testing responsive design system...")

try:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import QRect
    
    print("PyQt5 imported successfully")
    
    # Create minimal QApplication
    app = QApplication([])
    print("QApplication created")
    
    # Get screen info
    screen = app.primaryScreen()
    geometry = screen.geometry()
    print(f"Current screen: {geometry.width()}x{geometry.height()}")
    
    # Test scale factor calculation logic
    def test_scale_factor(width, height):
        print(f"\nTesting {width}x{height}:")
        
        # Calculate base scale factor
        width_scale = width / 1920
        height_scale = height / 1080
        base_scale = min(width_scale, height_scale)
        print(f"  Base scale factor: {base_scale:.3f}")
        
        # Apply scale factor logic
        if width < 1366:
            scale_factor = max(0.08, min(0.12, base_scale))
            category = "Small (EXTREME-COMPACT-0.10)"
        elif width == 1366:
            scale_factor = max(0.25, min(0.35, base_scale))
            category = "1366x768 (ULTRA-COMPACT-0.30)"
        elif width <= 1600:
            scale_factor = max(0.75, min(1.0, base_scale))
            category = "Medium"
        else:
            scale_factor = max(0.8, min(1.5, base_scale))
            category = "Large"
        
        print(f"  Applied scale factor: {scale_factor:.3f}")
        print(f"  Category: {category}")
        
        # Test font size calculation
        base_font = 12
        scaled_font = int(base_font * scale_factor * 0.8)
        
        if width < 1366:
            final_font = max(7, min(9, scaled_font))
        elif width == 1366:
            final_font = max(8, min(10, scaled_font))
        elif width <= 1600:
            final_font = max(10, min(13, scaled_font))
        else:
            final_font = max(11, min(15, scaled_font))
        
        print(f"  Font: 12px → {final_font}px")
        
        # Test row height calculation
        base_row = 30
        scaled_row = int(base_row * scale_factor * 0.6)
        
        if width < 1366:
            final_row = max(15, min(22, scaled_row))
        elif width == 1366:
            final_row = max(18, min(25, scaled_row))
        elif width <= 1600:
            final_row = max(35, min(45, scaled_row))
        else:
            final_row = max(40, min(50, scaled_row))
        
        print(f"  Row: 30px → {final_row}px")
        
        return scale_factor, final_font, final_row
    
    # Test different resolutions
    test_resolutions = [
        (1024, 768),   # Small screen
        (1280, 720),   # Small screen
        (1366, 768),   # 1366x768
        (1440, 900),   # Medium screen
        (1920, 1080),  # Large screen
        (2560, 1440),  # Large screen
    ]
    
    print("\n" + "="*60)
    print("RESPONSIVE DESIGN VERIFICATION RESULTS")
    print("="*60)
    
    for width, height in test_resolutions:
        scale, font, row = test_scale_factor(width, height)
    
    print("\n" + "="*60)
    print("VERIFICATION COMPLETE")
    print("="*60)
    
    app.quit()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
