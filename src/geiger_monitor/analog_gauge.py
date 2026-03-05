"""Analog gauge widget for displaying radiation dose rate on a logarithmic scale."""

import math
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont
from PyQt6.QtWidgets import QWidget


class AnalogGauge(QWidget):
    """Logarithmic analog gauge for displaying radiation dose rate in µSv/h."""

    def __init__(self, parent=None):
        """Initialize the analog gauge.

        Args:
            parent: Parent widget.
        """
        super().__init__(parent)
        self.m_min = 0.01  # µSv/h
        self.m_max = 1000.0  # µSv/h
        self.m_value = 0.01
        self.setMinimumSize(160, 160)

    def setRange(self, min_value: float, max_value: float) -> None:
        """Set the range of the gauge.

        Args:
            min_value: Minimum value in µSv/h (must be > 0).
            max_value: Maximum value in µSv/h (must be > min_value).
        """
        if min_value <= 0.0 or max_value <= min_value:
            return
        self.m_min = min_value
        self.m_max = max_value
        if self.m_value < self.m_min:
            self.m_value = self.m_min
        if self.m_value > self.m_max:
            self.m_value = self.m_max
        self.update()

    def setValue(self, value: float) -> None:
        """Set the current value displayed by the gauge.

        Args:
            value: Value in µSv/h.
        """
        if value <= 0.0:
            self.m_value = self.m_min
        elif value < self.m_min:
            self.m_value = self.m_min
        elif value > self.m_max:
            self.m_value = self.m_max
        else:
            self.m_value = value
        self.update()

    def paintEvent(self, event):
        """Paint the gauge widget.

        Args:
            event: Paint event (unused).
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        side = min(self.width(), self.height())
        painter.translate(self.width() / 2.0, self.height() / 2.0)
        painter.scale(side / 200.0, side / 200.0)

        start_angle_deg = 210.0  # left side
        end_angle_deg = -30.0  # right side

        def value_to_angle(v: float) -> float:
            """Convert a value to an angle using logarithmic scale.

            Args:
                v: Value to convert.

            Returns:
                Angle in degrees.
            """
            log_min = math.log(self.m_min)
            log_max = math.log(self.m_max)
            lv = math.log(max(v, self.m_min))
            t = (lv - log_min) / (log_max - log_min)
            t = max(0.0, min(1.0, t))
            return start_angle_deg + t * (end_angle_deg - start_angle_deg)

        # Background
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(30, 30, 30))
        painter.drawEllipse(0, 0, 95, 95)

        # Scale arc
        painter.setPen(QPen(Qt.GlobalColor.lightGray, 3))
        arc_rect = (-80, -80, 160, 160)
        angle_span = int((start_angle_deg - end_angle_deg) * 16)
        start_angle = int((90 - start_angle_deg) * 16)
        painter.drawArc(*arc_rect, start_angle, angle_span)

        # Decade markers
        painter.setPen(QPen(Qt.GlobalColor.white, 2))
        decades = [0.01, 0.1, 1.0, 10.0, 100.0, 1000.0]
        for decade in decades:
            if decade < self.m_min or decade > self.m_max:
                continue

            angle = math.radians(value_to_angle(decade))
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            r1 = 70.0
            r2 = 80.0

            p1_x = r1 * cos_a
            p1_y = -r1 * sin_a
            p2_x = r2 * cos_a
            p2_y = -r2 * sin_a
            painter.drawLine(int(p1_x), int(p1_y), int(p2_x), int(p2_y))

            # Decade labels
            if decade < 1.0:
                label = f"{decade:.2f}"
            else:
                label = f"{decade:.3g}"

            rt = 55.0
            pt_x = rt * cos_a
            pt_y = -rt * sin_a

            font = painter.font()
            font.setPointSize(7)
            painter.setFont(font)
            painter.drawText(
                int(pt_x - 12), int(pt_y - 8), 24, 16,
                Qt.AlignmentFlag.AlignCenter, label
            )

        # Needle
        angle = math.radians(value_to_angle(self.m_value))
        painter.setPen(QPen(Qt.GlobalColor.red, 3))
        r_needle = 75.0
        p1_x, p1_y = 0, 0
        p2_x = r_needle * math.cos(angle)
        p2_y = -r_needle * math.sin(angle)
        painter.drawLine(int(p1_x), int(p1_y), int(p2_x), int(p2_y))

        # Center point
        painter.setBrush(Qt.GlobalColor.red)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(-4, -4, 8, 8)

        # Label
        painter.setPen(Qt.GlobalColor.white)
        font = painter.font()
        font.setPointSize(8)
        painter.setFont(font)
        painter.drawText(-60, 40, 120, 20, Qt.AlignmentFlag.AlignCenter, "µSv/h (log)")
