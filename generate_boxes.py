"""
Regenera la seccion de Cajas del PC en pokeone_equipo.html
a partir del JSON exportado de PokeOne.

Uso:
    python generate_boxes.py input/input_jsolerca.json pokeone_equipo.html

El script sustituye el bloque entre los marcadores
    <!-- BOX-SECTION-START -->
    <!-- BOX-SECTION-END -->
y actualiza el badge de resumen en la cabecera de la seccion.

Los unicos campos que genera automaticamente son los derivables del JSON:
  - nombre, nivel, naturaleza, habilidad, IVs, tipo sprite
  - rareza (clase CSS) segun % total de IVs
  - score % mostrado en el badge rb
  - posicion Fx*Cy calculada por Position dentro de cada caja

Los campos que NO toca (se mantienen del HTML existente o hay que poner a mano):
  - etiquetas TOP / LIBERAR / GUARDAR  -> por defecto sin etiqueta
  - clase sl-top / sl-drop             -> por defecto sin clase especial
  - openRbModal con razonamientos      -> mantiene id generico box-N-P
"""

import json, re, sys, math
from pathlib import Path
from datetime import date

# ── helpers ──────────────────────────────────────────────────────────────────

def iv_pct(ivs: dict) -> int:
    return round(sum(ivs.values()) / 186 * 100)

def rarity_class(pct: int) -> str:
    if pct >= 75: return "rarity-purple"
    if pct >= 65: return "rarity-blue"
    if pct >= 55: return "rarity-green"
    if pct >= 45: return "rarity-white"
    return "rarity-grey"

def rb_class(pct: int) -> str:
    if pct >= 70: return "rb-green"
    if pct >= 55: return "rb-blue"
    if pct >= 45: return "rb-amber"
    return "rb-red"

def sprite_url(icon: str) -> str:
    name = icon.replace(".png", "")
    return f"https://img.pokemondb.net/sprites/black-white/normal/{name}"

def fila_col(position: int, cols: int = 6):
    """Position (1-based) -> 'F1*C3' style label."""
    f = math.ceil(position / cols)
    c = ((position - 1) % cols) + 1
    return f"F{f}·C{c}"

def iv_str(ivs: dict) -> str:
    order = ["HP", "Atk", "Def", "SpAtk", "SpDef", "Speed"]
    labels = ["HP", "Atk", "Def", "SpA", "SpD", "Spe"]
    parts = []
    for stat, lbl in zip(order, labels):
        parts.append(f"{lbl} {ivs.get(stat, '?')}")
    return ", ".join(parts)

# ── slot builder ─────────────────────────────────────────────────────────────

def build_slot(p: dict, box_num: int) -> str:
    payload  = p["Pokemon"]["Payload"]
    static   = p["Pokemon"]["StaticData"]
    position = p["Position"]

    name     = static["Name"]
    level    = payload["Level"]
    nature   = payload["NatureName"]
    ability  = p["Pokemon"]["Ability"]
    ivs      = payload["IVs"]
    icon     = static["Icon"]

    pct      = iv_pct(ivs)
    rc       = rarity_class(pct)
    rbc      = rb_class(pct)
    fc       = fila_col(position)
    spr      = sprite_url(icon)
    modal_id = f"box-{box_num}-{position}"
    iv_text  = iv_str(ivs)

    return (
        f'      <div class="box-slot">'
        f'<span class="slot-pos">{fc}</span>'
        f'<img class="slot-spr" src="{spr}.png">'
        f'<span class="slot-name {rc}">{name}</span>'
        f'<span class="slot-meta">Lv.{level} &bull; {nature} &bull; {ability} &bull; {iv_text}</span>'
        f'<span class="slot-rb {rbc}" onclick="openRbModal(\'{modal_id}\')">'
        f'<span class="srb-score">{pct}%</span></span>'
        f'</div>'
    )

# ── main ─────────────────────────────────────────────────────────────────────

def generate(json_path: str, html_path: str):
    with open(json_path, "rb") as f:
        raw = f.read().lstrip(b'\xe2\x80\x8b')  # strip zero-width space BOM
    data = json.loads(raw)

    boxes_raw = data["data"]["pokemon"]
    # solo cajas con contenido, por indice real (Box 0 = equipo activo)
    non_empty = [(i, box) for i, box in enumerate(boxes_raw) if box and i > 0]

    total_pokemon = sum(len(b) for _, b in non_empty)
    total_cajas   = len(non_empty)

    lines = []
    for box_index, box in non_empty:
        box_label = f"CAJA {box_index}"
        count     = len(box)
        slots     = "\n".join(build_slot(p, box_index) for p in box)

        lines.append(
            f'    <div class="box-block">\n'
            f'      <div class="box-header">'
            f'<span class="box-num">{box_label}</span>'
            f'<span class="box-counts">{count} Pokemon</span>'
            f'</div>\n'
            f'{slots}\n'
            f'    </div>'
        )

    inner = "\n\n".join(lines)
    new_block = (
        "  <div class=\"box-section-grid\" style=\"display:none\">\n"
        + inner
        + "\n\n  </div>"
    )

    html = Path(html_path).read_text(encoding="utf-8")

    # sustituir bloque entre marcadores
    pattern = r'<!-- BOX-SECTION-START -->.*?<!-- BOX-SECTION-END -->'
    replacement = f'<!-- BOX-SECTION-START -->\n{new_block}\n<!-- BOX-SECTION-END -->'
    new_html, n = re.subn(pattern, replacement, html, flags=re.DOTALL)
    if n == 0:
        print("ERROR: no se encontraron los marcadores <!-- BOX-SECTION-START --> / <!-- BOX-SECTION-END --> en el HTML.")
        print("Añadelos manualmente alrededor del bloque <div class=\"box-section-grid\"> existente.")
        sys.exit(1)

    # actualizar badge resumen
    new_html = re.sub(
        r'(<div class="section" id="cajas">.*?<div class="badge">)[^<]*(</div>)',
        rf'\g<1>{total_pokemon} Pokemon &middot; {total_cajas} cajas\g<2>',
        new_html,
        flags=re.DOTALL,
        count=1,
    )

    # actualizar fecha — soporta ambos formatos de los dos dashboards
    today = date.today()
    meses = ["Enero","Febrero","Marzo","Abril","Mayo","Junio",
             "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]
    fecha_larga = f"{today.day} de {meses[today.month-1]} {today.year}"
    fecha_corta = today.strftime("%Y-%m-%d")
    new_html = re.sub(
        r'Ultima actualizacion:.*?&nbsp;&bull;&nbsp; jsolerca',
        f'Ultima actualizacion: {fecha_larga} &nbsp;&bull;&nbsp; jsolerca',
        new_html,
        count=1,
    )
    new_html = re.sub(
        r'Actualizado: \d{4}-\d{2}-\d{2}',
        f'Actualizado: {fecha_corta}',
        new_html,
        count=1,
    )

    Path(html_path).write_text(new_html, encoding="utf-8")
    print(f"OK: {total_pokemon} Pokemon en {total_cajas} cajas regeneradas en {html_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python generate_boxes.py <json_path> <html_path>")
        sys.exit(1)
    generate(sys.argv[1], sys.argv[2])
