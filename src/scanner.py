import hashlib
import pathspec
import yaml
from pathlib import Path
from typing import Dict, Any

# 使用相对导入，完美兼容 PyInstaller 内部打包机制
from . import storage
from . import deep_dive

class Scanner:
    """
    核心扫描引擎：负责目录遍历、规则过滤、Hash 计算、内容备份与深潜提取。
    """
    def __init__(self, root_dir: str, rules_path: str):
        self.root_dir = Path(root_dir).resolve()
        self.rules = self._load_rules(rules_path)
        self.ignore_spec = self._build_ignore_spec()
        
        self.storage_engine = storage.Storage(str(self.root_dir))
        self.diver = deep_dive.DeepDiver(self.rules.get('deep_dive_rules', []))
        
        self.copy_exts = [ext.lower() for ext in self.rules.get('copy_content_extensions', [])]

    def _load_rules(self, path: str) -> Dict[str, Any]:
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _build_ignore_spec(self) -> pathspec.PathSpec:
        patterns = self.rules.get('ignore_patterns', [])
        return pathspec.PathSpec.from_lines('gitwildmatch', patterns)

    def _calculate_hash(self, file_path: Path) -> str:
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    def scan(self) -> Dict[str, Dict[str, Any]]:
        results = {}
        for path in self.root_dir.rglob('*'):
            rel_path = path.relative_to(self.root_dir).as_posix()
            
            if self.ignore_spec.match_file(rel_path):
                continue
            
            try:
                if path.is_file():
                    file_hash = self._calculate_hash(path)
                    stat = path.stat()
                    
                    info = {
                        'type': 'file',
                        'hash': file_hash,
                        'size': stat.st_size,
                        'mtime': stat.st_mtime
                    }
                    
                    if path.suffix.lower() in self.copy_exts:
                        self.storage_engine.save_content(path, file_hash)
                        info['has_content'] = True
                        
                    metadata = self.diver.extract(path)
                    if metadata:
                        info['metadata'] = metadata
                        
                    results[rel_path] = info
                    
                elif path.is_dir():
                    results[rel_path] = {
                        'type': 'dir',
                        'hash': '',
                        'size': 0,
                        'mtime': path.stat().st_mtime
                    }
                    
            except (PermissionError, OSError) as e:
                print(f"[Warning] 无法读取 {rel_path}: {e}")
                    
        return results