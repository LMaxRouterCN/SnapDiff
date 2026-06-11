import sys
import os
import yaml
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QPushButton, QLineEdit, QTreeWidget, 
                               QTreeWidgetItem, QTextEdit, QLabel, QFileDialog, QMessageBox, QSplitter)
from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtGui import QColor, QFont

from src.scanner import Scanner
from src.storage import Storage
from src.differ import Differ
from src.changelog import ChangelogGenerator
from src.paths import DEFAULT_RULES_PATH

class ScanWorker(QThread):
    finished = Signal(dict, dict, dict)
    error = Signal(str)

    def __init__(self, root_dir, rules_path):
        super().__init__()
        self.root_dir = root_dir
        self.rules_path = rules_path

    def run(self):
        try:
            scanner = Scanner(self.root_dir, self.rules_path)
            storage = Storage(self.root_dir)
            
            old_snapshot = storage.load_snapshot()
            new_snapshot = scanner.scan()
            
            differ = Differ(old_snapshot, new_snapshot)
            diffs = differ.compare()
            
            storage.save_snapshot(new_snapshot)
            
            self.finished.emit(old_snapshot, new_snapshot, diffs)
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SnapDiff - 快照对比引擎")
        self.resize(1200, 800)
        
        self.old_snapshot = {}
        self.new_snapshot = {}
        self.diffs = {}
        
        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # ================= 左侧面板 (垂直分割) =================
        left_splitter = QSplitter(Qt.Vertical)
        
        # -- 左侧上半部分 (目录与树状图) --
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        top_layout.setContentsMargins(0, 0, 5, 0)
        top_layout.setSpacing(10)
        
        top_bar = QHBoxLayout()
        self.dir_input = QLineEdit()
        self.dir_input.setPlaceholderText("选择需要追踪变动的目标目录...")
        browse_btn = QPushButton("浏览目录")
        browse_btn.clicked.connect(self.browse_dir)
        self.scan_btn = QPushButton("执行扫描与对比")
        self.scan_btn.clicked.connect(self.start_scan)
        
        top_bar.addWidget(QLabel("目标:"))
        top_bar.addWidget(self.dir_input)
        top_bar.addWidget(browse_btn)
        top_bar.addWidget(self.scan_btn)
        top_layout.addLayout(top_bar)
        
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["变动类型", "路径 / 说明", "详细信息"])
        self.tree.setAlternatingRowColors(True)
        self.tree.setColumnWidth(0, 150)
        top_layout.addWidget(self.tree)
        
        # -- 左侧下半部分 (摘要与生成) --
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)
        bottom_layout.setSpacing(2)
        bottom_layout.setContentsMargins(0, 5, 0, 0)
        
        bottom_layout.addWidget(QLabel("本次更新核心摘要 / Bug修复 (人话描述):"))
        self.summary_input = QTextEdit()
        self.summary_input.setPlaceholderText("例如：修复了刷铁机不工作的bug，优化了服务器TPS...")
        bottom_layout.addWidget(self.summary_input)
        
        self.gen_btn = QPushButton("生成 Markdown 日志")
        self.gen_btn.clicked.connect(self.generate_log)
        bottom_layout.addWidget(self.gen_btn)
        
        left_splitter.addWidget(top_widget)
        left_splitter.addWidget(bottom_widget)
        left_splitter.setSizes([600, 200])
        
        # ================= 右侧面板 =================
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(10, 0, 0, 0)
        right_layout.setSpacing(10)
        
        right_layout.addWidget(QLabel("生成的 Markdown 日志源码:"))
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setFont(QFont("Consolas", 12))
        self.log_display.setPlaceholderText("扫描并生成日志后，源码将显示在此处...")
        right_layout.addWidget(self.log_display)
        
        self.copy_btn = QPushButton("一键复制日志源码")
        self.copy_btn.clicked.connect(self.copy_log)
        self.copy_btn.setEnabled(False)
        right_layout.addWidget(self.copy_btn)
        
        splitter.addWidget(left_splitter)
        splitter.addWidget(right_widget)
        splitter.setSizes([700, 500])

    def apply_styles(self):
        qss = """
        QWidget {
            background-color:  #1e1e1e;
            color:  #d4d4d4;
            font-family: "Consolas", "Courier New", monospace;
            font-size: 13px;
            border-radius: 0px;
        }
        QLineEdit, QTextEdit {
            background-color:  #252526;
            border: 1px solid  #333333;
            padding: 8px;
            color:  #d4d4d4;
        }
        QPushButton {
            background-color:  #2d2d2d;
            border: 1px solid  #555555;
            padding: 10px 20px;
            font-weight: bold;
            color:  #d4d4d4;
        }
        QPushButton:hover {
            background-color:  #3e3e3e;
            border: 1px solid  #007acc;
            color:  #ffffff;
        }
        QPushButton:pressed {
            background-color:  #007acc;
        }
        QPushButton:disabled {
            background-color:  #1e1e1e;
            color:  #666666;
            border: 1px solid  #333333;
        }
        QTreeWidget {
            border: 1px solid  #333333;
            background-color:  #1e1e1e;
            color:  #d4d4d4;
        }
        QTreeWidget::item {
            padding: 6px;
            color:  #d4d4d4;
        }
        QTreeWidget::item:hover {
            background-color:  #2a2d2e;
        }
        QTreeWidget::item:selected {
            background-color:  #094771;
            border: none;
        }
        QHeaderView::section {
            background-color:  #252526;
            color:  #d4d4d4;
            border: none;
            border-bottom: 1px solid  #555555;
            border-right: 1px solid  #333333;
            padding: 8px;
            font-weight: bold;
        }
        """
        self.setStyleSheet(qss)

    def browse_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "选择目标目录")
        if dir_path:
            self.dir_input.setText(dir_path)

    def start_scan(self):
        root_dir = self.dir_input.text()
        if not root_dir or not os.path.isdir(root_dir):
            QMessageBox.warning(self, "错误", "请选择有效的目录")
            return
            
        # 使用统一管理的配置路径，无视打包环境偏移
        rules_path = DEFAULT_RULES_PATH
        if not os.path.exists(rules_path):
             QMessageBox.critical(self, "致命错误", f"找不到配置文件:\n{rules_path}")
             return
             
        self.scan_btn.setEnabled(False)
        self.scan_btn.setText("扫描中...")
        self.tree.clear()
        self.log_display.clear()
        self.copy_btn.setEnabled(False)
        
        self.worker = ScanWorker(root_dir, rules_path)
        self.worker.finished.connect(self.on_scan_finished)
        self.worker.error.connect(self.on_scan_error)
        self.worker.start()

    def on_scan_finished(self, old_snap, new_snap, diffs):
        self.old_snapshot = old_snap
        self.new_snapshot = new_snap
        self.diffs = diffs
        
        self.render_diffs()
        
        self.scan_btn.setEnabled(True)
        self.scan_btn.setText("执行扫描与对比")
        QMessageBox.information(self, "完成", "扫描与对比完成！可以填写摘要并生成日志了。")

    def on_scan_error(self, err_msg):
        self.scan_btn.setEnabled(True)
        self.scan_btn.setText("执行扫描与对比")
        QMessageBox.critical(self, "扫描出错", err_msg)

    def render_diffs(self):
        def add_category(name, items, color):
            if not items: return
            cat_item = QTreeWidgetItem([name, f"({len(items)} 项)", ""])
            cat_item.setForeground(0, color)
            self.tree.addTopLevelItem(cat_item)
            for item in items:
                path = item.get('path', item.get('new_path', ''))
                if item.get('type') == 'dir':
                    path = f"[目录] {path}"
                child = QTreeWidgetItem(["", path, ""])
                cat_item.addChild(child)
            cat_item.setExpanded(True)

        add_category("新增 (Added)", self.diffs.get('added', []), QColor(" #4ec9b0"))
        add_category("删除 (Deleted)", self.diffs.get('deleted', []), QColor(" #f48771"))
        add_category("修改 (Modified)", self.diffs.get('modified', []), QColor(" #dcdcaa"))
        add_category("重命名 (Renamed)", self.diffs.get('renamed', []), QColor(" #c586c0"))
        add_category("移动 (Moved)", self.diffs.get('moved', []), QColor(" #569cd6"))

    def generate_log(self):
        if not self.diffs:
            QMessageBox.warning(self, "提示", "请先执行扫描")
            return
            
        summary = self.summary_input.toPlainText()
        
        # 加载规则配置以获取模板名称
        try:
            with open(DEFAULT_RULES_PATH, 'r', encoding='utf-8') as f:
                rules = yaml.safe_load(f)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"读取配置文件失败:\n{e}")
            return
            
        generator = ChangelogGenerator(rules)
        md_content = generator.generate(self.diffs, self.new_snapshot, summary)
        
        self.log_display.setPlainText(md_content)
        self.copy_btn.setEnabled(True)

    def copy_log(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.log_display.toPlainText())
        self.copy_btn.setText("已复制到剪贴板！")
        QThread.msleep(1500) 
        self.copy_btn.setText("一键复制日志源码")