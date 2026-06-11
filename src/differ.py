from typing import Dict, List, Any

class Differ:
    def __init__(self, old_snapshot: Dict[str, Dict[str, Any]], new_snapshot: Dict[str, Dict[str, Any]]):
        self.old = old_snapshot
        self.new = new_snapshot

    def compare(self) -> Dict[str, List[Dict[str, Any]]]:
        old_paths = set(self.old.keys())
        new_paths = set(self.new.keys())

        added_paths = new_paths - old_paths
        deleted_paths = old_paths - new_paths
        common_paths = old_paths & new_paths

        modified = []
        unchanged = []

        for path in common_paths:
            old_info = self.old[path]
            new_info = self.new[path]
            
            # 目录没有 Hash，只要还在就视为 unchanged
            if old_info.get('type') == 'dir':
                unchanged.append({'path': path, 'type': 'dir'})
                continue

            if old_info['hash'] != new_info['hash']:
                modified.append({
                    'path': path,
                    'type': 'file',
                    'old_hash': old_info['hash'],
                    'new_hash': new_info['hash']
                })
            else:
                unchanged.append({'path': path, 'type': 'file'})

        renamed = []
        moved = []
        
        deleted_by_hash = {}
        for p in deleted_paths:
            info = self.old[p]
            if info.get('type') == 'dir':
                continue # 目录不参与 Hash 匹配重命名逻辑
            h = info['hash']
            if h not in deleted_by_hash:
                deleted_by_hash[h] = []
            deleted_by_hash[h].append(p)

        final_added = []
        for p in added_paths:
            info = self.new[p]
            if info.get('type') == 'dir':
                final_added.append({'path': p, 'type': 'dir', 'hash': ''})
                continue

            h = info['hash']
            if h in deleted_by_hash and deleted_by_hash[h]:
                old_p = deleted_by_hash[h].pop(0)
                
                old_dir = old_p.rsplit('/', 1)[0] if '/' in old_p else ''
                new_dir = p.rsplit('/', 1)[0] if '/' in p else ''
                
                if old_dir == new_dir:
                    renamed.append({'old_path': old_p, 'new_path': p, 'hash': h, 'type': 'file'})
                else:
                    moved.append({'old_path': old_p, 'new_path': p, 'hash': h, 'type': 'file'})
            else:
                final_added.append({'path': p, 'type': 'file', 'hash': h})

        final_deleted = []
        for p in deleted_paths:
            info = self.old[p]
            is_renamed_or_moved = any(r['old_path'] == p for r in renamed) or any(m['old_path'] == p for m in moved)
            if not is_renamed_or_moved:
                final_deleted.append({'path': p, 'type': info.get('type', 'file'), 'hash': info.get('hash', '')})

        return {
            'added': final_added,
            'deleted': final_deleted,
            'modified': modified,
            'renamed': renamed,
            'moved': moved,
            'unchanged': unchanged
        }