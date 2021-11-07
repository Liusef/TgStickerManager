import asyncio

from qasync import asyncSlot

import src
from src import assets, gvars
from PySide6.QtWidgets import QWidget, QStackedWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout
from PySide6.QtGui import QPixmap, QIcon, QFont
from PySide6.QtCore import Qt
import phonenumbers

from src.Qt.gui import generate_font, nest_widget, get_pixmap
from src.Tg import auth


class TgLoginWidget(QWidget):
    class TgLoginInputWidget(QStackedWidget):
        def __init__(self):
            super().__init__()
            self.insertWidget(0, self.page1())
            self.pn: str = ""
            self.code: str = ""

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

            layout.addWidget(nest_widget(phone))

            cont = QPushButton()
            cont.setText("Next")
            cont.setFont(generate_font(cont, 12))
            cont.setFixedWidth(150)
            cont.setEnabled(False)

            def is_valid_phone(phone: str) -> bool:
                try:
                    return phonenumbers.is_valid_number(phonenumbers.parse('+' + phone))
                except phonenumbers.phonenumberutil.NumberParseException as e:
                    print(e)
                    return False

            def phone_textchanged():
                self.pn = phone.text()
                cont.setEnabled(is_valid_phone(self.pn))

            phone.textChanged.connect(phone_textchanged)

            cont.clicked.connect(self.next_page_nparams)
            phone.returnPressed.connect(self.next_page_nparams)

            layout.addWidget(nest_widget(cont))

            return widget

        def page2(self, code: str) -> QWidget:
            layout = QVBoxLayout()
            widget = QWidget()
            widget.setLayout(layout)

            title = QLabel()
            title.setText(code)
            title.setFont(generate_font(title, 30, QFont.Bold))
            title.setAlignment(Qt.AlignHCenter)
            layout.addWidget(title)

            desc = QLabel()
            desc.setText("We've sent the code to the Telegram app on your\nother device or SMS.")
            desc.setFont(generate_font(desc, 14, QFont.Medium))
            desc.setAlignment(Qt.AlignHCenter)
            layout.addWidget(desc)

            broke = QWidget()
            broke.setLayout(QHBoxLayout())

            ncode = QPushButton()
            bfont = generate_font(ncode, 12)
            ncode.setFont(bfont)
            ncode.setText("New code?")
            ncode.setFixedWidth(150)
            ncode.clicked.connect(self.get_new_code)
            broke.layout().addWidget(nest_widget(ncode))

            wrongphone = QPushButton()
            wrongphone.setFont(bfont)
            wrongphone.setText("Wrong phone?")
            wrongphone.setFixedWidth(150)
            wrongphone.clicked.connect(lambda: print('this does nothing right now oops'))
            broke.layout().addWidget(nest_widget(wrongphone))
            layout.addWidget(broke)

            code = QLineEdit()
            code.setFont(generate_font(code, 14, QFont.DemiBold))
            code.setAlignment(Qt.AlignHCenter)
            code.setMaximumWidth(300)

            layout.addWidget(nest_widget(code))

            cont = QPushButton()
            cont.setText("Next")
            cont.setFont(generate_font(cont, 12))
            cont.setFixedWidth(150)
            cont.setEnabled(False)
            cont.clicked.connect(self.shit)
            code.returnPressed.connect(self.shit)

            layout.addWidget(nest_widget(cont))

            def phone_textchanged():
                self.code = code.text()
                cont.setEnabled(len(self.code) == 5)

            code.textEdited.connect(phone_textchanged)

            layout.addStretch()

            return widget

        @asyncSlot()
        async def get_new_code(self):
            await auth.signin_handler_request_new_code(self.pn)
            print('new code request')

        @asyncSlot()
        async def shit(self):
            print('sending signin code for auth')
            print(f'phone: {self.pn}\ncode: {self.code}')
            await auth.signin_handler_code(self.pn, self.code)
            urmom = await gvars.client.is_user_authorized()
            print(f'user is authorized: {urmom}')
            if urmom:
                self.insertWidget(2, QWidget())
                self.setCurrentIndex(2)

        @asyncSlot()
        async def next_page_nparams(self):
            print('src.Qt.pages.login.next_page_nparams called, coroutine added to the event loop')
            await self.next_page(self.pn)

        async def next_page(self, phone: str):
            if not gvars.client.is_connected():
                print('tgclient is not connected, connecting...')
                await gvars.client.connect()
                print('tgclient connected!')
                gvars.state = gvars.state.CONNECTED_NSI

            print('creating signin_handler coroutine')
            await auth.signin_handler_phone(phone)
            print('sent sign-in code if one has not been sent and been unused recently')

            while self.count() > 1: self.removeWidget(self.widget(1))
            phone = phonenumbers.format_number(phonenumbers.parse('+' + phone),
                                               phonenumbers.PhoneNumberFormat.INTERNATIONAL)
            self.insertWidget(1, self.page2(phone))
            self.setCurrentIndex(1)

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
