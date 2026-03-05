"""Main application window for Geiger Monitor."""

from datetime import datetime, timedelta
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QDoubleValidator
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QComboBox, QPushButton, QLabel, QPlainTextEdit, QDoubleSpinBox
)
from PyQt6.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt6.QtChart import QChart, QChartView, QLineSeries
from PyQt6.QtCore import QDateTime

from .analog_gauge import AnalogGauge


class Sample:
    """Represents a counted sample with timestamp."""

    def __init__(self, timestamp: datetime, counts: int):
        """Initialize a sample.

        Args:
            timestamp: When the sample was recorded.
            counts: Number of counts in the sample period.
        """
        self.timestamp = timestamp
        self.counts = counts


class MainWindow(QMainWindow):
    """Main application window for Geiger Monitor."""

    def __init__(self, parent=None):
        """Initialize the main window.

        Args:
            parent: Parent widget.
        """
        super().__init__(parent)
        
        # Serial port and data
        self.m_serial = QSerialPort(self)
        self.m_read_buffer = bytearray()
        self.m_samples = []  # sliding window (~60s)

        # UI components
        self.m_port_combo = None
        self.m_refresh_button = None
        self.m_connect_button = None
        self.m_status_label = None
        self.m_cpm_label = None
        self.m_cps_label = None
        self.m_dose_label = None
        self.m_conversion_spin = None
        self.m_gauge = None
        self.m_chart_view = None
        self.m_series = None
        self.m_axis_x = None
        self.m_axis_y = None
        self.m_log_edit = None

        self.setup_ui()
        self.connect_signals()
        self.refresh_serial_ports()
        self.update_status()

    def setup_ui(self):
        """Set up the user interface."""
        central = QWidget(self)
        main_layout = QVBoxLayout(central)

        # Top grid layout
        top_layout = QGridLayout()

        # Port selection
        port_label = QLabel(self.tr("Port szeregowy:"), central)
        self.m_port_combo = QComboBox(central)
        self.m_refresh_button = QPushButton(self.tr("Odśwież"), central)
        self.m_connect_button = QPushButton(self.tr("Połącz"), central)

        # Statistics labels
        cpm_text_label = QLabel(self.tr("CPM (ostatnia minuta):"), central)
        self.m_cpm_label = QLabel(self.tr("-"), central)

        cps_text_label = QLabel(self.tr("CPS (ostatnia próbka):"), central)
        self.m_cps_label = QLabel(self.tr("-"), central)

        dose_text_label = QLabel(self.tr("Dawka: (µSv/h)"), central)
        self.m_dose_label = QLabel(self.tr("-"), central)

        # Conversion factor
        conv_label = QLabel(self.tr("Wsp. µSv/h na CPS:"), central)
        self.m_conversion_spin = QDoubleSpinBox(central)
        self.m_conversion_spin.setDecimals(6)
        self.m_conversion_spin.setRange(0.000001, 1.0)
        self.m_conversion_spin.setSingleStep(0.0001)
        self.m_conversion_spin.setValue(0.005)

        top_layout.addWidget(port_label, 0, 0)
        top_layout.addWidget(self.m_port_combo, 0, 1)
        top_layout.addWidget(self.m_refresh_button, 0, 2)
        top_layout.addWidget(self.m_connect_button, 0, 3)

        top_layout.addWidget(cpm_text_label, 1, 0)
        top_layout.addWidget(self.m_cpm_label, 1, 1)
        top_layout.addWidget(cps_text_label, 1, 2)
        top_layout.addWidget(self.m_cps_label, 1, 3)

        top_layout.addWidget(dose_text_label, 2, 0)
        top_layout.addWidget(self.m_dose_label, 2, 1)
        top_layout.addWidget(conv_label, 2, 2)
        top_layout.addWidget(self.m_conversion_spin, 2, 3)

        self.m_status_label = QLabel(self.tr("Nie połączono"), central)

        # Chart
        self.m_series = QLineSeries(self)
        chart = QChart()
        chart.addSeries(self.m_series)
        chart.legend().hide()
        chart.setTitle(self.tr("CPS w czasie"))

        from PyQt6.QtChart import QValueAxis
        self.m_axis_x = QValueAxis(self)
        self.m_axis_x.setTitleText(self.tr("Czas (s, ostatnie 60 s)"))
        self.m_axis_x.setRange(0.0, 60.0)

        self.m_axis_y = QValueAxis(self)
        self.m_axis_y.setTitleText(self.tr("CPS"))
        self.m_axis_y.setRange(0.0, 100.0)

        chart.addAxis(self.m_axis_x, Qt.AlignmentFlag.AlignBottom)
        chart.addAxis(self.m_axis_y, Qt.AlignmentFlag.AlignLeft)
        self.m_series.attachAxis(self.m_axis_x)
        self.m_series.attachAxis(self.m_axis_y)

        self.m_chart_view = QChartView(chart, central)
        self.m_chart_view.setMinimumHeight(200)

        # Analog gauge
        self.m_gauge = AnalogGauge(central)
        self.m_gauge.setRange(0.01, 1000.0)

        middle_layout = QHBoxLayout()
        middle_layout.addWidget(self.m_chart_view, 3)
        middle_layout.addWidget(self.m_gauge, 2)

        # Log display
        self.m_log_edit = QPlainTextEdit(central)
        self.m_log_edit.setReadOnly(True)
        self.m_log_edit.setMinimumHeight(120)

        main_layout.addLayout(top_layout)
        main_layout.addLayout(middle_layout)
        main_layout.addWidget(self.m_status_label)
        main_layout.addWidget(QLabel(self.tr("Odebrane próbki (licznik Geigera):"), central))
        main_layout.addWidget(self.m_log_edit, 1)

        self.setCentralWidget(central)
        self.setWindowTitle(self.tr("Geiger Monitor"))
        self.resize(900, 600)

    def connect_signals(self):
        """Connect signal/slot connections."""
        self.m_refresh_button.clicked.connect(self.refresh_serial_ports)
        self.m_connect_button.clicked.connect(self.toggle_connection)
        self.m_serial.readyRead.connect(self.handle_ready_read)

    @pyqtSlot()
    def refresh_serial_ports(self):
        """Refresh the list of available serial ports."""
        current = self.m_port_combo.currentText()
        self.m_port_combo.clear()

        for info in QSerialPortInfo.availablePorts():
            label = info.portName()
            if info.description():
                label += f" ({info.description()})"
            self.m_port_combo.addItem(label, info.systemLocation())

        # Try to restore previous selection
        idx = self.m_port_combo.findText(current)
        if idx >= 0:
            self.m_port_combo.setCurrentIndex(idx)

    @pyqtSlot()
    def toggle_connection(self):
        """Toggle serial connection on/off."""
        if self.m_serial.isOpen():
            self.m_serial.close()
            self.m_connect_button.setText(self.tr("Połącz"))
            self.update_status()
            return

        if self.m_port_combo.currentIndex() < 0:
            self.m_status_label.setText(self.tr("Brak wybranego portu."))
            return

        port_name = self.m_port_combo.currentData()
        self.m_serial.setPortName(port_name)

        # Typical Geiger counter settings
        self.m_serial.setBaudRate(QSerialPort.BaudRate.Baud9600)
        self.m_serial.setDataBits(QSerialPort.DataBits.Data8)
        self.m_serial.setParity(QSerialPort.Parity.NoParity)
        self.m_serial.setStopBits(QSerialPort.StopBits.OneStop)
        self.m_serial.setFlowControl(QSerialPort.FlowControl.NoFlowControl)

        if not self.m_serial.open(QSerialPort.OpenModeFlag.ReadOnly):
            error = self.m_serial.errorString()
            self.m_status_label.setText(self.tr(f"Błąd otwarcia portu: {error}"))
            return

        self.m_read_buffer.clear()
        self.m_samples.clear()

        self.m_connect_button.setText(self.tr("Rozłącz"))
        self.update_status()

    @pyqtSlot()
    def handle_ready_read(self):
        """Handle incoming serial data."""
        self.m_read_buffer.extend(self.m_serial.readAll())

        while True:
            newline_idx = self.m_read_buffer.find(b'\n')
            if newline_idx < 0:
                break

            line = bytes(self.m_read_buffer[:newline_idx])
            del self.m_read_buffer[:newline_idx + 1]

            line = line.strip()
            if line:
                self.process_line(line)

    def process_line(self, line: bytes):
        """Process a line of data from the Geiger counter.

        Args:
            line: The line to process.
        """
        try:
            value = int(line.decode('latin1'))
        except (ValueError, UnicodeDecodeError):
            now = datetime.now()
            self.m_log_edit.appendPlainText(
                f"[{now.isoformat()}] Nieprawidłowa próbka: {line.decode('latin1', errors='replace')}"
            )
            return

        now = datetime.now()
        self.m_samples.append(Sample(now, value))

        # Keep 60 second window
        cutoff = now - timedelta(seconds=60)
        while self.m_samples and self.m_samples[0].timestamp < cutoff:
            self.m_samples.pop(0)

        self.m_log_edit.appendPlainText(f"[{now.isoformat()}] {value}")

        # Update statistics
        cpm = self.current_cpm()
        if cpm >= 0.0:
            self.m_cpm_label.setText(f"{cpm:.1f}")
        else:
            self.m_cpm_label.setText(self.tr("-"))

        cps = self.current_cps()
        if cps >= 0.0:
            self.m_cps_label.setText(f"{cps:.1f}")
        else:
            self.m_cps_label.setText(self.tr("-"))

        dose = self.current_dose_rate()
        if dose >= 0.0:
            self.m_dose_label.setText(f"{dose:.4g}")
            self.m_gauge.setValue(dose)
        else:
            self.m_dose_label.setText(self.tr("-"))
            self.m_gauge.setValue(0.01)

        # Update chart
        self.m_series.clear()
        if self.m_samples:
            newest = self.m_samples[-1].timestamp
            max_cps = 1.0
            for sample in self.m_samples:
                dt = (newest - sample.timestamp).total_seconds()
                x = 60.0 - dt
                if x < 0.0:
                    continue
                y = float(sample.counts)
                self.m_series.append(x, y)
                if y > max_cps:
                    max_cps = y

            self.m_axis_x.setRange(0.0, 60.0)
            self.m_axis_y.setRange(0.0, max(10.0, max_cps * 1.2))

        self.update_status()

    def current_cpm(self) -> float:
        """Get current CPM (counts per minute) from last 60 seconds.

        Returns:
            CPM value or -1.0 if no samples.
        """
        if not self.m_samples:
            return -1.0

        total = sum(s.counts for s in self.m_samples)
        return float(total)

    def current_cps(self) -> float:
        """Get current CPS (counts per second) from last sample.

        Returns:
            CPS value or -1.0 if no samples.
        """
        if not self.m_samples:
            return -1.0

        return float(self.m_samples[-1].counts)

    def current_dose_rate(self) -> float:
        """Get current dose rate in µSv/h.

        Returns:
            Dose rate or -1.0 if unavailable.
        """
        cps = self.current_cps()
        if cps < 0.0 or not self.m_conversion_spin:
            return -1.0

        factor = self.m_conversion_spin.value()
        return cps * factor

    def update_status(self):
        """Update the status label."""
        if not self.m_serial.isOpen():
            self.m_status_label.setText(self.tr("Nie połączono"))
            return

        info = f"Połączono z {self.m_serial.portName()}"
        info += f" | próbki: {len(self.m_samples)}"

        cpm = self.current_cpm()
        if cpm >= 0.0:
            info += f" | CPM: {cpm:.1f}"
            cps = self.current_cps()
            if cps >= 0.0:
                info += f" | CPS: {cps:.1f}"
            dose = self.current_dose_rate()
            if dose >= 0.0:
                info += f" | µSv/h: {dose:.4g}"

        self.m_status_label.setText(info)
