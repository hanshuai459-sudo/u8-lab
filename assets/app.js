(function () {
    'use strict';
    var key = 'u8-lab-progress-v1', state = {}, storageOK = true;
    var lab = document.body.getAttribute('data-lab');
    function el(id) { return document.getElementById(id); }
    function text(node, value) { if (node) { if ('textContent' in node) { node.textContent = value; } else { node.innerText = value; } } }
    function on(node, event, fn) { if (!node) { return; } if (node.addEventListener) { node.addEventListener(event, fn, false); } else { node.attachEvent('on' + event, fn); } }
    function message(value) { text(el('message'), value); }
    function validProgress(data) {
        var id, row, result = {}, count = 0;
        if (!data || Object.prototype.toString.call(data) !== '[object Object]') { throw new Error('进度内容必须是对象'); }
        for (id in data) {
            if (Object.prototype.hasOwnProperty.call(data, id)) {
                count += 1; row = data[id];
                if (!/^(0[1-9]|1[0-3])$/.test(id) || !row || Object.prototype.toString.call(row) !== '[object Object]' ||
                    !/^(todo|doing|done)$/.test(row.status) || typeof row.step !== 'string' || typeof row.note !== 'string' ||
                    row.step.length > 500 || row.note.length > 5000) { throw new Error('实验编号、状态或记录格式不正确'); }
                result[id] = {status: row.status, step: row.step, note: row.note};
            }
        }
        if (count > 13) { throw new Error('实验数量超出范围'); }
        return result;
    }
    function persist() {
        try { window.localStorage.setItem(key, JSON.stringify(state)); storageOK = true; }
        catch (e) { storageOK = false; }
        text(el('storage-state'), storageOK ? '进度保存在当前浏览器；学校电脑与个人电脑不会自动同步，请离开前导出。' : '浏览器无法保存本地进度！当前记录仅在本页有效，刷新前请立即导出。');
    }
    function statusName(code) { return code === 'done' ? '已完成' : code === 'doing' ? '进行中' : '未开始'; }
    function refresh() {
        var i, node, id, row, count = 0, spans = document.getElementsByTagName('span');
        for (i = 0; i < spans.length; i += 1) {
            node = spans[i]; id = node.getAttribute('data-progress');
            if (id) { row = state[id] || {}; text(node, statusName(row.status)); node.className = 'tag' + (row.status === 'done' ? ' done' : row.status === 'doing' ? ' blue' : ''); }
            id = node.getAttribute('data-saved-step');
            if (id) { text(node, state[id] && state[id].step ? '上次记录：' + state[id].step : '尚无步骤记录'); }
        }
        for (id in state) { if (Object.prototype.hasOwnProperty.call(state, id) && state[id].status === 'done') { count += 1; } }
        text(el('done-count'), String(count));
        if (lab && el('progress-status')) { row = state[lab] || {status: 'todo', step: '', note: ''}; el('progress-status').value = row.status; el('progress-step').value = row.step; el('progress-note').value = row.note; }
    }
    function selectManual(value, explanation) {
        var box = el('manual-copy'), area = el('copy-text');
        box.className = 'manual'; text(el('copy-help'), explanation); area.value = value; area.focus(); area.select();
    }
    function copy(value) {
        var success = false;
        try { if (window.clipboardData && window.clipboardData.setData) { success = window.clipboardData.setData('Text', value); } } catch (ignore) {}
        if (!success) {
            selectManual(value, '自动复制受限时，请按 Ctrl+C；手机可长按选择并复制。');
            try { success = !!(document.execCommand && document.execCommand('copy')); } catch (ignore2) {}
        }
        if (success) { el('manual-copy').className = 'manual hidden'; message('已复制。请核对 U8 目标输入框后粘贴。'); }
        else { message('请在复制框中手动按 Ctrl+C。'); }
    }
    function collectRow(row) {
        var inputs = row.getElementsByTagName('input'), values = [], i;
        for (i = 0; i < inputs.length; i += 1) { if (inputs[i].getAttribute('data-field') === '1') { values.push(inputs[i].value); } }
        return values.join('\t');
    }
    function bindCopy() {
        var buttons = document.getElementsByTagName('button'), i;
        for (i = 0; i < buttons.length; i += 1) {
            if (buttons[i].getAttribute('data-copy')) {
                on(buttons[i], 'click', function () {
                    var type = this.getAttribute('data-copy'), target = el(this.getAttribute('data-target')), rows, j, lines = [], heads, k, names = [];
                    if (type === 'field') { copy(target.value); }
                    else if (type === 'row') { copy(collectRow(target)); }
                    else {
                        heads = target.getElementsByTagName('th');
                        for (k = 0; k < heads.length - 1; k += 1) { names.push(heads[k].getAttribute('data-label')); }
                        lines.push(names.join('\t')); rows = target.getElementsByTagName('tr');
                        for (j = 1; j < rows.length; j += 1) { if (rows[j].style.display !== 'none' && rows[j].getElementsByTagName('input').length > 0) { lines.push(collectRow(rows[j])); } }
                        if (lines.length === 1) { message('没有可复制的数据。'); return; }
                        copy(lines.join('\r\n'));
                    }
                });
            }
        }
    }
    function search() {
        var query = el('search').value.toLowerCase().replace(/^\s+|\s+$/g, ''), all = document.getElementsByTagName('*'), i, hay, count = 0, rows, j, visible;
        for (i = 0; i < all.length; i += 1) {
            hay = all[i].getAttribute('data-search');
            if (hay !== null) { all[i].style.display = hay.toLowerCase().indexOf(query) !== -1 ? '' : 'none'; if (all[i].style.display !== 'none') { count += 1; } }
        }
        for (i = 0; i < all.length; i += 1) {
            if (all[i].id && all[i].id.indexOf('section-') === 0) {
                rows = all[i].getElementsByTagName('tr'); visible = !query;
                for (j = 1; j < rows.length; j += 1) { if (rows[j].style.display !== 'none') { visible = true; } }
                all[i].style.display = visible ? '' : 'none';
            }
        }
        text(el('search-result'), '找到 ' + count + (lab ? ' 条已录入数据' : ' 个实验'));
    }
    function exportProgress() {
        var payload = {app: 'u8-lab', version: 1, progress: state};
        el('transfer-text').value = JSON.stringify(payload, null, 2);
        message('已生成进度文本。可下载文件，或复制文本，通过自己的邮箱/网盘转移。请勿包含账号密码。');
        return el('transfer-text').value;
    }
    try { var saved = window.localStorage.getItem(key); if (saved) { state = validProgress(JSON.parse(saved)); } }
    catch (e) { storageOK = false; message('本地记录无法读取；可尝试导入之前导出的进度。'); }
    text(el('storage-state'), storageOK ? '进度保存在当前浏览器；学校电脑与个人电脑不会自动同步，请离开前导出。' : '本地存储不可用或记录损坏；请使用进度导出功能备份。');
    refresh(); bindCopy();
    var fieldInputs = document.getElementsByTagName('input'), fi;
    for (fi = 0; fi < fieldInputs.length; fi += 1) { if (fieldInputs[fi].getAttribute('data-field') === '1') { on(fieldInputs[fi], 'focus', function () { this.select(); }); } }
    on(el('save-progress'), 'click', function () {
        state[lab] = {status: el('progress-status').value, step: el('progress-step').value, note: el('progress-note').value}; persist(); refresh();
        message(storageOK ? '进度已保存到当前浏览器。' : '记录暂存在本页，请立即导出备份。');
    });
    on(el('search-button'), 'click', search); on(el('search'), 'keyup', search); on(el('search'), 'input', search);
    on(el('copy-close'), 'click', function () { el('manual-copy').className = 'manual hidden'; });
    on(el('export-text'), 'click', exportProgress);
    on(el('copy-progress'), 'click', function () { copy(exportProgress()); });
    on(el('download-progress'), 'click', function () {
        var value = exportProgress(), blob, url, anchor;
        try {
            blob = new Blob(['\ufeff' + value], {type: 'application/json;charset=utf-8'});
            if (window.navigator.msSaveBlob) { window.navigator.msSaveBlob(blob, 'u8-lab-progress.json'); return; }
            if (window.URL && window.URL.createObjectURL && 'download' in document.createElement('a')) {
                url = window.URL.createObjectURL(blob); anchor = document.createElement('a'); anchor.href = url; anchor.download = 'u8-lab-progress.json'; document.body.appendChild(anchor); anchor.click(); document.body.removeChild(anchor); window.setTimeout(function () { window.URL.revokeObjectURL(url); }, 10000); return;
            }
        } catch (ignore) {}
        selectManual(value, '当前浏览器不支持下载。请按 Ctrl+C 保存进度文本，用邮箱或网盘转移。');
    });
    on(el('import-file'), 'change', function () {
        var input = this, reader;
        if (!window.FileReader || !input.files || !input.files[0]) { message('此浏览器不支持读取文件，请粘贴进度文本。'); return; }
        if (input.files[0].size > 200000) { message('文件过大，请选择本工具导出的进度文件。'); return; }
        reader = new FileReader(); reader.onload = function () { el('transfer-text').value = String(reader.result).replace(/^\ufeff/, ''); message('已读取文件，点击“导入并合并进度”应用。'); }; reader.onerror = function () { message('文件读取失败，请粘贴进度文本。'); }; reader.readAsText(input.files[0], 'UTF-8');
    });
    on(el('import-progress'), 'click', function () {
        var data, incoming, id;
        try {
            if (el('transfer-text').value.length > 200000) { throw new Error('进度文本过长'); }
            data = JSON.parse(el('transfer-text').value.replace(/^\ufeff/, ''));
            if (!data || data.app !== 'u8-lab' || data.version !== 1) { throw new Error('不是本工具的版本1进度文件'); }
            incoming = validProgress(data.progress);
            for (id in incoming) { if (Object.prototype.hasOwnProperty.call(incoming, id)) { state[id] = incoming[id]; } }
            persist(); refresh(); message(storageOK ? '进度已导入：文件中同编号实验覆盖本地记录，其他实验保留。' : '进度已读入但本地保存失败；请立即导出。');
        } catch (error) { message('导入失败，原进度未更改：' + error.message); }
    });
}());
