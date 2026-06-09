"""
Igual que update_box_ivs.py pero para dani_equipo.html con input_dani_20260609.json
"""
import json, re, math, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('input_dani_20260609.json', 'rb') as f:
    raw = json.loads(f.read().lstrip(b'\xef\xbb\xbf\xe2\x80\x8b').decode('utf-8'))

all_pok = []
for group in raw['data']['pokemon']:
    if isinstance(group, list):
        all_pok.extend(group)
    elif isinstance(group, dict):
        all_pok.append(group)

print('Total pokemon in JSON:', len(all_pok))

box_map = {}
for p in all_pok:
    box = p['Box']
    pos = p['Position']
    if box == 0:
        continue
    iv = p['Pokemon']['Payload']['IVs']
    box_map.setdefault(box, {})[pos] = {
        'name':    p['Pokemon']['StaticData']['Name'],
        'nature':  p['Pokemon']['Payload']['NatureName'],
        'ability': p['Pokemon']['Ability'],
        'level':   p['Pokemon']['Payload']['Level'],
        'ivs':     iv,
    }

print('Boxes in JSON (non-team):', sorted(box_map.keys()))

def pos_to_fc(pos):
    fila = math.ceil(pos / 6)
    col  = ((pos - 1) % 6) + 1
    return fila, col

def iv_pct(iv):
    total = iv['HP'] + iv['Atk'] + iv['Def'] + iv['SpAtk'] + iv['SpDef'] + iv['Speed']
    return round(total / 186 * 100), total

def pct_to_cls(pct):
    if pct >= 85: return 'rb-gold'
    if pct >= 70: return 'rb-green'
    if pct >= 55: return 'rb-blue'
    if pct >= 40: return 'rb-amber'
    return 'rb-red'

BULL = '·'

html_path = '../dani_equipo.html'
with open(html_path, encoding='utf-8') as f:
    html = f.read()

box_block_re = re.compile(
    r'(<div class="box-block">\s*<div class="box-header">'
    r'<span class="box-num">CAJA (\d+)</span>.*?</div>\n)'
    r'(.*?)'
    r'(    </div>\n)',
    re.DOTALL
)

changes = 0
not_found = []

def process_box_block(m):
    global changes
    header = m.group(1)
    box_num = int(m.group(2))
    body = m.group(3)
    footer = m.group(4)

    if box_num not in box_map:
        return m.group(0)

    pok_by_pos = box_map[box_num]

    for pos, data in pok_by_pos.items():
        fila, col = pos_to_fc(pos)
        slot_pos_str = f'F{fila}{BULL}C{col}'

        iv = data['ivs']
        pct, total = iv_pct(iv)
        rb_cls = pct_to_cls(pct)
        star = ' ⭐' if pct >= 90 else ''
        iv_text = (f"HP {iv['HP']}, Atk {iv['Atk']}, Def {iv['Def']}, "
                   f"SpA {iv['SpAtk']}, SpD {iv['SpDef']}, Spe {iv['Speed']}")
        new_meta = f'Lv.{data["level"]} &bull; {data["nature"]} &bull; {data["ability"]} &bull; {iv_text}'
        new_score = f'{pct}%{star}'

        slot_pattern = (
            r'(<div class="box-slot[^"]*">'
            r'<span class="slot-pos">' + re.escape(slot_pos_str) + r'</span>'
            r'<img[^>]+>'
            r'<span class="slot-name[^"]*">[^<]*</span>'
            r'<span class="slot-meta">)'
            r'[^<]*'
            r'(</span>)'
            r'((?:<span[^>]*>[^<]*</span>)*?)'
            r'(<span class="slot-rb )(?:rb-[a-z]+)(" onclick="[^"]*"><span class="srb-score">)'
            r'[^<]+'
            r'(</span></span></div>)'
        )

        nm, ns, cls = new_meta, new_score, rb_cls
        def repl(m2, _nm=nm, _ns=ns, _cls=cls):
            return (m2.group(1) + _nm + m2.group(2) +
                    m2.group(3) +
                    m2.group(4) + _cls + m2.group(5) + _ns + m2.group(6))

        new_body, n = re.subn(slot_pattern, repl, body)
        if n == 1:
            body = new_body
            changes += 1
        elif n == 0:
            not_found.append((box_num, pos, data['name'], slot_pos_str))
        else:
            new_body2, _ = re.subn(slot_pattern, repl, body, count=1)
            body = new_body2
            changes += 1

    return header + body + footer

new_html = box_block_re.sub(process_box_block, html)

print(f'Changes: {changes}')
if not_found:
    print(f'Not found ({len(not_found)}):')
    for b, p2, n, sp in not_found:
        print(f'  Box {b} Pos {p2} ({sp}): {n}')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(new_html)
print('Done.')
