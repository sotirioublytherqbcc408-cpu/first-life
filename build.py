#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第一次的人生 · 静态站点生成器

  content/*.json  ──┐
  web/app.css,app.js ─┴─►  docs/            首页 + 438 个条目页 + 18 个篇章页 + 离线单文件版
                            docs/sitemap.xml, robots.txt, .nojekyll, CNAME

用法：
  python3 build.py                                  # 部署在域名根目录（默认）
  python3 build.py --base /first-life/ --url https://user.github.io/first-life
                                                    # 部署在子路径（GitHub Pages 项目站）

改内容只动 content/ 下的 JSON，然后重跑本脚本即可。
"""
import json, glob, os, re, html, shutil, argparse, datetime

ROOT = os.path.dirname(os.path.abspath(__file__))     # 仓库根目录（脚本所在处）
CONTENT = os.path.join(ROOT, 'content')
WEB = os.path.join(ROOT, 'web')

BASE_PATH = '/'
SITE_URL = 'https://thefirst.easymoreai.com'
CNAME = 'thefirst.easymoreai.com'

EMOJI = re.compile('[\U0001F000-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF\uFE0F\u200D\u20E3]')

def u(path=''):
    """把站内绝对路径拼上部署前缀：u('entry/x/') -> /entry/x/ 或 /repo/entry/x/"""
    p = path.lstrip('/')
    base = BASE_PATH if BASE_PATH.endswith('/') else BASE_PATH + '/'
    return base + p

def clean_label(section):
    s = re.sub(r'^\s*[0-9]+\s*', '', section or '')
    s = EMOJI.sub('', s)
    s = re.sub(r'[（(][^）)]*[）)]', '', s)
    s = s.replace('/', '、').replace('／', '、')
    return re.sub(r'\s{2,}', ' ', s).strip() or section

def e(x):
    return html.escape(str(x), quote=True)

# ---------------------------------------------------------------- 图标（线性 1.5px）
def ico(paths, size=28):
    return ('<svg class="ico" width="%d" height="%d" viewBox="0 0 24 24" fill="none" '
            'stroke="currentColor" stroke-width="1.5" stroke-linecap="round" '
            'stroke-linejoin="round" aria-hidden="true">%s</svg>') % (size, size, paths)

ICONS = {
    'plane':  '<path d="M3 11l18-7-7 18-2.5-7.5L3 11z"/>',
    'home':   '<path d="M4 10.5L12 4l8 6.5V20a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1z"/><path d="M9.5 21v-6h5v6"/>',
    'card':   '<rect x="3" y="5.5" width="18" height="13" rx="2.5"/><path d="M3 10h18"/><path d="M7 14.5h3"/>',
    'book':   '<path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H19v15H6.5A2.5 2.5 0 0 0 4 20.5z"/><path d="M4 5.5v15"/>',
    'clip':   '<rect x="5" y="4" width="14" height="17" rx="2.5"/><path d="M9 4V2.8h6V4"/><path d="M9 12h6M12 9v6"/>',
    'shield': '<path d="M12 3l7.5 2.8v5.9c0 4.7-3.1 7.6-7.5 9.3-4.4-1.7-7.5-4.6-7.5-9.3V5.8z"/><path d="M9 12.2l2.2 2.2L15.2 10"/>',
}

CATS = [
    ('travel', '出行与旅行', '从买票进站、坐飞机住酒店，到出境过关', 'plane',  ['01', '02', '03', '15'], 'wide'),
    ('living', '生活与居住', '搬进新家、上路开车、下馆子',           'home',   ['04', '11', '17'],       ''),
    ('money',  '金钱与消费', '开卡借贷、买东西与退货维权',           'card',   ['05', '06'],             ''),
    ('work',   '学习与工作', '从选课考试到入职离职',                 'book',   ['07', '08'],             ''),
    ('public', '医疗与办事', '看病报销、办证与打官司',               'clip',   ['09', '10'],             ''),
    ('safety', '关系与安全', '与人相处、护住自己',                   'shield', ['12', '13', '14', '16', '18'], 'wide'),
]
SEC2CAT = {n: key for key, _, _, _, nums, _ in CATS for n in nums}

def load():
    secs = []
    for f in sorted(glob.glob(os.path.join(CONTENT, '*.json'))):
        d = json.load(open(f, encoding='utf-8'))
        if 'entries' not in d:
            continue
        d['num'] = os.path.basename(f)[:2]
        d['label'] = clean_label(d.get('section', ''))
        d['date'] = datetime.datetime.fromtimestamp(os.path.getmtime(f)).strftime('%Y-%m-%d')
        d['cat'] = SEC2CAT.get(d['num'], 'safety')
        for i, ent in enumerate(d['entries']):
            ent['_sec'] = d
            ent['_i'] = i
        secs.append(d)
    return secs

def effort_of(ent):
    return ((ent.get('cost') or {}).get('willpower') or '').strip()

def is_free(ent):
    m = ((ent.get('cost') or {}).get('money') or '').strip()
    return '1' if re.match(r'^0|^不花|免费|0 ?元', m) else '0'

def badge(ev):
    return '<span class="badge %s">证据 %s</span>' % ((ev or 'C').lower(), e(ev))

# ---------------------------------------------------------------- 页面外壳
def head(title, desc, canonical, extra=''):
    return '''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s</title>
<meta name="description" content="%s">
<link rel="canonical" href="%s">
<meta property="og:type" content="article">
<meta property="og:site_name" content="第一次的人生">
<meta property="og:title" content="%s">
<meta property="og:description" content="%s">
<meta property="og:url" content="%s">
<meta property="og:locale" content="zh_CN">
<meta name="twitter:card" content="summary">
<link rel="stylesheet" href="%s">
<noscript><style>.reveal{opacity:1!important;transform:none!important}.nav{position:static}</style></noscript>
%s</head>
<body>
<a class="skip" href="#main">跳到正文</a>
''' % (e(title), e(desc), e(canonical), e(title), e(desc), e(canonical), u('assets/app.css'), extra)

def nav():
    return '''<nav class="nav">
  <div class="nav-in">
    <a class="brand" href="%s">第一次的人生</a>
    <div class="nav-links">
      <a href="%s">篇章</a>
      <a href="%s">全部条目</a>
      <a href="%s">离线版</a>
    </div>
  </div>
</nav>
''' % (u(''), u('#categories'), u('#all'), u('offline.html'))

def footer():
    return '''<footer class="site">
  <div class="wrap">
    <div>内容仅供办事参考，具体以官方最新规定为准。本站不构成医疗、法律或投资建议。</div>
    <div class="fnote">
      站点形式参考 GitHub 开源项目 <a href="https://github.com/eternity4719/HowToLiveBetter" rel="noopener">高性价比人生指南（HowToLiveBetter）</a>，
      该项目以 CC BY 4.0 协议开源；本站正文由《第一次的人生》大纲整理、合并、增补而成，每条均标注官方依据与证据等级。
      证据分级：A 法规与官方文件，B 官方科普或权威媒体，C 经验性、多家一致。
    </div>
  </div>
</footer>
<script src="%s" defer></script>
</body>
</html>
''' % u('assets/app.js')

# ---------------------------------------------------------------- 首页
def render_home(secs):
    total = sum(len(s['entries']) for s in secs)

    freq = {}
    for s in secs:
        for en in s['entries']:
            for t in (en.get('tags') or []):
                freq[t] = freq.get(t, 0) + 1
    hot = [t for t, _ in sorted(freq.items(), key=lambda x: -x[1])[:18]]

    bento = []
    for key, label, desc, icon, nums, mod in CATS:
        n = sum(len(s['entries']) for s in secs if s['cat'] == key)
        bento.append('''<a class="card %s reveal" href="#cat-%s" data-cat="%s">
      %s<h3>%s</h3><p>%s</p><div class="count">%d 条 · %d 篇</div></a>''' % (
            mod, key, key, ico(ICONS[icon]), e(label), e(desc), n, len(nums)))

    blocks = []
    for key, label, desc, icon, nums, mod in CATS:
        inner = []
        for s in [x for x in secs if x['cat'] == key]:
            rows = []
            for en in s['entries']:
                tags = ' '.join(en.get('tags') or [])
                txt = re.sub(r'\s+', ' ', (en['title'] + ' ' + (en.get('body', {}).get('plain') or '') + ' ' + tags)).lower()
                rows.append('''<li><a class="row" href="%s" data-row data-cat="%s" data-group="%s" data-ev="%s" data-eff="%s" data-free="%s" data-text="%s">
          <span class="t">%s</span>%s<span class="effort">%s</span></a></li>''' % (
                    u('entry/%s/' % en['id']), key, e(s['num']), e(en.get('evidence', 'C')), e(effort_of(en)),
                    is_free(en), e(txt), e(en['title']),
                    ('<span class="badge add">增补</span>' if en.get('addition') else ''), e(effort_of(en) or '—')))
            inner.append('''<div class="secgroup" data-group="%s">
        <h4><a href="%s">%s</a></h4>
        <p class="sechint">%d 条</p>
        <ul class="rows">%s</ul>
      </div>''' % (e(s['num']), u('section/%s/' % s['num']), e(s['label']), len(s['entries']), ''.join(rows)))
        blocks.append('''<div class="catlist" data-block id="cat-%s">
      <h3>%s</h3><p class="catmeta">%s</p>
      %s
    </div>''' % (key, e(label), e(desc), ''.join(inner)))

    seg_ev = ''.join('<button type="button" data-filter="ev" data-value="%s" aria-pressed="false">证据 %s</button>' % (g, g) for g in ['A', 'B', 'C'])
    seg_eff = ''.join('<button type="button" data-filter="eff" data-value="%s" aria-pressed="false">%s</button>' % (v, v) for v in ['低', '中', '高'])
    chips = ''.join('<button type="button" class="chip" data-kw="%s">%s</button>' % (e(t), e(t)) for t in hot)

    body = '''%s
<main id="main">
  <section class="hero">
    <div class="wrap">
      <h1>第一次的人生</h1>
      <p class="lede">每个人都会遇到、却没人教过的那些「第一次」。每条写清怎么办、容易踩什么坑、依据哪份官方文件。</p>
      <div class="searchbox">
        %s
        <input id="q" type="search" placeholder="搜一件事，比如：退票、租房押金、劳动仲裁" autocomplete="off" aria-label="搜索条目">
      </div>
      <p class="searchmeta" id="searchmeta"></p>
    </div>
  </section>

  <section class="block alt" id="filters">
    <div class="wrap">
      <div class="filters">
        <div class="fgroup"><span class="flabel">证据等级</span><div class="seg" role="group" aria-label="按证据等级筛选">%s</div></div>
        <div class="fgroup"><span class="flabel">花多少力气</span><div class="seg" role="group" aria-label="按花费力气筛选">%s</div>
          <button type="button" class="chip" data-filter="free" aria-pressed="false">不花钱</button></div>
        <div class="fgroup"><span class="flabel">热门关键词</span><div class="chiprow">%s</div></div>
      </div>
    </div>
  </section>

  <section class="block" id="categories">
    <div class="wrap">
      <h2 class="h2">六个篇章</h2>
      <p class="sub">按你正要做的事找，不用先想它属于哪一类。</p>
      <div class="bento">%s</div>
    </div>
  </section>

  <section class="block alt" id="all">
    <div class="wrap js-list-start">
      <h2 class="h2">全部条目</h2>
      <p class="sub">%d 条，每条都有自己的页面，点进去看「怎么办 / 坑 / 依据」。</p>
      %s
      <div class="empty" id="empty" hidden><span class="big">没有匹配的条目</span>换个词试试，比如「退票」「医保」「AED」；也可以 <button type="button" class="chip" id="resetall">清空筛选</button></div>
    </div>
  </section>
</main>
%s''' % (nav(),
         ico('<circle cx="11" cy="11" r="7"/><path d="M16.5 16.5L21 21"/>', 20),
         seg_ev, seg_eff, chips, ''.join(bento), total, ''.join(blocks), footer())

    return head('第一次的人生 · 第一次做事之前，先看这一页',
                '把每个人都会遇到、却没人教过的「第一次」写成可检索的说明书：出行、金钱、办事、医疗、工作、安全。共 %d 条，每条写清怎么办、容易踩什么坑、依据哪份官方文件。' % total,
                SITE_URL + '/',
                extra='<script type="application/ld+json">%s</script>\n' % json.dumps({
                    "@context": "https://schema.org", "@type": "WebSite", "name": "第一次的人生",
                    "url": SITE_URL + "/", "inLanguage": "zh-CN",
                    "description": "把每个人都会遇到、却没人教过的「第一次」写成可检索的说明书"}, ensure_ascii=False)) + body

# ---------------------------------------------------------------- 条目页
def render_entry(en, sec, prev_en, next_en):
    url = '%s/entry/%s/' % (SITE_URL, en['id'])
    steps = ''.join('<li>%s</li>' % e(x) for x in (en.get('body', {}).get('steps') or []))
    pits = ''.join('<li>%s</li>' % e(x) for x in (en.get('body', {}).get('pitfalls') or []))
    srcs = ''.join('<li><a href="%s" rel="noopener nofollow">%s</a><div class="note">%s</div></li>' % (
        e(s.get('url', '#')), e(s.get('name', '')), e(s.get('note', ''))) for s in (en.get('sources') or []))
    mf = en.get('merged_from') or []
    merged = ('<section><h2>它覆盖了哪些「第一次」</h2><ul class="steps">%s</ul></section>' % ''.join('<li>%s</li>' % e(x) for x in mf)) if mf else ''
    why = ('<section><h2>为什么补这一条</h2><p>%s</p></section>' % e(en.get('why', ''))) if en.get('addition') else ''
    cost = en.get('cost') or {}
    meta = [badge(en.get('evidence', 'C'))]
    if en.get('addition'):
        meta.append('<span class="badge add">增补</span>')
    for label, key in (('花费', 'money'), ('耗时', 'time'), ('力气', 'willpower')):
        if cost.get(key):
            meta.append('<span>%s：%s</span>' % (label, e(cost[key])))
    meta.append('<span>最后核对：%s</span>' % e(sec.get('date', '')))

    pager = ['<a href="%s">← 返回%s</a>' % (u('section/%s/' % sec['num']), e(sec['label'])),
             '<span class="mid">第 %d / %d 条</span>' % (en['_i'] + 1, len(sec['entries']))]
    pager.append(('<a href="%s">下一条：%s →</a>' % (u('entry/%s/' % next_en['id']), e(next_en['title'][:18]))) if next_en else '<span class="mid">已是最后一条</span>')
    prevline = ('<div class="pager"><a href="%s">← 上一条：%s</a><span class="mid"></span><span class="mid"></span></div>' % (
        u('entry/%s/' % prev_en['id']), e(prev_en['title'][:18]))) if prev_en else ''

    body = '''%s
<main id="main" class="article">
  <div class="wrap">
    <nav class="crumb" aria-label="面包屑"><a href="%s">首页</a> / <a href="%s">%s</a></nav>
    <h1>%s</h1>
    <div class="meta">%s</div>
    <div class="detail narrow">
      <section><h2>怎么办</h2><p>%s</p>%s</section>
      <section><h2>容易踩什么坑</h2><div class="pit"><ul>%s</ul></div></section>
      <section><h2>依据</h2><ul class="src">%s</ul></section>
      %s%s
    </div>
    %s
    <div class="pager">%s</div>
  </div>
</main>
%s''' % (nav(), u(''), u('section/%s/' % sec['num']), e(sec['label']), e(en['title']), ''.join(meta),
         e(en.get('body', {}).get('plain', '')),
         ('<ol class="steps">%s</ol>' % steps) if steps else '',
         pits or '<li>—</li>', srcs, merged, why, prevline, ''.join(pager), footer())

    ld = json.dumps({
        "@context": "https://schema.org", "@type": "Article",
        "headline": en['title'], "inLanguage": "zh-CN",
        "dateModified": sec.get('date', ''), "url": url,
        "isPartOf": {"@type": "WebSite", "name": "第一次的人生", "url": SITE_URL + "/"},
        "articleSection": sec['label'],
        "citation": [s.get('name', '') for s in (en.get('sources') or [])],
    }, ensure_ascii=False)

    return head('%s · 第一次的人生' % en['title'],
                (en.get('body', {}).get('plain', '') or en['title'])[:110],
                url, extra='<script type="application/ld+json">%s</script>\n' % ld) + body

# ---------------------------------------------------------------- 篇章页
def render_section(sec, secs):
    rows = ''.join('''<li><a class="row" href="%s"><span class="t">%s</span>%s<span class="effort">%s</span></a></li>''' % (
        u('entry/%s/' % en['id']), e(en['title']), badge(en.get('evidence', 'C')), e(effort_of(en) or '—'))
        for en in sec['entries'])
    others = ''.join('''<li><a class="row" href="%s"><span class="t">%s</span><span class="effort">%d 条</span></a></li>''' % (
        u('section/%s/' % s['num']), e(s['label']), len(s['entries'])) for s in secs if s['num'] != sec['num'])
    body = '''%s
<main id="main" class="article">
  <div class="wrap">
    <nav class="crumb" aria-label="面包屑"><a href="%s">首页</a> / %s</nav>
    <h1>%s</h1>
    <div class="meta"><span>%d 条</span><span>原大纲 %d 条合并而来</span><span>最后核对：%s</span></div>
    <ul class="rows">%s</ul>
    <h2 class="h2" style="margin-top:var(--s7)">其他篇章</h2>
    <ul class="rows">%s</ul>
  </div>
</main>
%s''' % (nav(), u(''), e(sec['label']), e(sec['label']), len(sec['entries']), sec.get('source_count', 0),
         e(sec.get('date', '')), rows, others, footer())
    return head('%s · 第一次的人生' % sec['label'],
                '「%s」共 %d 条：%s' % (sec['label'], len(sec['entries']), '、'.join(x['title'][:16] for x in sec['entries'][:6])),
                '%s/section/%s/' % (SITE_URL, sec['num'])) + body

# ---------------------------------------------------------------- 离线单文件版
def render_offline(secs):
    css = open(os.path.join(WEB, 'app.css'), encoding='utf-8').read()
    payload = [{'label': s['label'], 'num': s['num'], 'entries': [
        {'id': x['id'], 't': x['title'], 'ev': x.get('evidence', 'C'), 'eff': effort_of(x),
         'plain': x.get('body', {}).get('plain', ''),
         'steps': x.get('body', {}).get('steps') or [], 'pits': x.get('body', {}).get('pitfalls') or [],
         'src': [{'n': y.get('name', ''), 'u': y.get('url', '')} for y in (x.get('sources') or [])]}
        for x in s['entries']]} for s in secs]
    data = json.dumps(payload, ensure_ascii=False, separators=(',', ':'))
    return '''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>第一次的人生 · 离线版（单文件）</title>
<meta name="robots" content="noindex">
<style>%s
.off{max-width:760px}
.off article{background:var(--bg-alt);border-radius:var(--r-card);padding:var(--s4);margin:0 0 var(--s2)}
.off h3{margin:0 0 var(--s1);font-size:var(--fs-h3);font-weight:600}
.off .m{display:flex;gap:var(--s2);flex-wrap:wrap;color:var(--fg-2);font-size:var(--fs-cap);margin-bottom:var(--s2)}
.off details summary{cursor:pointer;color:var(--accent);font-size:var(--fs-sm)}
</style>
</head>
<body>
<nav class="nav"><div class="nav-in"><a class="brand" href="%s">第一次的人生</a>
<div class="nav-links"><a href="%s">在线版</a></div></div></nav>
<main class="article"><div class="wrap">
<h1>离线版 · 整本书在一个文件里</h1>
<p style="color:var(--fg-2)">断网、发给别人、放到手机上都能打开。搜索框支持即时过滤。</p>
<div class="searchbox" style="margin:var(--s5) 0 var(--s3)">
  %s
  <input id="q" type="search" placeholder="搜：退票、医保、AED" autocomplete="off" aria-label="搜索">
</div>
<p class="searchmeta" id="searchmeta"></p>
<div id="list" class="off"></div>
</div></main>
%s
<script>
var DATA=%s;
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
function render(q){
  q=(q||'').trim().toLowerCase(); var out='',n=0;
  DATA.forEach(function(sec){
    var items=sec.entries.filter(function(x){
      if(!q) return true;
      return (x.t+x.plain+x.steps.join('')+x.pits.join('')+x.src.map(function(s){return s.n;}).join('')).toLowerCase().indexOf(q)>=0;
    });
    if(!items.length) return; n+=items.length;
    out+='<h2 class="h2" style="margin-top:var(--s6)">'+esc(sec.label)+'</h2>';
    items.forEach(function(x){
      out+='<article id="'+x.id+'"><h3>'+esc(x.t)+'</h3><div class="m"><span class="badge '+x.ev.toLowerCase()+'">证据 '+esc(x.ev)+'</span><span>力气 '+esc(x.eff||'—')+'</span></div>'
        +'<p>'+esc(x.plain)+'</p><details><summary>怎么做 / 坑 / 依据</summary><ol class="steps">'
        +x.steps.map(function(s){return '<li>'+esc(s)+'</li>';}).join('')+'</ol>'
        +'<div class="pit" style="margin-top:var(--s2)"><ul>'+x.pits.map(function(s){return '<li>'+esc(s)+'</li>';}).join('')+'</ul></div>'
        +'<ul class="src" style="margin-top:var(--s2)">'+x.src.map(function(s){return '<li><a href="'+esc(s.u)+'">'+esc(s.n)+'</a></li>';}).join('')+'</ul>'
        +'</details></article>';
    });
  });
  document.getElementById('list').innerHTML=out||'<p class="empty">没有匹配的条目，换个词试试。</p>';
  document.getElementById('searchmeta').textContent = q? ('找到 '+n+' 条') : ('共 '+DATA.reduce(function(a,s){return a+s.entries.length;},0)+' 条');
}
document.getElementById('q').addEventListener('input',function(ev){render(ev.target.value);});
render('');
</script>
</body></html>''' % (css, u(''), u(''), ico('<circle cx="11" cy="11" r="7"/><path d="M16.5 16.5L21 21"/>', 20), footer().split('<script')[0], data)

# ---------------------------------------------------------------- 输出
def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w', encoding='utf-8').write(text)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', default='/', help='部署路径前缀，子目录部署时用，例如 /first-life/')
    ap.add_argument('--url', default='https://thefirst.easymoreai.com', help='站点完整地址（写进 canonical / sitemap）')
    ap.add_argument('--cname', default='', help='自定义域名，写了就在产物里生成 CNAME 文件')
    ap.add_argument('--out', default='docs', help='输出目录，默认 docs（GitHub Pages 可直接发布）')
    args = ap.parse_args()

    global BASE_PATH, SITE_URL
    BASE_PATH = args.base if args.base.startswith('/') else '/' + args.base
    if not BASE_PATH.endswith('/'):
        BASE_PATH += '/'
    SITE_URL = args.url.rstrip('/')
    out = os.path.join(ROOT, args.out)

    secs = load()
    total = sum(len(s['entries']) for s in secs)

    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out, exist_ok=True)
    shutil.copytree(WEB, os.path.join(out, 'assets'))
    open(os.path.join(out, '.nojekyll'), 'w').write('')
    if args.cname:
        open(os.path.join(out, 'CNAME'), 'w').write(args.cname + '\n')

    write(os.path.join(out, 'index.html'), render_home(secs))
    for s in secs:
        write(os.path.join(out, 'section', s['num'], 'index.html'), render_section(s, secs))
        for i, en in enumerate(s['entries']):
            write(os.path.join(out, 'entry', en['id'], 'index.html'),
                  render_entry(en, s, s['entries'][i - 1] if i > 0 else None,
                               s['entries'][i + 1] if i + 1 < len(s['entries']) else None))
    write(os.path.join(out, 'offline.html'), render_offline(secs))

    urls = [SITE_URL + '/'] + ['%s/section/%s/' % (SITE_URL, s['num']) for s in secs] + \
           ['%s/entry/%s/' % (SITE_URL, en['id']) for s in secs for en in s['entries']]
    today = datetime.date.today().isoformat()
    write(os.path.join(out, 'sitemap.xml'),
          '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
          ''.join('  <url><loc>%s</loc><lastmod>%s</lastmod></url>\n' % (x, today) for x in urls) + '</urlset>\n')
    write(os.path.join(out, 'robots.txt'),
          'User-agent: *\nAllow: /\nDisallow: /offline.html\nSitemap: %s/sitemap.xml\n' % SITE_URL)

    print('输出目录   %s  (base=%s, url=%s)' % (args.out, BASE_PATH, SITE_URL))
    print('首页       index.html')
    print('条目页     %d 个' % total)
    print('篇章页     %d 个' % len(secs))
    print('离线版     offline.html')
    print('站点地图   %d 个 URL' % len(urls))

if __name__ == '__main__':
    main()
