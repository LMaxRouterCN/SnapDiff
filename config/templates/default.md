# 更新日志 ({{ date }})

{% if summary %}
## 核心摘要
{{ summary }}
{% endif %}

{% if mods_added or mods_removed or mods_updated %}
## 模组变动
{% if mods_added %}
### 新增
{% for item in mods_added %}
- {{ item }}
{% endfor %}
{% endif %}

{% if mods_removed %}
### 移除
{% for item in mods_removed %}
- {{ item }}
{% endfor %}
{% endif %}

{% if mods_updated %}
### 修改/更新
{% for item in mods_updated %}
- {{ item }}
{% endfor %}
{% endif %}
{% endif %}

{% if configs_modified %}
## 配置与脚本变动
{% for item in configs_modified %}
- {{ item }}
{% endfor %}
{% endif %}

{% if renamed_items or moved_items %}
## 重命名与移动
{% if renamed_items %}
### 重命名
{% for item in renamed_items %}
- {{ item }}
{% endfor %}
{% endif %}

{% if moved_items %}
### 移动
{% for item in moved_items %}
- {{ item }}
{% endfor %}
{% endif %}
{% endif %}

{% if dirs_added or dirs_removed %}
## 目录变动
{% if dirs_added %}
### 新增目录
{% for item in dirs_added %}
- {{ item }}
{% endfor %}
{% endif %}

{% if dirs_removed %}
### 删除目录
{% for item in dirs_removed %}
- {{ item }}
{% endfor %}
{% endif %}
{% endif %}

{% if others_added or others_removed %}
## 其他文件变动
{% if others_added %}
### 新增
{% for item in others_added %}
- {{ item }}
{% endfor %}
{% endif %}

{% if others_removed %}
### 移除
{% for item in others_removed %}
- {{ item }}
{% endfor %}
{% endif %}
{% endif %}