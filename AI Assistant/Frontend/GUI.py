from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QStackedWidget, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QIcon, QMovie, QColor, QFont, QPixmap, QTextBlockFormat, QTextCursor, QTextCharFormat
from PyQt5.QtCore import QSize, QTimer, Qt
from dotenv import dotenv_values
import sys
import os

env = dotenv_values(".env")
AssistantName = env.get("AssistantName", "Aurora")
current_dir = os.getcwd()
old_chat_message = "*"
TempDirPath = current_dir + "/Frontend/Files"
GraphicsDirPath = current_dir + "/Frontend/Graphics"

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)

def QueryModifier(query):
    new_query = query.lower().strip()
    if not new_query:
        return ""

    query_words = new_query.split()
    if not query_words:
        return ""

    question_words = [
        "how", "what", "where", "when", "why", "which", "whose", "whom",
        "can you", "what's", "where's", "how's"
    ]

    if any(word + " " in new_query for word in question_words):
        if query_words[-1] in ["!", "?", "."]:
            new_query = new_query[:-1]
        else:
            new_query += "?"
    else:
        if query_words[-1] in ["!", "?", "."]:
            new_query = new_query[:-1]
        else:
            new_query += "."

    return new_query.capitalize()


def SetMicrophoneStatus(Command):
    with open(rf'{TempDirPath}/Mic.data', 'w', encoding='utf-8') as file:
        file.write(Command)

def GetMicrophoneStatus():
    with open(rf'{TempDirPath}/Mic.data', 'r', encoding='utf-8') as file:
        return file.read()

def SetAssistantStatus(Status):
    with open(rf'{TempDirPath}/Status.data', 'w', encoding='utf-8') as file:
        file.write(Status)

def GetAssistantStatus():
    with open(rf'{TempDirPath}/Status.data', 'r', encoding='utf-8') as file:
        return file.read()

def MicButtonInitiated():
    SetMicrophoneStatus("False")

def MicButtonClosed():
    SetMicrophoneStatus("True")

def GraphicsDirectoryPath(Filename):
    return rf'{GraphicsDirPath}/{Filename}'

def TempDirectoryPath(Filename):
    return rf'{TempDirPath}/{Filename}'

def ShowToTextScreen(Text):
    with open(rf'{TempDirPath}/Responses.data', 'w', encoding='utf-8') as file:
        file.write(Text)

class ChatSection(QWidget):
    def __init__(self):
        super(ChatSection, self).__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 40, 40, 100)
        layout.setSpacing(10)

        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
        self.chat_text_edit.setStyleSheet("background-color: black; color: white;")
        font = QFont()
        font.setPointSize(13)
        self.chat_text_edit.setFont(font)

        layout.addWidget(self.chat_text_edit)

        self.gif_label = QLabel()
        self.gif_label.setStyleSheet("border: none;")
        movie = QMovie(GraphicsDirectoryPath("Jarvis.gif"))
        movie.setScaledSize(QSize(300, 300))  # Changed GIF size to 400x400
        self.gif_label.setAlignment(Qt.AlignCenter)
        self.gif_label.setMovie(movie)
        movie.start()

        layout.addWidget(self.gif_label)

        self.label = QLabel("...")
        self.label.setStyleSheet("color: white; font-size:16px; margin-right: 195px; border: none; margin-top:-30px;")
        self.label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.label)

        self.setLayout(layout)
        self.setStyleSheet("background-color: black;")

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadMessages)
        self.timer.timeout.connect(self.SpeechRecText)
        self.timer.start(500)

    def loadMessages(self):
        global old_chat_message
        with open(TempDirectoryPath('Responses.data'), "r", encoding='utf-8') as file:
            messages = file.read()
        if not messages or len(messages) <= 1 or old_chat_message == messages:
            return
        self.addMessage(message=messages, color='White')
        old_chat_message = messages

    def SpeechRecText(self):
        with open(TempDirectoryPath('Status.data'), "r", encoding='utf-8') as file:
            messages = file.read()
        self.label.setText(messages)

    def addMessage(self, message, color):
        cursor = self.chat_text_edit.textCursor()
        blockFormat = QTextBlockFormat()
        blockFormat.setTopMargin(10)
        cursor.setBlockFormat(blockFormat)
        charFormat = QTextCharFormat()
        charFormat.setForeground(QColor(color))
        cursor.insertText(message + "\n", charFormat)
        self.chat_text_edit.setTextCursor(cursor)

class InitialScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        screen_rect = QApplication.primaryScreen().geometry()
        screen_width, screen_height = screen_rect.width(), screen_rect.height()

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)

        gif_container = QWidget()
        gif_container.setStyleSheet("background-color: transparent;")
        gif_layout = QVBoxLayout(gif_container)
        gif_layout.setAlignment(Qt.AlignCenter)
        gif_label = QLabel()
        movie = QMovie(GraphicsDirectoryPath('Jarvis.gif'))
        gif_label.setMovie(movie)
        movie.setScaledSize(QSize(600, 600))  # Changed GIF size to 400x400
        gif_label.setAlignment(Qt.AlignCenter)
        movie.start()
        gif_layout.addWidget(gif_label)

        self.icon_label = QLabel()
        self.icon_label.setStyleSheet("background-color: transparent; margin-top: -100px;")
        self.load_icon(GraphicsDirectoryPath('Mic_on.png'))
        self.icon_label.setFixedSize(100, 100)
        self.icon_label.setAlignment(Qt.AlignCenter)  # Ensures it's in the center
        self.icon_label.mousePressEvent = self.toggle_icon
        self.toggled = True

        self.label = QLabel("*")
        self.label.setStyleSheet("color: white; font-size:16px; margin-bottom:0;")
        self.label.setAlignment(Qt.AlignHCenter)

        content_layout.addWidget(gif_container)
        content_layout.addWidget(self.label)
        content_layout.addWidget(self.icon_label)

        self.setLayout(content_layout)
        self.setFixedSize(screen_width, screen_height)
        self.setStyleSheet("background-color: black;")

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.SpeechRecText)
        self.timer.start(500)

    def load_icon(self, path):
        pixmap = QPixmap(path).scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.icon_label.setPixmap(pixmap)

    def toggle_icon(self, event=None):
        if self.toggled:
            self.load_icon(GraphicsDirectoryPath('Mic_of.png'))
            MicButtonClosed()
        else:
            self.load_icon(GraphicsDirectoryPath('Mic_on.png'))
            MicButtonInitiated()
        self.toggled = not self.toggled

    def SpeechRecText(self):
        with open(TempDirectoryPath('Status.data'), "r", encoding='utf-8') as file:
            messages = file.read()
        self.label.setText(messages)

class MessageScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        screen_rect = QApplication.primaryScreen().geometry()
        self.setFixedSize(screen_rect.width(), screen_rect.height())
        layout = QVBoxLayout()
        layout.addWidget(ChatSection())
        self.setLayout(layout)
        self.setStyleSheet("background-color: black;")

class CustomTopBar(QWidget):
    def __init__(self, parent, stacked_widget):
        super().__init__(parent)
        self.stacked_widget = stacked_widget
        self.initUI()

    def initUI(self):
        self.setFixedHeight(50)
        layout = QHBoxLayout()

        title_label = QLabel("Aurora")
        title_label.setStyleSheet("color: white; font-size:18px; background-color:black;")

        home_button = QPushButton("Home")
        home_button.setIcon(QIcon(GraphicsDirectoryPath('Home.png')))
        home_button.setStyleSheet("background-color:black; color:white;")
        home_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))

        message_button = QPushButton("Chat")
        message_button.setIcon(QIcon(GraphicsDirectoryPath('Chats.png')))
        message_button.setStyleSheet("background-color:black; color:white;")
        message_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))

        minimize_button = QPushButton()
        minimize_button.setIcon(QIcon(GraphicsDirectoryPath('Minimize2.png')))
        minimize_button.clicked.connect(self.parent().showMinimized)
        minimize_button.setStyleSheet("background-color:black;")

        self.maximize_button = QPushButton()
        self.maximize_icon = QIcon(GraphicsDirectoryPath('Maximize.png'))
        self.restore_icon = QIcon(GraphicsDirectoryPath('Minimize.png'))
        self.maximize_button.setIcon(self.maximize_icon)
        self.maximize_button.clicked.connect(self.toggleMaximize)
        self.maximize_button.setStyleSheet("background-color:black;")

        close_button = QPushButton()
        close_button.setIcon(QIcon(GraphicsDirectoryPath('Close.png')))
        close_button.clicked.connect(self.parent().close)
        close_button.setStyleSheet("background-color:black;")

        layout.addWidget(title_label)
        layout.addWidget(home_button)
        layout.addWidget(message_button)
        layout.addStretch()
        layout.addWidget(minimize_button)
        layout.addWidget(self.maximize_button)
        layout.addWidget(close_button)

        self.setLayout(layout)
        self.setStyleSheet("background-color: black;")

    def toggleMaximize(self):
        if self.parent().isMaximized():
            self.parent().showNormal()
            self.maximize_button.setIcon(self.maximize_icon)
        else:
            self.parent().showMaximized()
            self.maximize_button.setIcon(self.restore_icon)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setupUi()

    def setupUi(self):
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(0, 0, screen.width(), screen.height())

        self.stacked_widget = QStackedWidget()
        self.initial_screen = InitialScreen()
        self.message_screen = MessageScreen()

        self.stacked_widget.addWidget(self.initial_screen)
        self.stacked_widget.addWidget(self.message_screen)

        self.top_bar = CustomTopBar(self, self.stacked_widget)

        self.setCentralWidget(self.stacked_widget)
        self.setMenuWidget(self.top_bar)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F11:
            if self.menuWidget().isVisible():
                self.menuWidget().hide()
            else:
                self.menuWidget().show()

def GraphicalUserInterface():
    app = QApplication(sys.argv)
    window = MainWindow()
    app.setStyleSheet("""
    QWidget {
        background-color: black;
        color: white;
    }
    QPushButton {
        background-color: black;
        color: white;
        border: none;
    }
    QLabel {
        background-color: black;
        color: white;
    }
    QTextEdit {
        background-color: black;
        color: white;
    }
""")
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    GraphicalUserInterface()
