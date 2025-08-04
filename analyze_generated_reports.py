#!/usr/bin/env python3
"""
Phân tích và thống kê dữ liệu báo cáo đã tạo
"""

import json
import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict

def load_all_reports():
    """Tải tất cả báo cáo từ thư mục reports"""
    reports_dir = Path("src/data/reports")
    reports = []
    
    if not reports_dir.exists():
        print("❌ Thư mục reports không tồn tại")
        return []
    
    for file_path in reports_dir.glob("report_*.json"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                report = json.load(f)
                reports.append(report)
        except Exception as e:
            print(f"⚠️ Lỗi đọc file {file_path}: {e}")
    
    return reports

def analyze_reports_statistics(reports):
    """Phân tích thống kê báo cáo"""
    print("📊 THỐNG KÊ TỔNG QUAN")
    print("="*50)
    
    total_reports = len(reports)
    print(f"Tổng số báo cáo: {total_reports}")
    
    if total_reports == 0:
        return
    
    # Thống kê theo ngày
    dates = [report.get("display_date", "N/A") for report in reports]
    dates.sort()
    print(f"Từ ngày: {dates[0]} đến {dates[-1]}")
    
    # Thống kê tổng số mẻ
    total_batches = [report.get("total_batches", 0) for report in reports]
    avg_batches = sum(total_batches) / len(total_batches)
    max_batches = max(total_batches)
    min_batches = min(total_batches)
    
    print(f"Số mẻ trung bình/ngày: {avg_batches:.1f}")
    print(f"Số mẻ cao nhất: {max_batches:.1f}")
    print(f"Số mẻ thấp nhất: {min_batches:.1f}")
    
    # Thống kê tổng feed và mix
    total_feed = [report.get("total_feed", 0) for report in reports]
    total_mix = [report.get("total_mix", 0) for report in reports]
    
    avg_feed = sum(total_feed) / len(total_feed)
    avg_mix = sum(total_mix) / len(total_mix)
    
    print(f"Cám trung bình/ngày: {avg_feed:.1f} kg")
    print(f"Mix trung bình/ngày: {avg_mix:.1f} kg")
    
    # Thống kê scenarios (nếu có)
    scenarios = defaultdict(int)
    for report in reports:
        scenario = report.get("scenario", "Không xác định")
        scenarios[scenario] += 1
    
    if scenarios:
        print(f"\n🎭 THỐNG KÊ TÌNH HUỐNG")
        print("="*30)
        for scenario, count in scenarios.items():
            percentage = (count / total_reports) * 100
            print(f"{scenario}: {count} ngày ({percentage:.1f}%)")
    
    # Thống kê thời tiết (nếu có)
    weather_conditions = defaultdict(int)
    for report in reports:
        weather = report.get("weather", {})
        condition = weather.get("description", "Không xác định")
        weather_conditions[condition] += 1
    
    if weather_conditions:
        print(f"\n🌤️ THỐNG KÊ THỜI TIẾT")
        print("="*30)
        for condition, count in weather_conditions.items():
            percentage = (count / total_reports) * 100
            print(f"{condition}: {count} ngày ({percentage:.1f}%)")

def analyze_production_trends(reports):
    """Phân tích xu hướng sản xuất"""
    print(f"\n📈 XU HƯỚNG SẢN XUẤT")
    print("="*30)
    
    # Sắp xếp báo cáo theo ngày
    reports_sorted = sorted(reports, key=lambda x: x.get("date", ""))
    
    if len(reports_sorted) < 7:
        print("Cần ít nhất 7 báo cáo để phân tích xu hướng")
        return
    
    # Tính xu hướng 7 ngày đầu vs 7 ngày cuối
    first_week = reports_sorted[:7]
    last_week = reports_sorted[-7:]
    
    first_week_avg = sum(r.get("total_batches", 0) for r in first_week) / 7
    last_week_avg = sum(r.get("total_batches", 0) for r in last_week) / 7
    
    trend = ((last_week_avg - first_week_avg) / first_week_avg) * 100 if first_week_avg > 0 else 0
    
    print(f"Tuần đầu - Trung bình: {first_week_avg:.1f} mẻ/ngày")
    print(f"Tuần cuối - Trung bình: {last_week_avg:.1f} mẻ/ngày")
    
    if trend > 5:
        print(f"📈 Xu hướng tăng: +{trend:.1f}%")
    elif trend < -5:
        print(f"📉 Xu hướng giảm: {trend:.1f}%")
    else:
        print(f"➡️ Xu hướng ổn định: {trend:.1f}%")

def analyze_ingredients_usage(reports):
    """Phân tích sử dụng nguyên liệu"""
    print(f"\n🥫 PHÂN TÍCH NGUYÊN LIỆU")
    print("="*30)
    
    # Tổng hợp nguyên liệu feed
    feed_totals = defaultdict(float)
    mix_totals = defaultdict(float)
    
    for report in reports:
        feed_ingredients = report.get("feed_ingredients", {})
        mix_ingredients = report.get("mix_ingredients", {})
        
        for ingredient, amount in feed_ingredients.items():
            feed_totals[ingredient] += amount
        
        for ingredient, amount in mix_ingredients.items():
            mix_totals[ingredient] += amount
    
    # Top 5 nguyên liệu feed
    print("🌾 Top 5 nguyên liệu cám:")
    top_feed = sorted(feed_totals.items(), key=lambda x: x[1], reverse=True)[:5]
    for ingredient, total in top_feed:
        avg_daily = total / len(reports)
        print(f"  {ingredient}: {total:.1f} kg tổng ({avg_daily:.1f} kg/ngày)")
    
    # Top 5 nguyên liệu mix
    print("\n🧪 Top 5 nguyên liệu mix:")
    top_mix = sorted(mix_totals.items(), key=lambda x: x[1], reverse=True)[:5]
    for ingredient, total in top_mix:
        avg_daily = total / len(reports)
        print(f"  {ingredient}: {total:.1f} kg tổng ({avg_daily:.1f} kg/ngày)")

def analyze_area_performance(reports):
    """Phân tích hiệu suất theo khu vực"""
    print(f"\n🏭 HIỆU SUẤT THEO KHU VỰC")
    print("="*30)
    
    area_totals = defaultdict(float)
    area_counts = defaultdict(int)
    
    for report in reports:
        total_batches_by_area = report.get("total_batches_by_area", {})
        
        for area, batches in total_batches_by_area.items():
            area_totals[area] += batches
            area_counts[area] += 1
    
    # Tính trung bình theo khu vực
    for area in area_totals:
        total = area_totals[area]
        count = area_counts[area]
        avg = total / count if count > 0 else 0
        
        print(f"{area}: {total:.1f} mẻ tổng ({avg:.1f} mẻ/ngày)")

def generate_summary_report(reports):
    """Tạo báo cáo tổng kết"""
    print(f"\n📋 BÁO CÁO TỔNG KẾT")
    print("="*50)
    
    total_reports = len(reports)
    if total_reports == 0:
        print("Không có dữ liệu để tạo báo cáo tổng kết")
        return
    
    # Tính tổng các chỉ số
    total_batches_sum = sum(r.get("total_batches", 0) for r in reports)
    total_feed_sum = sum(r.get("total_feed", 0) for r in reports)
    total_mix_sum = sum(r.get("total_mix", 0) for r in reports)
    
    print(f"Tổng số ngày có báo cáo: {total_reports}")
    print(f"Tổng số mẻ sản xuất: {total_batches_sum:.1f}")
    print(f"Tổng lượng cám sử dụng: {total_feed_sum:.1f} kg")
    print(f"Tổng lượng mix sử dụng: {total_mix_sum:.1f} kg")
    print(f"Tổng nguyên liệu: {total_feed_sum + total_mix_sum:.1f} kg")
    
    # Hiệu suất
    if total_reports > 0:
        avg_efficiency = sum(r.get("efficiency_score", 0) for r in reports if "efficiency_score" in r)
        efficiency_count = sum(1 for r in reports if "efficiency_score" in r)
        
        if efficiency_count > 0:
            avg_efficiency = avg_efficiency / efficiency_count
            print(f"Điểm hiệu suất trung bình: {avg_efficiency:.1f}%")
        
        avg_quality = sum(r.get("quality_score", 0) for r in reports if "quality_score" in r)
        quality_count = sum(1 for r in reports if "quality_score" in r)
        
        if quality_count > 0:
            avg_quality = avg_quality / quality_count
            print(f"Điểm chất lượng trung bình: {avg_quality:.1f}%")

def main():
    """Hàm chính phân tích báo cáo"""
    print("🔍 BẮT ĐẦU PHÂN TÍCH DỮ LIỆU BÁO CÁO")
    print("="*60)
    
    # Tải tất cả báo cáo
    reports = load_all_reports()
    
    if not reports:
        print("❌ Không tìm thấy báo cáo nào để phân tích")
        return
    
    # Chạy các phân tích
    analyze_reports_statistics(reports)
    analyze_production_trends(reports)
    analyze_ingredients_usage(reports)
    analyze_area_performance(reports)
    generate_summary_report(reports)
    
    print(f"\n✅ HOÀN THÀNH PHÂN TÍCH!")
    print(f"Đã phân tích {len(reports)} báo cáo thành công.")

if __name__ == "__main__":
    main()
