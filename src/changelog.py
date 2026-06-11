from datetime import datetime
from typing import Dict, List, Any
from jinja2 import Environment, FileSystemLoader, select_autoescape
import os

class ChangelogGenerator:
    """
    日志生成引擎：使用 Jinja2 渲染 Markdown 模板。
    """
    def __init__(self, rules: Dict[str, Any]):
        self.rules = rules
        # 定位 templates 目录
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.template_dir = os.path.join(base_dir, 'config', 'templates')
        
        # 初始化 Jinja2 环境
        self.env = Environment(
            loader=FileSystemLoader(self.template_dir),
            autoescape=select_autoescape(['html', 'xml']), # Markdown 不需要转义，但保留默认安全设置
            trim_blocks=True,
            lstrip_blocks=True
        )

    def _prepare_context(self, diffs: Dict[str, List], new_snapshot: Dict[str, Any]) -> Dict[str, Any]:
        """
        清洗后端传来的原始 diffs 数据，转换为模板易于遍历的结构。
        """
        context = {
            'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'mods_updated': [],
            'mods_added': [],
            'mods_removed': [],
            'configs_modified': [],
            'others_added': [],
            'others_removed': [],
            'dirs_added': [],
            'dirs_removed': [],
            'renamed_items': [],
            'moved_items': []
        }
        
        # 处理修改
        for item in diffs.get('modified', []):
            path = item['path']
            info = new_snapshot.get(path, {})
            meta = info.get('metadata', {})
            
            if meta.get('displayName') or meta.get('name'):
                name = meta.get('displayName') or meta.get('name')
                context['mods_updated'].append(f"**{name}** (内容已修改/配置更新)")
            else:
                context['configs_modified'].append(f"修改了 `{path}`")
                
        # 处理新增
        for item in diffs.get('added', []):
            path = item['path']
            if item.get('type') == 'dir':
                context['dirs_added'].append(f"`{path}`")
                continue
            info = new_snapshot.get(path, {})
            meta = info.get('metadata', {})
            name = meta.get('displayName') or meta.get('name') or path.split('/')[-1]
            
            if path.endswith('.jar'):
                context['mods_added'].append(f"新增 **{name}**")
            else:
                context['others_added'].append(f"`{path}`")
                
        # 处理删除
        for item in diffs.get('deleted', []):
            path = item['path']
            if item.get('type') == 'dir':
                context['dirs_removed'].append(f"`{path}`")
                continue
            if path.endswith('.jar'):
                context['mods_removed'].append(f"移除 `{path.split('/')[-1]}`")
            else:
                context['others_removed'].append(f"`{path}`")
                
        # 处理重命名与移动
        for item in diffs.get('renamed', []):
            old_name = item['old_path'].split('/')[-1]
            new_name = item['new_path'].split('/')[-1]
            context['renamed_items'].append(f"`{old_name}` -> `{new_name}`")
            
        for item in diffs.get('moved', []):
            context['moved_items'].append(f"`{item['old_path']}` 移动至 `{item['new_path']}`")
            
        return context

    def generate(self, diffs: Dict[str, List], new_snapshot: Dict[str, Any], summary: str) -> str:
        """
        渲染并返回 Markdown 字符串。
        """
        template_name = self.rules.get('template_file', 'default.md')
        try:
            template = self.env.get_template(template_name)
        except Exception as e:
            return f"错误：找不到模板文件 {template_name} ({e})"
            
        context = self._prepare_context(diffs, new_snapshot)
        context['summary'] = summary.strip()
        
        return template.render(context)