"""
Logo for the Chicken Farm App
"""

from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QFont, QBrush, QPen, QLinearGradient
from PyQt5.QtCore import Qt, QRect, QSize, QPoint

def create_app_logo(size=64):
    """Create a logo for the application

    Args:
        size: Size of the logo in pixels

    Returns:
        QIcon: Application logo
    """
    # Create a pixmap for the logo
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    # Create a painter
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # Draw background circle
    gradient = QLinearGradient(0, 0, size, size)
    gradient.setColorAt(0, QColor(74, 134, 232))  # Light blue
    gradient.setColorAt(1, QColor(32, 85, 153))   # Dark blue

    painter.setBrush(QBrush(gradient))
    painter.setPen(Qt.NoPen)
    painter.drawEllipse(2, 2, size-4, size-4)

    # Draw chicken silhouette
    painter.setBrush(QBrush(QColor(255, 255, 255)))
    painter.setPen(QPen(QColor(255, 255, 255), 1))

    # Draw body
    painter.drawEllipse(size//4, size//3, size//2, size//2)

    # Draw head
    painter.drawEllipse(size//2, size//5, size//3, size//3)

    # Draw beak
    painter.setBrush(QBrush(QColor(255, 165, 0)))  # Orange
    points = [
        (size//2 + size//3, size//5 + size//6),
        (size//2 + size//3 + size//8, size//5 + size//6 - size//12),
        (size//2 + size//3 + size//8, size//5 + size//6 + size//12)
    ]
    painter.drawPolygon(*[QPoint(x, y) for x, y in points])

    # Draw text
    font = QFont("Arial", size//8, QFont.Bold)
    painter.setFont(font)
    painter.setPen(QPen(QColor(255, 255, 255)))
    painter.drawText(QRect(0, size - size//4, size, size//4), Qt.AlignCenter, "FARM")

    # End painting
    painter.end()

    # Create and return icon
    return QIcon(pixmap)

def create_splash_image(width=400, height=300):
    """Create a splash image for the application

    Args:
        width: Width of the splash image
        height: Height of the splash image

    Returns:
        QPixmap: Splash image
    """
    # Create a pixmap for the splash
    pixmap = QPixmap(width, height)

    # Create gradient background
    gradient = QLinearGradient(0, 0, width, height)
    gradient.setColorAt(0, QColor(74, 134, 232))  # Light blue
    gradient.setColorAt(1, QColor(32, 85, 153))   # Dark blue

    # Create a painter
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # Fill background
    painter.fillRect(0, 0, width, height, QBrush(gradient))

    # Draw app logo
    logo_size = min(width, height) // 2
    logo_pixmap = create_app_logo(logo_size).pixmap(QSize(logo_size, logo_size))
    painter.drawPixmap((width - logo_size) // 2, height // 4 - logo_size // 2, logo_pixmap)

    # Draw app name
    font = QFont("Arial", height // 12, QFont.Bold)
    painter.setFont(font)
    painter.setPen(QPen(QColor(255, 255, 255)))
    painter.drawText(QRect(0, height // 2, width, height // 6), Qt.AlignCenter, "Phần mềm Quản lý Cám - Trại Gà")

    # Draw version
    font = QFont("Arial", height // 24)
    painter.setFont(font)
    painter.drawText(QRect(0, height // 2 + height // 6, width, height // 12), Qt.AlignCenter, "Phiên bản 2.0")

    # Draw loading text
    font = QFont("Arial", height // 30)
    painter.setFont(font)
    painter.drawText(QRect(0, height - height // 8, width, height // 8), Qt.AlignCenter, "Đang khởi động...")

    # End painting
    painter.end()

    return pixmap