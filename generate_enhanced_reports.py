#!/usr/bin/env python3
"""
Tạo dữ liệu báo cáo nâng cao với các tình huống đặc biệt
"""

import json
import os
import random
from datetime import datetime, timedelta
from pathlib import Path

def create_special_scenarios():
    """Tạo các tình huống đặc biệt cho báo cáo"""
    scenarios = {
        "high_production": {
            "description": "Ngày sản xuất cao",
            "feed_multiplier": 1.5,
            "mix_multiplier": 1.3,
            "probability": 0.1
        },
        "low_production": {
            "description": "Ngày sản xuất thấp",
            "feed_multiplier": 0.6,
            "mix_multiplier": 0.7,
            "probability": 0.1
        },
        "maintenance_day": {
            "description": "Ngày bảo trì",
            "feed_multiplier": 0.3,
            "mix_multiplier": 0.4,
            "probability": 0.05
        },
        "holiday": {
            "description": "Ngày lễ",
            "feed_multiplier": 0.4,
            "mix_multiplier": 0.5,
            "probability": 0.05
        },
        "normal": {
            "description": "Ngày bình thường",
            "feed_multiplier": 1.0,
            "mix_multiplier": 1.0,
            "probability": 0.7
        }
    }
    return scenarios

def select_scenario_for_date(date_obj):
    """Chọn tình huống cho ngày cụ thể"""
    scenarios = create_special_scenarios()
    
    # Một số ngày đặc biệt
    if date_obj.weekday() == 6:  # Sunday
        return scenarios["low_production"]
    elif date_obj.day in [1, 15]:  # Đầu tháng và giữa tháng có thể bảo trì
        if random.random() < 0.3:
            return scenarios["maintenance_day"]
    elif date_obj.weekday() in [0, 1]:  # Monday, Tuesday
        if random.random() < 0.2:
            return scenarios["high_production"]
    
    # Chọn ngẫu nhiên dựa trên xác suất
    rand = random.random()
    cumulative_prob = 0
    
    for scenario_name, scenario in scenarios.items():
        cumulative_prob += scenario["probability"]
        if rand <= cumulative_prob:
            return scenario
    
    return scenarios["normal"]

def generate_weather_impact():
    """Tạo tác động thời tiết"""
    weather_conditions = [
        {"condition": "sunny", "impact": 1.0, "description": "Nắng đẹp"},
        {"condition": "rainy", "impact": 0.8, "description": "Mưa"},
        {"condition": "stormy", "impact": 0.6, "description": "Bão"},
        {"condition": "cloudy", "impact": 0.9, "description": "Nhiều mây"},
        {"condition": "hot", "impact": 0.85, "description": "Nắng nóng"}
    ]
    
    return random.choice(weather_conditions)

def generate_enhanced_feed_usage(date_obj, scenario, weather):
    """Tạo dữ liệu sử dụng cám nâng cao"""
    areas = {
        "Khu 1": ["T1", "T2", "T4", "T6"],
        "Khu 2": ["T1", "T2", "T4", "T6"],
        "Khu 3": ["1D", "2D", "4D", "2N"],
        "Khu 4": ["T2", "T4", "T6", "T8", "Trại 1 khu 4"],
        "Khu 5": [""]
    }
    
    # Tính toán multiplier tổng hợp
    total_multiplier = scenario["feed_multiplier"] * weather["impact"]
    
    feed_usage = {}
    for area, farms in areas.items():
        feed_usage[area] = {}
        for farm in farms:
            if farm == "":  # Khu 5 thường không hoạt động
                feed_usage[area][farm] = {"Sáng": 0.0, "Chiều": 0.0}
                continue
                
            # Tạo giá trị cơ bản
            base_morning = random.uniform(0.5, 1.8) * total_multiplier
            base_afternoon = random.uniform(0.5, 1.8) * total_multiplier
            
            morning = round(max(0, base_morning), 1)
            afternoon = round(max(0, base_afternoon), 1)
            
            # Xử lý trường hợp đặc biệt
            if scenario["description"] == "Ngày bảo trì":
                # Một số trại có thể hoàn toàn không hoạt động
                if random.random() < 0.4:
                    morning = 0.0
                    afternoon = 0.0
            elif weather["condition"] == "stormy":
                # Thời tiết xấu có thể làm gián đoạn hoạt động
                if random.random() < 0.3:
                    morning = 0.0
                if random.random() < 0.3:
                    afternoon = 0.0
            
            feed_usage[area][farm] = {
                "Sáng": morning,
                "Chiều": afternoon
            }
    
    return feed_usage

def generate_enhanced_mix_ingredients(total_batches, scenario, weather):
    """Tạo dữ liệu nguyên liệu mix nâng cao"""
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
    
    # Tính toán multiplier
    total_multiplier = scenario["mix_multiplier"] * weather["impact"]
    
    mix_ingredients = {}
    for ingredient, base_amount in base_ingredients.items():
        # Biến động ngẫu nhiên
        variation = random.uniform(0.8, 1.2)
        amount = base_amount * total_batches * total_multiplier * variation
        
        # Xử lý trường hợp đặc biệt
        if scenario["description"] == "Ngày bảo trì":
            # Một số nguyên liệu có thể không sử dụng
            if random.random() < 0.2:
                amount = 0.0
        elif scenario["description"] == "Ngày sản xuất cao":
            # Tăng cường một số nguyên liệu quan trọng
            if ingredient in ["L-Lysine", "DL-Methionine", "Premix 0.25% layer"]:
                amount *= 1.1
        
        # Làm tròn
        if amount < 0.1:
            amount = 0.0
        else:
            amount = round(amount, 1)
            
        mix_ingredients[ingredient] = amount
    
    return mix_ingredients

def generate_production_notes(scenario, weather, total_batches):
    """Tạo ghi chú sản xuất"""
    notes = []
    
    # Ghi chú về tình huống
    if scenario["description"] != "Ngày bình thường":
        notes.append(f"Tình huống: {scenario['description']}")
    
    # Ghi chú về thời tiết
    if weather["condition"] != "sunny":
        notes.append(f"Thời tiết: {weather['description']} (ảnh hưởng {weather['impact']*100:.0f}%)")
    
    # Ghi chú về sản lượng
    if total_batches > 25:
        notes.append("Sản lượng cao - cần theo dõi chất lượng")
    elif total_batches < 10:
        notes.append("Sản lượng thấp - kiểm tra nguyên nhân")
    
    # Ghi chú ngẫu nhiên
    random_notes = [
        "Kiểm tra chất lượng nguyên liệu đầu vào",
        "Bảo trì thiết bị định kỳ",
        "Theo dõi nhiệt độ kho bảo quản",
        "Cập nhật báo cáo tồn kho",
        "Kiểm tra hệ thống cân đo",
        "Vệ sinh khu vực sản xuất"
    ]
    
    if random.random() < 0.3:  # 30% cơ hội có ghi chú ngẫu nhiên
        notes.append(random.choice(random_notes))
    
    return notes

def generate_enhanced_report_for_date(date_obj):
    """Tạo báo cáo nâng cao cho một ngày cụ thể"""
    date_str = date_obj.strftime("%Y%m%d")
    display_date = date_obj.strftime("%d/%m/%Y")
    
    # Chọn tình huống và thời tiết
    scenario = select_scenario_for_date(date_obj)
    weather = generate_weather_impact()
    
    # Tạo dữ liệu
    feed_usage = generate_enhanced_feed_usage(date_obj, scenario, weather)
    
    # Tính toán tổng số mẻ
    total_batches = 0
    total_batches_by_area = {}
    
    for area, farms in feed_usage.items():
        area_total = 0
        for farm, shifts in farms.items():
            area_total += shifts["Sáng"] + shifts["Chiều"]
        total_batches_by_area[area] = area_total
        total_batches += area_total
    
    # Tạo nguyên liệu
    feed_ingredients = generate_enhanced_mix_ingredients(total_batches, scenario, weather)  # Sử dụng cho cả feed và mix
    mix_ingredients = generate_enhanced_mix_ingredients(total_batches, scenario, weather)
    
    # Tạo ghi chú
    production_notes = generate_production_notes(scenario, weather, total_batches)
    
    # Tạo công thức sử dụng
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
            morning_formula = random.choices(formulas, weights=[70, 20, 10])[0]
            afternoon_formula = random.choices(formulas, weights=[70, 20, 10])[0]
            
            formula_usage[area][farm] = {
                "Sáng": morning_formula,
                "Chiều": afternoon_formula
            }
    
    # Tạo column mix formulas
    column_formulas = [
        "Khu 1-5", "Khu 2(1, 2, 3, 6)", "Khu 2(4,5)",
        "Khu 3 - Gà con công thức", "Khu 4(2, 3, 4, 5)", "Khu 4(6, 7, 8)"
    ]
    
    column_mix_formulas = {}
    for i in range(18):
        column_mix_formulas[str(i)] = random.choice(column_formulas)
    
    # Tạo báo cáo
    report = {
        "date": date_str,
        "display_date": display_date,
        "scenario": scenario["description"],
        "weather": weather,
        "production_notes": production_notes,
        "feed_usage": feed_usage,
        "formula_usage": formula_usage,
        "feed_ingredients": feed_ingredients,
        "mix_ingredients": mix_ingredients,
        "total_batches": round(total_batches, 1),
        "total_batches_by_area": total_batches_by_area,
        "default_formula": "GD",
        "total_feed": round(sum(feed_ingredients.values()), 1),
        "total_mix": round(sum(mix_ingredients.values()), 1),
        "batch_count": round(total_batches, 1),
        "column_mix_formulas": column_mix_formulas,
        "efficiency_score": round(random.uniform(85, 98), 1),
        "quality_score": round(random.uniform(90, 99), 1)
    }
    
    return report

def main():
    """Hàm chính tạo báo cáo nâng cao"""
    print("🔄 Tạo dữ liệu báo cáo nâng cao với tình huống đặc biệt...")
    
    # Tạo thư mục reports
    reports_dir = Path("src/data/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    # Ngày bắt đầu: 25/08/2025 (tháng sau)
    start_date = datetime(2025, 8, 25)
    
    # Tạo báo cáo cho 31 ngày
    reports_created = 0
    scenarios_count = {}
    
    for i in range(31):
        current_date = start_date + timedelta(days=i)
        
        # Tạo báo cáo nâng cao
        report = generate_enhanced_report_for_date(current_date)
        
        # Đếm scenarios
        scenario = report["scenario"]
        scenarios_count[scenario] = scenarios_count.get(scenario, 0) + 1
        
        # Lưu file
        filename = f"report_{current_date.strftime('%Y%m%d')}.json"
        filepath = reports_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=4)
        
        reports_created += 1
        weather_desc = report["weather"]["description"]
        print(f"✅ {filename} - {current_date.strftime('%d/%m/%Y')} - {scenario} - {weather_desc}")
    
    print(f"\n🎉 Hoàn thành! Đã tạo {reports_created} báo cáo nâng cao")
    print(f"📁 Các file được lưu trong: {reports_dir}")
    
    # Thống kê scenarios
    print(f"\n📊 Thống kê tình huống:")
    for scenario, count in scenarios_count.items():
        percentage = (count / reports_created) * 100
        print(f"   - {scenario}: {count} ngày ({percentage:.1f}%)")

if __name__ == "__main__":
    main()
