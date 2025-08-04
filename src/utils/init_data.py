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
    print("🔧 Initializing data files...")

    # Create directories if they don't exist using persistent paths
    config_dir = str(persistent_path_manager.config_path)
    presets_dir = str(persistent_path_manager.data_path / "presets")
    reports_dir = str(persistent_path_manager.reports_path)

    print(f"🔧 Config directory: {config_dir}")
    print(f"🔧 Presets directory: {presets_dir}")
    print(f"🔧 Reports directory: {reports_dir}")

    os.makedirs(config_dir, exist_ok=True)
    os.makedirs(os.path.join(presets_dir, "feed"), exist_ok=True)
    os.makedirs(os.path.join(presets_dir, "mix"), exist_ok=True)
    os.makedirs(reports_dir, exist_ok=True)

    # Save feed formula
    feed_formula_path = str(get_config_file_path("feed_formula.json"))
    print(f"🔧 Saving feed formula to: {feed_formula_path}")
    save_data(feed_formula_path, LAYER_FEED_FORMULA)

    # Save mix formula
    mix_formula_path = str(get_config_file_path("mix_formula.json"))
    print(f"🔧 Saving mix formula to: {mix_formula_path}")
    save_data(mix_formula_path, LAYER_MIX_FORMULA)

    # Save inventory
    inventory_path = str(get_config_file_path("inventory.json"))
    print(f"🔧 Saving inventory to: {inventory_path}")
    save_data(inventory_path, INITIAL_INVENTORY)

    # Save formula links
    formula_links_path = str(get_config_file_path("formula_links.json"))
    print(f"🔧 Saving formula links to: {formula_links_path}")
    save_data(formula_links_path, {
        "current_formula": "",
        "preset_links": {}
    })

    # Save default formulas as presets
    feed_preset_path = os.path.join(presets_dir, "feed", "gà_đẻ.json")
    mix_preset_path = os.path.join(presets_dir, "mix", "gà_đẻ.json")

    print(f"🔧 Saving feed preset to: {feed_preset_path}")
    save_data(feed_preset_path, LAYER_FEED_FORMULA)

    print(f"🔧 Saving mix preset to: {mix_preset_path}")
    save_data(mix_preset_path, LAYER_MIX_FORMULA)

    print("✅ Đã khởi tạo dữ liệu thành công!")

if __name__ == "__main__":
    init_data()
