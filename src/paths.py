import sys
import os

def get_app_root():
    """
    获取程序运行的根目录 (兼容源码运行与 PyInstaller 打包)
    """
    if getattr(sys, 'frozen', False):
        # PyInstaller 打包后，exe 所在目录 (即 dist/SnapDiff/)
        return os.path.dirname(sys.executable)
    else:
        # 源码运行，项目根目录
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

APP_ROOT = get_app_root()
CONFIG_DIR = os.path.join(APP_ROOT, 'config')
TEMPLATES_DIR = os.path.join(CONFIG_DIR, 'templates')
DEFAULT_RULES_PATH = os.path.join(CONFIG_DIR, 'default_rules.yaml')