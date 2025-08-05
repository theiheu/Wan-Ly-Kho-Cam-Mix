from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QBrush, QPen, QFont
from PyQt5.QtCore import Qt, QRect, QSize, QPoint

def create_app_icon():
    """Create an app icon for the Quan_Ly_Kho_Cam_&_Mix farm app"""
    # Create a pixmap for the icon
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.transparent)

    # Create a painter to draw on the pixmap
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # Draw Quan_Ly_Kho_Cam_&_Mix silhouette
    painter.setPen(QPen(QColor(50, 50, 50), 2))
    painter.setBrush(QBrush(QColor(255, 200, 0)))  # Golden yellow for Quan_Ly_Kho_Cam_&_Mix

    # Body
    painter.drawEllipse(10, 20, 40, 30)

    # Head
    painter.drawEllipse(45, 15, 15, 15)

    # Beak
    painter.setBrush(QBrush(QColor(255, 100, 0)))  # Orange beak
    points = [
        (60, 22),
        (65, 25),
        (60, 28)
    ]
    painter.drawPolygon(*[QPoint(*point) for point in points])

    # Comb
    painter.setBrush(QBrush(QColor(255, 0, 0)))  # Red comb
    points = [
        (50, 10),
        (55, 5),
        (60, 10),
        (55, 15)
    ]
    painter.drawPolygon(*[QPoint(*point) for point in points])

    # Legs
    painter.setPen(QPen(QColor(255, 150, 0), 2))
    painter.drawLine(20, 50, 15, 60)
    painter.drawLine(35, 50, 40, 60)

    # Feed symbol
    painter.setPen(QPen(QColor(100, 50, 0), 1))
    painter.setBrush(QBrush(QColor(150, 100, 50)))  # Brown for feed
    painter.drawEllipse(5, 40, 10, 10)
    painter.drawEllipse(10, 45, 8, 8)
    painter.drawEllipse(3, 45, 7, 7)

    # Add text "CAM" for feed
    painter.setPen(QColor(50, 50, 50))
    font = QFont("Arial", 8, QFont.Bold)
    painter.setFont(font)
    painter.drawText(QRect(5, 45, 30, 15), Qt.AlignLeft, "CÁM")

    # End painting
    painter.end()

    # Create and return the icon
    return QIcon(pixmap)

def create_app_logo(size=QSize(200, 200)):
    """Create a larger app logo for the Quan_Ly_Kho_Cam_&_Mix"""
    # Calculate scale factor
    scale_factor = min(size.width() / 64.0, size.height() / 64.0)

    # Create a pixmap for the logo
    pixmap = QPixmap(size)
    pixmap.fill(Qt.transparent)

    # Create a painter to draw on the pixmap
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # Scale the painter
    painter.scale(scale_factor, scale_factor)

    # Draw Quan_Ly_Kho_Cam_&_Mix silhouette
    painter.setPen(QPen(QColor(50, 50, 50), 2))
    painter.setBrush(QBrush(QColor(255, 200, 0)))  # Golden yellow for Quan_Ly_Kho_Cam_&_Mix

    # Body
    painter.drawEllipse(10, 20, 40, 30)

    # Head
    painter.drawEllipse(45, 15, 15, 15)

    # Beak
    painter.setBrush(QBrush(QColor(255, 100, 0)))  # Orange beak
    points = [
        (60, 22),
        (65, 25),
        (60, 28)
    ]
    painter.drawPolygon(*[QPoint(*point) for point in points])

    # Comb
    painter.setBrush(QBrush(QColor(255, 0, 0)))  # Red comb
    points = [
        (50, 10),
        (55, 5),
        (60, 10),
        (55, 15)
    ]
    painter.drawPolygon(*[QPoint(*point) for point in points])

    # Legs
    painter.setPen(QPen(QColor(255, 150, 0), 2))
    painter.drawLine(20, 50, 15, 60)
    painter.drawLine(35, 50, 40, 60)

    # Feed symbol
    painter.setPen(QPen(QColor(100, 50, 0), 1))
    painter.setBrush(QBrush(QColor(150, 100, 50)))  # Brown for feed
    painter.drawEllipse(5, 40, 10, 10)
    painter.drawEllipse(10, 45, 8, 8)
    painter.drawEllipse(3, 45, 7, 7)

    # Add text "CAM" for feed
    painter.setPen(QColor(50, 50, 50))
    font = QFont("Arial", 8, QFont.Bold)
    painter.setFont(font)
    painter.drawText(QRect(5, 45, 30, 15), Qt.AlignLeft, "CÁM")

    # End painting
    painter.end()

    # Return the pixmap
    return pixmap