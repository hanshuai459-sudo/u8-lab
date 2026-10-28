"""Validate static links, generated fields and provenance without dependencies."""
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
from build import ROOT, validate

class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.path, self.ids, self.links, self.fields = path, set(), [], {}
        self.feed(path.read_text(encoding='utf-8'))
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get('id'):
            assert a['id'] not in self.ids, f'duplicate id {self.path}: {a["id"]}'
            self.ids.add(a['id'])
        for attr in ['href', 'src']:
            if attr in a: self.links.append(a[attr])
        if a.get('data-field') == '1':
            assert tag == 'input' and a.get('type') == 'text' and 'readonly' in a
            self.fields[a['id']] = a['value']

data = json.loads((ROOT/'data/labs.json').read_text(encoding='utf-8'))
validate(data)
pages = {p.resolve(): Page(p) for p in [ROOT/'index.html', *sorted((ROOT/'labs').glob('*.html'))]}
assert len(pages) == 14
links = 0
for path, page in pages.items():
    for link in page.links:
        url = urlsplit(link)
        assert not url.scheme and not url.netloc, 'site pages must be independent of external resources'
        target = (path.parent/unquote(url.path)).resolve() if url.path else path
        assert target.is_file(), f'broken link {path}: {link}'
        if url.fragment:
            assert url.fragment in pages[target].ids, f'broken anchor {path}: {link}'
        links += 1
    assert '输入密码' not in path.read_text(encoding='utf-8')
fields = 0
for lab in data['labs']:
    page = pages[(ROOT/'labs'/f'{lab["id"]}.html').resolve()]
    for table in lab['tables']:
        for ri, row in enumerate(table['rows']):
            for ci, value in enumerate(row['values']):
                fid = f'{table["id"]}-r{ri}-c{ci}'
                if row['verified']:
                    assert page.fields[fid] == value, f'field mismatch {fid}'
                    fields += 1
                else:
                    assert fid not in page.fields, 'unverified data must not have copy fields'
print(f'PASS: {len(pages)} pages, {links} local links/anchors, {fields} exact string fields, no external page resources')
print('PASS: directory names, all values strings, source attribution, pending rows excluded from copying')
