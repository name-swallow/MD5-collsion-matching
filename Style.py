import sys, os, json
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QTextEdit, QPushButton, QComboBox,
                             QGroupBox, QProgressBar, QFrame,
                             QGraphicsDropShadowEffect, QMessageBox, QFileDialog, QSplitter)
from PyQt5.QtCore import Qt, QEasingCurve
from PyQt5.QtGui import QFont, QColor
from Function_pro import StyleManager, Function

class Tog:
    def __init__(self, splitter, sidebar_index, original_width, toggle_button):
        self.splitter = splitter
        self.sidebar_index = sidebar_index
        self.original_width = original_width
        self.toggle_button = toggle_button
        self.is_expanded = True

    def toggle(self):
        if self.is_expanded:
            sizes = [self.splitter.width(), 0]
            self.splitter.setSizes(sizes)
            self.is_expanded = False
            self.toggle_button.setText("▶")
        else:
            total_width = self.splitter.width()
            main_width = total_width - self.original_width
            sizes = [main_width, self.original_width]
            self.splitter.setSizes(sizes)
            self.is_expanded = True
            self.toggle_button.setText("◀")


# 主应用程序类
class MD5CrackerPro(QWidget):
    def __init__(self):
        super().__init__()
        # 设计系统配置
        self.design_config = {
            "colors": {
                "primary": "#7C4DFF",
                "secondary": "#00BFA5",
                "background": "#1A1C24",
                "surface": "#272A36",
                "error": "#FF5252",
                "text": "#FFFFFF"
            },
            "spacing": {
                "xl": 24,
                "lg": 16,
                "md": 12,
                "sm": 8
            },
            "animation": {
                "duration": 400,
                "easing": QEasingCurve.OutExpo
            }
        }
        self.current_files = {}
        self.style_manager = StyleManager(self.design_config)
        self.function = Function(self)
        self.tog = Tog(None, 1, 330, None)  # 用占位符初始化
        self.init_ui()
        self.setup_style()
        self.setup_connections()
        self.config_file = os.path.join(os.getcwd(), "md5_cracker_config.json")
        self.load_settings()

    def load_settings(self):
        """加载配置文件中的字典设置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    valid_files = {}
                    for display_name, path in data.get('dictionaries', {}).items():
                        if os.path.exists(path):
                            valid_files[display_name] = path
                            self.dict_combo.addItem(display_name)
                    self.current_files = valid_files
                    if valid_files:
                        self.dict_combo.setCurrentIndex(0)
        except json.JSONDecodeError:
            QMessageBox.warning(self, "配置错误", "配置文件格式错误，将使用默认配置")
        except Exception as e:
            QMessageBox.warning(self, "配置错误", f"加载配置失败: {str(e)}")

    def save_settings(self):
        """保存当前字典设置到配置文件"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump({'dictionaries': self.current_files}, f, indent=2)
        except PermissionError:
            QMessageBox.warning(self, "权限错误", "无权限写入配置文件")
        except Exception as e:
            QMessageBox.warning(self, "保存错误", f"保存配置失败: {str(e)}")

    def add_dictionary_file(self):
        """添加字典文件"""
        path, _ = QFileDialog.getOpenFileName(
            self, "选择字典文件", "", "文本文件 (*.txt);;所有文件 (*)")
        if path:
            display_name = f"{os.path.basename(path)} [{os.path.dirname(path)}]"
            if display_name not in self.current_files:
                self.current_files[display_name] = path
                self.dict_combo.addItem(display_name)
                self.dict_combo.setCurrentIndex(self.dict_combo.count() - 1)
                self.save_settings()
            else:
                QMessageBox.information(self, "提示", "该字典已存在列表中")

    def remove_dictionary(self):
        """移除选中的字典"""
        current = self.dict_combo.currentIndex()
        if current >= 0:
            display_name = self.dict_combo.currentText()
            confirm = QMessageBox.question(
                self, "确认移除",
                f"确定要从列表移除字典吗？\n{display_name}",
                QMessageBox.Yes | QMessageBox.No
            )
            if confirm == QMessageBox.Yes:
                del self.current_files[display_name]
                self.dict_combo.removeItem(current)
                self.save_settings()

    def init_ui(self):
        """初始化用户界面"""
        self.splitter = QSplitter(Qt.Horizontal)
        self.main_panel = self.create_main_panel()
        self.sidebar = self.create_sidebar()
        self.splitter.addWidget(self.main_panel)
        self.splitter.addWidget(self.sidebar)
        self.splitter.setStretchFactor(0, 7)  # 主面板占70%
        self.splitter.setStretchFactor(1, 3)  # 侧边栏占30%
        self.splitter.setCollapsible(1, True)  # 侧边栏可折叠
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.splitter)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.apply_shadow_effect()
        # 配置 Tog 实例
        self.tog.splitter = self.splitter
        self.tog.toggle_button = self.sidebar_toggle

    def create_main_panel(self):
        """创建主面板"""
        panel = QWidget()
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(
            self.design_config["spacing"]["xl"],
            self.design_config["spacing"]["xl"],
            self.design_config["spacing"]["xl"],
            self.design_config["spacing"]["xl"]
        )
        # 标题行
        title_layout = QHBoxLayout()
        title = QLabel("MD5破解工作站")
        title.setObjectName("mainTitle")
        title_layout.addWidget(title)
        self.sidebar_toggle = self.create_icon_button("◀", self.tog.toggle)  # 初始展开状态
        title_layout.addStretch()
        title_layout.addWidget(self.sidebar_toggle)
        panel_layout.addLayout(title_layout)
        # 核心内容
        content_layout = QHBoxLayout()
        content_layout.addLayout(self.create_input_section(), 1)
        content_layout.addLayout(self.create_output_section(), 2)
        panel_layout.addLayout(content_layout)
        return panel

    def create_input_section(self):
        """创建输入区域"""
        layout = QVBoxLayout()
        layout.setSpacing(self.design_config["spacing"]["lg"])
        layout.addWidget(self.create_input_group(
            "目标哈希值",
            self.create_hash_input(),
            "输入32位MD5哈希值"
        ))
        layout.addWidget(self.create_input_group(
            "密码字典管理",
            self.create_dictionary_controls(),
            "管理密码字典内容"
        ))
        return layout

    def create_output_section(self):
        """创建输出区域"""
        layout = QVBoxLayout()
        layout.setSpacing(self.design_config["spacing"]["lg"])
        layout.addWidget(self.create_output_group(
            "破解结果",
            self.create_result_display()
        ))
        layout.addWidget(self.create_output_group(
            "破解进度",
            self.create_progress_system()
        ))
        layout.addLayout(self.create_control_buttons())
        return layout

    def create_input_group(self, title, widget, tooltip):
        """创建输入分组"""
        group = QGroupBox(title)
        group.setToolTip(tooltip)
        layout = QVBoxLayout(group)
        layout.addWidget(widget)
        return group

    def create_output_group(self, title, widget):
        """创建输出分组"""
        group = QGroupBox(title)
        layout = QVBoxLayout(group)
        layout.addWidget(widget)
        return group

    def create_hash_input(self):
        """创建哈希输入框"""
        self.hash_input = QTextEdit()
        self.hash_input.setObjectName("hashInput")
        self.hash_input.setPlaceholderText("请输入32位的md5值")
        self.hash_input.setMaximumHeight(100)
        return self.hash_input

    def create_dictionary_controls(self):
        """创建字典管理控件"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(self.design_config["spacing"]["md"])
        # 字典选择行
        combo_layout = QHBoxLayout()
        self.dict_combo = QComboBox()
        self.dict_combo.setObjectName("dict_Combo")
        self.dict_combo.setMinimumWidth(175)
        combo_layout.addWidget(self.dict_combo, 3)
        combo_layout.addWidget(self.create_icon_button("➕", self.add_dictionary_file))
        combo_layout.addWidget(self.create_icon_button("➖", self.remove_dictionary))
        layout.addLayout(combo_layout)
        # 字典编辑器
        self.dict_editor = QTextEdit()
        self.dict_editor.setPlaceholderText("每行输入一个密码...")
        layout.addWidget(self.dict_editor)
        # 保存按钮
        self.save_btn = self.create_icon_button("💾 追加字典", self.function.on_save_click)
        self.save_btn.setFixedSize(50, 50)
        layout.addWidget(self.save_btn)
        return container

    def create_progress_system(self):
        """创建进度系统"""
        container = QWidget()
        layout = QVBoxLayout(container)
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("progressBar")
        layout.addWidget(self.progress_bar)
        status_layout = QHBoxLayout()
        self.progress_label = QLabel("0%")
        self.time_remaining = QLabel("预计剩余时间：--:--:--")
        status_layout.addWidget(self.progress_label)
        status_layout.addStretch()
        status_layout.addWidget(self.time_remaining)
        layout.addLayout(status_layout)
        return container

    def create_result_display(self):
        """创建结果显示框"""
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        self.result_display.setStyleSheet("background: #1E1E1E;")
        return self.result_display

    def create_control_buttons(self):
        """创建控制按钮"""
        layout = QHBoxLayout()
        layout.setSpacing(self.design_config["spacing"]["md"])
        self.start_btn = QPushButton("🚀 开始破解")
        self.stop_btn = QPushButton("⏹ 停止破解")
        self.clear_btn = QPushButton("🧹 清空全部")
        layout.addWidget(self.start_btn)
        layout.addWidget(self.stop_btn)
        layout.addWidget(self.clear_btn)
        return layout

    def create_sidebar(self):
        """创建侧边栏"""
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setMinimumSize(330, 720)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(
            self.design_config["spacing"]["xl"],
            self.design_config["spacing"]["xl"],
            self.design_config["spacing"]["md"],
            self.design_config["spacing"]["xl"]
        )
        # 侧边栏头部
        header = QHBoxLayout()
        header.addWidget(QLabel("高级工具"))
        layout.addLayout(header)
        # 工具
        layout.addWidget(self.create_tool_panel("MD5生成器", self.create_md5_generator()))
        layout.addWidget(self.create_tool_panel("正则匹配", self.create_regex_tool()))
        return sidebar

    def create_tool_panel(self, title, widget):
        """创建工具面板"""
        group = QGroupBox(title)
        layout = QVBoxLayout(group)
        layout.addWidget(widget)
        return group

    def create_md5_generator(self):
        """创建MD5生成器"""
        container = QWidget()
        layout = QVBoxLayout(container)
        self.md5_input = QTextEdit()
        self.md5_input.setPlaceholderText("输入要加密的字符串...")
        self.md5_output = QTextEdit()
        self.md5_output.setReadOnly(True)
        generate_btn = QPushButton("生成MD5")
        generate_btn.clicked.connect(lambda: self.function.generate_md5())
        layout.addWidget(self.md5_input)
        layout.addWidget(generate_btn)
        layout.addWidget(self.md5_output)
        return container

    def create_regex_tool(self):
        """创建正则匹配工具"""
        container = QWidget()
        layout = QVBoxLayout(container)
        self.regex_input = QTextEdit()
        self.regex_input.setPlaceholderText("输入正则表达式...")
        self.regex_output = QTextEdit()
        self.regex_output.setReadOnly(True)
        test_btn = QPushButton("测试匹配")
        test_btn.clicked.connect(lambda: self.function.test_regex())
        layout.addWidget(self.regex_input)
        layout.addWidget(test_btn)
        layout.addWidget(self.regex_output)
        return container

    def setup_style(self):
        """设置全局样式"""
        style = self.style_manager.get_style_sheet()
        self.setStyleSheet(style)

    def setup_connections(self):
        """设置按钮事件连接"""
        self.start_btn.clicked.connect(self.function.start_cracking)
        self.stop_btn.clicked.connect(self.function.stop_crack)
        self.clear_btn.clicked.connect(self.function.clear_content)

    def apply_shadow_effect(self):
        """为侧边栏应用阴影效果"""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(6, 6)
        self.sidebar.setGraphicsEffect(shadow)

    def create_icon_button(self, icon, callback):
        """创建图标按钮"""
        btn = QPushButton(icon)
        btn.setFont(QFont("Segoe MDL2 Assets", 12))
        btn.setFixedSize(32, 32)
        if callback:
            btn.clicked.connect(callback)
        return btn


