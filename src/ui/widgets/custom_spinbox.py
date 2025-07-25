"""
Custom spinbox widgets for the Chicken Farm App
"""

from PyQt5.QtWidgets import QDoubleSpinBox
from src.utils.formatting import format_number

class CustomDoubleSpinBox(QDoubleSpinBox):
    """Custom QDoubleSpinBox để định dạng số theo yêu cầu"""

    def textFromValue(self, value):
        """Định dạng số với dấu phẩy ngăn cách hàng nghìn, tối đa 2 chữ số thập phân và loại bỏ số 0 thừa ở cuối"""
        # Nếu giá trị là 0, trả về chuỗi rỗng thay vì số 0
        if value == 0:
            return ""
        return format_number(value)

    def valueFromText(self, text):
        """Chuyển đổi từ chuỗi có định dạng về số"""
        # Loại bỏ dấu phẩy ngăn cách hàng nghìn
        text = text.replace(',', '')
        return float(text) if text else 0