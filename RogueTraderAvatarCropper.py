import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, 
    QVBoxLayout, QHBoxLayout, QFileDialog, QGraphicsView, 
    QGraphicsScene, QGraphicsPixmapItem, QMessageBox, QSpinBox, 
    QScrollArea
)
from PyQt5.QtGui import QPixmap, QPainter, QDesktopServices
from PyQt5.QtCore import Qt, QRectF, QUrl

# Словарь локализации (Русский / Английский)
LANG_DATA = {
    "ru": {
        "window_title": "Rogue Trader — Нарезка аватарок",
        "btn_load": "📂 Выбрать исходную фотографию",
        "status_none": "Фото не выбрано",
        "status_selected": "Выбрано: ",
        "btn_save": "Сохранить ",
        "btn_lang": "ENG",
        "btn_about": "ℹ️ Справка",
        "msg_warning_title": "Внимание",
        "msg_warning_text": "Сначала выберите исходную фотографию!",
        "dir_dialog": "Выберите папку для сохранения",
        "success_title": "Успех",
        "success_text": "Файл успешно сохранен:\n",
        "error_title": "Ошибка",
        "error_text": "Не удалось сохранить файл!",
        "about_title": "О программе",
        "about_html": """
            <h2 style='color: #2b5d8f; margin-bottom: 5px;'><b>Rogue Trader Avatar Cropper</b></h2>
            <p style='color: #2c3e50; font-size: 13px;'>A tool for creating and cropping portraits for Warhammer 40,000: Rogue Trader.</p>
            <p style='color: #7f8c8d; font-size: 12px; font-style: italic;'>Free and open source software</p>
            <hr style='border: none; border-top: 1px solid #dcdde1; margin: 10px 0;'>
            <p style='color: #2c3e50; font-size: 12px;'>© 2026 <a href='https://github.com/Lyagoosh/Rogue-Trader-Avatar-Cropper' style='color: #2980b9; text-decoration: none; font-weight: bold;'>Lyagoosh</a></p>
        """
    },
    "en": {
        "window_title": "Rogue Trader Avatar Cropper",
        "btn_load": "📂 Select Source Image",
        "status_none": "No image selected",
        "status_selected": "Selected: ",
        "btn_save": "Save ",
        "btn_lang": "RUS",
        "btn_about": "ℹ️ About",
        "msg_warning_title": "Warning",
        "msg_warning_text": "Please select a source image first!",
        "dir_dialog": "Select target directory",
        "success_title": "Success",
        "success_text": "File successfully saved:\n",
        "error_title": "Error",
        "error_text": "Failed to save file!",
        "about_title": "About",
        "about_html": """
            <h2 style='color: #2b5d8f; margin-bottom: 5px;'><b>Rogue Trader Avatar Cropper</b></h2>
            <p style='color: #2c3e50; font-size: 13px;'>A tool for creating and cropping portraits for Warhammer 40,000: Rogue Trader.</p>
            <p style='color: #7f8c8d; font-size: 12px; font-style: italic;'>Free and open source software</p>
            <hr style='border: none; border-top: 1px solid #dcdde1; margin: 10px 0;'>
            <p style='color: #2c3e50; font-size: 12px;'>© 2026 <a href='https://github.com/Lyagoosh/Rogue-Trader-Avatar-Cropper' style='color: #2980b9; text-decoration: none; font-weight: bold;'>Lyagoosh</a></p>
        """
    }
}

class AvatarCropView(QGraphicsView):
    def __init__(self, default_w, default_h):
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        
        self.pixmap_item = None
        self.target_width = default_w
        self.target_height = default_h
        
        self.setFocusPolicy(Qt.StrongFocus)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        
        self.update_aspect_ratio(default_w, default_h)

    def update_aspect_ratio(self, width, height):
        self.target_width = width
        self.target_height = height
        
        aspect = width / height if height > 0 else 1.0
        vis_h = 240
        vis_w = int(vis_h * aspect)
        
        if vis_w > 420:
            vis_w = 420
            vis_h = int(vis_w / aspect)
        elif vis_w < 150:
            vis_w = 150
            vis_h = int(vis_w / aspect)
            
        self.setFixedSize(vis_w, vis_h)
        self.scene.setSceneRect(0, 0, width, height)

    def set_image(self, pixmap):
        self.scene.clear()
        self.pixmap_item = QGraphicsPixmapItem(pixmap)
        self.pixmap_item.setFlag(QGraphicsPixmapItem.ItemIsMovable, True)
        self.scene.addItem(self.pixmap_item)
        self.pixmap_item.setPos(0, 0)
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatioByExpanding)

    def wheelEvent(self, event):
        if not self.pixmap_item:
            return
        zoom_in_factor = 1.15
        zoom_out_factor = 1.0 / zoom_in_factor
        
        if event.angleDelta().y() > 0:
            self.scale(zoom_in_factor, zoom_in_factor)
        else:
            self.scale(zoom_out_factor, zoom_out_factor)

    def get_cropped_image(self):
        if not self.pixmap_item:
            return None
        
        view_rect = self.viewport().rect()
        scene_rect = self.mapToScene(view_rect).boundingRect()
        
        result_pixmap = QPixmap(self.target_width, self.target_height)
        result_pixmap.fill(Qt.transparent)
        
        painter = QPainter(result_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        
        target_rect = QRectF(0, 0, self.target_width, self.target_height)
        self.scene.render(painter, target_rect, scene_rect)
        painter.end()
        
        return result_pixmap


class RogueTraderAvatarMaker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_lang = "ru"  # Русский язык по умолчанию
        self.current_image_path = None
        
        self.init_ui()
        self.retranslate_ui()

    def init_ui(self):
        self.setMinimumSize(1100, 750)
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f4f5f7;
            }
            QLabel {
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
                color: #2c3e50;
            }
            QPushButton {
                background-color: #2b5d8f;
                color: white;
                border-radius: 6px;
                padding: 8px 16px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #3470ab;
            }
            QPushButton:pressed {
                background-color: #20456d;
            }
            QSpinBox {
                padding: 4px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QGraphicsView {
                border: 2px solid #dcdde1;
                border-radius: 8px;
                background-color: #2f3640;
            }
            .CardWidget {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #dcdde1;
            }
        """)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)
        
        central_widget = QWidget()
        scroll_area.setWidget(central_widget)
        self.setCentralWidget(scroll_area)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Верхняя панель управления
        top_card = QWidget()
        top_card.setObjectName("CardWidget")
        top_layout = QHBoxLayout(top_card)
        top_layout.setContentsMargins(15, 15, 15, 15)
        
        self.btn_load = QPushButton()
        self.btn_load.setMinimumHeight(40)
        self.btn_load.clicked.connect(self.load_image)
        top_layout.addWidget(self.btn_load)
        
        self.lbl_status = QLabel()
        self.lbl_status.setStyleSheet("color: #7f8c8d; font-style: italic;")
        top_layout.addWidget(self.lbl_status)
        top_layout.addStretch()
        
        # Кнопки смены языка и справки
        self.btn_lang = QPushButton()
        self.btn_lang.setMinimumHeight(40)
        self.btn_lang.clicked.connect(self.toggle_language)
        top_layout.addWidget(self.btn_lang)
        
        self.btn_about = QPushButton()
        self.btn_about.setMinimumHeight(40)
        self.btn_about.clicked.connect(self.show_about_dialog)
        top_layout.addWidget(self.btn_about)
        
        main_layout.addWidget(top_card)
        
        # Секция рамок
        frames_layout = QHBoxLayout()
        frames_layout.setSpacing(15)
        
        self.v_full, self.view_full, self.btn_save_full = self.create_avatar_box("FullLength.png", 1080, 1480)
        frames_layout.addWidget(self.v_full)
        
        self.v_med, self.view_med, self.btn_save_med = self.create_avatar_box("Medium.png", 448, 600)
        frames_layout.addWidget(self.v_med)
        
        self.v_small, self.view_small, self.btn_save_small = self.create_avatar_box("Small.png", 260, 336)
        frames_layout.addWidget(self.v_small)
        
        main_layout.addLayout(frames_layout)
        
        # Сохраняем ссылки для перевода текста кнопок сохранения
        self.save_buttons = [
            (self.btn_save_full, "FullLength.png"),
            (self.btn_save_med, "Medium.png"),
            (self.btn_save_small, "Small.png")
        ]

    def create_avatar_box(self, filename, default_w, default_h):
        card = QWidget()
        card.setObjectName("CardWidget")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        title_name = filename.split('.')[0]
        title_lbl = QLabel(f"<b>{title_name}</b>")
        title_lbl.setStyleSheet("font-size: 15px; color: #1e272e;")
        layout.addWidget(title_lbl)
        
        size_layout = QHBoxLayout()
        w_spin = QSpinBox()
        w_spin.setRange(50, 5000)
        w_spin.setValue(default_w)
        
        h_spin = QSpinBox()
        h_spin.setRange(50, 5000)
        h_spin.setValue(default_h)
        
        size_layout.addWidget(QLabel("Ш:"))
        size_layout.addWidget(w_spin)
        size_layout.addWidget(QLabel("В:"))
        size_layout.addWidget(h_spin)
        layout.addLayout(size_layout)
        
        view = AvatarCropView(default_w, default_h)
        layout.addWidget(view)
        
        w_spin.valueChanged.connect(lambda val: view.update_aspect_ratio(val, h_spin.value()))
        h_spin.valueChanged.connect(lambda val: view.update_aspect_ratio(w_spin.value(), val))
        
        btn_save = QPushButton()
        btn_save.clicked.connect(lambda: self.save_avatar(view, filename))
        layout.addWidget(btn_save)
        
        return card, view, btn_save

    def toggle_language(self):
        self.current_lang = "en" if self.current_lang == "ru" else "ru"
        self.retranslate_ui()

    def retranslate_ui(self):
        lang = LANG_DATA[self.current_lang]
        
        self.setWindowTitle(lang["window_title"])
        self.btn_load.setText(lang["btn_load"])
        if not self.current_image_path:
            self.lbl_status.setText(lang["status_none"])
        self.btn_lang.setText(lang["btn_lang"])
        self.btn_about.setText(lang["btn_about"])
        
        for btn, filename in self.save_buttons:
            btn.setText(f"{lang['btn_save']} {filename}")

    def show_about_dialog(self):
        lang = LANG_DATA[self.current_lang]
        msg = QMessageBox(self)
        msg.setWindowTitle(lang["about_title"])
        msg.setTextFormat(Qt.RichText)
        msg.setText(lang["about_html"])
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def load_image(self):
        lang = LANG_DATA[self.current_lang]
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выбрать фото", "", "Изображения (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            self.current_image_path = file_path
            short_name = file_path.split('/')[-1].split('\\')[-1]
            self.lbl_status.setText(f"{lang['status_selected']} {short_name}")
            self.lbl_status.setStyleSheet("color: #27ae60; font-weight: bold;")
            
            self.view_full.set_image(QPixmap(file_path))
            self.view_med.set_image(QPixmap(file_path))
            self.view_small.set_image(QPixmap(file_path))

    def save_avatar(self, view_widget, filename):
        lang = LANG_DATA[self.current_lang]
        if not self.current_image_path:
            QMessageBox.warning(self, lang["msg_warning_title"], lang["msg_warning_text"])
            return
            
        dir_path = QFileDialog.getExistingDirectory(self, lang["dir_dialog"])
        if dir_path:
            cropped_pixmap = view_widget.get_cropped_image()
            if cropped_pixmap:
                full_path = f"{dir_path}/{filename}"
                success = cropped_pixmap.save(full_path, "PNG")
                if success:
                    QMessageBox.information(self, lang["success_title"], f"{lang['success_text']}{full_path}")
                else:
                    QMessageBox.critical(self, lang["error_title"], lang["error_text"])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RogueTraderAvatarMaker()
    window.show()
    sys.exit(app.exec_())