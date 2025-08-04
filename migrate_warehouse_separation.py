#!/usr/bin/env python3
"""
Data migration script to split existing inventory.json into separate warehouse files
"""

import json
import os
import shutil
from pathlib import Path
from datetime import datetime

def backup_existing_files():
    """Create backups of existing files before migration"""
    print("=== Creating Backups ===")
    
    backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    files_to_backup = [
        "src/data/config/inventory.json",
        "src/data/config/packaging_info.json"
    ]
    
    for file_path in files_to_backup:
        if os.path.exists(file_path):
            backup_path = os.path.join(backup_dir, os.path.basename(file_path))
            shutil.copy2(file_path, backup_path)
            print(f"✅ Backed up {file_path} to {backup_path}")
        else:
            print(f"⚠️ File not found: {file_path}")
    
    print(f"✅ Backups created in {backup_dir}")
    return backup_dir

def load_categorization_analysis():
    """Load the categorization analysis results"""
    categorization_file = "inventory_categorization_analysis.json"
    
    if not os.path.exists(categorization_file):
        print(f"❌ Categorization file not found: {categorization_file}")
        print("Please run analyze_inventory_categorization.py first")
        return None
    
    with open(categorization_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def migrate_inventory_data(categorization):
    """Migrate inventory data to separate warehouse files"""
    print("\n=== Migrating Inventory Data ===")
    
    feed_warehouse = categorization["feed_warehouse"]
    mix_warehouse = categorization["mix_warehouse"]
    
    # Create warehouse inventory files
    feed_inventory_path = "src/data/config/feed_inventory.json"
    mix_inventory_path = "src/data/config/mix_inventory.json"
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(feed_inventory_path), exist_ok=True)
    
    # Save feed warehouse inventory
    with open(feed_inventory_path, 'w', encoding='utf-8') as f:
        json.dump(feed_warehouse, f, ensure_ascii=False, indent=4)
    print(f"✅ Created {feed_inventory_path} with {len(feed_warehouse)} items")
    
    # Save mix warehouse inventory
    with open(mix_inventory_path, 'w', encoding='utf-8') as f:
        json.dump(mix_warehouse, f, ensure_ascii=False, indent=4)
    print(f"✅ Created {mix_inventory_path} with {len(mix_warehouse)} items")
    
    # Verify data integrity
    total_migrated = sum(feed_warehouse.values()) + sum(mix_warehouse.values())
    print(f"✅ Total inventory value migrated: {total_migrated}")
    
    return True

def migrate_packaging_data(categorization):
    """Migrate packaging data to separate warehouse files"""
    print("\n=== Migrating Packaging Data ===")
    
    # Load existing packaging info
    packaging_file = "src/data/config/packaging_info.json"
    packaging_info = {}
    
    if os.path.exists(packaging_file):
        with open(packaging_file, 'r', encoding='utf-8') as f:
            packaging_info = json.load(f)
    
    # Split packaging info by warehouse
    feed_packaging = {}
    mix_packaging = {}
    
    feed_ingredients = set(categorization["feed_warehouse"].keys())
    mix_ingredients = set(categorization["mix_warehouse"].keys())
    
    # Assign packaging info to appropriate warehouse
    for ingredient in feed_ingredients:
        if ingredient in packaging_info:
            feed_packaging[ingredient] = packaging_info[ingredient]
        else:
            # Default bag size for feed ingredients
            feed_packaging[ingredient] = 25
    
    for ingredient in mix_ingredients:
        if ingredient in packaging_info:
            mix_packaging[ingredient] = packaging_info[ingredient]
        else:
            # Default bag size for mix ingredients
            mix_packaging[ingredient] = 20
    
    # Save warehouse packaging files
    feed_packaging_path = "src/data/config/feed_packaging_info.json"
    mix_packaging_path = "src/data/config/mix_packaging_info.json"
    
    with open(feed_packaging_path, 'w', encoding='utf-8') as f:
        json.dump(feed_packaging, f, ensure_ascii=False, indent=4)
    print(f"✅ Created {feed_packaging_path} with {len(feed_packaging)} items")
    
    with open(mix_packaging_path, 'w', encoding='utf-8') as f:
        json.dump(mix_packaging, f, ensure_ascii=False, indent=4)
    print(f"✅ Created {mix_packaging_path} with {len(mix_packaging)} items")
    
    return True

def verify_migration(categorization):
    """Verify that migration was successful"""
    print("\n=== Verifying Migration ===")
    
    # Load migrated files
    feed_inventory_path = "src/data/config/feed_inventory.json"
    mix_inventory_path = "src/data/config/mix_inventory.json"
    feed_packaging_path = "src/data/config/feed_packaging_info.json"
    mix_packaging_path = "src/data/config/mix_packaging_info.json"
    
    try:
        # Verify inventory files
        with open(feed_inventory_path, 'r', encoding='utf-8') as f:
            migrated_feed = json.load(f)
        
        with open(mix_inventory_path, 'r', encoding='utf-8') as f:
            migrated_mix = json.load(f)
        
        # Verify packaging files
        with open(feed_packaging_path, 'r', encoding='utf-8') as f:
            migrated_feed_packaging = json.load(f)
        
        with open(mix_packaging_path, 'r', encoding='utf-8') as f:
            migrated_mix_packaging = json.load(f)
        
        # Check data integrity
        original_feed = categorization["feed_warehouse"]
        original_mix = categorization["mix_warehouse"]
        
        # Verify inventory data
        if migrated_feed == original_feed:
            print("✅ Feed inventory data verified")
        else:
            print("❌ Feed inventory data mismatch")
            return False
        
        if migrated_mix == original_mix:
            print("✅ Mix inventory data verified")
        else:
            print("❌ Mix inventory data mismatch")
            return False
        
        # Verify packaging data
        feed_ingredients = set(original_feed.keys())
        mix_ingredients = set(original_mix.keys())
        
        if set(migrated_feed_packaging.keys()) == feed_ingredients:
            print("✅ Feed packaging data verified")
        else:
            print("❌ Feed packaging data mismatch")
            return False
        
        if set(migrated_mix_packaging.keys()) == mix_ingredients:
            print("✅ Mix packaging data verified")
        else:
            print("❌ Mix packaging data mismatch")
            return False
        
        # Verify totals
        original_total = sum(original_feed.values()) + sum(original_mix.values())
        migrated_total = sum(migrated_feed.values()) + sum(migrated_mix.values())
        
        if abs(original_total - migrated_total) < 0.01:
            print(f"✅ Total inventory value preserved: {migrated_total}")
        else:
            print(f"❌ Total inventory value mismatch: original={original_total}, migrated={migrated_total}")
            return False
        
        print("✅ All migration verification checks passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        return False

def create_migration_summary(backup_dir, categorization):
    """Create a summary of the migration process"""
    print("\n=== Creating Migration Summary ===")
    
    summary = {
        "migration_date": datetime.now().isoformat(),
        "backup_directory": backup_dir,
        "original_inventory_count": len(categorization["feed_warehouse"]) + len(categorization["mix_warehouse"]),
        "feed_warehouse": {
            "item_count": len(categorization["feed_warehouse"]),
            "total_value": sum(categorization["feed_warehouse"].values()),
            "file_path": "src/data/config/feed_inventory.json"
        },
        "mix_warehouse": {
            "item_count": len(categorization["mix_warehouse"]),
            "total_value": sum(categorization["mix_warehouse"].values()),
            "file_path": "src/data/config/mix_inventory.json"
        },
        "files_created": [
            "src/data/config/feed_inventory.json",
            "src/data/config/mix_inventory.json",
            "src/data/config/feed_packaging_info.json",
            "src/data/config/mix_packaging_info.json"
        ],
        "migration_status": "SUCCESS"
    }
    
    summary_file = "warehouse_migration_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Migration summary saved to {summary_file}")
    
    # Print summary to console
    print("\n" + "="*60)
    print("WAREHOUSE SEPARATION MIGRATION SUMMARY")
    print("="*60)
    print(f"Migration Date: {summary['migration_date']}")
    print(f"Backup Directory: {summary['backup_directory']}")
    print(f"Original Inventory Items: {summary['original_inventory_count']}")
    print(f"Feed Warehouse: {summary['feed_warehouse']['item_count']} items, value: {summary['feed_warehouse']['total_value']}")
    print(f"Mix Warehouse: {summary['mix_warehouse']['item_count']} items, value: {summary['mix_warehouse']['total_value']}")
    print("Files Created:")
    for file_path in summary['files_created']:
        print(f"  - {file_path}")
    print(f"Migration Status: {summary['migration_status']}")
    print("="*60)

def main():
    """Main migration function"""
    print("Starting Warehouse Separation Migration...")
    print("="*60)
    
    try:
        # Step 1: Create backups
        backup_dir = backup_existing_files()
        
        # Step 2: Load categorization analysis
        categorization = load_categorization_analysis()
        if not categorization:
            return False
        
        # Step 3: Migrate inventory data
        if not migrate_inventory_data(categorization):
            print("❌ Failed to migrate inventory data")
            return False
        
        # Step 4: Migrate packaging data
        if not migrate_packaging_data(categorization):
            print("❌ Failed to migrate packaging data")
            return False
        
        # Step 5: Verify migration
        if not verify_migration(categorization):
            print("❌ Migration verification failed")
            return False
        
        # Step 6: Create migration summary
        create_migration_summary(backup_dir, categorization)
        
        print("\n🎉 WAREHOUSE SEPARATION MIGRATION COMPLETED SUCCESSFULLY!")
        print("\nNext steps:")
        print("1. Test the application with the new warehouse system")
        print("2. Update any custom scripts that reference inventory.json")
        print("3. If everything works correctly, you can remove the backup files")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()
