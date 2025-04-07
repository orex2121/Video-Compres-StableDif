import sys
import os
import json
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QComboBox,
    QMessageBox, QLineEdit, QTextEdit, QFrame
)
from PySide6.QtGui import QFont, QIcon
from PySide6.QtCore import QProcess, Qt

class VideoConverterApp(QWidget):
    def __init__(self):
        super().__init__()
        self.load_language_data()
        self.load_config()
        self.setWindowTitle(self.trans("title"))
        self.setGeometry(300, 300, 400, 470)
        self.setWindowIcon(QIcon("camera.png"))

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(20, 20, 20, 20)

        # Верхняя панель переключения языка
        lang_switch = QHBoxLayout()
        lang_switch.addStretch()

        self.lang_label = QLabel("RU")
        self.lang_label.setFixedWidth(25)
        self.lang_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.lang_button = QPushButton("⇆")
        self.lang_button.setFixedSize(40, 25)
        self.lang_button.clicked.connect(self.toggle_language)

        lang_switch.addWidget(self.lang_label)
        lang_switch.addWidget(self.lang_button)
        self.layout.addLayout(lang_switch)

        self.path_input = QLineEdit()
        self.layout.addWidget(self.path_input)

        file_layout = QHBoxLayout()
        self.file_label = QLabel()
        file_layout.addWidget(self.file_label)

        self.load_button = QPushButton()
        self.load_button.clicked.connect(self.load_file)
        file_layout.addWidget(self.load_button)

        self.layout.addLayout(file_layout)

        line1 = QFrame()
        line1.setFrameShape(QFrame.HLine)
        line1.setFrameShadow(QFrame.Sunken)
        line_wrapper = QVBoxLayout()
        line_wrapper.setContentsMargins(0, 0, 0, 15)
        line_wrapper.addWidget(line1)
        self.layout.addLayout(line_wrapper)

        quality_layout = QHBoxLayout()
        self.quality_label = QLabel()
        quality_layout.addWidget(self.quality_label)

        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["default", "640x360", "854x480", "1280x720", "1920x1080", "2560x1440"])
        quality_layout.addWidget(self.quality_combo)
        self.layout.addLayout(quality_layout)

        crf_layout = QHBoxLayout()
        self.crf_label = QLabel()
        crf_layout.addWidget(self.crf_label)

        self.crf_input = QLineEdit()
        self.crf_input.setText("24")
        self.crf_input.setFixedWidth(50)
        crf_layout.addWidget(self.crf_input)
        self.layout.addLayout(crf_layout)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.layout.addWidget(line)

        self.convert_button = QPushButton()
        self.convert_button.setMinimumHeight(60)
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.convert_button.setFont(font)
        self.convert_button.setStyleSheet("""
            QPushButton {
                background-color: #00BFFF;
                color: white;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #1E90FF;
            }
        """)
        self.convert_button.clicked.connect(self.convert_video)
        button_wrapper = QVBoxLayout()
        button_wrapper.setContentsMargins(0, 20, 0, 20)
        button_wrapper.addWidget(self.convert_button)
        self.layout.addLayout(button_wrapper)

        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.layout.addWidget(self.console)

        self.setLayout(self.layout)
        self.update_texts()

    def load_language_data(self):
        with open("lang.json", "r", encoding="utf-8") as f:
            self.lang_data = json.load(f)

    def load_config(self):
        """Загружаем сохраненные настройки (язык) из файла config.json"""
        try:
            with open("config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
                self.current_language = config.get("language", "ru")  # По умолчанию русский
        except FileNotFoundError:
            self.current_language = "ru"  # Если конфиг не найден, по умолчанию русский

    def save_config(self):
        """Сохраняем выбранный язык в config.json"""
        config = {"language": self.current_language}
        with open("config.json", "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=4)

    def trans(self, key):
        return self.lang_data[self.current_language].get(key, key)

    def update_texts(self):
        self.setWindowTitle(self.trans("title"))
        self.path_input.setPlaceholderText(self.trans("path_placeholder"))
        self.file_label.setText(self.trans("file_label"))
        self.load_button.setText(self.trans("load_file"))
        self.quality_label.setText(self.trans("resolution"))
        self.crf_label.setText(self.trans("crf_label"))
        self.convert_button.setText(self.trans("convert_button"))
        self.console.setPlaceholderText(self.trans("console_placeholder"))
        self.console.clear()
        self.console.append(self.trans("console_intro"))
        self.lang_label.setText(self.current_language.upper())

    def toggle_language(self):
        """Переключаем язык и сохраняем настройки"""
        self.current_language = 'en' if self.current_language == 'ru' else 'ru'
        self.update_texts()
        self.save_config()  # Сохраняем выбранный язык

    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, self.trans("load_file"))
        if file_path:
            self.path_input.setText(file_path)

    def convert_video(self):
        selected_quality = self.quality_combo.currentText()
        file_path = self.path_input.text().strip()
        crf_value = self.crf_input.text().strip()

        if not file_path or not os.path.isfile(file_path):
            QMessageBox.warning(self, self.trans("error_title"), self.trans("error_file"))
            return

        if not crf_value.isdigit():
            QMessageBox.warning(self, self.trans("error_title"), self.trans("error_crf"))
            return

        input_dir = os.path.dirname(file_path)
        input_filename = os.path.basename(file_path)
        name, _ = os.path.splitext(input_filename)
        output_filename = f"compres-{name}.mp4"
        output_path = os.path.join(input_dir, output_filename)
        ffmpeg_path = os.path.join(os.path.dirname(__file__), "ffmpeg.exe")

        if not os.path.isfile(ffmpeg_path):
            QMessageBox.critical(self, self.trans("error_title"), self.trans("error_ffmpeg"))
            return

        cmd = [
            ffmpeg_path,
            "-i", file_path,
            "-vcodec", "libx264",
            "-crf", crf_value,
            "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2",
            "-y", output_path
        ]

        if selected_quality != "default":
            cmd.insert(3, "-s")
            cmd.insert(4, selected_quality)

        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.handle_finished)
        self.process.start(cmd[0], cmd[1:])

    def handle_stdout(self):
        data = self.process.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        self.console.append(stdout)

    def handle_stderr(self):
        data = self.process.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        self.console.append(stderr)

    def handle_finished(self):
        if self.process.exitCode() == 0:
            QMessageBox.information(
                self,
                self.trans("done_title"),
                f"{self.trans('done_message')}\n{self.path_input.text().strip()}"
            )
        else:
            QMessageBox.critical(self, self.trans("error_title"), self.trans("error_ffmpeg"))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoConverterApp()
    window.show()
    sys.exit(app.exec())
