import json
import os
from src.utils.default_formulas import (
    LAYER_FEED_FORMULA,
    LAYER_MIX_FORMULA,
    INITIAL_INVENTORY
)

def save_data(filename, data):
    """Save data to JSON file"""
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Đã lưu thành công file {filename}")
        return True
    except Exception as e:
        print(f"Lỗi khi lưu {filename}: {e}")
        return False

def init_data():
    """Initialize all data files"""
    # Create directories if they don't exist
    os.makedirs("src/data/config", exist_ok=True)
    os.makedirs("src/data/presets/feed", exist_ok=True)
    os.makedirs("src/data/presets/mix", exist_ok=True)
    os.makedirs("src/data/reports", exist_ok=True)

    # Save feed formula
    save_data("src/data/config/feed_formula.json", LAYER_FEED_FORMULA)

    # Save mix formula
    save_data("src/data/config/mix_formula.json", LAYER_MIX_FORMULA)

    # Save inventory
    save_data("src/data/config/inventory.json", INITIAL_INVENTORY)

    # Save formula links
    save_data("src/data/config/formula_links.json", {
        "current_formula": "",
        "preset_links": {}
    })

    # Save default formulas as presets
    save_data("src/data/presets/feed/gà_đẻ.json", LAYER_FEED_FORMULA)
    save_data("src/data/presets/mix/gà_đẻ.json", LAYER_MIX_FORMULA)

    print("Đã khởi tạo dữ liệu thành công!")

if __name__ == "__main__":
    init_data()