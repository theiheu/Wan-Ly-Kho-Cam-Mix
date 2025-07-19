import json
import os
from typing import Dict, Any, List, Tuple, Optional

class FormulaManager:
    """Class to manage feed and mix formulas"""

    def __init__(self):
        # Cập nhật đường dẫn file
        self.feed_formula_file = "src/data/config/feed_formula.json"
        self.mix_formula_file = "src/data/config/mix_formula.json"
        self.formula_links_file = "src/data/config/formula_links.json"
        self.formulas_dir = "src/data/presets"

        # Create formulas directory if it doesn't exist
        if not os.path.exists(self.formulas_dir):
            os.makedirs(self.formulas_dir)

        # Load current formulas
        self.feed_formula = self.load_formula(self.feed_formula_file)
        self.mix_formula = self.load_formula(self.mix_formula_file)

        # Load saved formula presets
        self.feed_presets = self.load_presets("feed")
        self.mix_presets = self.load_presets("mix")

        # Load formula links
        self.formula_links = self.load_formula_links()

        # Ensure formula_links has the correct structure
        if "preset_links" not in self.formula_links:
            self.formula_links["preset_links"] = {}

        # Legacy support: move old linked_mix_formula to current formula if exists
        if "linked_mix_formula" in self.formula_links and self.formula_links["linked_mix_formula"]:
            self.formula_links["current_formula"] = self.formula_links["linked_mix_formula"]

        # Ensure current_formula key exists
        if "current_formula" not in self.formula_links:
            self.formula_links["current_formula"] = ""

        # Save updated structure
        self.save_formula_links()

    def load_formula(self, filename: str) -> Dict[str, float]:
        """Load a formula from a JSON file"""
        try:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error loading formula from {filename}: {e}")
            return {}

    def save_formula(self, formula: Dict[str, float], filename: str) -> bool:
        """Save a formula to a JSON file"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(filename), exist_ok=True)

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(formula, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Error saving formula to {filename}: {e}")
            return False

    def load_formula_links(self) -> Dict[str, Any]:
        """Load formula links from JSON file"""
        try:
            if os.path.exists(self.formula_links_file):
                with open(self.formula_links_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {"current_formula": "", "preset_links": {}}
        except Exception as e:
            print(f"Error loading formula links from {self.formula_links_file}: {e}")
            return {"current_formula": "", "preset_links": {}}

    def save_formula_links(self) -> bool:
        """Save formula links to JSON file"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.formula_links_file), exist_ok=True)

            with open(self.formula_links_file, 'w', encoding='utf-8') as f:
                json.dump(self.formula_links, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Error saving formula links to {self.formula_links_file}: {e}")
            return False

    def load_presets(self, formula_type: str) -> Dict[str, Dict[str, float]]:
        """Load all formula presets of a specific type"""
        presets = {}
        preset_dir = os.path.join(self.formulas_dir, formula_type)

        if not os.path.exists(preset_dir):
            os.makedirs(preset_dir)
            return presets

        for filename in os.listdir(preset_dir):
            if filename.endswith('.json'):
                preset_name = filename[:-5]  # Remove .json extension
                preset_path = os.path.join(preset_dir, filename)
                presets[preset_name] = self.load_formula(preset_path)

        return presets

    def save_preset(self, formula_type: str, preset_name: str, formula: Dict[str, float]) -> bool:
        """Save a formula as a preset"""
        preset_dir = os.path.join(self.formulas_dir, formula_type)

        if not os.path.exists(preset_dir):
            os.makedirs(preset_dir)

        preset_path = os.path.join(preset_dir, f"{preset_name}.json")
        success = self.save_formula(formula, preset_path)

        if success:
            # Update presets in memory
            if formula_type == "feed":
                self.feed_presets[preset_name] = formula

                # Nếu đang cập nhật preset hiện tại, cập nhật cả công thức hiện tại
                if self.feed_formula == self.feed_presets.get(preset_name, {}):
                    self.feed_formula = formula
                    self.save_formula(formula, self.feed_formula_file)
            else:
                self.mix_presets[preset_name] = formula

                # Nếu đang cập nhật preset hiện tại, cập nhật cả công thức hiện tại
                if self.mix_formula == self.mix_presets.get(preset_name, {}):
                    self.mix_formula = formula
                    self.save_formula(formula, self.mix_formula_file)

            # Nếu preset này được liên kết với một công thức cám, cập nhật liên kết
            if formula_type == "mix":
                for feed_preset, linked_mix in self.formula_links.get("preset_links", {}).items():
                    if linked_mix == preset_name:
                        # Đánh dấu công thức cám cần cập nhật
                        print(f"Cập nhật công thức cám '{feed_preset}' liên kết với mix '{preset_name}'")

        return success

    def delete_preset(self, formula_type: str, preset_name: str) -> bool:
        """Delete a formula preset"""
        preset_dir = os.path.join(self.formulas_dir, formula_type)
        preset_path = os.path.join(preset_dir, f"{preset_name}.json")

        if os.path.exists(preset_path):
            try:
                os.remove(preset_path)

                # Remove from memory
                if formula_type == "feed":
                    if preset_name in self.feed_presets:
                        del self.feed_presets[preset_name]

                    # Remove any links for this preset
                    if preset_name in self.formula_links["preset_links"]:
                        del self.formula_links["preset_links"][preset_name]
                        self.save_formula_links()
                else:
                    if preset_name in self.mix_presets:
                        del self.mix_presets[preset_name]

                return True
            except Exception as e:
                print(f"Error deleting preset {preset_name}: {e}")
                return False

        return False

    def get_feed_formula(self) -> Dict[str, float]:
        """Get the current feed formula"""
        return self.feed_formula

    def get_mix_formula(self) -> Dict[str, float]:
        """Get the current mix formula"""
        return self.mix_formula

    def get_linked_mix_formula_name(self, feed_preset_name: str = None) -> str:
        """Get the name of the linked mix formula for a specific feed preset or current formula"""
        if feed_preset_name:
            # Return the linked mix formula for a specific feed preset
            return self.formula_links["preset_links"].get(feed_preset_name, "")
        else:
            # Return the linked mix formula for the current formula
            return self.formula_links.get("current_formula", "")

    def set_linked_mix_formula(self, mix_formula_name: str, feed_preset_name: str = None) -> bool:
        """Set the linked mix formula name for a specific feed preset or current formula and save it"""
        if feed_preset_name:
            # Set link for a specific feed preset
            self.formula_links["preset_links"][feed_preset_name] = mix_formula_name
        else:
            # Set link for the current formula
            self.formula_links["current_formula"] = mix_formula_name

        return self.save_formula_links()

    def get_linked_mix_formula(self, feed_preset_name: str = None) -> Dict[str, float]:
        """Get the linked mix formula data for a specific feed preset or current formula"""
        mix_formula_name = self.get_linked_mix_formula_name(feed_preset_name)
        if mix_formula_name:
            # If a specific mix formula is linked, use it
            return self.mix_presets.get(mix_formula_name, self.mix_formula)
        else:
            # Otherwise use the current mix formula
            return self.mix_formula

    def calculate_mix_total(self, mix_formula: Dict[str, float]) -> float:
        """Calculate the total amount of mix ingredients"""
        return sum(mix_formula.values())

    def set_feed_formula(self, formula: Dict[str, float]) -> bool:
        """Set and save the current feed formula"""
        self.feed_formula = formula
        return self.save_formula(formula, self.feed_formula_file)

    def set_mix_formula(self, formula: Dict[str, float]) -> bool:
        """Set and save the current mix formula"""
        self.mix_formula = formula
        return self.save_formula(formula, self.mix_formula_file)

    def get_feed_presets(self) -> List[str]:
        """Get list of feed formula preset names"""
        return list(self.feed_presets.keys())

    def get_mix_presets(self) -> List[str]:
        """Get list of mix formula preset names"""
        return list(self.mix_presets.keys())

    def load_feed_preset(self, preset_name: str) -> Dict[str, float]:
        """Load a feed formula preset"""
        return self.feed_presets.get(preset_name, {})

    def load_mix_preset(self, preset_name: str) -> Dict[str, float]:
        """Load a mix formula preset"""
        return self.mix_presets.get(preset_name, {})

    def calculate_ingredients(self, batches: float) -> Dict[str, float]:
        """Calculate ingredients needed for given number of batches"""
        ingredients = {}

        # Calculate feed ingredients
        for ingredient, amount_per_batch in self.feed_formula.items():
            if ingredient != "Nguyên liệu tổ hợp":
                ingredients[ingredient] = amount_per_batch * batches

        # Calculate mix ingredients
        tong_hop_amount = self.feed_formula.get("Nguyên liệu tổ hợp", 0)
        if tong_hop_amount > 0:
            # Use the linked mix formula if available
            mix_formula = self.get_linked_mix_formula()
            mix_total = self.calculate_mix_total(mix_formula)

            if mix_total > 0:
                for ingredient, amount in mix_formula.items():
                    # Calculate proportional amount
                    ratio = amount / mix_total
                    mix_amount = ratio * tong_hop_amount * batches

                    if ingredient in ingredients:
                        ingredients[ingredient] += mix_amount
                    else:
                        ingredients[ingredient] = mix_amount

        return ingredients