import json
from pathlib import Path
from typing import Dict, Any

class Storage:
    """
    持久化引擎：管理 .snapdiff 目录、快照元数据与文本内容备份。
    """
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir).resolve()
        self.snapdiff_dir = self.root_dir / '.snapdiff'
        self.contents_dir = self.snapdiff_dir / 'contents'
        self.snapshot_file = self.snapdiff_dir / 'snapshot.json'
        
        # 确保核心目录存在
        self.snapdiff_dir.mkdir(exist_ok=True)
        self.contents_dir.mkdir(exist_ok=True)

    def save_content(self, file_path: Path, file_hash: str):
        """
        保存文本文件内容。
        以 Hash 命名去重存储，避免相同内容的文件占用多份空间。
        """
        content_file = self.contents_dir / f"{file_hash}.txt"
        if not content_file.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                with open(content_file, 'w', encoding='utf-8') as f:
                    f.write(content)
            except UnicodeDecodeError:
                # 遇到伪装成文本的二进制文件，跳过
                pass

    def get_content(self, file_hash: str) -> str:
        """根据 Hash 读取历史文本内容"""
        content_file = self.contents_dir / f"{file_hash}.txt"
        if content_file.exists():
            with open(content_file, 'r', encoding='utf-8') as f:
                return f.read()
        return ""

    def save_snapshot(self, snapshot: Dict[str, Any]):
        """保存本次扫描的快照元数据"""
        with open(self.snapshot_file, 'w', encoding='utf-8') as f:
            json.dump(snapshot, f, indent=4, ensure_ascii=False)

    def load_snapshot(self) -> Dict[str, Any]:
        """加载上一次的历史快照"""
        if self.snapshot_file.exists():
            with open(self.snapshot_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}