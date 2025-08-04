#!/usr/bin/env python3
"""
Analyze current inventory and categorize ingredients into feed vs mix warehouses
"""

import json
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, 'src')

def load_json_file(filepath):
    """Load JSON file safely"""
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return {}

def analyze_inventory_categorization():
    """Analyze current inventory and categorize ingredients"""
    print("=== Analyzing Inventory Categorization ===")
    
    # Load current data
    inventory = load_json_file("src/data/config/inventory.json")
    feed_formula = load_json_file("src/data/config/feed_formula.json")
    mix_formula = load_json_file("src/data/config/mix_formula.json")
    
    print(f"Current inventory items: {len(inventory)}")
    print(f"Feed formula ingredients: {len(feed_formula)}")
    print(f"Mix formula ingredients: {len(mix_formula)}")
    
    # Categorize ingredients
    feed_ingredients = set(feed_formula.keys())
    mix_ingredients = set(mix_formula.keys())
    inventory_ingredients = set(inventory.keys())
    
    # Find overlaps and unique items
    feed_only = feed_ingredients - mix_ingredients
    mix_only = mix_ingredients - feed_ingredients
    both_formulas = feed_ingredients & mix_ingredients
    inventory_only = inventory_ingredients - feed_ingredients - mix_ingredients
    
    print("\n=== CATEGORIZATION ANALYSIS ===")
    print(f"Feed-only ingredients: {len(feed_only)}")
    for ingredient in sorted(feed_only):
        amount = inventory.get(ingredient, 0)
        print(f"  - {ingredient}: {amount}")
    
    print(f"\nMix-only ingredients: {len(mix_only)}")
    for ingredient in sorted(mix_only):
        amount = inventory.get(ingredient, 0)
        print(f"  - {ingredient}: {amount}")
    
    print(f"\nIngredients in BOTH formulas: {len(both_formulas)}")
    for ingredient in sorted(both_formulas):
        amount = inventory.get(ingredient, 0)
        print(f"  - {ingredient}: {amount} (NEEDS DECISION)")
    
    print(f"\nInventory-only ingredients (not in any formula): {len(inventory_only)}")
    for ingredient in sorted(inventory_only):
        amount = inventory.get(ingredient, 0)
        print(f"  - {ingredient}: {amount} (NEEDS CATEGORIZATION)")
    
    # Proposed categorization strategy
    print("\n=== PROPOSED CATEGORIZATION STRATEGY ===")
    
    # Strategy 1: Based on primary usage
    feed_warehouse_items = {}
    mix_warehouse_items = {}
    
    # Feed warehouse: Feed-only + shared items that are primarily feed ingredients
    for ingredient in feed_only:
        if ingredient in inventory:
            feed_warehouse_items[ingredient] = inventory[ingredient]
    
    # Mix warehouse: Mix-only ingredients
    for ingredient in mix_only:
        if ingredient in inventory:
            mix_warehouse_items[ingredient] = inventory[ingredient]
    
    # Handle shared ingredients - categorize based on typical usage patterns
    shared_categorization = {
        # These are typically feed ingredients even if used in mix
        "DCP": "feed",
        "Đá hạt": "feed", 
        "Đá bột mịn": "feed",
        # Add more as needed based on domain knowledge
    }
    
    for ingredient in both_formulas:
        if ingredient in inventory:
            category = shared_categorization.get(ingredient, "mix")  # Default to mix for additives
            if category == "feed":
                feed_warehouse_items[ingredient] = inventory[ingredient]
            else:
                mix_warehouse_items[ingredient] = inventory[ingredient]
    
    # Handle inventory-only items - categorize based on name patterns
    for ingredient in inventory_only:
        amount = inventory[ingredient]
        ingredient_lower = ingredient.lower()
        
        # Categorization rules based on ingredient names
        if any(keyword in ingredient_lower for keyword in ['cám', 'bắp', 'nành', 'dầu', 'gạo']):
            feed_warehouse_items[ingredient] = amount
            print(f"  → {ingredient}: Categorized as FEED (name pattern)")
        elif any(keyword in ingredient_lower for keyword in ['performix', 'premix', 'enzyme', 'lysine', 'methionine', 'choline']):
            mix_warehouse_items[ingredient] = amount
            print(f"  → {ingredient}: Categorized as MIX (name pattern)")
        else:
            # Default to mix for unknown additives/supplements
            mix_warehouse_items[ingredient] = amount
            print(f"  → {ingredient}: Categorized as MIX (default for additives)")
    
    print(f"\n=== FINAL CATEGORIZATION ===")
    print(f"Feed warehouse will contain: {len(feed_warehouse_items)} items")
    total_feed_value = sum(feed_warehouse_items.values())
    print(f"Total feed inventory value: {total_feed_value}")
    
    print(f"\nMix warehouse will contain: {len(mix_warehouse_items)} items")
    total_mix_value = sum(mix_warehouse_items.values())
    print(f"Total mix inventory value: {total_mix_value}")
    
    print(f"\nTotal inventory preserved: {total_feed_value + total_mix_value}")
    print(f"Original inventory total: {sum(inventory.values())}")
    
    # Verify no data loss
    if abs((total_feed_value + total_mix_value) - sum(inventory.values())) < 0.01:
        print("✅ No data loss - all inventory amounts preserved")
    else:
        print("❌ Data loss detected - check categorization")
    
    # Save categorization results
    categorization_result = {
        "feed_warehouse": feed_warehouse_items,
        "mix_warehouse": mix_warehouse_items,
        "analysis": {
            "feed_only_count": len(feed_only),
            "mix_only_count": len(mix_only),
            "shared_count": len(both_formulas),
            "inventory_only_count": len(inventory_only),
            "total_feed_items": len(feed_warehouse_items),
            "total_mix_items": len(mix_warehouse_items),
            "total_feed_value": total_feed_value,
            "total_mix_value": total_mix_value
        }
    }
    
    with open("inventory_categorization_analysis.json", "w", encoding="utf-8") as f:
        json.dump(categorization_result, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Analysis saved to inventory_categorization_analysis.json")
    
    return categorization_result

if __name__ == "__main__":
    analyze_inventory_categorization()
