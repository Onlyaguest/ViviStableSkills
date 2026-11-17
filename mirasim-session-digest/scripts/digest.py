#!/usr/bin/env python3
"""session-digest：给空间里的某个人出「会话摘要」——先是按时间的活动记录，后面每个会话一份摘要；
每天只补上次以后的新轮次。只读源会话和聊天记录，不改它们。

  python3 digest.py init  --user <uid|名字> [--requester <uid|名字>] [--dir DIR] [--days N | --since 'YYYY-MM-DD HH:MM'] [--title 标题]
  python3 digest.py prep  --dir DIR [--end ISO]     # 找新轮次，出材料包 work/packets/<label>/batchN.txt
  （写事件：照 references/writer-guide.md，每批写 work/out/<label>/batchN.json）
  python3 digest.py check --dir DIR <label>         # 只检查事件文件，不并
  python3 digest.py merge --dir DIR <label>         # 并进底库，重出 md + html，打印本次新增
  python3 digest.py html  --dir DIR                 # 只从 md 重出网页
  python3 digest.py status --dir DIR

DIR 里的东西：config.json（给谁出、谁要的、标签）、<标题>.md、<标题>.html、activity-digest.md、summaries/、
manifest.json、data/（底库和进度）、work/（材料包和事件）、历史版/（每次一份快照）。
重的命令前加 nice -n 10。环境变量 MIRASIM_HOME 可改 ~/.mirasim 的位置。
"""
import json, os, re, sys, glob, html, datetime, collections, argparse
try:
    import fcntl
except ImportError:  # Windows 上没有，就不加锁
    fcntl = None

M = os.environ.get('MIRASIM_HOME') or os.path.expanduser('~/.mirasim')
CHAT = f'{M}/chat'
TZ = datetime.timezone(datetime.timedelta(hours=8))
DEFAULT_TAGS = ['#产品与研发', '#运营与增长', '#客户与支持', '#内容与宣传', '#数据与分析',
                '#定价与额度', '#团队与协作', '#固定任务与报表', '#助手怎么用']
FALLBACK_TAG = '#其他'
STATUS = {'已完成', '进行中', '中断', '失败', '阻塞或等待', '等待验收', '无新增产物'}
AUTO = {'自动任务', '自动派生'}
INCLUDE = {'her', 'task', 'sched', 'matrix'}
EMAIL = re.compile(r'[\w.+-]+@[\w-]+\.[\w.]+')
SECRET = re.compile(r'(sk-[\w-]{10,}|ghp_\w{10,}|gho_\w{10,}|AKIA\w{12,}|xox[bp]-[\w-]{10,}|(?:token|key|secret)=[\w-]{10,})', re.I)
SELF_MARKS = ['会话摘要每日增量', 'session-digest 每日增量']
ASSIST0 = {'Claude', 'Mira Bot', 'mira bot', 'Matrix', 'Codex'}


# ---------------------------------------------------------------- 小工具
def load(p, d=None):
    try:
        return json.load(open(p, encoding='utf-8'))
    except (FileNotFoundError, json.JSONDecodeError):
        return d


def save(p, o):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = p + '.tmp'
    json.dump(o, open(tmp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    os.replace(tmp, p)


def jsonl(p):
    if not os.path.exists(p):
        return
    for l in open(p, encoding='utf-8'):
        try:
            yield json.loads(l)
        except Exception:
            continue


def now_iso():
    return datetime.datetime.now(TZ).replace(second=0, microsecond=0).isoformat()


def ts(ms):
    return datetime.datetime.fromtimestamp(int(ms) / 1000, TZ) if ms else None


def hm(iso):
    return iso[:16].replace('T', ' ') if iso else '?'


def bj(iso):
    if not iso:
        return '未知'
    return datetime.datetime.fromisoformat(iso.replace('Z', '+00:00')).astimezone(TZ).strftime('%Y-%m-%d %H:%M:%S')


def loc(key):
    """会话链接：在 mirasim 里点开就进那个会话。"""
    ag, sid = key.split(':', 1)
    return f'mirasim://session/{ag}/{sid}'


def path_of(key):
    ag, sid = key.split(':', 1)
    return f'~/.mirasim/sessions/{ag}/{sid}/'


def cj(s):
    """拉丁字母或数字结尾的名字后面接中文时，中间加个空格。"""
    return s + ' ' if s and s[-1].isascii() and s[-1].isalnum() else s


def slug(t):
    t = re.sub(r'[\\/:*?"<>|\s「」『』《》（）()，,。.!！？?、；;：]+', '', t or '')
    return t[:14] or '会话'


def clean(x):
    return SECRET.sub('[密钥略]', EMAIL.sub('[邮箱略]', x or ''))


def is_wait(x, e):
    """等这个人定的：阻塞或等待，下一步里有「等<名字>」（不管中间有没有空格）。"""
    return e.get('status') == '阻塞或等待' and re.sub(r'\s', '', x.wait_word) in re.sub(r'\s', '', e.get('next') or '')


def assistant_names():
    m = {}
    for a in (load(f'{CHAT}/assistants.json', {}) or {}).get('assistants') or []:
        if a.get('id'):
            m[a['id']] = m['ai-' + a['id']] = a.get('name') or a['id']
    return m


class Ctx:
    """一个人的摘要：配置和所有路径。"""

    def __init__(self, d):
        self.dir = os.path.abspath(os.path.expanduser(d))
        self.cfg = load(f'{self.dir}/config.json')
        if not self.cfg:
            sys.exit(f'{self.dir} 里没有 config.json，先跑 init')
        c = self.cfg
        self.U, self.R = c['target'], c['requester']
        self.names = set(c['names'])
        self.display = c['display']
        self.dn = cj(self.display)
        self.self_mode = self.U == self.R
        self.you = '你' if self.self_mode else self.display
        self.wait_word = c.get('wait_word') or f'等{self.you}'
        self.tags = list(c.get('tags') or DEFAULT_TAGS)
        if FALLBACK_TAG not in self.tags:
            self.tags.append(FALLBACK_TAG)
        self.title = c['title']
        self.work = f'{self.dir}/work'
        self.data = f'{self.dir}/data'
        self.store_p = f'{self.data}/store.json'
        self.state_p = f'{self.data}/state.json'
        self.md = f'{self.dir}/{self.title}.md'
        self.html = f'{self.dir}/{self.title}.html'


# ---------------------------------------------------------------- 人和可读范围
def members():
    out = {}
    for m in (load(f'{CHAT}/members.json', {}) or {}).get('members', []):
        out[m['uid']] = m.get('name') or ''
    return out


def profile(uid):
    return load(f'{CHAT}/users/{uid}/profile.json', {}) or {}


def resolve_user(arg):
    if not arg:
        return None
    if arg.startswith('usr_'):
        return arg
    hits = set()
    a = arg.strip().lower()
    for p in glob.glob(f'{CHAT}/users/usr_*/profile.json'):
        j = load(p, {}) or {}
        ns = [j.get('name') or ''] + list(j.get('formerNames') or [])
        if any(n and n.lower() == a for n in ns):
            hits.add(j.get('uid'))
    for uid, n in members().items():
        if n and n.lower() == a:
            hits.add(uid)
    if len(hits) != 1:
        sys.exit(f'认不出「{arg}」是谁：{sorted(hits) or "没找到"}；请直接给 usr_ 开头的 uid')
    return hits.pop()


def names_of(uid):
    p = profile(uid)
    ns = {p.get('name')} | set(p.get('formerNames') or []) | {members().get(uid)}
    return sorted(n for n in ns if n)


_room_cache = {}


def room_members(room):
    if room not in _room_cache:
        j = load(f'{CHAT}/rooms/{room}/room.json') or load(f'{CHAT}/rooms/{room}/room.json.before-reinsert') or {}
        _room_cache[room] = j.get('members')
    return _room_cache[room]


def readable(room, R):
    """请求人能看的地方：大厅、事项、会话评论、没有成员名单的群；私信和有成员名单的群只在他本人在里面时。"""
    if not room:
        return False
    if room in ('general', 'items') or room.startswith('s-'):
        return True
    if room.startswith('dm-'):
        return R in room[3:].split('+')
    mem = room_members(room)
    if mem is None:
        return False  # 看不到成员名单就当不能读
    return R in mem


# ---------------------------------------------------------------- 找会话（来源 A–G）
def find_candidates(x):
    U, R = x.U, x.R
    cands = collections.defaultdict(lambda: {'via': set(), 'asked': set(), 'ai': set()})

    def add(key, via, asked=None, ai=None):
        if key and ':' in key:
            cands[key]['via'].add(via)
            if asked:
                cands[key]['asked'].add(asked)
            if ai:
                cands[key]['ai'].add(ai)

    hers, lines, skipped_rooms = set(), [], set()
    for f in sorted(glob.glob(f'{CHAT}/rooms/*/log/*.jsonl')):
        room = f.split('/rooms/')[1].split('/')[0]
        if not readable(room, R):
            skipped_rooms.add(room)
            continue
        for r in jsonl(f):
            lines.append((room, r))
            if r.get('by') == U and r.get('seq') is not None:
                hers.add((room, r['seq']))
                for s in r.get('sessions') or []:
                    add(s, 'C', f'{room}#{r["seq"]}')
    # A 助手接她的话；B 派单卡问的是她那条
    for room, r in lines:
        c = r.get('card')
        if not isinstance(c, dict):
            continue
        t, s = c.get('type'), c.get('session')
        if t in ('assist', 'ask') and s and (room, c.get('request')) in hers:
            add(s, 'A', f'{room}#{c["request"]}', r.get('by') if str(r.get('by')).startswith('ai-') else None)
        elif t == 'dispatch' and s:
            a = c.get('asked')
            if isinstance(a, dict) and (a.get('room'), a.get('seq')) in hers:
                add(s, 'B', f'{a["room"]}#{a["seq"]}', c.get('assistant'))
            elif not a and (room, r.get('reply')) in hers:
                add(s, 'B', f'{room}#{r["reply"]}', c.get('assistant'))
    # D 任务账本
    for k, t in ((load(f'{CHAT}/assistants/dispatched.json', {}) or {}).get('tasks') or {}).items():
        o = t.get('origin') or {}
        if t.get('requester') == U and readable(o.get('room'), R):
            add(k, 'D', f'{o.get("room")}#{o.get("seq")}', t.get('assistant'))
    # E 工作台里她自己开、自己说的：只有给本人出时才算
    if x.self_mode:
        for r in jsonl(f'{M}/collab/turns.jsonl'):
            b = r.get('by')
            b = b.get('userId') if isinstance(b, dict) else b
            if b == U:
                add(r.get('k'), 'E')
    # F 定时任务
    mine, names = set(), {}
    if x.self_mode:
        for sid, u in ((load(f'{M}/schedules/setters.json', {}) or {}).get('setters') or {}).items():
            if u == U:
                mine.add(sid)
    for s in (load(f'{M}/schedules.json', {}) or {}).get('schedules') or []:
        names[s.get('id')] = s.get('name')

    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, dict) and U in (v.get('requester'), v.get('for'), v.get('setter')):
                    if x.self_mode or readable(v.get('room'), R):
                        mine.add(k)
                        names.setdefault(k, v.get('name') or (v.get('prompt') or '')[:40])
                walk(v)
    walk(load(f'{M}/schedules/assistants.json', {}) or {})
    runs = collections.Counter()
    for r in jsonl(f'{M}/schedules/runs.jsonl'):
        if r.get('scheduleId') in mine and r.get('sessionKey'):
            add(r['sessionKey'], 'F', 'sched:' + r['scheduleId'])
            runs[r['scheduleId']] += 1
    # G Matrix 自动接她的话
    pat = re.compile(r'^【Matrix】回复 · ([\w+\-]+)#(\d+)')
    for rec in glob.glob(f'{M}/sessions/*/*/record.json'):
        j = load(rec) or {}
        m = pat.match(j.get('title') or '')
        if m and (m.group(1), int(m.group(2))) in hers:
            add(f'{j.get("agent")}:{j.get("sessionId")}', 'G', f'{m.group(1)}#{m.group(2)}')
    out = []
    for k, c in cands.items():
        ag, sid = k.split(':', 1)
        p = f'{M}/sessions/{ag}/{sid}/record.json'
        meta = {}
        if os.path.exists(p):
            j = load(p) or {}
            meta = {f: j.get(f) for f in ('createdAt', 'updatedAt', 'workdir', 'title', 'runState')}
        out.append({'key': k, 'via': sorted(c['via']), 'asked': sorted(c['asked']), 'assistants': sorted(c['ai']),
                    'exists': os.path.exists(p), **meta})
    out.sort(key=lambda s: s.get('createdAt') or '')
    save(f'{x.work}/candidates.json', {'target_messages': len(hers), 'skipped_rooms': len(skipped_rooms),
                                       'schedules': {s: [names.get(s), runs[s]] for s in mine}, 'sessions': out})
    return out, len(hers), len(skipped_rooms)


# ---------------------------------------------------------------- 逐轮判定谁触发
FROM = re.compile(r'(?:From|来自)\s+(?:DM|#\s*[^·\n]{0,30}|[^·\n]{0,30})\s*·\s*([^\[\n—]{1,40}?)\s*(?:\[(usr_[0-9a-f]+|ai-[\w-]+)\])?\s*—\s*([\w+\-]+#\d+)')
OWN = re.compile(r"^(.{1,40}?)'s own words \(([\w+\-]+#\d+)")


def strip_wrapper(p):
    if OWN.match(p):
        body = p.split('\n', 1)[1] if '\n' in p else p
        return body.split("\n\nMira Bot's notes")[0].strip()[:600]
    return re.split(r'\n\s*——\s*\n', p)[0].strip()[:600]


def classify_turns(x, cands):
    U, names = x.U, x.names
    col = {}
    for r in jsonl(f'{M}/collab/turns.jsonl'):
        if r.get('t') == 'turn':
            b = r.get('by')
            col[r.get('id')] = (b.get('userId'), b.get('label')) if isinstance(b, dict) else (b, b)
    assist = set(ASSIST0)
    for a in (load(f'{CHAT}/assistants.json', {}) or {}).get('assistants') or []:
        assist |= {a.get('name'), a.get('id')}
    name_re = re.compile('|'.join(re.escape(n) for n in names)) if names else None
    her_texts = []
    for f in glob.glob(f'{CHAT}/rooms/*/log/*.jsonl'):
        room = f.split('/rooms/')[1].split('/')[0]
        if not readable(room, x.R):
            continue
        for l in open(f, encoding='utf-8'):
            if U in l:
                try:
                    r = json.loads(l)
                except Exception:
                    continue
                if r.get('by') == U and r.get('sessions'):
                    her_texts.append(re.sub(r'@对话\S*|\s+', '', r.get('text') or ''))

    def who_of(r, p, created_by_her):
        tid = r.get('taskId')
        if tid in col:
            u, lab = col[tid]
            return ('her', None) if u == U else ('other:' + str(lab), None)
        if not p.strip() or p.lstrip().startswith(('<task-notification', '[SYSTEM NOTIFICATION', '<system-reminder')):
            return ('cont', None)
        m = OWN.match(p)
        if m:
            return ('her' if m.group(1).strip() in names else 'other:' + m.group(1).strip(), m.group(2))
        if any(s in p[:600] for s in SELF_MARKS + list(x.cfg.get('self_marks') or [])):
            return ('self', None)
        if p.startswith(('你在跑定时任务', '(Your scheduled task', '（你设的定时任务')):
            return ('sched', None)
        if p.startswith('【Matrix】'):
            return ('matrix', None)
        head = re.search(r'\n\s*——\s*\n((?:From|来自)[^\n]*)', p)
        ms = FROM.findall(head.group(1)) if head else []
        if ms:
            name, uid, at = ms[0]
            if uid == U or (not uid and name.strip() in names):
                return ('her', at)
            return ('other:' + name.strip(), at)
        if created_by_her:
            return ('her', None)
        return ('unknown', None)

    def fix(who, ask, via):
        if who.startswith('other:') and who[6:] in assist and name_re and name_re.search(ask[:300]):
            return 'task'
        if who == 'unknown' and via == ['C']:
            a = re.sub(r'\s+', '', ask)
            return 'her' if a and any(a in t for t in her_texts) else 'other:原会话主人'
        return who

    seen, out, stat = set(), [], collections.Counter()
    for c in cands:
        if not c['exists']:
            continue
        ag, sid = c['key'].split(':', 1)
        tp = f'{M}/sessions/{ag}/{sid}/turns.jsonl'
        if not os.path.exists(tp):
            continue
        created_by_her = 'E' in c['via']
        turns, prev = [], None
        for r in jsonl(tp):
            tid, p = r.get('taskId'), r.get('prompt') or ''
            who, at = who_of(r, p, created_by_her)
            who = fix(who, strip_wrapper(p), c['via'])
            if at and not readable(at.split('#')[0], x.R):
                who = 'hidden'  # 这一轮来自请求人看不到的私信或私密群：不纳入
            if who == 'cont':
                eff = prev or 'unknown'
            else:
                eff = prev = who
            dup = tid in seen
            seen.add(tid)
            st, up = ts(r.get('startedAt')), ts(r.get('updatedAt'))
            turns.append({'taskId': tid, 'who': who, 'who_eff': eff, 'at': at, 'dup': dup,
                          'start': st.isoformat() if st else None, 'end': up.isoformat() if up else None,
                          'ask': strip_wrapper(p) if who != 'cont' else '',
                          'incomplete': r.get('incomplete'), 'error': r.get('error')})
            stat[('dup-' if dup else '') + eff.split(':')[0]] += 1
        out.append({**c, 'turns': turns})
    save(f'{x.work}/turns.json', out)
    return out, stat


# ---------------------------------------------------------------- init
def cmd_init(a):
    U = resolve_user(a.user)
    R = resolve_user(a.requester) or U
    ns = names_of(U)
    if not ns:
        sys.exit(f'{U} 在本机没有名字记录，确认 uid 对不对')
    display = profile(U).get('name') or members().get(U) or ns[0]
    rdisplay = profile(R).get('name') or members().get(R) or R
    d = os.path.abspath(os.path.expanduser(a.dir or (f'~/workspaces/session-digest/{U}' if U == R
                                                     else f'~/workspaces/session-digest/{U}-for-{R}')))
    if os.path.exists(f'{d}/config.json'):
        sys.exit(f'{d} 已经初始化过了（config.json 在），要重来先把这个目录挪走')
    if a.since:
        since = datetime.datetime.strptime(a.since, '%Y-%m-%d %H:%M').replace(tzinfo=TZ)
    else:
        since = datetime.datetime.now(TZ).replace(second=0, microsecond=0) - datetime.timedelta(days=a.days)
    title = a.title or f'{cj(display)}的会话摘要'
    cfg = {'target': U, 'requester': R, 'display': display, 'requester_display': rdisplay, 'names': ns, 'title': title,
           'since': since.isoformat(), 'tags': DEFAULT_TAGS, 'tags_confirmed': False,
           'created': now_iso(), 'max_batches': 8, 'batch_bytes': 110000}
    os.makedirs(d, exist_ok=True)
    save(f'{d}/config.json', cfg)
    save(f'{d}/data/store.json', {'windows': [], 'sessions': {}, 'excluded': [
        {'id': '本摘要自己的定时任务轮次', 'reason': '是这份摘要自己在跑，不算'},
        {'id': '同一会话里别人说的轮次', 'reason': '只计数，不纳入'}]})
    save(f'{d}/data/state.json', {'window_end': since.isoformat(), 'processed': []})
    print(json.dumps({'dir': d, 'target': U, 'display': display, 'names': ns, 'requester': R,
                      'mode': '给本人出' if U == R else '替别人出（只读请求人在里面的私信和群，工作台和本人私设的定时任务不读）',
                      'since': hm(since.isoformat()), 'title': title}, ensure_ascii=False, indent=1))


# ---------------------------------------------------------------- prep
def tid_of(key, t):
    return t.get('taskId') or f'{key}@{t.get("start") or t.get("end")}'


def full_answer(key, tid):
    ag, sid = key.split(':', 1)
    for r in jsonl(f'{M}/sessions/{ag}/{sid}/turns.jsonl'):
        if r.get('taskId') == tid:
            return r.get('text') or ''
    return ''


def group_of(s):
    v = set(s.get('via') or [])
    w = {t['who_eff'] for t in s.get('turns') or []}
    if 'F' in v or 'sched' in w:
        return '定时任务'
    if v & {'B', 'D'} or 'task' in w:
        return '派出去的任务'
    if v & {'A', 'C'} or any(t['who_eff'].startswith('other') for t in s.get('turns') or []):
        return '私信或群里@助手'
    if v == {'G'}:
        return 'Matrix 自动接话'
    return '工作台自己开的'


def cmd_prep(x, end=None, force=False):
    state, store = load(x.state_p), load(x.store_p)
    merged = {w['label'] for w in store['windows']}
    for ixp in glob.glob(f'{x.work}/packets/*/index.json'):
        pd = os.path.dirname(ixp)
        lb = os.path.basename(pd)
        age = (datetime.datetime.now().timestamp() - os.path.getmtime(ixp)) / 60
        if lb not in merged and not os.path.exists(f'{pd}/emptied') and age < 120 and not force:
            sys.exit(f'{lb} 的材料包 {int(age)} 分钟前出过、还没并：多半有人正在跑这份摘要，不要重出，接着写事件再 merge {lb}。'
                     '确定是你自己上次半路失败、要重出，加 --force')
    start, since = state['window_end'], x.cfg['since']
    end = end or now_iso()
    label = end[5:7] + end[8:10]
    if any(w['label'] == label for w in store['windows']):
        label += end[11:13] + end[14:16]
    cands, nh, nskip = find_candidates(x)
    S, stat = classify_turns(x, cands)
    processed = set(state['processed'])
    disp = (load(f'{CHAT}/assistants/dispatched.json', {}) or {}).get('tasks') or {}
    blocks, newtids, others = [], {}, 0
    an = assistant_names()
    who_lab = {'her': x.display, 'task': f'Mira Bot 按{x.dn}的话派活', 'sched': '定时任务触发',
               'matrix': f'Matrix 自动接{x.dn}的话', 'cont': '续跑（后台回来接着做）'}
    for s in S:
        key = s['key']
        fresh = [t for t in s['turns'] if tid_of(key, t) not in processed and since <= (t['start'] or t['end'] or '') < end]
        if not fresh:
            continue
        keep = [t for t in fresh if not t['dup'] and t['who_eff'].split(':')[0] in INCLUDE]
        newtids[key] = [tid_of(key, t) for t in fresh]
        others += len(fresh) - len(keep)
        if not any(t['who'] in INCLUDE for t in keep):
            if not keep or key not in store['sessions']:
                continue  # 只有续跑、又不在底库里：不单独成条
        old = store['sessions'].get(key)
        title = (disp.get(key, {}).get('title') or s.get('title') or '').split('\n')[0][:80]
        m = re.match(r'^[(（](?:Your scheduled task|你设的定时任务)\s*「([^」]+)」', title)
        if m:
            title = f'定时任务「{m.group(1)}」'
        title = re.sub(r'usr_[0-9a-f]{8,}', lambda u: members().get(u.group(0)) or profile(u.group(0)).get('name') or '某人', title)
        grp = old['group'] if old else group_of(s)
        L = [f'##### SESSION {key}', f'分组：{grp}', f'原标题：{clean(title)}',
             f'创建：{hm(bj(s["createdAt"]).replace(" ", "T")) if s.get("createdAt") else "未知"}；工作目录：{s.get("workdir")}',
             f'{x.dn}的触发消息：{", ".join(s.get("asked") or []) or "无（工作台直接说）"}',
             f'回话的助手：{"、".join(dict.fromkeys(an.get(i, i) for i in s.get("assistants") or [])) or "材料里看不出"}']
        if old:
            L.append('底库里这个会话已有的事（只供参考，不要重写）：' + '；'.join(
                f'{e["start"][5:]} {e["title"]}（{e["status"]}）' for e in old['events'][-8:]))
        else:
            L.append('这是底库里没有的新会话')
        for t in keep:
            ans = full_answer(key, t['taskId'])
            lim = 3500 if t['who'] != 'cont' else 2000
            if len(ans) > lim:
                ans = '…' + ans[-lim:]
            flag = ' [中断/未完成]' if str(t.get('incomplete')) == 'True' else ''
            L.append(f'--- 轮 · {hm(t["start"] or t["end"])}–{(t["end"] or "")[11:19]} · {who_lab.get(t["who"], t["who"])}{flag}'
                     f' · taskId {str(t["taskId"])[:8]}' + (f' · 消息 {t["at"]}' if t.get('at') else ''))
            if t['ask'] and t['who'] != 'cont':
                L.append('问：' + clean((t['ask'] if t['who'] != 'sched' else t['ask'][:300])[:1200]))
            L.append('答：' + (clean(ans.strip()) or '（空）'))
        blocks.append({'key': key, 'group': grp, 'title': title, 'txt': '\n'.join(L),
                       'tids': [str(t['taskId'])[:8] for t in keep], 'is_new': not old})
    d = f'{x.work}/packets/{label}'
    os.makedirs(d, exist_ok=True)
    for f in glob.glob(f'{d}/batch*.txt'):
        os.remove(f)
    total = sum(len(b['txt'].encode()) for b in blocks)
    n = max(1, min(int(x.cfg.get('max_batches', 8)), -(-total // int(x.cfg.get('batch_bytes', 110000)))))
    bins, size = [[] for _ in range(n)], [0] * n
    for b in sorted(blocks, key=lambda b: -len(b['txt'])):
        i = size.index(min(size))
        bins[i].append(b)
        size[i] += len(b['txt'].encode())
    batches = []
    for i, bn in enumerate(bins, 1):
        if bn:
            p = f'{d}/batch{i}.txt'
            open(p, 'w', encoding='utf-8').write('\n\n'.join(b['txt'] for b in sorted(bn, key=lambda b: b['key'])))
            batches.append({'batch': i, 'path': p, 'bytes': size[i - 1], 'sessions': [b['key'] for b in bn]})
    who_reads = ('就是本人：正文里称「你」' if x.self_mode else
                 f'请求人 {x.cfg.get("requester_display") or x.R}，不是{x.dn}本人：正文里直接写「{x.display}」，不要称「你」')
    bl = [f'# 这一次（{label}）写给谁', '',
          f'- 摘要对象：{x.display}（{x.U}）；材料里出现的这些名字都是这个人：{"、".join(sorted(x.names))}',
          f'- 读摘要的人：{who_reads}',
          f'- 窗口：{hm(start)}（含）至 {hm(end)}（不含），北京时间。start/end 落在窗口里；接着上次没跑完的轮次，start 可以早一点，最多早两天',
          f'- 等这个人拍板或回话的事：status 写「阻塞或等待」，next 以「{x.wait_word}」开头写清等什么，例如「{cj(x.wait_word)}定活动方案」',
          '- 标签只能从下面选一个：' + ' '.join(x.tags) + f'（都不合适才用 {FALLBACK_TAG}）',
          '- 隐私：材料只来自请求人能看到的地方；别人私信里说的只写结论，不引原话；'
          + ('这个人自己的话可以短引，一句以内；' if x.self_mode else f'替别人出，谁的原话都不引，{x.dn}自己的话也只写意思；')
          + '不写邮箱、密钥、带 token 的链接；'
          'clues 里只能提材料里出现过的消息编号',
          '', '## 各批的文件（绝对路径）', '']
    for b in batches:
        bl.append(f'- 第 {b["batch"]} 批：读 {b["path"]}，写 {x.work}/out/{label}/batch{b["batch"]}.json（目录不在就建），'
                  f'材料里 {len(b["sessions"])} 个会话')
    bl += ['', '写完自查（N 换成你的批号）：', '', '```bash',
           'python3 -c "import json;d=json.load(open(\'' + f'{x.work}/out/{label}/batchN.json' +
           '\'));print(len(d), sum(len(s[\'events\']) for s in d))"', '```', '']
    open(f'{d}/brief.md', 'w', encoding='utf-8').write('\n'.join(bl))
    save(f'{d}/index.json', {'label': label, 'window': {'start': start, 'end': end}, 'batches': batches,
                             'sessions': [{k: b[k] for k in ('key', 'group', 'title', 'tids', 'is_new')} for b in blocks],
                             'new_taskids': newtids, 'others_turns': others})
    print(json.dumps({'label': label, 'window': [hm(start), hm(end)], 'target_messages': nh, 'rooms_skipped_for_privacy': nskip,
                      'candidates': len(cands), 'sessions': len(blocks), 'new_sessions': sum(b['is_new'] for b in blocks),
                      'others_turns_dropped': others, 'tags_confirmed': x.cfg.get('tags_confirmed'),
                      'batches': [{'batch': b['batch'], 'kb': b['bytes'] // 1024, 'sessions': len(b['sessions']),
                                   'packet': b['path'], 'out': f'{x.work}/out/{label}/batch{b["batch"]}.json'} for b in batches]},
                     ensure_ascii=False, indent=1))


# ---------------------------------------------------------------- check / merge
def check(x, label):
    ix = load(f'{x.work}/packets/{label}/index.json')
    if not ix:
        sys.exit(f'没有 {label} 的材料包')
    got, problems = {}, []
    for f in sorted(glob.glob(f'{x.work}/out/{label}/batch*.json')):
        try:
            for s in json.load(open(f, encoding='utf-8')):
                got[s['key']] = s
        except Exception as e:
            problems.append(f'{os.path.basename(f)} 读不了：{e}')
    allow = {s['key']: set(s['tids']) for s in ix['sessions']}
    for s in ix['sessions']:
        if s['key'] not in got:
            problems.append(f'缺会话 {s["key"]}')
    lo = (datetime.datetime.fromisoformat(ix['window']['start']) - datetime.timedelta(days=2)).strftime('%Y-%m-%d %H:%M')
    hi = hm(ix['window']['end'])
    for key, s in got.items():
        if key not in allow:
            problems.append(f'多出会话 {key}，不并')
            continue
        if re.search(r'usr_[0-9a-f]{8}|[\w+\-]+#\d{2,}', s.get('orig_title') or ''):
            problems.append(f'{key} 原标题里有 uid 或消息编号（删掉）')
        for e in s.get('events') or []:
            if e.get('tag') not in x.tags:
                problems.append(f'{key} 标签不对 {e.get("tag")}（只能用 config.json 的 tags）')
            if e.get('status') not in STATUS:
                problems.append(f'{key} 状态不对 {e.get("status")}')
            if not (lo <= (e.get('start') or '') <= hi + ':59'):
                problems.append(f'{key} 时间出窗 {e.get("start")}')
            if e.get('end') and not ((e.get('start') or '') <= e['end'] <= hi + ':59'):
                problems.append(f'{key} 结束时间不对 {e.get("end")}（要不早于 start、不晚于窗口结束）')
            bad = [t for t in e.get('turns') or [] if t[:8] not in allow[key]]
            if bad:
                problems.append(f'{key} turn 对不上 {bad}')
            blob = json.dumps(e, ensure_ascii=False)
            if EMAIL.search(blob) or SECRET.search(blob):
                problems.append(f'{key} 有邮箱或密钥（并的时候会抹掉，最好改掉）')
            for ref in sorted(set(re.findall(r'((?:dm|g)-[\w+\-]+)#\d+', blob))):
                if not readable(ref, x.R):
                    problems.append(f'{key} 提到请求人看不到的地方 {ref}（必须删掉）')
            body = json.dumps({f: e.get(f) for f in ('title', 'one_line', 'summary', 'evidence', 'judgement', 'next')}, ensure_ascii=False)
            if re.search(r'~/|/Users/|[\w+\-]+#\d{2,}|usr_[0-9a-f]{8}', body):
                problems.append(f'{key}「{e.get("title")}」正文里有路径或编号（挪到 clues）')
    return ix, got, allow, problems


def scrub(o):
    if isinstance(o, str):
        return clean(o)
    if isinstance(o, list):
        return [scrub(v) for v in o]
    if isinstance(o, dict):
        return {k: scrub(v) for k, v in o.items()}
    return o


def cmd_merge(x, label):
    store, state = load(x.store_p), load(x.state_p)
    if any(w['label'] == label for w in store['windows']):
        lm = load(f'{x.data}/last-merge.json') or {}
        if lm.get('label') == label:
            print(json.dumps(lm, ensure_ascii=False, indent=1))
        sys.exit(f'{label} 已经并过了，不要重并' + ('（上面是那次合并打印的新增，写交付的话照用）' if lm.get('label') == label else ''))
    ix, got, allow, problems = check(x, label)
    hard = [p for p in problems if p.startswith(('缺会话', '多出会话')) or '读不了' in p or '标签不对' in p or '状态不对' in p or '看不到的地方' in p]
    if hard:
        print('\n'.join(problems))
        sys.exit('有问题，先改对应的 out 文件再并')
    added = []
    for key, s in got.items():
        s = scrub(s)
        evs = s.get('events') or []
        for e in evs:
            e['window'] = label
        if key in store['sessions']:
            store['sessions'][key]['events'].extend(evs)
        else:
            s['group'] = next(i['group'] for i in ix['sessions'] if i['key'] == key)
            store['sessions'][key] = s
        added += [(e, key) for e in evs]
    win = ix['window']
    store['windows'].append({'label': label, 'start': win['start'], 'end': win['end']})
    processed = set(state['processed'])
    for ts_ in ix['new_taskids'].values():
        processed.update(ts_)
    save(x.store_p, store)
    save(x.state_p, {'window_end': win['end'], 'processed': sorted(processed)})
    render(x, store, label)
    st = collections.Counter(e['status'] for e, _ in added)
    summary = {'label': label, 'window': [hm(win['start']), hm(win['end'])], 'new_events': len(added),
                      'sessions_touched': len(got), 'new_sessions': sum(1 for i in ix['sessions'] if i['is_new']),
                      'status': st, 'wait_on_person': sum(1 for e, _ in added if is_wait(x, e)),
                      'titles': [f'{e["start"][5:]} {e["title"]}' for e, _ in sorted(added, key=lambda z: z[0]['start'])][:12],
                      'md': x.md, 'html': x.html, 'problems': problems, 'merged_at': hm(now_iso())}
    save(f'{x.data}/last-merge.json', summary)
    print(json.dumps(summary, ensure_ascii=False, indent=1))


def cmd_empty(x, label):
    """这段时间没有新会话：只推进截止时间，不重出文件。"""
    ix = load(f'{x.work}/packets/{label}/index.json')
    state = load(x.state_p)
    processed = set(state['processed'])
    for ts_ in ix['new_taskids'].values():
        processed.update(ts_)
    save(x.state_p, {'window_end': ix['window']['end'], 'processed': sorted(processed)})
    open(f'{x.work}/packets/{label}/emptied', 'w').write(now_iso())
    save(f'{x.data}/last-merge.json', {'label': label, 'window': [hm(ix['window']['start']), hm(ix['window']['end'])],
                                       'new_events': 0, 'empty': True, 'merged_at': hm(now_iso())})
    print('没有新会话，截止时间推进到', hm(ix['window']['end']))


# ---------------------------------------------------------------- render md
def run_time(e):
    s, t = e.get('start', ''), e.get('end', '') or e.get('start', '')
    return f'{s}–{t[11:]} 北京时间' if s[:10] == t[:10] else f'{s} 至 {t} 北京时间'


def summary_md(s, windows):
    k = s['key']
    wl = {e.get('window') for e in s['events']}
    wtxt = '；'.join(f'{hm(w["start"])}（含）至 {hm(w["end"])}（不含）' for w in windows if w['label'] in wl)
    L = [f'# {s.get("title")}', '',
         f'- Agent：mirasim 本机 · {s.get("assistant") or "未知"}（{k.split(":")[0]}）',
         f'- Session ID：{k}',
         f'- Session：[{s.get("orig_title") or s.get("title")}]({loc(k)})（会话原标题）',
         f'- Session开始时间：{s.get("created") or "见首个活动"}',
         f'- 本次处理窗口：{wtxt}，Asia/Shanghai',
         f'- 来源：{s.get("source")}', '', '## Events', '']
    for i, e in enumerate(sorted(s['events'], key=lambda e: e.get('start', '')), 1):
        L += [f'### {i}. {e.get("title")}', '',
              f'- 活动时间：{run_time(e)}',
              f'- 活动一句话：{e.get("one_line")}',
              f'- 高层总结：{e.get("summary")}',
              f'- 判断/状态：{e.get("status")}',
              '- 证据/结果：'] + [f'  - {v}' for v in (e.get('evidence') or ['无'])] + [
              f'- 下一步：{e.get("next") or "无"}',
              f'- 项目标签：{e.get("tag")}',
              f'- 细节线索：{e.get("clues") or "无"}；turns {", ".join(e.get("turns") or []) or "—"}', '']
    return '\n'.join(L)


def digest_entry(e, s):
    k = s['key']
    return '\n'.join([f'- {e["start"][11:]} [{e.get("title")}]({loc(k)}) {e.get("tag")}',
                      f'  - Session：[{s.get("title") or s.get("orig_title")}]({loc(k)})（{k}）',
                      f'  - 运行时间：{run_time(e)}',
                      f'  - 状态：{e.get("status")}；{e.get("trigger") or s.get("source")}',
                      '  - 证据'] + [f'    - {v}' for v in (e.get('evidence') or ['无'])][:4] + [
                      f'  - 判断：{e.get("judgement")}',
                      f'  - 下一检查：{e.get("next") or "无"}',
                      f'  - source：{k}；摘要 summaries/{s["file"]}'])


def render(x, store, latest=None):
    os.makedirs(f'{x.dir}/summaries', exist_ok=True)
    W, S = store['windows'], store['sessions']
    cands = {c['key']: c for c in (load(f'{x.work}/candidates.json', {}) or {}).get('sessions', [])}
    for s in S.values():
        s['events'].sort(key=lambda e: e.get('start', ''))
        if not s.get('file'):
            f0 = s['events'][0]['start'] if s['events'] else '0000-00-00'
            s['file'] = f'{f0[5:7]}{f0[8:10]}-{slug(s.get("title"))}-{s["key"].split(":")[1][:8]}.md'
        c = cands.get(s['key'], {})
        if c.get('createdAt'):
            s['created'] = bj(c['createdAt']) + ' 北京时间'
        open(f'{x.dir}/summaries/{s["file"]}', 'w', encoding='utf-8').write(summary_md(s, W) + '\n')
    evs = sorted(((e, s) for s in S.values() for e in s['events']), key=lambda z: z[0].get('start', ''))
    act = [z for z in evs if (z[0].get('trigger') or z[1].get('source')) not in AUTO]
    aut = [z for z in evs if (z[0].get('trigger') or z[1].get('source')) in AUTO]
    st = collections.Counter(e['status'] for e, _ in evs)
    tg = collections.Counter(e['tag'] for e, _ in evs)
    grp = collections.Counter(s['group'] for s in S.values())
    wait = [z for z in evs if is_wait(x, z[0])]
    first, last = W[0], W[-1]
    scope = (f'本机 mirasim 上{x.dn}触发的会话，跨所有助手和工作目录：自己在工作台开的、私信和群里叫助手的、Mira Bot 按其话派出去的、其设的定时任务、Matrix 自动接其话的'
             if x.self_mode else
             f'本机 mirasim 上{x.dn}触发的会话，只取请求人能看到的地方（大厅、群、事项、请求人在里面的私信和私密群）；{x.dn}的工作台会话和私设的定时任务不读')
    head = [f'- Session Activity Digest · {first["start"][:10]} 至 {last["end"][:10]}',
            f'  - 窗口：{hm(first["start"])}（含）至 {hm(last["end"])}（不含），Asia/Shanghai；分 {len(W)} 次处理（首次从起点补齐，之后每天增量）',
            f'  - 范围：{scope}；主动 = 用户主动 + 明确派工，自动 = 自动任务 + 自动派生',
            '  - 来源：' + ('mirasim 本机会话记录、频道日志、任务账本、工作台轮次记录、定时任务运行记录' if x.self_mode else
                           'mirasim 本机会话记录、请求人能看到的频道日志和任务账本、请求人能看到的定时任务运行记录') + '；只读',
            f'  - 活动：{len(S)} 个 Session，{len(evs)} 段活动',
            '  - 覆盖：不完整（只算本机）；同会话里别人说的话不纳入；这份摘要自己的定时任务不算' +
            ('' if x.self_mode else '；来自请求人看不到的私信和私密群的轮次不纳入'),
            '  - 说明：时间都是实际 turn 时间；「会话自报」的结果和核过的分开写；每次只补上次截止以后的新轮次，旧的事不改写']

    def by_day(items):
        L, cur = [], None
        days = collections.Counter(e['start'][:10] for e, _ in items)
        for e, s in reversed(items):
            if e['start'][:10] != cur:
                cur = e['start'][:10]
                L += ['', f'### {cur[5:]}（{days[cur]} 段）', '']
            L.append(digest_entry(e, s))
        return L

    digest = head + ['', f'## 主动的（{len(act)} 段）'] + by_day(act) + ['', f'## 自动跑的（{len(aut)} 段）'] + by_day(aut)
    open(f'{x.dir}/activity-digest.md', 'w', encoding='utf-8').write('\n'.join(digest) + '\n')
    lw = next((w for w in W if w['label'] == latest), W[-1])
    new = [z for z in evs if z[0].get('window') == lw['label']]
    L = [f'# {x.title}', '',
         f'更新到 {hm(last["end"])}（北京时间）。先是按时间的活动记录，后面是每个会话一份摘要；每天增量补上一次以后的新会话和新活动。', '',
         f'## 最新一次新增（{hm(lw["start"])} 至 {hm(lw["end"])}，{len(new)} 段）', '']
    L += [f'- {e["start"][5:]} {e["title"]} {e["tag"]} · {e["status"]}' for e, s in sorted(new, key=lambda z: z[0]['start'], reverse=True)] or ['- 这段时间没有新的会话活动']
    L += ['', '## 一眼看完', '',
          f'- {len(S)} 个会话，{len(evs)} 段活动；主动的 {len(act)} 段，自动跑的 {len(aut)} 段',
          '- 会话怎么来的：' + '，'.join(f'{k} {v}' for k, v in grp.most_common()),
          '- 状态：' + '，'.join(f'{k} {v}' for k, v in st.most_common()),
          '- 主题：' + '，'.join(f'{k} {v}' for k, v in tg.most_common()),
          f'- {cj(x.wait_word)}定的：{len(wait)} 段（状态是阻塞或等待、下一步写着{x.wait_word}）', '',
          '# 一、Activity Digest', ''] + digest + ['', '# 二、每个会话的摘要', '']
    for s in sorted(S.values(), key=lambda s: s['events'][-1]['start'] if s['events'] else '', reverse=True):
        L.append(re.sub(r'^(#+) ', r'#\1 ', summary_md(s, W), flags=re.M))
        L.append('')
    open(x.md, 'w', encoding='utf-8').write('\n'.join(L))
    save(f'{x.dir}/manifest.json', {
        'schema_version': 1, 'skill': 'session-digest', 'target': x.U, 'requester': x.R,
        'source_scope': scope, 'windows': W,
        'window': {'start': first['start'], 'end_exclusive': last['end'], 'timezone': 'Asia/Shanghai'},
        'coverage': {'status': 'partial', 'sources_checked': [
            '~/.mirasim/sessions/*/*/record.json, turns.jsonl', '~/.mirasim/chat/rooms/*/log/*.jsonl（只读请求人能看的）',
            '~/.mirasim/chat/assistants/dispatched.json', '~/.mirasim/collab/turns.jsonl', '~/.mirasim/schedules/runs.jsonl']},
        'counts': {'sessions': len(S), 'events': len(evs), 'groups': grp, 'status': st, 'tags': tg},
        'sessions': [{'session_id': s['key'], 'title': s.get('title'), 'source_locator': path_of(s['key']), 'link': loc(s['key']), 'group': s['group'],
                      'turn_ids': sorted({t for e in s['events'] for t in e.get('turns') or []}),
                      'windows': sorted({e.get('window') for e in s['events']}),
                      'first_activity': s['events'][0]['start'] if s['events'] else None,
                      'last_activity': max((e.get('end') or e['start']) for e in s['events']) if s['events'] else None,
                      'trigger': s.get('source'), 'summary_path': f'summaries/{s["file"]}', 'evidence_as_of': hm(last['end'])}
                     for s in S.values()],
        'excluded': store.get('excluded', []), 'digest_path': 'activity-digest.md'})
    save(x.store_p, store)
    build_html(x)
    snap = f'{x.dir}/历史版'
    os.makedirs(snap, exist_ok=True)
    tag = (latest or last['label'])
    for src in (x.md, x.html):
        b = os.path.basename(src).rsplit('.', 1)
        with open(src, 'rb') as fa, open(f'{snap}/{b[0]}-{tag}.{b[1]}', 'wb') as fz:
            fz.write(fa.read())


# ---------------------------------------------------------------- md -> html（每条都能收起，手机能看）
def inline(t, links=True):
    """links=False 用在可收起的标题行：点标题是展开，不跳走。"""
    t = html.escape(t, quote=False)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
    if links:
        t = re.sub(r'\[([^\]]+)\]\((https?://[^)\s]+)\)', r'<a href="\2" target="_blank" rel="noopener">\1</a>', t)
        t = re.sub(r'\[([^\]]+)\]\((mirasim://[^)\s]+)\)', r'<a href="\2">\1</a>', t)
    t = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\1', t)
    t = re.sub(r'(?<![\w&])(#[一-鿿]{2,8})', r'<span class="tag">\1</span>', t)
    return t


STATUS_CLS = {'已完成': 'ok', '进行中': 'go', '阻塞或等待': 'wait', '等待验收': 'go', '中断': 'stop', '失败': 'stop', '无新增产物': 'none'}


def parse_md(text):
    root = {'h': 0, 'text': '', 'kids': []}
    hstack, lstack = [root], []
    for raw in text.split('\n'):
        line = raw.rstrip()
        if not line.strip() or line.startswith('```'):
            continue
        m = re.match(r'^(#{1,6}) (.*)$', line)
        if m:
            lv = len(m.group(1))
            while hstack[-1]['h'] >= lv:
                hstack.pop()
            n = {'h': lv, 'text': m.group(2), 'kids': []}
            hstack[-1]['kids'].append(n)
            hstack.append(n)
            lstack = []
            continue
        m = re.match(r'^(\s*)[-*] (.*)$', line)
        if m:
            ind = len(m.group(1))
            n = {'li': m.group(2), 'kids': []}
            while lstack and lstack[-1][0] >= ind:
                lstack.pop()
            (lstack[-1][1]['kids'] if lstack else hstack[-1]['kids']).append(n)
            lstack.append((ind, n))
            continue
        hstack[-1]['kids'].append({'p': line.strip()})
        lstack = []
    return root


def status_of(n):
    for k in n.get('kids', []):
        m = re.match(r'^(?:判断/)?状态：([^；;（(]+)', k.get('li') or '')
        if m:
            return m.group(1).strip()
        if 'h' in k or k.get('kids'):
            r = status_of(k)
            if r:
                return r
    return None


def text_of(n):
    return ' '.join([n.get('text') or n.get('li') or n.get('p') or ''] + [text_of(k) for k in n.get('kids', [])])


def build_html(x):
    def entry_attrs(n):
        t = text_of(n)
        tags = ' '.join(sorted(set(re.findall(r'#[一-鿿]{2,8}', t))))
        wait = '1' if (status_of(n) == '阻塞或等待' and re.sub(r'\s', '', x.wait_word) in re.sub(r'\s', '', t)) else '0'
        return f' class="entry" data-tags="{html.escape(tags)}" data-wait="{wait}"'

    def badge(st):
        return f' <span class="st {STATUS_CLS.get(st, "none")}">{html.escape(st)}</span>' if st else ''

    def nodes(kids, ctx):
        out, lis = [], []
        for n in kids:
            if 'li' in n:
                lis.append(li(n, ctx))
                continue
            if lis:
                out.append('<ul>' + ''.join(lis) + '</ul>')
                lis = []
            out.append(head(n, ctx) if 'h' in n else f'<p>{inline(n["p"])}</p>')
        if lis:
            out.append('<ul>' + ''.join(lis) + '</ul>')
        return ''.join(out)

    def li(n, ctx):
        if not n['kids']:
            m = re.match(r'^([^：]{1,8})：(.*)$', n['li'])
            if m and len(m.group(1)) <= 6:
                return f'<li><span class="k">{html.escape(m.group(1))}</span>{inline(m.group(2))}</li>'
            return f'<li>{inline(n["li"])}</li>'
        entry = ctx.get('entry_level') == 'li' and not ctx.get('in_entry')
        sub = dict(ctx, in_entry=ctx.get('in_entry') or entry)
        return (f'<li{entry_attrs(n) if entry else ""}><details><summary>{inline(n["li"], False)}{badge(status_of(n) if entry else None)}</summary>'
                f'{nodes(n["kids"], sub)}</details></li>')

    def head(n, ctx):
        lv, t, part, sub = n['h'], n['text'], ctx.get('part'), dict(ctx)
        if lv == 1:
            sub['part'] = 'digest' if 'Activity Digest' in t else ('sessions' if '每个会话' in t else None)
            return f'<section class="part"><h2 class="ptitle">{inline(t)}</h2>{nodes(n["kids"], sub)}</section>'
        opn, cls, attrs, extra, st = True, f'h{lv}', '', '', None
        if part == 'digest' and lv == 3:
            sub['entry_level'] = 'li'
            opn = t[:5] in ctx.get('recent_days', ())
            cls += ' day'
        if part == 'sessions' and lv == 2:
            opn, cls, attrs = False, cls + ' sess', entry_attrs(n)
            sub['in_entry'] = True
            extra = f' <span class="cnt">{sum(1 for k in n["kids"] for kk in k.get("kids", []) if kk.get("h") == 4)} 件</span>'
        if part == 'sessions' and lv == 4:
            opn, st = False, status_of(n)
        return (f'<div{attrs}><details class="{cls}"{" open" if opn else ""}><summary>{inline(t, False)}{extra}{badge(st)}</summary>'
                f'<div class="body">{nodes(n["kids"], sub)}</div></details></div>')

    text = open(x.md, encoding='utf-8').read()
    tree = parse_md(text)
    tnode = tree['kids'][0] if tree['kids'] and tree['kids'][0].get('h') == 1 else None
    ctx = {'recent_days': set(sorted(set(re.findall(r'^### (\d\d-\d\d)（', text, flags=re.M)), reverse=True)[:2])}
    lead, body = '', []
    if tnode:
        for k in tnode['kids']:
            if 'p' in k and not lead:
                lead = k['p']
            else:
                body.append(k)
        rest = tree['kids'][1:]
    else:
        rest = tree['kids']
    chips = ''.join(f'<button class="chip" data-tag="{t}">{t[1:]}</button>' for t in x.tags)
    out = ['<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">',
           '<meta name="viewport" content="width=device-width,initial-scale=1">',
           f'<title>{html.escape(x.title)}</title><style>{CSS}</style></head><body><div class="wrap">',
           f'<div class="hero"><div class="eyebrow">Session Digest · 每天增量</div><h1>{html.escape(x.title)}</h1>',
           f'<p>{inline(lead)}</p></div>',
           '<div class="bar"><div class="row"><input id="q" class="search" type="search" placeholder="搜标题、人名、产物…">',
           f'<button class="btn" id="wait">{html.escape(cj(x.wait_word))}定的</button></div>',
           f'<div class="chips"><button class="chip ctl" id="openall">全部展开</button><button class="chip ctl" id="closeall">全部收起</button>{chips}</div>'
           '<div class="found" id="found"></div></div>',
           nodes(body, ctx), nodes(rest, ctx), f'</div><script>{JS}</script></body></html>']
    open(x.html, 'w', encoding='utf-8').write(''.join(out))
    print('网页', x.html, os.path.getsize(x.html) // 1024, 'KB')


CSS = """
:root{--bg:#f7f7ef;--ink:#193c35;--green:#295e4c;--mint:#e1efe6;--mint2:#cfe5d8;--peach:#fae3d6;--cream:#f3ecd9;--note:#fbf1b8;
--line:rgba(25,60,53,.13);--soft:rgba(25,60,53,.62);--card:#fffdf7;color-scheme:light}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:15.5px/1.65 -apple-system,BlinkMacSystemFont,"PingFang SC","Hiragino Sans GB","Noto Sans SC","Microsoft YaHei",sans-serif;overflow-x:hidden}
.wrap{max-width:780px;margin:0 auto;padding:0 16px 60px}
.eyebrow{font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--green);font-weight:600}
h1{font-size:28px;line-height:1.25;margin:6px 0 8px}.hero{padding:26px 0 6px}.hero p{margin:0 0 12px;color:var(--soft);font-size:14px}
.bar{position:sticky;top:0;z-index:5;background:rgba(247,247,239,.96);backdrop-filter:blur(6px);-webkit-backdrop-filter:blur(6px);border-bottom:1px solid var(--line);padding:8px 0 7px;margin-bottom:10px}
.row{display:flex;gap:6px;align-items:center}
.search{flex:1 1 auto;min-width:0;border:1px solid var(--line);background:#fff;border-radius:999px;padding:8px 14px;font-size:15px;color:var(--ink);outline:none}
.search:focus{border-color:var(--green)}
.btn{border:1px solid var(--line);background:var(--card);color:var(--green);border-radius:999px;padding:5px 10px;font-size:12.5px;cursor:pointer;white-space:nowrap;flex:none}
.btn.on{background:var(--green);color:#fff;border-color:var(--green)}
.chips{display:flex;flex-wrap:nowrap;gap:5px;margin-top:6px;overflow-x:auto;-webkit-overflow-scrolling:touch;scrollbar-width:none;padding-bottom:2px}
.chips::-webkit-scrollbar{display:none}
.chip{font-size:12.5px;color:var(--green);background:var(--mint);border:0;border-radius:999px;padding:3px 9px;cursor:pointer;white-space:nowrap}
.chip.on{background:var(--green);color:#fff}.chip.ctl{background:var(--cream)}
.found{font-size:12.5px;color:var(--soft);margin-top:2px}.found:empty{display:none}
.part{margin:18px 0 8px}.ptitle{font:italic 600 22px/1.3 Georgia,"Times New Roman",serif;color:var(--green);margin:18px 0 8px}
details{margin:0}summary{cursor:pointer;list-style:none;padding:9px 12px;border-radius:14px;outline:none}
summary::-webkit-details-marker{display:none}
summary::before{content:"›";display:inline-block;width:14px;color:var(--green);font-weight:700;transition:transform .15s}
details[open]>summary::before{transform:rotate(90deg)}
details.h2>summary{font-size:18px;font-weight:600;background:var(--cream);margin:10px 0 6px}
details.h3>summary{font-size:16px;font-weight:600;background:var(--mint);margin:8px 0 6px}
details.h4>summary{font-size:15px;font-weight:600;background:var(--card);border:1px solid var(--line);margin:6px 0}
details.sess>summary{font-size:15.5px;background:var(--card);border:1px solid var(--line)}
details.day>summary{background:var(--cream)}
.body{padding:0 0 4px 8px}ul{list-style:none;margin:0;padding:0 0 0 10px}li{margin:3px 0}
li>details>summary{padding:6px 10px;border-radius:12px}
.entry>details>summary{background:var(--card);border:1px solid var(--line);margin:6px 0;padding:10px 12px;font-weight:500}
.entry>details[open]>summary{border-color:var(--green)}
li:not(.entry)>details>summary{background:rgba(255,255,255,.5)}
li>span.k{display:inline-block;color:var(--soft);font-size:13px;margin-right:4px}
li:not(:has(details)){padding:2px 10px 2px 22px;position:relative}
li:not(:has(details))::before{content:"";position:absolute;left:10px;top:.85em;width:5px;height:5px;border-radius:50%;background:var(--mint2)}
.tag{font-size:11.5px;border-radius:999px;padding:1px 8px;background:var(--mint);color:var(--green);white-space:nowrap;margin-left:4px}
.st{font-size:11.5px;border-radius:999px;padding:1px 8px;margin-left:6px;white-space:nowrap}
.st.ok{background:var(--mint2);color:var(--green)}.st.go{background:#dcebf3;color:#24506a}.st.wait{background:var(--note);color:#6b5300}
.st.stop{background:var(--peach);color:#8a3f1d}.st.none{background:#ecebe4;color:var(--soft)}
.cnt{font-size:12px;color:var(--soft);margin-left:6px;font-weight:400}
p{margin:6px 12px}code{background:var(--cream);border-radius:6px;padding:0 4px;font-size:13px}.hide{display:none!important}
@media (max-width:420px){body{font-size:15px}h1{font-size:24px}summary{padding:8px 10px}}
"""

JS = """
const q=document.getElementById('q'),found=document.getElementById('found');let tag='',wait=false;
const entries=[...document.querySelectorAll('.entry')];entries.forEach(e=>e._t=e.textContent.toLowerCase());
function apply(){const s=q.value.trim().toLowerCase();let n=0;
 entries.forEach(e=>{const ok=(!s||e._t.includes(s))&&(!tag||e.dataset.tags.includes(tag))&&(!wait||e.dataset.wait==='1');
  e.classList.toggle('hide',!ok);if(ok&&e.tagName==='LI')n++;});
 document.querySelectorAll('details.day').forEach(d=>{const has=[...d.querySelectorAll('.entry')].some(e=>!e.classList.contains('hide'));
  d.parentElement.classList.toggle('hide',!has);if((s||tag||wait)&&has)d.open=true;});
 found.textContent=(s||tag||wait)?('找到 '+n+' 条'):'';}
q.addEventListener('input',apply);
document.querySelectorAll('.chip[data-tag]').forEach(c=>c.addEventListener('click',()=>{tag=(tag===c.dataset.tag)?'':c.dataset.tag;
 document.querySelectorAll('.chip').forEach(x=>x.classList.toggle('on',x.dataset.tag===tag));apply();}));
document.getElementById('wait').addEventListener('click',e=>{wait=!wait;e.target.classList.toggle('on',wait);apply();});
document.getElementById('openall').addEventListener('click',()=>document.querySelectorAll('details').forEach(d=>d.open=true));
document.getElementById('closeall').addEventListener('click',()=>document.querySelectorAll('details').forEach(d=>d.open=false));
"""


# ---------------------------------------------------------------- status
def cmd_status(x):
    store, state = load(x.store_p), load(x.state_p)
    print(json.dumps({'target': x.U, 'display': x.display, 'requester': x.R, 'mode': '本人' if x.self_mode else '替别人',
                      'since': hm(x.cfg['since']), 'window_end': hm(state['window_end']), 'windows': len(store['windows']),
                      'sessions': len(store['sessions']), 'events': sum(len(s['events']) for s in store['sessions'].values()),
                      'tags': x.tags, 'tags_confirmed': x.cfg.get('tags_confirmed'),
                      'md': x.md if os.path.exists(x.md) else None, 'html': x.html if os.path.exists(x.html) else None,
                      'last_merge': load(f'{x.data}/last-merge.json')},
                     ensure_ascii=False, indent=1))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('cmd', choices=['init', 'prep', 'check', 'merge', 'empty', 'html', 'render', 'status'])
    ap.add_argument('label', nargs='?')
    ap.add_argument('--dir')
    ap.add_argument('--user')
    ap.add_argument('--requester')
    ap.add_argument('--days', type=int, default=7)
    ap.add_argument('--since')
    ap.add_argument('--title')
    ap.add_argument('--end')
    ap.add_argument('--force', action='store_true')
    a = ap.parse_intermixed_args()
    if a.cmd in ('check', 'merge', 'empty') and not a.label:
        sys.exit(f'{a.cmd} 要 label（prep 打印的那个，如 1112）')
    if a.cmd == 'init':
        if not a.user:
            sys.exit('init 要 --user')
        return cmd_init(a)
    if not a.dir:
        sys.exit('要 --dir（init 打印的目录）')
    x = Ctx(a.dir)
    lk = None
    if fcntl and a.cmd in ('prep', 'merge', 'empty', 'render', 'html'):
        lk = open(f'{x.dir}/.lock', 'w')
        try:
            fcntl.flock(lk, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            sys.exit('另一个进程正在改这份摘要（同一个目录），等它跑完再来；同一份摘要同时只能有一处在跑')
    if a.cmd == 'prep':
        cmd_prep(x, a.end, a.force)
    elif a.cmd == 'check':
        _, got, _, problems = check(x, a.label)
        print(json.dumps({'sessions': len(got), 'events': sum(len(s.get('events') or []) for s in got.values()),
                          'problems': problems}, ensure_ascii=False, indent=1))
    elif a.cmd == 'merge':
        cmd_merge(x, a.label)
    elif a.cmd == 'empty':
        cmd_empty(x, a.label)
    elif a.cmd == 'html':
        build_html(x)
    elif a.cmd == 'render':
        render(x, load(x.store_p))
    elif a.cmd == 'status':
        cmd_status(x)


if __name__ == '__main__':
    main()
