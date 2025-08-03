import json
import os
try:
    from src.utils.default_formulas import (
        LAYER_FEED_FORMULA,
        LAYER_MIX_FORMULA,
        INITIAL_INVENTORY
    )
    from src.utils.persistent_paths import get_data_file_path, get_config_file_path, persistent_path_manager
except ImportError:
    from utils.default_formulas import (
        LAYER_FEED_FORMULA,
        LAYER_MIX_FORMULA,
        INITIAL_INVENTORY
    )
    from utils.persistent_paths import get_data_file_path, get_config_file_path, persistent_path_manager

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
    # Create directories if they don't exist using persistent paths
    config_dir = str(persistent_path_manager.config_path)
    presets_dir = str(persistent_path_manager.data_path / "presets")
    reports_dir = str(persistent_path_manager.reports_path)

    os.makedirs(config_dir, exist_ok=True)
    os.makedirs(os.path.join(presets_dir, "feed"), exist_ok=True)
    os.makedirs(os.path.join(presets_dir, "mix"), exist_ok=True)
    os.makedirs(reports_dir, exist_ok=True)

    # Save feed formula
    save_data(str(get_config_file_path("feed_formula.json")), LAYER_FEED_FORMULA)

    # Save mix formula
    save_data(str(get_config_file_path("mix_formula.json")), LAYER_MIX_FORMULA)

    # Save inventory
    save_data(str(get_config_file_path("inventory.json")), INITIAL_INVENTORY)

    # Save formula links
    save_data(str(get_config_file_path("formula_links.json")), {
        "current_formula": "",
        "preset_links": {}
    })

    # Save default formulas as presets
    save_data(os.path.join(presets_dir, "feed", "gà_đẻ.json"), LAYER_FEED_FORMULA)
    save_data(os.path.join(presets_dir, "mix", "gà_đẻ.json"), LAYER_MIX_FORMULA)

    print("Đã khởi tạo dữ liệu thành công!")

if __name__ == "__main__":
    init_data()