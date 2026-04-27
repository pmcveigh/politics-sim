from __future__ import annotations

from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout


class Card(QFrame):
    def __init__(self, title: str, body: str = "") -> None:
        super().__init__()
        self.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(self)
        self.title = QLabel(f"<b>{title}</b>")
        self.body = QLabel(body)
        self.body.setWordWrap(True)
        layout.addWidget(self.title)
        layout.addWidget(self.body)

    def update_body(self, text: str) -> None:
        self.body.setText(text)
