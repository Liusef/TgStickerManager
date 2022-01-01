from PySide6.QtGui import QFont, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel

from src.Qt import gui
from src.Qt.ClickWidget import ClickWidget, LitClickWidget
from src.Qt.GridView import GridView
from src.Qt.pages.home import HomePage
from src.Tg.stickers import TgStickerPack, TgSticker


class BaseStickerPage(QWidget):
    def __init__(self, pack: TgStickerPack):
        super().__init__()
        self.setLayout(QVBoxLayout())
        self.layout().setSpacing(0)
        self.panel: QWidget = QWidget()
        self.panel.setLayout(QVBoxLayout())
        self.panel.layout().setSpacing(0)
        self.panel.setStyleSheet("background-color: #24282c")
        self.grid: GridView = GridView(5, cell_width=130, cell_height=130, allow_move=False)
        self.grid.setStyleSheet('border: none')

        # Stuff for the info panel

        thumb = QLabel()
        thumb.setFixedSize(84, 84)
        thumb.setPixmap(gui.get_pixmap_from_file(pack.get_thumb_path()))
        thumb.setScaledContents(True)

        txt_info = QWidget()
        txt_info.setLayout(QVBoxLayout())
        txt_info.layout().addWidget(gui.basic_label(pack.name, gui.generate_font(20, QFont.Bold), Qt.AlignLeft))
        txt_info.layout().addWidget(gui.basic_label(pack.sn, gui.generate_font(12), Qt.AlignLeft))

        info = QWidget()
        info.setLayout(QHBoxLayout())
        info.layout().setAlignment(Qt.AlignTop)
        info.layout().addWidget(gui.nest_widget(thumb))
        info.layout().addWidget(txt_info)

        home = LitClickWidget()
        home.setLayout(QVBoxLayout())
        home.layout().addWidget(gui.basic_label("Home", gui.generate_font(10)))
        home.setFixedSize(80, 80)
        home.setContentsMargins(0, 0, 0, 0)
        home.clicked.connect(lambda: self.parentWidget().setCentralWidget(HomePage()))
        nhome = gui.nest_widget(home)

        top = QWidget()
        top.setLayout(QHBoxLayout())
        top.layout().addWidget(info)
        top.layout().addStretch()
        top.layout().addWidget(nhome)

        # Stuff for the stickers list

        gv_nest = gui.nest_widget(self.grid)
        gv_nest.setMinimumWidth(self.grid.max_cols * self.grid.cell_width)
        self.grid.set_contents([CellWidget(q) for q in pack.stickers])

        gv_nest.setStyleSheet("background-color: #24282c")

        bot = QWidget()
        bot.setLayout(QHBoxLayout())
        bot.layout().addWidget(gv_nest)
        bot.layout().addStretch()
        bot.layout().addWidget(self.panel)
        bot.layout().addStretch()

        self.layout().addWidget(gui.nest_widget(top, Qt.AlignLeft))
        self.layout().addWidget(bot)

    def add_button(self, button: QWidget):
        self.panel.layout().addWidget(button)


class CellWidget(ClickWidget):
    def __init__(self, sticker: TgSticker):
        super().__init__()
        self.clicked.connect(lambda: print(sticker.parent_sn))  # For Testing only
        img = gui.get_pixmap_from_file(sticker.get_file_path())
        label = QLabel()
        label.setScaledContents(True)
        label.setFixedSize(80, 80)
        label.setContentsMargins(0, 0, 0, 0)
        label.setPixmap(img)
        nest_label = gui.nest_widget(label)

        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignCenter)
        self.layout().addWidget(nest_label)

        text = gui.basic_label(sticker.emojis, alignment=Qt.AlignCenter)
        text.setContentsMargins(0, 0, 0, 0)

        self.layout().addWidget(text)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(2)

        self.setStyleSheet("background-color: none")

