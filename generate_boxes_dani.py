import json
import math

NATURES = ['Hardy','Lonely','Brave','Adamant','Naughty',
           'Bold','Docile','Relaxed','Impish','Lax',
           'Timid','Hasty','Serious','Jolly','Naive',
           'Modest','Mild','Quiet','Bashful','Rash',
           'Calm','Gentle','Sassy','Careful','Quirky']

with open(r'C:\Users\Usuario\Desktop\pokeone-repo\input\input_dani.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

all_boxes = data['data']['pokemon']  # list; index 0 = team, 1..N = boxes
# Only process non-empty boxes (skip index 0 = active team)
boxes_data = [(i, box) for i, box in enumerate(all_boxes) if i > 0 and len(box) > 0]

total_pokemon = 0
num_boxes = len(boxes_data)

lines = []
lines.append('  <div class="box-section-grid" style="display:none">')

for box_num, pokemon_list in boxes_data:
    count = len(pokemon_list)
    total_pokemon += count

    lines.append('    <div class="box-block">')
    lines.append(f'      <div class="box-header"><span class="box-num">CAJA {box_num}</span><span class="box-counts">{count} Pokemon</span></div>')

    for entry in pokemon_list:
        pos     = entry['Position']
        poke    = entry['Pokemon']
        payload = poke['Payload']
        static  = poke['StaticData']

        F = math.ceil(pos / 6)
        C = ((pos - 1) % 6) + 1

        hp   = payload['IVs']['HP']
        atk  = payload['IVs']['Atk']
        def_ = payload['IVs']['Def']
        spa  = payload['IVs']['SpAtk']
        spd  = payload['IVs']['SpDef']
        spe  = payload['IVs']['Speed']

        sumIvs = hp + atk + def_ + spa + spd + spe
        pct = round(sumIvs / 186 * 100)

        if pct < 26:
            rarityClass = 'rarity-grey'
        elif pct < 46:
            rarityClass = 'rarity-white'
        elif pct < 58:
            rarityClass = 'rarity-green'
        elif pct < 71:
            rarityClass = 'rarity-blue'
        elif pct < 84:
            rarityClass = 'rarity-purple'
        else:
            rarityClass = 'rarity-gold'

        if pct >= 70:
            rbClass = 'rb-green'
        elif pct >= 55:
            rbClass = 'rb-blue'
        elif pct >= 45:
            rbClass = 'rb-amber'
        else:
            rbClass = 'rb-red'

        raw_name = static['Name']
        if raw_name == 'Nidoran♂':
            sprName = 'nidoran-m'
        elif raw_name == 'Nidoran♀':
            sprName = 'nidoran-f'
        else:
            sprName = raw_name.lower().replace(' ', '-')

        nature_idx = payload['Nature']
        nature = NATURES[nature_idx] if 0 <= nature_idx < len(NATURES) else str(nature_idx)
        ability = poke['Ability']
        level   = payload['Level']

        slot_pos   = f'F{F}·C{C}'
        sprite_url = f'https://img.pokemondb.net/sprites/black-white/normal/{sprName}.png'
        meta = (
            f'Lv.{level} &bull; {nature} &bull; {ability} &bull; '
            f'HP {hp}, Atk {atk}, Def {def_}, SpA {spa}, SpD {spd}, Spe {spe}'
        )
        modal_id = f'box-{box_num}-{pos}'

        slot = (
            f'      <div class="box-slot">'
            f'<span class="slot-pos">{slot_pos}</span>'
            f'<img class="slot-spr" src="{sprite_url}">'
            f'<span class="slot-name {rarityClass}">{raw_name}</span>'
            f'<span class="slot-meta">{meta}</span>'
            f'<span class="slot-rb {rbClass}" onclick="openRbModal(\'{modal_id}\')">'
            f'<span class="srb-score">{pct}%</span>'
            f'</span>'
            f'</div>'
        )
        lines.append(slot)

    lines.append('    </div>')

lines.append('  </div>')

html_output = '\n'.join(lines)

print(f"Total Pokemon: {total_pokemon}")
print(f"Number of boxes: {num_boxes}")
print()
print(html_output)
