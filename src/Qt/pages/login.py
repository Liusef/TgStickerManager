import asyncio

from logging import debug, info, warning, error, critical
from PySide6.QtWidgets import QWidget, QStackedWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout
from PySide6.QtGui import QPixmap, QIcon, QFont
from PySide6.QtCore import Qt
import phonenumbers
from qasync import asyncSlot

import src
from src import assets, gvars, utils
from src.Qt.gui import generate_font, nest_widget, get_pixmap, Loading
from src.Qt.pages.home import HomePage
from src.Tg import auth


class TgLoginWidget(QWidget):
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

        layout.addWidget(TgLoginInputWidget())

        layout.addStretch()


class TgLoginInputWidget(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.insertWidget(0, self.page0())
        self.pn: str = ""
        self.code: str = ""

    def next(self, widget: QWidget):
        self.addWidget(widget)
        self.setCurrentIndex(self.indexOf(widget))

    def prev(self):
        widget = self.widget(self.currentIndex())
        self.setCurrentIndex(self.currentIndex() - 1)
        self.removeWidget(widget)

    def page0(self) -> QWidget:
        layout = QVBoxLayout()
        widget = QWidget()
        widget.setLayout(layout)

        title = QLabel()
        title.setText("Welcome!")
        title.setFont(generate_font(title, 30, QFont.Bold))
        title.setAlignment(Qt.AlignHCenter)
        layout.addWidget(title)

        desc = QLabel()
        desc.setText('This app needs to connect to Telegram\'s servers to continue.\nClick below to connect.')
        desc.setFont(generate_font(desc, 14, QFont.Medium))
        desc.setAlignment(Qt.AlignHCenter)
        layout.addWidget(desc)

        layout.addSpacing(16)

        connect = QPushButton()
        connect.setText("Connect")
        connect.setFont(generate_font(connect, 12))
        connect.setFixedWidth(150)
        layout.addWidget(nest_widget(connect))

        @asyncSlot()
        async def connect_clicked():
            loading = Loading()
            layout.addWidget(loading)
            if not gvars.client.is_connected():
                info('Connecting to Telegram')
                debug('creating tgclient.connect coroutine and adding to the event loop')
                await gvars.client.connect()
                gvars.state = auth.SignInState.CONNECTED_NSI
                info('Connected!')
            layout.removeWidget(loading)

            if await gvars.client.is_user_authorized():
                info("You're signed in and ready to go!")
                self.parentWidget().parentWidget().setCentralWidget(HomePage("Welcome Back!"))
            else:
                self.next(self.page1())

        connect.clicked.connect(connect_clicked)

        return widget

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
        layout.addWidget(nest_widget(cont))

        def phone_textchanged():
            self.pn = phone.text()
            cont.setEnabled(utils.is_valid_phone(self.pn))

        phone.textChanged.connect(phone_textchanged)

        @asyncSlot()
        async def cont_clicked():
            if not cont.isEnabled(): return
            loading = Loading()
            layout.addWidget(loading)
            await self.check_connected()

            info(f'Sending sign in request to telegram with phone: {self.pn}')
            debug('creating tgclient.sign_in coroutine and adding to the event loop')
            await auth.signin_handler_phone(self.pn)
            layout.removeWidget(loading)

            if gvars.state == auth.SignInState.AWAITING_CODE:
                info('Sign-in code has been sent if another one hasn\'t been sent recently')
                self.next(self.page2())

        cont.clicked.connect(cont_clicked)
        phone.returnPressed.connect(cont_clicked)

        return widget

    def page2(self) -> QWidget:
        layout = QVBoxLayout()
        widget = QWidget()
        widget.setLayout(layout)

        title = QLabel()
        title.setText(utils.format_phone('+' + self.pn))
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
        broke.layout().addWidget(nest_widget(ncode))

        wrongphone = QPushButton()
        wrongphone.setFont(bfont)
        wrongphone.setText("Wrong phone?")
        wrongphone.setFixedWidth(150)
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
        layout.addWidget(nest_widget(cont))

        def ncode_clicked():
            info('This method doesn\'t actually do anything oops')

        ncode.clicked.connect(ncode_clicked)

        def wrongphone_clicked():
            gvars.state = auth.SignInState.CONNECTED_NSI
            self.prev()

        wrongphone.clicked.connect(wrongphone_clicked)

        def phone_textchanged():
            self.code = code.text()
            cont.setEnabled(len(self.code) == 5)

        code.textEdited.connect(phone_textchanged)

        @asyncSlot()
        async def cont_clicked():
            if not cont.isEnabled(): return
            loading = Loading()
            layout.addWidget(loading)
            await self.check_connected()

            info('Sending sign in request to telegram with Phone and Code')
            debug('creating tgclient.sign_in coroutine and adding to the event loop')
            await auth.signin_handler_code(self.pn, self.code)

            if gvars.state == auth.SignInState.SIGNED_IN:
                info('Signed in!')
                self.parentWidget().parentWidget().setCentralWidget(HomePage())

        cont.clicked.connect(cont_clicked)
        code.returnPressed.connect(cont_clicked)

        return widget

    def urloggedinyay_temp(self) -> QWidget:
        widget = QWidget()
        widget.setLayout(QVBoxLayout())
        label = QLabel()
        label.setText(f"Yay ur signed in!!!")
        label.setAlignment(Qt.AlignHCenter)
        widget.layout().addWidget(label)
        widget.layout().addStretch()
        return widget

    # TODO the src.tg.auth file already has a method to ensure connection, maybe just integrate that into the
    # TODO handlers instead of having 2 methods in different files that effectively do the same thing
    async def check_connected(self):
        if not gvars.client.is_connected():
            info('Client is not connected, attempting to connect')
            debug('Creating tgclient.connect coroutine and adding to the event loop')
            await gvars.client.connect()
            gvars.state = auth.SignInState.CONNECTED_NSI
            info('Connected!')
