"""Build static pages. Only Python stdlib; keep all accounting values as strings."""
import json
from pathlib import Path
from html import escape

ROOT = Path(__file__).resolve().parents[1]
NAMES = ['系统管理业务', '基础设置业务', '总账管理子系统初始设置', '总账管理系统日常业务处理', '总账管理系统期末处理', 'UFO报表管理', '薪资管理', '固定资产管理业务', '供应链管理系统初始化', '采购与应付管理', '销售与应收管理', '库存管理与存货核算', '费用报销系统设计与开发']
def e(value):
    return escape(str(value), quote=True)

def validate(data):
    labs = data['labs']
    assert len(labs) == 13, '必须保留13个实验'
    assert [x['name'] for x in labs] == NAMES, '名称必须与用户目录一致'
    assert [x['id'] for x in labs] == [f'{i:02}' for i in range(1, 14)]
    ids = set()
    for lab in labs:
        for table in lab['tables']:
            assert table['id'].isascii() and table['id'].replace('-', '').isalnum()
            assert table['id'] not in ids, '表格id必须全站唯一'
            ids.add(table['id'])
            assert table['source'] and table['columns']
            for row in table['rows']:
                assert len(row['values']) == len(table['columns'])
                assert all(isinstance(v, str) for v in row['values']), '所有编号、账号、金额必须用字符串'
                assert row['source'] and isinstance(row['verified'], bool)
                if row['verified']:
                    assert all('待核对' not in v for v in row['values']), '待核对内容不得开放复制'
        for step in lab['steps']:
            assert all(isinstance(step.get(k), str) and step[k] for k in ['title', 'source', 'menu', 'button', 'fields', 'save', 'check'])

def transfer():
    return '''<div class="panel" id="transfer"><h2>进度备份与转移</h2>
<p id="storage-state" class="notice">学校电脑与个人电脑不会自动同步。请导出进度，通过自己的邮箱或网盘转移后导入。</p>
<p class="muted">只转移个人进度，不修改教材数据。导入时，同编号实验采用文件中的记录，未包含的实验保留本地记录。请先导出当前进度备份。</p>
<div class="toolbar"><button id="export-text" type="button">生成进度文本</button><button id="download-progress" type="button" class="secondary">下载进度文件</button><button id="copy-progress" type="button" class="secondary">复制当前进度</button></div>
<div class="form-row"><label for="import-file">选择进度文件（旧版 IE 可改用下方文本框）</label><input id="import-file" type="file" accept=".json,application/json"></div>
<div class="form-row"><label for="transfer-text">进度文本</label><textarea id="transfer-text" spellcheck="false" placeholder="在此粘贴导出的进度文本"></textarea></div>
<button id="import-progress" type="button">导入并合并进度</button></div>'''

def frame(labs, active, content):
    prefix = '../' if active else ''
    nav = '<li><a href="' + prefix + 'index.html"' + (' class="active"' if not active else '') + '>全部实验</a></li>'
    for lab in labs:
        href = ('' if active else 'labs/') + lab['id'] + '.html'
        nav += '<li><a href="' + href + '"' + (' class="active"' if active == lab['id'] else '') + '><span class="nav-num">' + lab['id'] + '</span>' + e(lab['name']) + '</a></li>'
    title = next((x['name'] for x in labs if x['id'] == active), '实验目录')
    return f'''<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta http-equiv="X-UA-Compatible" content="IE=edge"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="description" content="用友U8十三项实验资料库，教材数据查询、字段复制与进度备份。"><title>{e(title)} · 用友U8十三项实验资料库</title><link rel="stylesheet" href="{prefix}assets/style.css"></head>
<body data-lab="{active}"><div class="top"><a class="brand" href="{prefix}index.html"><span class="brand-mark">U8</span>十三项实验资料库</a><a class="top-link" href="#transfer">进度导入 / 导出</a><div class="clear"></div></div>
<div class="shell"><div class="sidebar"><p class="eyebrow">实验导航 / LAB DIRECTORY</p><ul class="nav">{nav}</ul><div class="notice">资料仅依据教材整理。待核对内容不开放复制。</div><a href="{prefix}index.html">返回实验目录 →</a></div><div class="main">
<noscript><div class="notice">JavaScript 已禁用：可浏览目录、教材数据和步骤；可选中文字按 Ctrl+C。搜索、按钮复制与进度管理需要启用 JavaScript。</div></noscript>
{content}
<div id="message" class="message" role="status" aria-live="polite"></div>{transfer()}</div><div class="clear"></div></div>
<div class="footer">用友 U8 实验辅助工具 · 不连接学校 U8 数据库 · 不保存 U8 账号密码<br>兼容设计目标：IE8 标准模式及以上；实际机房浏览器与 HTTPS 连通性待实测。</div>
<div id="manual-copy" class="manual hidden" role="dialog" aria-label="手动复制"><h3>手动复制</h3><p id="copy-help">请按 Ctrl+C</p><label for="copy-text">待复制内容</label><textarea id="copy-text" readonly="readonly"></textarea><button id="copy-close" type="button" class="secondary">关闭</button></div>
<script src="{prefix}assets/app.js"></script></body></html>'''

def home(labs):
    verified = sum(1 for lab in labs for table in lab['tables'] for row in table['rows'] if row['verified'])
    html = '''<div class="hero"><div class="eyebrow">ACCOUNTING INFORMATION SYSTEM</div><h1>用友U8十三项实验资料库</h1><p>打开实验，查找教材数据，复制到 U8。让机房里的每一次录入更清楚。</p><a class="button" href="labs/02.html">进入实验二：基础设置业务 →</a> <a class="button secondary" href="labs/03.html">进入实验三：总账初始设置 →</a></div>
<div class="notice"><strong>教材核对状态：</strong>已整理实验二第67～71页、实验三3张照片（页码待核对）及实验四第109～110页（11笔业务及角色清单）。目录照片、实验二第72～73页及实验四后续操作指导待提供。13项实验名称沿用用户文字，待目录照片核对。教材登录凭据与原始照片未公开。</div>
<table class="stats" role="presentation"><tr><td><span class="stat">13</span>实验入口</td><td><span class="stat">''' + str(verified) + '''</span>已核对数据行</td><td><span class="stat" id="done-count">0</span>已完成实验</td></tr></table>
<div class="search"><label for="search">查找实验</label><input id="search" type="text" placeholder="输入实验名称，如：基础设置"><button id="search-button" type="button">搜索</button><div class="muted" id="search-result">共13个实验；进度由你自行记录</div></div><div class="cards">'''
    for lab in labs:
        html += f'''<div class="card-wrap" data-search="{e(lab['id']+' '+lab['name'])}"><div class="card"><span class="eyebrow">实验 {lab['id']}</span> <span class="tag" data-progress="{lab['id']}">未开始</span><h2><a href="labs/{lab['id']}.html">{e(lab['name'])}</a></h2><div class="muted">教材页码：{e(lab['pages'])}</div><div class="muted">资料：{e(lab['sourceState'])}</div><div class="muted"><span data-saved-step="{lab['id']}">尚无步骤记录</span></div><div class="card-footer">独立实验页面<a href="labs/{lab['id']}.html">打开实验 →</a></div></div></div>'''
    return html + '</div>'

def table_html(table):
    tid = table['id']
    empty_label = table.get('emptyLabel', '教材留空')
    html = f'<div class="panel" id="section-{tid}"><h3>{e(table["title"])}</h3><p class="muted">教材来源：{e(table["source"])}</p>'
    if table.get('description'):
        html += '<p>' + e(table['description']) + '</p>'
    html += f'<button type="button" data-copy="table" data-target="{tid}">复制筛选后已核对表格</button> <a href="#data">返回资料分类 ↑</a><div class="table-scroll"><table class="data" id="{tid}"><thead><tr>'
    html += ''.join(f'<th scope="col" data-label="{e(c)}">{e(c)}</th>' for c in table['columns']) + '<th scope="col">核对 / 操作</th></tr></thead><tbody>'
    for index, row in enumerate(table['rows']):
        rid = f'{tid}-r{index}'
        html += f'<tr id="{rid}" data-search="{e(table["title"]+" "+" ".join(row["values"]))}">'
        for ci, value in enumerate(row['values']):
            fid = f'{rid}-c{ci}'
            if row['verified']:
                html += f'<td><input class="field" id="{fid}" data-field="1" type="text" readonly="readonly" aria-label="{e(table["columns"][ci])}" placeholder="{e(empty_label)}" value="{e(value)}">'
                html += f'<button class="copy-field secondary" type="button" data-copy="field" data-target="{fid}">复制</button>' if value else '<span class="muted">' + e(empty_label) + '</span>'
                html += '</td>'
            else:
                html += f'<td class="pending"><span class="pending-value">{e(value) if value else "待核对"}</span></td>'
        html += '<td><span class="muted">' + e(row['source']) + '</span><br>'
        html += f'<button class="copy-field secondary" type="button" data-copy="row" data-target="{rid}">复制整行</button>' if row['verified'] else '<span class="pending">待核对，暂不复制</span>'
        html += '</td></tr>'
    return html + '</tbody></table></div></div>'

def detail(lab):
    html = f'''<div class="muted"><a href="../index.html">全部实验</a> / 实验{lab['id']}</div><div class="hero"><div class="eyebrow">实验 {lab['id']} / U8 LAB</div><h1>{e(lab['name'])}</h1><p>教材页码：{e(lab['pages'])}</p><span class="tag" data-progress="{lab['id']}">未开始</span> <span class="tag">{e(lab['sourceState'])}</span></div>
<div class="panel anchor-nav"><a href="#data">教材数据</a><a href="#steps">操作步骤</a><a href="#progress">我的进度</a><a href="#transfer">进度转移</a></div>
<div class="panel" id="data"><h2>教材数据查询</h2><p class="muted">单字段用于 U8 输入框；整行和整表使用制表符分隔，适合粘贴至表格。请核对目标字段。编号与账号全程按文本保留。</p><div class="search"><label for="search">搜索资料</label><input id="search" type="text" placeholder="输入名称、编号或表名"><button id="search-button" type="button">搜索</button><div class="muted" id="search-result">仅搜索本实验已录入的数据；整表复制只含可见且已核对的行。</div></div>'''
    if not lab['tables']:
        html += '<div class="categories"><span>人员</span><span>部门</span><span>客户</span><span>供应商</span><span>银行账户</span><span>会计科目</span></div><div class="empty"><strong>待核对 · 尚未录入教材数据</strong>以上为预留资料分类，不代表教材实际包含这些表。<br>收到教材照片后逐项录入，并标记来源页码。税号、银行账号、科目编码和金额需逐项核对。</div>'
    if lab['tables']:
        if lab['id'] == '02':
            html += '<div class="notice">资料按照片转录，空白栏保持为空，不补成0或默认值。表3-14转账凭证限制科目被手指遮挡；表3-13主营业务成本方向印为“贷”，均标为待核对并暂停该行复制。实验要求：以账套主管“陈明”的身份进行基础设置（第71页）。</div>'
        if lab.get('notes'):
            html += '<div class="notice">' + e(lab['notes'][0]) + '<br>详细教材说明见下方 <a href="#textbook-notes">教材说明与录入提醒</a>。' + e(lab.get('notesLinkHint', '合计数与上级科目请按教材说明处理。')) + '</div>'
        html += '<div class="categories">'
        html += ''.join(f'<a class="button secondary" href="#section-{t["id"]}">{e(t["title"])}（{len(t["rows"])}）</a> ' for t in lab['tables'])
        html += '</div>'
    html += '</div>' + ''.join(table_html(t) for t in lab['tables'])
    if lab.get('notes'):
        html += '<div class="panel" id="textbook-notes"><h2>教材说明与录入提醒</h2>' + ''.join('<p>' + e(note) + '</p>' for note in lab['notes']) + '</div>'
    html += '<div class="panel" id="steps"><h2>操作步骤指导</h2>'
    if not lab['steps']:
        html += '<div class="empty"><strong>待核对 · 尚无可引用的教材步骤</strong>实验二等待第72～73页照片；其他实验等待对应教材。不会依据通用 U8 经验补写步骤。</div><p class="muted">收到教材后，每项操作按照“进入菜单 → 点击按钮 → 填写数据 → 保存 → 检查结果”展示；教材未说明的部分会单独标为待核对。</p>'
    for step in lab['steps']:
        html += '<div class="step"><h3>' + e(step['title']) + '</h3><p class="muted">来源：' + e(step['source']) + '</p><ol>'
        for label, k in [('进入菜单', 'menu'), ('点击按钮', 'button'), ('填写数据', 'fields'), ('保存', 'save'), ('检查结果', 'check')]:
            html += '<li>' + label + '：' + e(step[k]) + '</li>'
        html += '</ol></div>'
    html += '''</div><div class="panel" id="progress"><h2>我的实验进度</h2><p class="muted">资料核对状态与个人完成状态分别记录。请以你在机房实际完成的账套为准。</p><div class="form-row"><label for="progress-status">完成状态</label><select id="progress-status"><option value="todo">未开始</option><option value="doing">进行中</option><option value="done">已完成</option></select></div><div class="form-row"><label for="progress-step">具体完成到哪一步</label><input id="progress-step" type="text" maxlength="500" placeholder="填写你实际完成的菜单、步骤或教材位置"></div><div class="form-row"><label for="progress-note">下次继续事项</label><textarea id="progress-note" maxlength="5000" placeholder="只记录学习进度，请勿填写账号密码或真实个人隐私"></textarea></div><button id="save-progress" type="button">保存本实验进度</button></div>'''
    return html

def build():
    data = json.loads((ROOT / 'data/labs.json').read_text(encoding='utf-8'))
    validate(data)
    labs = data['labs']
    (ROOT / 'labs').mkdir(exist_ok=True)
    (ROOT / 'index.html').write_text(frame(labs, '', home(labs)), encoding='utf-8')
    for lab in labs:
        (ROOT / 'labs' / (lab['id'] + '.html')).write_text(frame(labs, lab['id'], detail(lab)), encoding='utf-8')
    print('Built 14 static pages; verified data rows: ' + str(sum(1 for lab in labs for t in lab['tables'] for r in t['rows'] if r['verified'])))

if __name__ == '__main__':
    build()
