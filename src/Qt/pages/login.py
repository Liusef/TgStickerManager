from src import assets
from PySide6.QtWidgets import QWidget, QStackedWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PySide6.QtGui import QPixmap, QIcon, QFont
from PySide6.QtCore import Qt
import phonenumbers

from src.Qt.gui import generate_font, nest_widget, get_pixmap


class TgLoginWidget(QWidget):
    class TgLoginInputWidget(QStackedWidget):
        def __init__(self):
            super().__init__()
            self.insertWidget(0, self.page1())

        def page1(self) -> QWidget:
            layout = QVBoxLayout()
            widget = QWidget()
            widget.setLayout(layout)

            title = QLabel()
            title.setText("Sign in to Telegram")
            title.setFont(generate_font(title, 30, QFont.Bold))
            title.setAlignment(Qt.AlignHCenter)
            layout.addWidget(title)

            desc = QLabel()
            desc.setText("Please enter your phone number starting with the country code.\nNo extra characters.")
            desc.setFont(generate_font(desc, 14, QFont.Medium))
            desc.setAlignment(Qt.AlignHCenter)
            layout.addWidget(desc)

            layout.addSpacing(16)

            phone = QLineEdit()
            phone.setFont(generate_font(phone, 14, QFont.DemiBold))
            phone.setAlignment(Qt.AlignHCenter)
            phone.setMaximumWidth(300)
            phone.returnPressed.connect(lambda: self.next_page(phone.text()))
            layout.addWidget(nest_widget(phone))

            cont = QPushButton()
            cont.setText("Next")
            cont.setFont(generate_font(cont, 12))
            cont.setFixedWidth(150)
            cont.setEnabled(False)
            phone.textChanged.connect(lambda: cont.setEnabled(self.is_valid_phone(phone.text())))
            cont.clicked.connect(lambda: self.next_page(phone.text()))
            layout.addWidget(nest_widget(cont))

            return widget

        def page2(self, phone: str) -> QWidget:
            layout = QVBoxLayout()
            widget = QWidget()
            widget.setLayout(layout)

            title = QLabel()
            title.setText(phone)
            title.setFont(generate_font(title, 30, QFont.Bold))
            title.setAlignment(Qt.AlignHCenter)
            layout.addWidget(title)

            desc = QLabel()
            desc.setText("We've sent the code to the Telegram app on your\nother device or SMS.")
            desc.setFont(generate_font(desc, 14, QFont.Medium))
            desc.setAlignment(Qt.AlignHCenter)
            layout.addWidget(desc)

            layout.addStretch()

            return widget

        def next_page(self, phone: str):
            while self.count() > 1: self.removeWidget(self.widget(1))
            phone = phonenumbers.format_number(phonenumbers.parse('+' + phone),
                                               phonenumbers.PhoneNumberFormat.INTERNATIONAL)
            self.insertWidget(1, self.page2(phone))
            self.setCurrentIndex(1)

        def is_valid_phone(self, phone: str) -> bool:
            try: return phonenumbers.is_valid_number(phonenumbers.parse('+' + phone))
            except phonenumbers.phonenumberutil.NumberParseException as e:
                print(e)
                return False


    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignHCenter)
        self.setLayout(layout)

        layout.addStretch()

        logo: QLabel = QLabel()
        logo.setPixmap(get_pixmap(assets, "app.png"))
        logo.setScaledContents(True)
        logo.setFixedSize(200, 200)
        logo_w: QWidget = QWidget()
        logo_w.setLayout(QVBoxLayout())
        logo_w.layout().addWidget(logo)
        logo_w.layout().setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_w)

        layout.addWidget(self.TgLoginInputWidget())

        layout.addStretch()