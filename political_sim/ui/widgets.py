from __future__ import annotations

from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QProgressBar, QVBoxLayout, QWidget


class Card(QFrame):
    def __init__(self, title: str, body: str = "", button_label: str | None = None, on_open=None) -> None:
        super().__init__()
        self.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(self)
        self.title = QLabel(f"<b>{title}</b>")
        self.body = QLabel(body)
        self.body.setWordWrap(True)
        layout.addWidget(self.title)
        layout.addWidget(self.body)
        if button_label:
            self.btn = QPushButton(button_label)
            if on_open:
                self.btn.clicked.connect(on_open)
            layout.addWidget(self.btn)

    def update_body(self, text: str) -> None:
        self.body.setText(text)


class SummaryCard(Card):
    pass


class MetricBar(QWidget):
    def __init__(self, label: str) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        self.label = QLabel(label)
        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        layout.addWidget(self.label)
        layout.addWidget(self.bar)

    def set_value(self, value: int) -> None:
        self.bar.setValue(value)


class AgendaItemCard(Card):
    pass


class StoryArcCard(Card):
    pass


class AlertCard(Card):
    pass


class RelationshipMiniCard(Card):
    pass


class DecisionButtonCard(Card):
    pass


class ConsequenceCard(Card):
    pass
