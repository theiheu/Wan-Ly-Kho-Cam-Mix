"""
Export Service for the Chicken Farm App
Handles exporting data to Excel and other formats
"""

import os
import pandas as pd
from datetime import datetime

class ExportService:
    """Service for exporting data to various formats"""

    def __init__(self):
        """Initialize the export service"""
        pass

    def export_to_excel(self, data, filename=None, sheet_name="Sheet1"):
        """Export data to Excel file"""
        # Generate filename if not provided
        if filename is None:
            date = datetime.now().strftime("%Y-%m-%d")
            filename = f"Báo cáo {date}.xlsx"

        # Create Excel writer
        writer = pd.ExcelWriter(filename, engine='xlsxwriter')

        # Get workbook and worksheet
        workbook = writer.book

        # Add formats
        header_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#D9E1F2',
            'border': 1
        })

        cell_format = workbook.add_format({
            'font_size': 11,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })

        number_format = workbook.add_format({
            'font_size': 11,
            'align': 'right',
            'valign': 'vcenter',
            'border': 1,
            'num_format': '#,##0.00'
        })

        # Convert data to DataFrame if it's not already
        if not isinstance(data, pd.DataFrame):
            df = pd.DataFrame(data)
        else:
            df = data

        # Write to Excel
        df.to_excel(writer, sheet_name=sheet_name, index=False)

        # Get the worksheet
        worksheet = writer.sheets[sheet_name]

        # Format headers
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)

        # Format cells
        for row_num in range(1, len(df) + 1):
            for col_num, value in enumerate(df.iloc[row_num - 1]):
                if isinstance(value, (int, float)):
                    worksheet.write(row_num, col_num, value, number_format)
                else:
                    worksheet.write(row_num, col_num, value, cell_format)

        # Auto-adjust column widths
        for col_num, value in enumerate(df.columns.values):
            max_len = max(df[value].astype(str).map(len).max(), len(str(value))) + 2
            worksheet.set_column(col_num, col_num, max_len)

        # Save the workbook
        writer.close()

        return filename

    def export_history_to_excel(self, history_data, filename=None):
        """Export history data to Excel with multiple sheets"""
        # Generate filename if not provided
        if filename is None:
            date = datetime.now().strftime("%Y-%m-%d")
            filename = f"Lịch sử {date}.xlsx"

        # Create Excel writer
        writer = pd.ExcelWriter(filename, engine='xlsxwriter')

        # Export each type of history data to a separate sheet
        if "usage" in history_data:
            usage_df = pd.DataFrame(history_data["usage"])
            usage_df.to_excel(writer, sheet_name="Sử dụng", index=False)

        if "feed" in history_data:
            feed_df = pd.DataFrame(history_data["feed"])
            feed_df.to_excel(writer, sheet_name="Nhập cám", index=False)

        if "mix" in history_data:
            mix_df = pd.DataFrame(history_data["mix"])
            mix_df.to_excel(writer, sheet_name="Nhập hỗn hợp", index=False)

        # Save the workbook
        writer.close()

        return filename