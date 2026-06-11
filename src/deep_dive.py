import zipfile
import json
from pathlib import Path
from typing import Dict, Any, List

# 兼容 Python 3.11 以下的 TOML 解析
try:
    import tomllib
except ImportError:
    import tomli as tomllib

class DeepDiver:
    """
    深潜引擎：针对压缩包(如 .jar)进入内部提取特定元数据。
    """
    def __init__(self, rules: List[Dict[str, Any]]):
        self.rules = rules or []

    def extract(self, file_path: Path) -> Dict[str, Any]:
        ext = file_path.suffix.lower()
        metadata = {}
        
        for rule in self.rules:
            if rule.get('extension') == ext:
                try:
                    # 尝试作为 Zip 压缩包打开
                    with zipfile.ZipFile(file_path, 'r') as zf:
                        for target in rule.get('targets', []):
                            internal_path = target.get('internal_path')
                            if internal_path and internal_path in zf.namelist():
                                with zf.open(internal_path) as f:
                                    content = f.read()
                                    fmt = target.get('format', 'json')
                                    
                                    # 根据配置格式解析
                                    if fmt == 'json':
                                        data = json.loads(content)
                                    elif fmt == 'toml':
                                        data = tomllib.loads(content.decode('utf-8'))
                                    else:
                                        continue
                                    
                                    # 提取指定字段
                                    for field in target.get('extract_fields', []):
                                        if field in data:
                                            metadata[field] = data[field]
                except Exception:
                    # 遇到损坏的压缩包或非标准格式，静默失败，不中断主流程
                    pass
        return metadata