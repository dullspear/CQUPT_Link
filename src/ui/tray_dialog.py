from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QVBoxLayout
from qfluentwidgets import CheckBox

from src.core.user_settings_manager import user_settings_manager


class TrayDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("关闭提示")
        self.setModal(True)
        self.resize(320, 120)
        layout = QVBoxLayout(self)
        label = QLabel("是否最小化到托盘？", self)
        layout.addWidget(label)

        # 复选框语义为:下次不再提醒 (True 表示不再提醒)
        self.checkbox = CheckBox("下次不再提醒", self)
        # 从设置初始化:settings 中记录的是是否显示提醒 (show_reminder)
        try:
            show_reminder = user_settings_manager.get_show_close_to_tray_reminder()
            # checkbox 表示"不再提醒",所以取反
            self.checkbox.setChecked(not bool(show_reminder))
        except Exception:
            # 回退为未勾选(默认显示提醒)
            self.checkbox.setChecked(False)
        layout.addWidget(self.checkbox)

        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Yes | QDialogButtonBox.StandardButton.No,
            self,
        )
        layout.addWidget(self.buttonBox)

        # 将按钮连接到 accept/reject
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        # 将“是”按钮设为默认（方便回车键确认）
        yes_btn = self.buttonBox.button(QDialogButtonBox.StandardButton.Yes)
        if yes_btn is not None:
            yes_btn.setDefault(True)
            yes_btn.setAutoDefault(True)

    def isChecked(self):
        return self.checkbox.isChecked()

    def setChecked(self, checked: bool):
        """外部可用来设置复选框状态（True 表示不再提醒）"""
        self.checkbox.setChecked(bool(checked))


if __name__ == "__main__":
    import sys

    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    dialog = TrayDialog()
    if dialog.exec() == QDialog.DialogCode.Accepted:
        print("Accepted")
    else:
        print("Rejected")
    print("Checkbox checked:", dialog.isChecked())
    sys.exit(0)
