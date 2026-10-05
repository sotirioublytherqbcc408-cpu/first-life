#!/usr/bin/env python3
# 校验 content/*.json：结构、条目覆盖、来源可达性
import json, glob, os, re, sys, subprocess
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.abspath(__file__))

def raw_titles():
    p = os.path.join(ROOT, 'outline', 'raw.json')
    if not os.path.exists(p):
        return set(), set()          # 没有原始大纲时跳过覆盖率检查
    secs = json.load(open(p, encoding='utf-8'))
    titles, headers = set(), set()
    for s in secs:
        for it in s['items']:
            if it.startswith('第一次'):
                titles.add(it)
            else:
                headers.add(it)
    return titles, headers

def check_url(u):
    try:
        r = subprocess.run(['curl', '-sIL', '-m', '20', '-o', '/dev/null', '-w', '%{http_code}', '-A', 'Mozilla/5.0', u],
                           capture_output=True, timeout=30)
        return u, r.stdout.decode().strip()
    except Exception as e:
        return u, 'ERR'

def main():
    titles, headers = raw_titles()
    files = sorted(glob.glob(os.path.join(ROOT, 'content', '*.json')))
    covered, problems, entries, sources = [], [], 0, set()
    print(f'{"篇":<28}{"原始":>6}{"合并":>6}{"比例":>7}{"条缺源":>8}')
    for f in files:
        try:
            d = json.load(open(f, encoding='utf-8'))
        except Exception as e:
            problems.append(f'{os.path.basename(f)}: JSON 解析失败 {e}'); continue
        es = d.get('entries', [])
        bad = 0
        for e in es:
            entries += 1
            for k in ('id', 'title', 'evidence'):
                if not e.get(k): problems.append(f'{d.get("section")} {e.get("id")}: 缺 {k}')
            if e.get('evidence') not in ('A', 'B', 'C'): problems.append(f'{e.get("id")}: evidence={e.get("evidence")} 不是 A/B/C')
            b = e.get('body') or {}
            if not b.get('plain'): problems.append(f'{e.get("id")}: 缺 body.plain')
            if not b.get('steps'): problems.append(f'{e.get("id")}: 缺 body.steps')
            if not (e.get('sources') or []): bad += 1; problems.append(f'{e.get("id")}: 没有出处')
            for s in (e.get('sources') or []):
                if not str(s.get('url', '')).startswith('http'): problems.append(f'{e.get("id")}: 出处 url 非法')
                else: sources.add(s['url'])
            covered += e.get('merged_from') or []
        src = d.get('source_count') or 0
        print(f'{d.get("section", os.path.basename(f)):<28}{src:>6}{len(es):>6}{(src/len(es) if es else 0):>6.1f}x{bad:>8}')
    missing = sorted(titles - set(covered))
    extra = sorted(set(covered) - titles)
    print(f'\n总计: 篇 {len(files)} | 条 {entries} | 唯一出处 {len(sources)}')
    print(f'原始标题覆盖: {len(titles & set(covered))}/{len(titles)}')
    if missing: print(f'⚠️ 未并入任何条目的原始标题 {len(missing)} 条:', missing[:12])
    if extra: print(f'⚠️ merged_from 里出现了大纲外的标题 {len(extra)} 条:', extra[:8])
    print(f'结构问题 {len(problems)} 处'); [print('   -', p) for p in problems[:20]]
    if sources and '--urls' in sys.argv:
        print('\n抽查出处可达性（全部唯一 URL）…')
        with ThreadPoolExecutor(max_workers=8) as ex:
            for u, code in ex.map(check_url, sorted(sources)):
                flag = '' if code.startswith('2') else '  ⚠️'
                print(f'  {code}  {u[:100]}{flag}')

def cross_checks():
    import collections
    files = sorted(glob.glob(os.path.join(ROOT, 'content', '*.json')))
    seen = collections.defaultdict(list)
    junk = []
    for f in files:
        d = json.load(open(f, encoding='utf-8'))
        for e in d.get('entries', []):
            for t in (e.get('merged_from') or []):
                seen[t].append(d.get('section'))
            if re.search(r'[A-Za-z]{2,}', e.get('title', '')):
                junk.append(e.get('title'))
    dup = {k: v for k, v in seen.items() if len(set(v)) > 1}
    other = {k: v for k, v in seen.items() if len(v) > 1 and len(set(v)) == 1}
    print(f'\n[跨篇重复] 同一原始标题被写进两篇 {len(dup)} 处')
    for k, v in list(dup.items())[:10]: print('   ', k, '→', sorted(set(v)))
    print(f'[同篇重复] 同一篇内重复引用 {len(other)} 处')
    for k, v in list(other.items())[:5]: print('   ', k, '×', len(v))
    if junk: print('[可疑标题] 含英文/异常的条目:', junk[:10])

def field_checks():
    import collections
    files = sorted(glob.glob(os.path.join(ROOT, 'content', '*.json')))
    ids = collections.Counter(); issues = []
    for f in files:
        d = json.load(open(f, encoding='utf-8'))
        for e in d.get('entries', []):
            ids[e['id']] += 1
            if not (e.get('tags') or []): issues.append(f"{e['id']}: 没有 tags")
            c = e.get('cost') or {}
            if not c.get('money') or not c.get('time') or c.get('willpower') not in ('低', '中', '高', '因人而异'):
                issues.append(f"{e['id']}: cost 字段不全 {c}")
            if not e.get('addition') and not (e.get('merged_from') or []):
                issues.append(f"{e['id']}: 非增补条目却没有 merged_from")
            if e.get('addition') and not e.get('why'):
                issues.append(f"{e['id']}: 增补条目没有 why")
            n = len((e.get('body') or {}).get('plain', '')) + sum(len(x) for x in (e['body'].get('steps') or []))
            if n < 80: issues.append(f"{e['id']}: 正文过短（{n} 字）")
    dup = {k: v for k, v in ids.items() if v > 1}
    print(f'\n[字段校验] id 唯一性: {"通过" if not dup else dup}')
    print(f'[字段校验] 问题 {len(issues)} 处')
    for i in issues[:15]: print('   -', i)

if __name__ == '__main__':
    main()
    if '--cross' in sys.argv:
        cross_checks()
    if '--fields' in sys.argv:
        field_checks()
