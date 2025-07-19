import os
import json
import sys
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

def format_number(value):
    """Format a number to display as integer if it has no decimal part, otherwise show decimal places without trailing zeros"""
    if value == int(value):
        return f"{int(value)}"
    else:
        # Sử dụng 'g' để loại bỏ số 0 thừa ở cuối
        s = f"{value:.10g}"
        # Nếu có dấu chấm nhưng không có số sau dấu chấm, thêm số 0
        if s.endswith('.'):
            s += '0'
        return s

def load_report(filename):
    """Load report data from JSON file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading report {filename}: {e}")
        return None

def ensure_reports_dir():
    """Ensure reports directory exists"""
    reports_dir = "src/data/reports"
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)
    return reports_dir

def visualize_feed_usage_by_khu(report_data):
    """Visualize feed usage by area"""
    if not report_data or "feed_usage" not in report_data:
        print("No feed usage data to visualize")
        return

    # Extract feed usage data by khu
    areas = []
    usage = []

    for khu, farms in report_data['feed_usage'].items():
        areas.append(khu)
        khu_total = 0

        # Sum up all farms in this khu
        for farm, shifts in farms.items():
            farm_total = sum(shifts.values())
            khu_total += farm_total

        usage.append(khu_total)

    # Create bar chart
    plt.figure(figsize=(10, 6))
    plt.bar(areas, usage, color='skyblue')
    plt.title(f"Feed Usage by Area - {report_data['date']}")
    plt.xlabel("Area")
    plt.ylabel("Batches")
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Add values on top of bars
    for i, v in enumerate(usage):
        plt.text(i, v + 0.1, format_number(v), ha='center')

    plt.tight_layout()

    # Save to reports directory
    reports_dir = ensure_reports_dir()
    output_file = os.path.join(reports_dir, f"feed_usage_by_khu_{report_data['date']}.png")
    plt.savefig(output_file)
    print(f"Chart saved as {output_file}")
    plt.show()

def visualize_feed_usage_by_farm(report_data):
    """Visualize feed usage by farm"""
    if not report_data or "feed_usage" not in report_data:
        print("No feed usage data to visualize")
        return

    # Extract feed usage data by farm
    farm_data = []

    for khu, farms in report_data['feed_usage'].items():
        for farm, shifts in farms.items():
            total = sum(shifts.values())
            farm_data.append((f"{khu}-{farm}", total))

    # Sort by usage
    farm_data.sort(key=lambda x: x[1], reverse=True)

    # Limit to top 15 farms for better visibility
    if len(farm_data) > 15:
        farm_data = farm_data[:15]
        title_suffix = " (Top 15)"
    else:
        title_suffix = ""

    farms = [item[0] for item in farm_data]
    usage = [item[1] for item in farm_data]

    # Create bar chart
    plt.figure(figsize=(12, 6))
    plt.bar(farms, usage, color='lightgreen')
    plt.title(f"Feed Usage by Farm - {report_data['date']}{title_suffix}")
    plt.xlabel("Farm")
    plt.ylabel("Batches")
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Add values on top of bars
    for i, v in enumerate(usage):
        plt.text(i, v + 0.1, format_number(v), ha='center')

    plt.tight_layout()

    # Save to reports directory
    reports_dir = ensure_reports_dir()
    output_file = os.path.join(reports_dir, f"feed_usage_by_farm_{report_data['date']}.png")
    plt.savefig(output_file)
    print(f"Chart saved as {output_file}")
    plt.show()

def visualize_feed_ingredients(report_data):
    """Visualize feed ingredients usage"""
    if not report_data or "feed_ingredients" not in report_data:
        print("No feed ingredients data to visualize")
        return

    # Extract top ingredients by usage
    ingredients = list(report_data['feed_ingredients'].keys())
    amounts = list(report_data['feed_ingredients'].values())

    # Sort by amount
    sorted_data = sorted(zip(ingredients, amounts), key=lambda x: x[1], reverse=True)
    ingredients = [item[0] for item in sorted_data]
    amounts = [item[1] for item in sorted_data]

    # Create bar chart
    plt.figure(figsize=(12, 6))
    plt.bar(ingredients, amounts, color='skyblue')
    plt.title(f"Feed Ingredients Usage - {report_data['date']}")
    plt.xlabel("Ingredient")
    plt.ylabel("Amount (kg)")
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Add values on top of bars
    for i, v in enumerate(amounts):
        plt.text(i, v + 5, format_number(v), ha='center')

    plt.tight_layout()

    # Save to reports directory
    reports_dir = ensure_reports_dir()
    output_file = os.path.join(reports_dir, f"feed_ingredients_{report_data['date']}.png")
    plt.savefig(output_file)
    print(f"Chart saved as {output_file}")
    plt.show()

def visualize_mix_ingredients(report_data):
    """Visualize mix ingredients usage"""
    if not report_data or "mix_ingredients" not in report_data:
        print("No mix ingredients data to visualize")
        return

    # Extract top ingredients by usage
    ingredients = list(report_data['mix_ingredients'].keys())
    amounts = list(report_data['mix_ingredients'].values())

    # Sort by amount
    sorted_data = sorted(zip(ingredients, amounts), key=lambda x: x[1], reverse=True)

    # Take top 15 for better visibility
    if len(sorted_data) > 15:
        sorted_data = sorted_data[:15]
        title_suffix = " (Top 15)"
    else:
        title_suffix = ""

    ingredients = [item[0] for item in sorted_data]
    amounts = [item[1] for item in sorted_data]

    # Create bar chart
    plt.figure(figsize=(12, 6))
    plt.bar(ingredients, amounts, color='lightgreen')
    plt.title(f"Mix Ingredients Usage - {report_data['date']}{title_suffix}")
    plt.xlabel("Ingredient")
    plt.ylabel("Amount (kg)")
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Add values on top of bars
    for i, v in enumerate(amounts):
        plt.text(i, v + 5, format_number(v), ha='center')

    plt.tight_layout()

    # Save to reports directory
    reports_dir = ensure_reports_dir()
    output_file = os.path.join(reports_dir, f"mix_ingredients_{report_data['date']}.png")
    plt.savefig(output_file)
    print(f"Chart saved as {output_file}")
    plt.show()

def list_reports():
    """List all available reports"""
    reports_dir = "src/data/reports"
    if not os.path.exists(reports_dir):
        print(f"Reports directory '{reports_dir}' not found")
        return None

    reports = [os.path.join(reports_dir, f) for f in os.listdir(reports_dir)
              if f.startswith('report_') and f.endswith('.json')]

    if not reports:
        print("No reports found")
        return None

    print("Available reports:")
    for i, report in enumerate(reports):
        print(f"{i+1}. {os.path.basename(report)}")

    try:
        choice = int(input("Select a report to visualize (number): "))
        if 1 <= choice <= len(reports):
            return reports[choice-1]
        else:
            print("Invalid choice")
            return None
    except ValueError:
        print("Please enter a valid number")
        return None

def main():
    print("Feed Usage Visualization Tool")
    print("============================")

    # Check if a report file was provided as argument
    if len(sys.argv) > 1:
        report_file = sys.argv[1]
    else:
        report_file = list_reports()

    if not report_file:
        return

    # Load report data
    report_data = load_report(report_file)
    if not report_data:
        return

    # Visualize data
    visualize_feed_usage_by_khu(report_data)
    visualize_feed_usage_by_farm(report_data)
    visualize_feed_ingredients(report_data)
    visualize_mix_ingredients(report_data)

if __name__ == "__main__":
    main()