#!/usr/bin/env python3
"""
Example integration of RemainingUsageCalculator with the main application
"""

from src.core.remaining_usage_calculator import RemainingUsageCalculator
from src.core.threshold_manager import ThresholdManager

def run_usage_analysis_example():
    """Example of how to use the remaining usage calculator"""
    
    # Initialize calculator
    calculator = RemainingUsageCalculator()
    
    # Run comprehensive analysis
    print("🚀 Starting usage analysis...")
    analysis = calculator.get_comprehensive_usage_analysis(days_history=7)
    
    # Get alerts
    alerts = calculator.get_critical_alerts(analysis)
    
    # Print results
    print("\n📋 ANALYSIS RESULTS:")
    print(f"Feed items: {len(analysis['feed'])}")
    print(f"Mix items: {len(analysis['mix'])}")
    
    print("\n🚨 ALERTS:")
    if alerts['critical']:
        print(f"Critical items ({len(alerts['critical'])}):")
        for item in alerts['critical']:
            print(f"  - {item['ingredient']} ({item['warehouse']}): {item['remaining_days']:.1f} days")
    
    if alerts['low']:
        print(f"Low stock items ({len(alerts['low'])}):")
        for item in alerts['low'][:5]:  # Show first 5
            print(f"  - {item['ingredient']} ({item['warehouse']}): {item['remaining_days']:.1f} days")
    
    # Generate full report
    report = calculator.generate_usage_report(days_history=7, save_to_file=True)
    
    print(f"\n📊 Report generated with {len(report.get('recommendations', []))} recommendations")
    for rec in report.get('recommendations', [])[:3]:
        print(f"  {rec}")
    
    return analysis, alerts, report

if __name__ == "__main__":
    run_usage_analysis_example()