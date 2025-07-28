#!/usr/bin/env python3
"""
Test script to verify imports
"""

try:
    print("Testing PyQt5 imports...")
    from PyQt5.QtWidgets import QApplication, QTextEdit, QWidget
    print("✅ QTextEdit imported successfully")
    
    print("Testing main.py import...")
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    
    # Test specific import
    from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout,
                                QHBoxLayout, QGridLayout, QLabel, QLineEdit, QPushButton,
                                QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
                                QMessageBox, QFileDialog, QSpinBox, QDoubleSpinBox, QInputDialog,
                                QGroupBox, QDialog, QRadioButton, QDateEdit, QScrollArea, QSizePolicy,
                                QMenu, QAction, QAbstractSpinBox, QAbstractItemView, QCalendarWidget,
                                QCheckBox, QListWidget, QListWidgetItem, QTextEdit)
    
    print("✅ All imports successful")
    
    # Test QTextEdit creation
    app = QApplication([])
    text_edit = QTextEdit()
    print("✅ QTextEdit created successfully")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
