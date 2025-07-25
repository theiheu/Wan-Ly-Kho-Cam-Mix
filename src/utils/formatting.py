"""
Utility functions for formatting data in the Chicken Farm App
"""

def format_number(value):
    """Format a number with thousands separator, max 2 decimal places, and remove trailing zeros"""
    # Nếu giá trị là 0, trả về chuỗi rỗng
    if value == 0:
        return ""

    if value == int(value):
        # Nếu là số nguyên, hiển thị không có phần thập phân và thêm dấu phẩy ngăn cách hàng nghìn
        return f"{int(value):,}"
    else:
        # Làm tròn đến 2 chữ số thập phân
        rounded_value = round(value, 2)

        # Định dạng với dấu phẩy ngăn cách hàng nghìn
        formatted = f"{rounded_value:,.2f}"

        # Tách phần nguyên và phần thập phân
        parts = formatted.split('.')
        if len(parts) == 2:
            # Loại bỏ số 0 thừa ở cuối phần thập phân
            decimal_part = parts[1].rstrip('0')
            if decimal_part:
                return f"{parts[0]}.{decimal_part}"
            else:
                return parts[0]
        return formatted