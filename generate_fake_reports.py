#!/usr/bin/env python3
"""
Tạo dữ liệu báo cáo giả cho một tháng tới
"""

import json
import os
import random
from datetime import datetime, timedelta
from pathlib import Path

def create_reports_directory():
    """Tạo thư mục reports nếu chưa có"""
    reports_dir = Path("src/data/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    return reports_dir

def generate_feed_usage(date_obj=None):
    """Tạo dữ liệu sử dụng cám ngẫu nhiên với biến thể theo ngày"""
    areas = {
        "Khu 1": ["T1", "T2", "T4", "T6"],
        "Khu 2": ["T1", "T2", "T4", "T6"],
        "Khu 3": ["1D", "2D", "4D", "2N"],
        "Khu 4": ["T2", "T4", "T6", "T8", "Trại 1 khu 4"],
        "Khu 5": [""]
    }

    # Tạo biến thể theo ngày trong tuần
    weekday_multiplier = 1.0
    if date_obj:
        weekday = date_obj.weekday()  # 0=Monday, 6=Sunday
        if weekday in [5, 6]:  # Weekend
            weekday_multiplier = 0.8  # Ít hoạt động hơn cuối tuần
        elif weekday in [0, 1]:  # Monday, Tuesday
            weekday_multiplier = 1.2  # Nhiều hoạt động đầu tuần

    feed_usage = {}
    for area, farms in areas.items():
        feed_usage[area] = {}
        for farm in farms:
            # Tạo giá trị ngẫu nhiên cho sáng và chiều
            base_morning = random.uniform(0.3, 1.5) * weekday_multiplier
            base_afternoon = random.uniform(0.3, 1.5) * weekday_multiplier

            morning = round(max(0, base_morning), 1)
            afternoon = round(max(0, base_afternoon), 1)

            # Đôi khi không sử dụng (15% cơ hội)
            if random.random() < 0.15:
                morning = 0.0
            if random.random() < 0.15:
                afternoon = 0.0

            feed_usage[area][farm] = {
                "Sáng": morning,
                "Chiều": afternoon
            }

    return feed_usage

def generate_formula_usage():
    """Tạo dữ liệu công thức sử dụng"""
    areas = {
        "Khu 1": ["T1", "T2", "T4", "T6"],
        "Khu 2": ["T1", "T2", "T4", "T6"],
        "Khu 3": ["1D", "2D", "4D", "2N"],
        "Khu 4": ["T2", "T4", "T6", "T8", "Trại 1 khu 4"],
        "Khu 5": [""]
    }

    formulas = ["GD", "CT2", "CT3"]

    formula_usage = {}
    for area, farms in areas.items():
        formula_usage[area] = {}
        for farm in farms:
            # Chọn công thức ngẫu nhiên, GD có tỷ lệ cao hơn
            morning_formula = random.choices(formulas, weights=[70, 20, 10])[0]
            afternoon_formula = random.choices(formulas, weights=[70, 20, 10])[0]

            formula_usage[area][farm] = {
                "Sáng": morning_formula,
                "Chiều": afternoon_formula
            }

    return formula_usage

def generate_feed_ingredients(total_batches):
    """Tạo dữ liệu nguyên liệu cám dựa trên số mẻ"""
    base_ingredients = {
        "Bắp": 1200,
        "Nành": 450,
        "Dầu": 8,
        "Nguyên liệu tổ hợp": 32.9,
        "DCP": 25,
        "Đá hạt": 32,
        "Đá bột mịn": 45,
        "Cám gạo": 260
    }

    feed_ingredients = {}
    for ingredient, base_amount in base_ingredients.items():
        # Thêm biến động ngẫu nhiên ±20%
        variation = random.uniform(0.8, 1.2)
        amount = base_amount * total_batches * variation
        feed_ingredients[ingredient] = round(amount, 1)

    return feed_ingredients

def generate_mix_ingredients(total_batches):
    """Tạo dữ liệu nguyên liệu mix dựa trên số mẻ"""
    base_ingredients = {
        "L-Lysine": 1.6,
        "DL-Methionine": 3.0,
        "Bio-Choline": 0.4,
        "Phytast": 0.3,
        "Performix 0.25% layer": 0.0,
        "Miamix": 0.5,
        "Premix 0.25% layer": 6.0,
        "Compound Enzyme FE808E": 0.3,
        "Carophy Red (Màu đỏ)": 0.6,
        "P-Zym": 0.4,
        "Oxytetracylin": 0.05,
        "Tiamulin": 0.05,
        "Amox": 0.0,
        "Immunewall": 0.2,
        "Lysoforte Dry": 0.5,
        "Nutriprotect": 0.15,
        "Defitox L1": 1.6,
        "Men Ecobiol": 0.6,
        "Lactic LD (axit hữu cơ)": 2.0,
        "Sodium bicarbonate": 2.0,
        "Bột đá mịn": 4.5,
        "Muối": 7.4,
        "DCP": 1.0
    }

    mix_ingredients = {}
    for ingredient, base_amount in base_ingredients.items():
        # Thêm biến động ngẫu nhiên ±15%
        variation = random.uniform(0.85, 1.15)
        amount = base_amount * total_batches * variation

        # Đôi khi một số nguyên liệu không sử dụng
        if random.random() < 0.1:  # 10% cơ hội không sử dụng
            amount = 0.0

        mix_ingredients[ingredient] = round(amount, 1)

    return mix_ingredients

def calculate_total_batches(feed_usage):
    """Tính tổng số mẻ từ dữ liệu sử dụng cám"""
    total = 0
    total_by_area = {}

    for area, farms in feed_usage.items():
        area_total = 0
        for farm, shifts in farms.items():
            area_total += shifts["Sáng"] + shifts["Chiều"]
        total_by_area[area] = area_total
        total += area_total

    return total, total_by_area

def generate_column_mix_formulas():
    """Tạo dữ liệu công thức mix cho các cột"""
    formulas = [
        "Khu 1-5",
        "Khu 2(1, 2, 3, 6)",
        "Khu 2(4,5)",
        "Khu 3 - Gà con công thức",
        "Khu 4(2, 3, 4, 5)",
        "Khu 4(6, 7, 8)"
    ]

    column_mix_formulas = {}
    for i in range(18):  # 18 cột
        formula = random.choice(formulas)
        column_mix_formulas[str(i)] = formula

    return column_mix_formulas

def generate_report_for_date(date_obj):
    """Tạo báo cáo cho một ngày cụ thể"""
    date_str = date_obj.strftime("%Y%m%d")
    display_date = date_obj.strftime("%d/%m/%Y")

    # Tạo dữ liệu với biến thể theo ngày
    feed_usage = generate_feed_usage(date_obj)
    formula_usage = generate_formula_usage()
    total_batches, total_batches_by_area = calculate_total_batches(feed_usage)

    feed_ingredients = generate_feed_ingredients(total_batches)
    mix_ingredients = generate_mix_ingredients(total_batches)

    total_feed = sum(feed_ingredients.values())
    total_mix = sum(mix_ingredients.values())

    column_mix_formulas = generate_column_mix_formulas()

    report = {
        "date": date_str,
        "display_date": display_date,
        "feed_usage": feed_usage,
        "formula_usage": formula_usage,
        "feed_ingredients": feed_ingredients,
        "mix_ingredients": mix_ingredients,
        "total_batches": total_batches,
        "total_batches_by_area": total_batches_by_area,
        "default_formula": "GD",
        "total_feed": round(total_feed, 1),
        "total_mix": round(total_mix, 1),
        "batch_count": total_batches,
        "column_mix_formulas": column_mix_formulas
    }

    return report

def main():
    """Hàm chính tạo báo cáo cho một tháng"""
    print("🔄 Bắt đầu tạo dữ liệu báo cáo giả cho một tháng tới...")

    # Tạo thư mục reports
    reports_dir = create_reports_directory()

    # Ngày bắt đầu: 25/07/2025 (ngày mai)
    start_date = datetime(2025, 7, 25)

    # Tạo báo cáo cho 31 ngày
    reports_created = 0

    for i in range(31):
        current_date = start_date + timedelta(days=i)

        # Tạo báo cáo cho ngày này
        report = generate_report_for_date(current_date)

        # Lưu file
        filename = f"report_{current_date.strftime('%Y%m%d')}.json"
        filepath = reports_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=4)

        reports_created += 1
        print(f"✅ Tạo báo cáo: {filename} - {current_date.strftime('%d/%m/%Y')}")

    print(f"\n🎉 Hoàn thành! Đã tạo {reports_created} báo cáo từ {start_date.strftime('%d/%m/%Y')} đến {(start_date + timedelta(days=30)).strftime('%d/%m/%Y')}")
    print(f"📁 Các file được lưu trong: {reports_dir}")

    # Thống kê
    print(f"\n📊 Thống kê:")
    print(f"   - Số báo cáo tạo: {reports_created}")
    print(f"   - Thư mục lưu: {reports_dir}")
    print(f"   - Định dạng file: report_YYYYMMDD.json")
    print(f"   - Dữ liệu bao gồm: feed_usage, formula_usage, ingredients, batches")

if __name__ == "__main__":
    main()
