#!/usr/bin/env python3
"""
Enhanced Formula Tab - Advanced formula management with add/edit/delete ingredient functionality
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
                             QMessageBox, QInputDialog, QGroupBox, QTabWidget,
                             QDialog, QDialogButtonBox, QLineEdit, QDoubleSpinBox,
                             QFormLayout, QListWidget, QListWidgetItem, QCheckBox,
                             QScrollArea, QFrame, QSplitter, QTextEdit, QSpinBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QIcon

try:
    from src.core.formula_manager import FormulaManager
    from src.core.inventory_manager import InventoryManager
    from src.utils.default_formulas import PACKAGING_INFO
except ImportError:
    from core.formula_manager import FormulaManager
    from core.inventory_manager import InventoryManager
    from utils.default_formulas import PACKAGING_INFO

# Constants for styling
DEFAULT_FONT_SIZE = 14
DEFAULT_FONT = QFont("Arial", DEFAULT_FONT_SIZE)
HEADER_FONT = QFont("Arial", DEFAULT_FONT_SIZE + 2, QFont.Bold)
BUTTON_FONT = QFont("Arial", DEFAULT_FONT_SIZE, QFont.Bold)
TABLE_HEADER_FONT = QFont("Arial", DEFAULT_FONT_SIZE + 1, QFont.Bold)
TABLE_CELL_FONT = QFont("Arial", DEFAULT_FONT_SIZE)

def format_number(value):
    """Format a number with thousands separator, max 2 decimal places, and remove trailing zeros"""
    if value == 0:
        return ""

    if value == int(value):
        return f"{int(value):,}"
    else:
        rounded_value = round(value, 2)
        formatted = f"{rounded_value:,.2f}"
        parts = formatted.split('.')
        if len(parts) == 2:
            decimal_part = parts[1].rstrip('0')
            if decimal_part:
                return f"{parts[0]}.{decimal_part}"
            else:
                return parts[0]
        return formatted

class CustomDoubleSpinBox(QDoubleSpinBox):
    """Custom QDoubleSpinBox with proper number formatting"""
    def textFromValue(self, value):
        if value == 0:
            return ""
        return format_number(value)

    def valueFromText(self, text):
        text = text.replace(',', '')
        try:
            return float(text) if text else 0.0
        except ValueError:
            return 0.0

class IngredientSelectionDialog(QDialog):
    """Dialog for selecting ingredients from inventory"""

    def __init__(self, parent=None, warehouse_type="feed", existing_ingredients=None):
        super().__init__(parent)
        self.warehouse_type = warehouse_type
        self.existing_ingredients = existing_ingredients or []
        self.inventory_manager = InventoryManager()
        self.selected_ingredients = []

        self.setWindowTitle(f"Chọn Nguyên Liệu - {warehouse_type.title()}")
        self.setModal(True)
        self.resize(600, 500)

        self.setup_ui()
        self.load_ingredients()

    def setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout(self)

        # Header
        header = QLabel(f"Chọn nguyên liệu cho công thức {self.warehouse_type}")
        header.setFont(HEADER_FONT)
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("QLabel { padding: 10px; background-color: #e3f2fd; border-radius: 5px; }")
        layout.addWidget(header)

        # Search box
        search_layout = QHBoxLayout()
        search_label = QLabel("Tìm kiếm:")
        search_label.setFont(DEFAULT_FONT)
        self.search_box = QLineEdit()
        self.search_box.setFont(DEFAULT_FONT)
        self.search_box.setPlaceholderText("Nhập tên nguyên liệu...")
        self.search_box.textChanged.connect(self.filter_ingredients)

        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_box)
        layout.addLayout(search_layout)

        # Ingredients list
        self.ingredients_list = QListWidget()
        self.ingredients_list.setFont(DEFAULT_FONT)
        self.ingredients_list.setSelectionMode(QListWidget.MultiSelection)
        layout.addWidget(self.ingredients_list)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def load_ingredients(self):
        """Load available ingredients based on warehouse type"""
        self.ingredients_list.clear()

        if self.warehouse_type == "feed":
            available_ingredients = self.inventory_manager.feed_inventory
        else:
            available_ingredients = self.inventory_manager.mix_inventory

        for ingredient_name, quantity in available_ingredients.items():
            if ingredient_name not in self.existing_ingredients:
                item = QListWidgetItem(f"{ingredient_name} ({format_number(quantity)} kg)")
                item.setData(Qt.UserRole, ingredient_name)
                self.ingredients_list.addItem(item)

    def filter_ingredients(self, text):
        """Filter ingredients based on search text"""
        for i in range(self.ingredients_list.count()):
            item = self.ingredients_list.item(i)
            ingredient_name = item.data(Qt.UserRole)
            item.setHidden(text.lower() not in ingredient_name.lower())

    def accept(self):
        """Accept dialog and collect selected ingredients"""
        self.selected_ingredients = []
        for i in range(self.ingredients_list.count()):
            item = self.ingredients_list.item(i)
            if item.isSelected():
                ingredient_name = item.data(Qt.UserRole)
                self.selected_ingredients.append(ingredient_name)
        super().accept()

class AddIngredientDialog(QDialog):
    """Dialog for adding a new ingredient with quantity"""

    def __init__(self, parent=None, ingredient_name="", warehouse_type="feed"):
        super().__init__(parent)
        self.ingredient_name = ingredient_name
        self.warehouse_type = warehouse_type
        self.quantity = 0.0

        self.setWindowTitle("Thêm Nguyên Liệu")
        self.setModal(True)
        self.resize(400, 200)

        self.setup_ui()

    def setup_ui(self):
        """Setup the dialog UI"""
        layout = QFormLayout(self)

        # Ingredient name (read-only if provided)
        self.name_edit = QLineEdit(self.ingredient_name)
        self.name_edit.setFont(DEFAULT_FONT)
        self.name_edit.setReadOnly(bool(self.ingredient_name))
        layout.addRow("Tên nguyên liệu:", self.name_edit)

        # Quantity
        self.quantity_spin = CustomDoubleSpinBox()
        self.quantity_spin.setFont(DEFAULT_FONT)
        self.quantity_spin.setRange(0, 10000)
        self.quantity_spin.setDecimals(2)
        self.quantity_spin.setSuffix(" kg")
        layout.addRow("Số lượng:", self.quantity_spin)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def accept(self):
        """Validate and accept the dialog"""
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên nguyên liệu!")
            return

        if self.quantity_spin.value() <= 0:
            QMessageBox.warning(self, "Lỗi", "Số lượng phải lớn hơn 0!")
            return

        self.ingredient_name = self.name_edit.text().strip()
        self.quantity = self.quantity_spin.value()
        super().accept()

class EnhancedFormulaTab(QWidget):
    """Enhanced formula tab with advanced ingredient management"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.formula_manager = FormulaManager()
        self.inventory_manager = InventoryManager()

        self.setup_ui()
        self.load_formulas()

    def setup_ui(self):
        """Setup the main UI"""
        layout = QVBoxLayout(self)

        # Header - minimal height
        header = QLabel("Quản Lý Công Thức Nâng Cao")
        minimal_header_font = QFont("Arial", DEFAULT_FONT_SIZE, QFont.Bold)
        header.setFont(minimal_header_font)
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("QLabel { padding: 2px; background-color: #e8f5e8; border-radius: 3px; margin: 1px; }")
        header.setMaximumHeight(30)  # Limit maximum height to 30px
        header.setMinimumHeight(25)  # Set minimum height to 25px
        layout.addWidget(header)

        # Create tabs for Feed and Mix formulas
        self.formula_tabs = QTabWidget()
        self.formula_tabs.setFont(DEFAULT_FONT)
        self.formula_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                background: white;
            }
            QTabBar::tab {
                background: #f0f0f0;
                border: 1px solid #cccccc;
                border-bottom-color: #cccccc;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 12px 20px;
                margin-right: 3px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: #4CAF50;
                color: white;
            }
            QTabBar::tab:!selected {
                margin-top: 3px;
            }
        """)

        # Create feed and mix formula tabs
        self.feed_tab = self.create_formula_tab("feed")
        self.mix_tab = self.create_formula_tab("mix")

        self.formula_tabs.addTab(self.feed_tab, "🌾 Công Thức Cám")
        self.formula_tabs.addTab(self.mix_tab, "🧪 Công Thức Mix")

        layout.addWidget(self.formula_tabs)

    def create_formula_tab(self, formula_type):
        """Create a formula tab for feed or mix"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Tab header
        tab_title = "Công Thức Cám" if formula_type == "feed" else "Công Thức Mix"
        tab_color = "#e3f2fd" if formula_type == "feed" else "#fff8e1"

        tab_header = QLabel(f"Quản Lý {tab_title}")
        minimal_tab_font = QFont("Arial", DEFAULT_FONT_SIZE - 1, QFont.Bold)  # Even smaller font
        tab_header.setFont(minimal_tab_font)
        tab_header.setAlignment(Qt.AlignCenter)
        tab_header.setStyleSheet(f"QLabel {{ padding: 1px; background-color: {tab_color}; border-radius: 2px; margin: 1px; }}")
        tab_header.setMaximumHeight(25)  # Limit maximum height to 25px
        tab_header.setMinimumHeight(20)  # Set minimum height to 20px
        layout.addWidget(tab_header)

        # Create splitter for table and controls
        splitter = QSplitter(Qt.Horizontal)

        # Left side - Formula table
        table_widget = self.create_formula_table(formula_type)
        splitter.addWidget(table_widget)

        # Right side - Controls
        controls_widget = self.create_controls_panel(formula_type)
        splitter.addWidget(controls_widget)

        # Set splitter proportions (70% table, 30% controls)
        splitter.setSizes([700, 300])
        layout.addWidget(splitter)

        return tab

    def create_formula_table(self, formula_type):
        """Create the formula table with enhanced functionality"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Table header with add/remove buttons
        header_layout = QHBoxLayout()

        table_title = QLabel(f"Danh Sách Nguyên Liệu - {formula_type.title()}")
        table_title.setFont(QFont("Arial", DEFAULT_FONT_SIZE + 1, QFont.Bold))
        header_layout.addWidget(table_title)

        header_layout.addStretch()

        # Add ingredient button
        add_btn = QPushButton("➕ Thêm Nguyên Liệu")
        add_btn.setFont(BUTTON_FONT)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 6px;
                padding: 8px 15px;
                min-width: 140px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        add_btn.clicked.connect(lambda: self.add_ingredient(formula_type))
        header_layout.addWidget(add_btn)

        # Remove ingredient button
        remove_btn = QPushButton("➖ Xóa Nguyên Liệu")
        remove_btn.setFont(BUTTON_FONT)
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border-radius: 6px;
                padding: 8px 15px;
                min-width: 140px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        remove_btn.clicked.connect(lambda: self.remove_ingredient(formula_type))
        header_layout.addWidget(remove_btn)

        layout.addLayout(header_layout)

        # Create table
        table = QTableWidget()
        table.setFont(TABLE_CELL_FONT)

        if formula_type == "feed":
            table.setColumnCount(3)
            table.setHorizontalHeaderLabels(["Thành phần", "Tỷ lệ (%)", "Lượng (kg)"])
            self.feed_formula_table = table
        else:
            table.setColumnCount(4)
            table.setHorizontalHeaderLabels(["Thành phần", "Tỷ lệ (%)", "1 mẻ (kg)", "10 mẻ (kg)"])
            self.mix_formula_table = table

        table.horizontalHeader().setFont(TABLE_HEADER_FONT)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Enhanced table styling
        accent_color = "#2196F3" if formula_type == "feed" else "#FF9800"
        table.setStyleSheet(f"""
            QTableWidget {{
                gridline-color: #e0e0e0;
                selection-background-color: #e3f2fd;
                alternate-background-color: #f8f9fa;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                background-color: white;
            }}
            QHeaderView::section {{
                background-color: {accent_color};
                color: white;
                padding: 10px;
                border: none;
                border-right: 1px solid #ffffff;
                font-weight: bold;
            }}
            QTableWidget::item {{
                padding: 8px;
                border-bottom: 1px solid #f0f0f0;
            }}
            QTableWidget::item:selected {{
                background-color: #e3f2fd;
                color: #1976d2;
                font-weight: bold;
            }}
        """)

        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)

        layout.addWidget(table)
        return widget

    def create_controls_panel(self, formula_type):
        """Create the controls panel for formula management"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Controls header
        controls_title = QLabel("Điều Khiển")
        controls_title.setFont(QFont("Arial", DEFAULT_FONT_SIZE + 1, QFont.Bold))
        controls_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(controls_title)

        # Preset management section
        preset_group = QGroupBox("Quản Lý Công Thức Có Sẵn")
        preset_group.setFont(DEFAULT_FONT)
        preset_layout = QVBoxLayout(preset_group)

        # Preset selection
        preset_label = QLabel("Chọn công thức:")
        preset_label.setFont(DEFAULT_FONT)
        preset_layout.addWidget(preset_label)

        if formula_type == "feed":
            self.feed_preset_combo = QComboBox()
            self.feed_preset_combo.setFont(DEFAULT_FONT)
            self.feed_preset_combo.currentIndexChanged.connect(lambda: self.load_preset("feed"))
            preset_layout.addWidget(self.feed_preset_combo)
        else:
            self.mix_preset_combo = QComboBox()
            self.mix_preset_combo.setFont(DEFAULT_FONT)
            self.mix_preset_combo.currentIndexChanged.connect(lambda: self.load_preset("mix"))
            preset_layout.addWidget(self.mix_preset_combo)

        layout.addWidget(preset_group)

        # Action buttons section
        actions_group = QGroupBox("Thao Tác")
        actions_group.setFont(DEFAULT_FONT)
        actions_layout = QVBoxLayout(actions_group)

        # Save current formula
        save_btn = QPushButton("💾 Lưu Công Thức")
        save_btn.setFont(BUTTON_FONT)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border-radius: 6px;
                padding: 10px;
                margin: 2px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        save_btn.clicked.connect(lambda: self.save_formula(formula_type))
        actions_layout.addWidget(save_btn)

        # Save as new preset
        save_as_btn = QPushButton("📋 Lưu Công Thức Mới")
        save_as_btn.setFont(BUTTON_FONT)
        save_as_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 6px;
                padding: 10px;
                margin: 2px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        save_as_btn.clicked.connect(lambda: self.save_as_preset(formula_type))
        actions_layout.addWidget(save_as_btn)

        # Delete preset
        delete_btn = QPushButton("🗑️ Xóa Công Thức")
        delete_btn.setFont(BUTTON_FONT)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border-radius: 6px;
                padding: 10px;
                margin: 2px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        delete_btn.clicked.connect(lambda: self.delete_preset(formula_type))
        actions_layout.addWidget(delete_btn)

        layout.addWidget(actions_group)

        # Validation section
        validation_group = QGroupBox("Kiểm Tra")
        validation_group.setFont(DEFAULT_FONT)
        validation_layout = QVBoxLayout(validation_group)

        # Validate ingredients
        validate_btn = QPushButton("✅ Kiểm Tra Nguyên Liệu")
        validate_btn.setFont(BUTTON_FONT)
        validate_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border-radius: 6px;
                padding: 10px;
                margin: 2px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        validate_btn.clicked.connect(lambda: self.validate_formula(formula_type))
        validation_layout.addWidget(validate_btn)

        # Export formula button
        export_btn = QPushButton("📤 Xuất Excel")
        export_btn.setFont(BUTTON_FONT)
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #9C27B0;
                color: white;
                border-radius: 6px;
                padding: 10px;
                margin: 2px;
            }
            QPushButton:hover {
                background-color: #7B1FA2;
            }
        """)
        export_btn.clicked.connect(lambda: self.export_formula(formula_type))
        validation_layout.addWidget(export_btn)

        layout.addWidget(validation_group)

        # Add stretch to push everything to top
        layout.addStretch()

        return widget

    def export_formula(self, formula_type):
        """Xuất công thức ra Excel với dialog tối ưu"""
        try:
            # Kiểm tra nếu parent có method open_export_dialog
            if hasattr(self.parent, 'open_export_dialog'):
                self.parent.open_export_dialog("formula")
            else:
                # Fallback: tạo dialog trực tiếp với ưu tiên dialog tối ưu
                try:
                    from src.ui.dialogs.enhanced_export_dialog import EnhancedExportDialog
                    dialog = EnhancedExportDialog(self.parent, "formula")
                    dialog.exec_()
                except ImportError:
                    try:
                        from ui.dialogs.enhanced_export_dialog import EnhancedExportDialog
                        dialog = EnhancedExportDialog(self.parent, "formula")
                        dialog.exec_()
                    except ImportError:
                        # Fallback to simple dialog
                        try:
                            from src.ui.dialogs.simple_warehouse_export_dialog import SimpleWarehouseExportDialog
                            dialog = SimpleWarehouseExportDialog(self.parent, "formula")
                            dialog.exec_()
                        except ImportError:
                            try:
                                from ui.dialogs.simple_warehouse_export_dialog import SimpleWarehouseExportDialog
                                dialog = SimpleWarehouseExportDialog(self.parent, "formula")
                                dialog.exec_()
                            except ImportError as e:
                                QMessageBox.critical(self, "Lỗi", f"Không thể tải dialog xuất báo cáo: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể xuất công thức: {str(e)}")

    def load_formulas(self):
        """Load current formulas and update tables"""
        self.update_formula_table("feed")
        self.update_formula_table("mix")
        self.update_preset_combos()

    def update_preset_combos(self):
        """Update preset combo boxes"""
        # Update feed presets
        if hasattr(self, 'feed_preset_combo'):
            self.feed_preset_combo.clear()
            feed_presets = self.formula_manager.get_feed_presets()
            for preset in feed_presets:
                self.feed_preset_combo.addItem(preset)

        # Update mix presets
        if hasattr(self, 'mix_preset_combo'):
            self.mix_preset_combo.clear()
            mix_presets = self.formula_manager.get_mix_presets()
            for preset in mix_presets:
                self.mix_preset_combo.addItem(preset)

    def add_ingredient(self, formula_type):
        """Add new ingredient(s) to formula"""
        try:
            # Get current formula to check existing ingredients
            if formula_type == "feed":
                current_formula = self.formula_manager.get_feed_formula()
            else:
                current_formula = self.formula_manager.get_mix_formula()

            existing_ingredients = list(current_formula.keys())

            # Show ingredient selection dialog
            dialog = IngredientSelectionDialog(
                parent=self,
                warehouse_type=formula_type,
                existing_ingredients=existing_ingredients
            )

            if dialog.exec_() == QDialog.Accepted:
                selected_ingredients = dialog.selected_ingredients

                if not selected_ingredients:
                    QMessageBox.information(self, "Thông báo", "Không có nguyên liệu nào được chọn!")
                    return

                # Add each selected ingredient with default quantity
                for ingredient_name in selected_ingredients:
                    # Show dialog to set quantity
                    quantity_dialog = AddIngredientDialog(
                        parent=self,
                        ingredient_name=ingredient_name,
                        warehouse_type=formula_type
                    )

                    if quantity_dialog.exec_() == QDialog.Accepted:
                        # Add ingredient to formula
                        current_formula[ingredient_name] = quantity_dialog.quantity

                # Save updated formula
                if formula_type == "feed":
                    self.formula_manager.set_feed_formula(current_formula)
                else:
                    self.formula_manager.set_mix_formula(current_formula)

                # Update table display
                self.update_formula_table(formula_type)

                # Success notification removed for cleaner UX

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể thêm nguyên liệu: {str(e)}")

    def remove_ingredient(self, formula_type):
        """Remove selected ingredient from formula"""
        try:
            # Get the appropriate table
            table = self.feed_formula_table if formula_type == "feed" else self.mix_formula_table

            # Get selected rows
            selected_rows = set()
            for item in table.selectedItems():
                selected_rows.add(item.row())

            if not selected_rows:
                QMessageBox.information(self, "Thông báo", "Vui lòng chọn nguyên liệu cần xóa!")
                return

            # Get current formula
            if formula_type == "feed":
                current_formula = self.formula_manager.get_feed_formula()
            else:
                current_formula = self.formula_manager.get_mix_formula()

            # Get ingredient names to remove
            ingredients_to_remove = []
            for row in selected_rows:
                # Skip total row (last row)
                if row < table.rowCount() - 1:
                    ingredient_item = table.item(row, 0)
                    if ingredient_item:
                        ingredient_name = ingredient_item.text()
                        ingredients_to_remove.append(ingredient_name)

            if not ingredients_to_remove:
                QMessageBox.information(self, "Thông báo", "Không có nguyên liệu hợp lệ để xóa!")
                return

            # Confirm deletion
            ingredient_list = "\n".join(ingredients_to_remove)
            reply = QMessageBox.question(
                self,
                "Xác nhận xóa",
                f"Bạn có chắc chắn muốn xóa các nguyên liệu sau khỏi công thức {formula_type}?\n\n{ingredient_list}",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                # Remove ingredients from formula
                for ingredient_name in ingredients_to_remove:
                    if ingredient_name in current_formula:
                        del current_formula[ingredient_name]

                # Save updated formula
                if formula_type == "feed":
                    self.formula_manager.set_feed_formula(current_formula)
                else:
                    self.formula_manager.set_mix_formula(current_formula)

                # Update table display
                self.update_formula_table(formula_type)

                # Success notification removed for cleaner UX

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể xóa nguyên liệu: {str(e)}")

    def validate_formula(self, formula_type):
        """Validate formula ingredients against inventory"""
        try:
            # Get current formula
            if formula_type == "feed":
                current_formula = self.formula_manager.get_feed_formula()
            else:
                current_formula = self.formula_manager.get_mix_formula()

            if not current_formula:
                QMessageBox.information(self, "Thông báo", f"Công thức {formula_type} trống!")
                return

            # Validate against inventory
            validation_result = self.inventory_manager.validate_formula_ingredients(
                current_formula, formula_type
            )

            if validation_result["valid"]:
                # Success notification removed for cleaner UX - validation passes silently
                pass
            else:
                missing_ingredients = validation_result.get("missing_ingredients", [])
                insufficient_ingredients = validation_result.get("insufficient_ingredients", [])

                error_msg = f"Công thức {formula_type} có vấn đề:\n\n"

                if missing_ingredients:
                    error_msg += "Nguyên liệu không có trong kho:\n"
                    for ingredient in missing_ingredients:
                        error_msg += f"• {ingredient}\n"
                    error_msg += "\n"

                if insufficient_ingredients:
                    error_msg += "Nguyên liệu không đủ số lượng:\n"
                    for ingredient_info in insufficient_ingredients:
                        ingredient = ingredient_info["ingredient"]
                        required = ingredient_info["required"]
                        available = ingredient_info["available"]
                        error_msg += f"• {ingredient}: cần {format_number(required)} kg, có {format_number(available)} kg\n"

                QMessageBox.warning(self, "Kiểm tra thất bại", error_msg)

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể kiểm tra công thức: {str(e)}")

    def update_formula_table(self, formula_type):
        """Update formula table with current data"""
        try:
            # Get current formula
            if formula_type == "feed":
                current_formula = self.formula_manager.get_feed_formula()
                table = self.feed_formula_table
            else:
                current_formula = self.formula_manager.get_mix_formula()
                table = self.mix_formula_table

            # Calculate total
            total_amount = sum(current_formula.values())

            # Set table row count (ingredients + total row)
            table.setRowCount(len(current_formula) + 1)

            # Populate table
            row = 0
            for ingredient, amount in current_formula.items():
                # Ingredient name
                ingredient_item = QTableWidgetItem(ingredient)
                ingredient_item.setFont(TABLE_CELL_FONT)
                table.setItem(row, 0, ingredient_item)

                # Percentage
                percentage = (amount / total_amount * 100) if total_amount > 0 else 0
                percentage_item = QTableWidgetItem(f"{format_number(percentage)} %")
                percentage_item.setFont(TABLE_CELL_FONT)
                percentage_item.setTextAlignment(Qt.AlignCenter)
                table.setItem(row, 1, percentage_item)

                if formula_type == "feed":
                    # Amount input for feed
                    amount_spin = CustomDoubleSpinBox()
                    amount_spin.setFont(TABLE_CELL_FONT)
                    amount_spin.setMinimumHeight(30)
                    amount_spin.setRange(0, 10000)
                    amount_spin.setDecimals(2)
                    amount_spin.setValue(amount)
                    amount_spin.valueChanged.connect(lambda: self.on_formula_value_changed(formula_type))
                    table.setCellWidget(row, 2, amount_spin)
                else:
                    # Mix formula - 1 batch and 10 batch columns
                    one_batch_amount = amount / 10
                    one_batch_item = QTableWidgetItem(format_number(one_batch_amount))
                    one_batch_item.setFont(TABLE_CELL_FONT)
                    one_batch_item.setTextAlignment(Qt.AlignCenter)
                    one_batch_item.setBackground(QColor(240, 248, 255))
                    table.setItem(row, 2, one_batch_item)

                    # 10 batch input
                    amount_spin = CustomDoubleSpinBox()
                    amount_spin.setFont(TABLE_CELL_FONT)
                    amount_spin.setMinimumHeight(30)
                    amount_spin.setRange(0, 10000)
                    amount_spin.setDecimals(2)
                    amount_spin.setValue(amount)
                    amount_spin.valueChanged.connect(lambda: self.on_formula_value_changed(formula_type))
                    table.setCellWidget(row, 3, amount_spin)

                row += 1

            # Add total row
            self.add_total_row(table, formula_type, total_amount)

            # Set row heights
            for i in range(table.rowCount()):
                table.setRowHeight(i, 40)

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể cập nhật bảng công thức: {str(e)}")

    def add_total_row(self, table, formula_type, total_amount):
        """Add total row to formula table"""
        total_row = table.rowCount() - 1

        # Total label
        total_item = QTableWidgetItem(f"Tổng lượng {formula_type.title()}")
        total_item.setFont(QFont("Arial", DEFAULT_FONT_SIZE + 1, QFont.Bold))
        table.setItem(total_row, 0, total_item)

        # Total percentage (always 100%)
        total_percentage = QTableWidgetItem("100 %")
        total_percentage.setFont(QFont("Arial", DEFAULT_FONT_SIZE + 1, QFont.Bold))
        total_percentage.setBackground(QColor(200, 230, 250))
        total_percentage.setTextAlignment(Qt.AlignCenter)
        table.setItem(total_row, 1, total_percentage)

        if formula_type == "feed":
            # Total amount for feed
            total_value = QTableWidgetItem(format_number(total_amount))
            total_value.setFont(QFont("Arial", DEFAULT_FONT_SIZE + 1, QFont.Bold))
            total_value.setBackground(QColor(200, 230, 250))
            table.setItem(total_row, 2, total_value)
        else:
            # Total for mix - both 1 batch and 10 batch
            total_one_batch = total_amount / 10
            total_one_batch_item = QTableWidgetItem(format_number(total_one_batch))
            total_one_batch_item.setFont(QFont("Arial", DEFAULT_FONT_SIZE + 1, QFont.Bold))
            total_one_batch_item.setBackground(QColor(230, 250, 200))
            total_one_batch_item.setTextAlignment(Qt.AlignCenter)
            table.setItem(total_row, 2, total_one_batch_item)

            total_ten_batch_item = QTableWidgetItem(format_number(total_amount))
            total_ten_batch_item.setFont(QFont("Arial", DEFAULT_FONT_SIZE + 1, QFont.Bold))
            total_ten_batch_item.setBackground(QColor(230, 250, 200))
            table.setItem(total_row, 3, total_ten_batch_item)

    def on_formula_value_changed(self, formula_type):
        """Handle formula value changes"""
        try:
            # Get the table
            table = self.feed_formula_table if formula_type == "feed" else self.mix_formula_table

            # Collect updated formula data
            updated_formula = {}

            for row in range(table.rowCount() - 1):  # Exclude total row
                ingredient_item = table.item(row, 0)
                if ingredient_item:
                    ingredient_name = ingredient_item.text()

                    if formula_type == "feed":
                        amount_widget = table.cellWidget(row, 2)
                    else:
                        amount_widget = table.cellWidget(row, 3)  # 10 batch column

                    if amount_widget and isinstance(amount_widget, CustomDoubleSpinBox):
                        amount = amount_widget.value()
                        updated_formula[ingredient_name] = amount

            # Save updated formula
            if formula_type == "feed":
                self.formula_manager.set_feed_formula(updated_formula)
            else:
                self.formula_manager.set_mix_formula(updated_formula)

            # Update table display (percentages and totals)
            self.update_formula_table(formula_type)

        except Exception as e:
            print(f"Error updating formula values: {e}")

    def load_preset(self, formula_type):
        """Load selected preset"""
        try:
            if formula_type == "feed":
                combo = self.feed_preset_combo
                preset_name = combo.currentText()
                if preset_name:
                    preset_formula = self.formula_manager.load_feed_preset(preset_name)
                    if preset_formula:
                        self.formula_manager.set_feed_formula(preset_formula)
                        self.update_formula_table("feed")
                        # Success notification removed for cleaner UX
            else:
                combo = self.mix_preset_combo
                preset_name = combo.currentText()
                if preset_name:
                    preset_formula = self.formula_manager.load_mix_preset(preset_name)
                    if preset_formula:
                        self.formula_manager.set_mix_formula(preset_formula)
                        self.update_formula_table("mix")
                        # Success notification removed for cleaner UX

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể tải công thức: {str(e)}")

    def save_formula(self, formula_type):
        """Save current formula"""
        try:
            if formula_type == "feed":
                success = self.formula_manager.set_feed_formula(self.formula_manager.get_feed_formula())
            else:
                success = self.formula_manager.set_mix_formula(self.formula_manager.get_mix_formula())

            # Success notification removed for cleaner UX
            if not success:
                QMessageBox.warning(self, "Lỗi", f"Không thể lưu công thức {formula_type}!")

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu công thức: {str(e)}")

    def save_as_preset(self, formula_type):
        """Save current formula as new preset"""
        try:
            preset_name, ok = QInputDialog.getText(self, "Lưu công thức mới", "Tên công thức:")

            if ok and preset_name.strip():
                preset_name = preset_name.strip()

                # Get current formula
                if formula_type == "feed":
                    current_formula = self.formula_manager.get_feed_formula()
                else:
                    current_formula = self.formula_manager.get_mix_formula()

                # Save as preset
                success = self.formula_manager.save_preset(formula_type, preset_name, current_formula)

                if success:
                    self.update_preset_combos()
                    # Success notification removed for cleaner UX
                else:
                    QMessageBox.warning(self, "Lỗi", f"Không thể lưu công thức '{preset_name}'!")

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu công thức mới: {str(e)}")

    def delete_preset(self, formula_type):
        """Delete selected preset"""
        try:
            if formula_type == "feed":
                combo = self.feed_preset_combo
            else:
                combo = self.mix_preset_combo

            preset_name = combo.currentText()

            if not preset_name:
                QMessageBox.information(self, "Thông báo", "Vui lòng chọn công thức cần xóa!")
                return

            # Confirm deletion
            reply = QMessageBox.question(
                self,
                "Xác nhận xóa",
                f"Bạn có chắc chắn muốn xóa công thức '{preset_name}'?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                success = self.formula_manager.delete_preset(formula_type, preset_name)

                if success:
                    self.update_preset_combos()
                    # Success notification removed for cleaner UX
                else:
                    QMessageBox.warning(self, "Lỗi", f"Không thể xóa công thức '{preset_name}'!")

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể xóa công thức: {str(e)}")
