# Constants for the Chicken Farm App

# Number of areas
AREAS = 5

# Shifts
SHIFTS = ["Sáng", "Chiều"]  # Morning and afternoon shifts

# Định nghĩa các trại cho từng khu
FARMS = {
    0: ["T1", "T2", "T4", "T6"],          # Khu 1
    1: ["T1", "T2", "T4", "T6"],          # Khu 2
    2: ["1D", "2D", "4D", "2N"],          # Khu 3
    3: ["T2", "T4", "T6", "T8", "Trại 1 khu 4"],  # Khu 4
    4: [""]                           # Khu 5
}

# Font settings
DEFAULT_FONT_SIZE = 14
HEADER_FONT_SIZE = DEFAULT_FONT_SIZE + 2
BUTTON_FONT_SIZE = DEFAULT_FONT_SIZE
TABLE_HEADER_FONT_SIZE = DEFAULT_FONT_SIZE + 1
TABLE_CELL_FONT_SIZE = DEFAULT_FONT_SIZE

# Packaging information
PACKAGING_INFO = {
    "Bắp": 50,
    "Nành": 50,
    "Cám gạo": 50,
    "Cám mì": 50,
    "Khô dầu dừa": 50,
    "DDGS": 50,
    "Bột cá": 50,
    "Bột thịt xương": 50,
    "Bột đá": 50,
    "Premix khoáng": 25,
    "Premix vitamin": 25,
    "Methionine": 25,
    "Lysine": 25,
    "Threonine": 25,
    "Choline": 25,
    "Enzyme phytase": 25,
    "Enzyme NSP": 25,
    "Chất chống mốc": 25,
    "Chất tạo màu": 25,
    "Muối": 50,
    "Nguyên liệu tổ hợp": 50
}