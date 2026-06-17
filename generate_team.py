"""
Genera (o sobreescribe) un HTML con el equipo activo de PokeOne.

Uso interactivo:
    python generate_team.py <json_path>

El script pregunta el nombre del equipo, genera el HTML y lo escribe en
    output/<nombre_equipo>.html

Si el archivo ya existe lo sobreescribe sin aviso extra.
El HTML es autónomo: CSS + JS embebidos, sin dependencias externas.
"""

import json, sys, re
from pathlib import Path

# ── movesets objetivo ─────────────────────────────────────────────────────────
_MOVESETS_PATH = Path(__file__).parent / "movesets.json"

def load_movesets() -> dict:
    if not _MOVESETS_PATH.exists():
        return {}
    raw = json.loads(_MOVESETS_PATH.read_text(encoding="utf-8"))
    return {k: v for k, v in raw.items() if not k.startswith("_")}

MOVESETS: dict = load_movesets()

# ── traducciones de movimientos (EN → ES, nombres oficiales Wikidex España) ───
MOVE_ES: dict[str, str] = {
    "Absorb":           "Absorber",
    "Acid":             "Ácido",
    "Acid Spray":       "Bomba Ácida",
    "Aerial Ace":       "Golpe Aéreo",
    "Agility":          "Agilidad",
    "Air Cutter":       "Aire Afilado",
    "Air Slash":        "Tajo Aéreo",
    "Amnesia":          "Amnesia",
    "Ancient Power":    "Poder Antiguo",
    "Aqua Jet":         "Acua Jet",
    "Aqua Ring":        "Acua Aro",
    "Aqua Tail":        "Acua Cola",
    "Assurance":        "Buena Baza",
    "Astonish":         "Impresionar",
    "Aurora Beam":      "Rayo Aurora",
    "Bestow":           "Ofrenda",
    "Bide":             "Resistir",
    "Bite":             "Mordisco",
    "Brick Break":      "Demolición",
    "Brine":            "Salmuera",
    "Bubble Beam":      "Rayo Burbuja",
    "Bug Bite":         "Picadura",
    "Bug Buzz":         "Zumbido",
    "Bulldoze":         "Terratemblor",
    "Bullet Punch":     "Puño Bala",
    "Bullet Seed":      "Semilladora",
    "Calm Mind":        "Paz Mental",
    "Charge":           "Carga",
    "Charge Beam":      "Rayo Carga",
    "Charm":            "Seducción",
    "Chip Away":        "Guardia Baja",
    "Clear Smog":       "Niebla Clara",
    "Close Combat":     "A Bocajarro",
    "Confuse Ray":      "Rayo Confuso",
    "Confusion":        "Confusión",
    "Constrict":        "Restricción",
    "Cotton Guard":     "Escudo Algodón",
    "Cotton Spore":     "Polen Algodón",
    "Crabhammer":       "Golpe Cangrejo",
    "Cross Chop":       "Tajo Cruzado",
    "Crunch":           "Triturar",
    "Curse":            "Maldición",
    "Cut":              "Corte",
    "Dark Pulse":       "Pulso Umbrío",
    "Dazzling Gleam":   "Brillo Deslumbrante",
    "Defense Curl":     "Rizo Defensa",
    "Dig":              "Excavar",
    "Disable":          "Anulación",
    "Disarming Voice":  "Voz Cautivadora",
    "Discharge":        "Chispazo",
    "Double Hit":       "Doble Golpe",
    "Double Kick":      "Doble Patada",
    "Double Slap":      "Doble Bofetón",
    "Double Team":      "Doble Equipo",
    "Dragon Rage":      "Furia Dragón",
    "Dragon Tail":      "Cola Dragón",
    "Dual Chop":        "Golpe Bis",
    "Earthquake":       "Terremoto",
    "Echoed Voice":     "Eco Voz",
    "Electro Ball":     "Bola Voltio",
    "Ember":            "Ascuas",
    "Endeavor":         "Equiparar",
    "Endure":           "Aguante",
    "Eruption":         "Erupción",
    "Explosion":        "Explosión",
    "Extrasensory":     "Paranormal",
    "Fairy Wind":       "Viento Feérico",
    "Fake Out":         "Sorpresa",
    "False Swipe":      "Falso Tortazo",
    "Feint":            "Amago",
    "Feint Attack":     "Finta",
    "Fire Spin":        "Giro Fuego",
    "Flail":            "Azote",
    "Flame Burst":      "Pirotecnia",
    "Flame Charge":     "Nitrocarga",
    "Flame Wheel":      "Rueda Fuego",
    "Flamethrower":     "Lanzallamas",
    "Flash":            "Destello",
    "Flash Cannon":     "Cañón Resplandor",
    "Fling":            "Lanzamiento",
    "Fly":              "Vuelo",
    "Focus Blast":      "Onda Certera",
    "Focus Energy":     "Foco Energía",
    "Foresight":        "Profecía",
    "Freeze-Dry":       "Liofilización",
    "Fury Attack":      "Ataque Furia",
    "Fury Cutter":      "Corte Furia",
    "Fury Swipes":      "Golpes Furia",
    "Gastro Acid":      "Bilis",
    "Giga Drain":       "Megaagotar",
    "Giga Impact":      "Gigaimpacto",
    "Growth":           "Desarrollo",
    "Growl":            "Gruñido",
    "Guillotine":       "Guillotina",
    "Gust":             "Tornado",
    "Gyro Ball":        "Giro Bola",
    "Harden":           "Endurecimiento",
    "Haze":             "Neblina",
    "Headbutt":         "Golpe Cabeza",
    "Helping Hand":     "Refuerzo",
    "High Jump Kick":   "Patada Salto Alta",
    "Horn Attack":      "Cornada",
    "Horn Drill":       "Perforador",
    "Howl":             "Aullido",
    "Hydro Pump":       "Hidrobomba",
    "Hyper Fang":       "Hipercolmillo",
    "Hypnosis":         "Hipnosis",
    "Ice Beam":         "Rayo Hielo",
    "Ice Fang":         "Colmillo Hielo",
    "Ice Punch":        "Puño Hielo",
    "Icicle Spear":     "Carámbano",
    "Incinerate":       "Calcinación",
    "Ingrain":          "Arraigo",
    "Iron Tail":        "Cola Férrea",
    "Karate Chop":      "Golpe Kárate",
    "Knock Off":        "Desarme",
    "Leaf Tornado":     "Ciclón de Hojas",
    "Leer":             "Malicioso",
    "Leech Life":       "Chupavidas",
    "Leech Seed":       "Drenadoras",
    "Lick":             "Lengüetazo",
    "Light Screen":     "Pantalla de Luz",
    "Lucky Chant":      "Conjuro",
    "Mach Punch":       "Ultrapuño",
    "Magnet Rise":      "Levitón",
    "Magnitude":        "Magnitud",
    "Mean Look":        "Mal de Ojo",
    "Mega Drain":       "Megaagotar",
    "Mega Punch":       "Megapuño",
    "Metal Sound":      "Eco Metálico",
    "Metronome":        "Metrónomo",
    "Minimize":         "Reducción",
    "Mirror Move":      "Espejo",
    "Mirror Shot":      "Disparo Espejo",
    "Moonlight":        "Luz Lunar",
    "Mud Bomb":         "Bomba Fango",
    "Mud Shot":         "Disparo Lodo",
    "Mud Sport":        "Lodazal",
    "Mud-Slap":         "Bofetón Lodo",
    "Nasty Plot":       "Maquinación",
    "Night Shade":      "Tinieblas",
    "Odor Sleuth":      "Rastreo",
    "Payback":          "Vendetta",
    "Peck":             "Picotazo",
    "Petal Blizzard":   "Tormenta Floral",
    "Pin Missile":      "Pin Misil",
    "Play Nice":        "Camaradería",
    "Pluck":            "Picoteo",
    "Poison Fang":      "Colmillo Veneno",
    "Poison Gas":       "Gas Venenoso",
    "Poison Powder":    "Polvo Veneno",
    "Poison Sting":     "Picotazo Veneno",
    "Pound":            "Destructor",
    "Power Gem":        "Gema Brillante",
    "Power-Up Punch":   "Puño Incremento",
    "Protect":          "Protección",
    "Psybeam":          "Psicorrayo",
    "Psych Up":         "Autosugestión",
    "Psychic":          "Psíquico",
    "Psyshock":         "Psicocarga",
    "Punishment":       "Castigo",
    "Pursuit":          "Persecución",
    "Quick Attack":     "Ataque Rápido",
    "Rage":             "Furia",
    "Rapid Spin":       "Giro Rápido",
    "Razor Leaf":       "Hoja Afilada",
    "Recover":          "Recuperación",
    "Reflect":          "Reflejo",
    "Refresh":          "Alivio",
    "Rest":             "Descanso",
    "Revenge":          "Desquite",
    "Reversal":         "Inversión",
    "Roar":             "Rugido",
    "Rock Blast":       "Pedradas",
    "Rock Polish":      "Pulimento",
    "Rock Slide":       "Pedrada",
    "Rock Smash":       "Golpe Roca",
    "Rock Throw":       "Lanzarrocas",
    "Rock Tomb":        "Tumba Rocas",
    "Rollout":          "Rodar",
    "Safeguard":        "Velo Sagrado",
    "Sand Attack":      "Ataque Arena",
    "Sand Tomb":        "Bucle Arena",
    "Scald":            "Escaldar",
    "Scary Face":       "Cara Susto",
    "Scratch":          "Arañazo",
    "Screech":          "Chirrido",
    "Self-Destruct":    "Autodestrucción",
    "Shadow Ball":      "Bola Sombra",
    "Signal Beam":      "Rayo Señal",
    "Sing":             "Canto",
    "Sky Attack":       "Ataque Aéreo",
    "Slack Off":        "Relajo",
    "Slam":             "Atizar",
    "Slash":            "Cuchillada",
    "Sleep Powder":     "Somnífero",
    "Sleep Talk":       "Sonámbulo",
    "Sludge":           "Lodo",
    "Sludge Bomb":      "Bomba Lodo",
    "Sludge Wave":      "Onda Tóxica",
    "Smack Down":       "Antiaéreo",
    "Smog":             "Polución",
    "Snore":            "Ronquido",
    "Soak":             "Empapar",
    "Soft-Boiled":      "Ovocuración",
    "Sonic Boom":       "Bomba Sónica",
    "Spark":            "Chispa",
    "Spikes":           "Púas",
    "Spite":            "Rencor",
    "Splash":           "Salpicadura",
    "Spore":            "Espora",
    "Spotlight":        "Foco",
    "Stealth Rock":     "Trampa Rocas",
    "Stomp":            "Pisotón",
    "Stone Edge":       "Roca Afilada",
    "Strength":         "Fuerza",
    "String Shot":      "Disparo Demora",
    "Struggle Bug":     "Agujón",
    "Stun Spore":       "Paralizador",
    "Submission":       "Sumisión",
    "Sucker Punch":     "Golpe Bajo",
    "Supersonic":       "Supersónico",
    "Surf":             "Surf",
    "Swallow":          "Tragar",
    "Sweet Kiss":       "Beso Dulce",
    "Sweet Scent":      "Dulce Aroma",
    "Swift":            "Meteoros",
    "Sword Dance":      "Danza Espada",
    "Swords Dance":     "Danza Espada",
    "Synthesis":        "Síntesis",
    "Tackle":           "Placaje",
    "Tail Whip":        "Látigo Cola",
    "Take Down":        "Derribo",
    "Teleport":         "Teletransporte",
    "Thrash":           "Saña",
    "Thunder Fang":     "Colmillo Rayo",
    "Thunder Punch":    "Puño Trueno",
    "Thunder Shock":    "Impactrueno",
    "Thunder Wave":     "Onda Trueno",
    "Thunderbolt":      "Rayo",
    "Toxic":            "Tóxico",
    "Toxic Spikes":     "Púas Tóxicas",
    "Transform":        "Transformación",
    "Tri Attack":       "Triataque",
    "Twineedle":        "Doble Aguijón",
    "Twister":          "Ciclón",
    "Vacuum Wave":      "Onda Vacío",
    "Venom Drench":     "Trampa Venenosa",
    "Venoshock":        "Carga Tóxica",
    "Vice Grip":        "Agarrón",
    "Vine Whip":        "Látigo Cepa",
    "Vital Throw":      "Llave Vital",
    "Wake-Up Slap":     "Espabila",
    "Water Gun":        "Pistola Agua",
    "Water Pulse":      "Hidropulso",
    "Water Sport":      "Hidrochorro",
    "Waterfall":        "Cascada",
    "Will-O-Wisp":      "Fuego Fatuo",
    "Wing Attack":      "Ataque Ala",
    "Wrap":             "Constricción",
    "X-Scissor":        "Tijera X",
    "Yawn":             "Bostezo",
    "Zen Headbutt":     "Cabezazo Zen",
}

def move_name_es(name: str) -> str:
    """Devuelve la traducción al castellano o el nombre original si no está en la tabla."""
    # soporta nombres compuestos tipo "Sword Dance / Agility"
    parts = [p.strip() for p in name.split(" / ")]
    return " / ".join(MOVE_ES.get(p, p) for p in parts)

# ── helpers de IV ─────────────────────────────────────────────────────────────

IV_ORDER  = ["HP", "Atk", "Def", "SpAtk", "SpDef", "Speed"]
IV_LABELS = ["HP", "Atk", "Def", "SpA", "SpD", "Spe"]

# IVs relevantes por rol — claves del dict IVs del JSON
ROLE_IV_KEYS: dict[str, list] = {
    "Atacante Físico":   ["HP", "Atk", "Speed"],
    "Atacante Especial": ["HP", "SpAtk", "Speed"],
    "Mixto":             ["HP", "Atk", "SpAtk", "Speed"],
    "Wall Físico":       ["HP", "Def", "SpDef"],
    "Wall Especial":     ["HP", "SpDef", "Def"],
    "Tanque Mixto":      ["HP", "Def", "SpDef"],
    "Soporte":           ["HP", "Speed"],
}

def iv_pct(ivs: dict, rol: str = "") -> int:
    keys = ROLE_IV_KEYS.get(rol)
    if keys:
        vals = [ivs.get(k, 0) for k in keys]
        return round(sum(vals) / (31 * len(vals)) * 100)
    return round(sum(ivs.values()) / 186 * 100)

def iv_css(v: int) -> str:
    if v >= 25: return "iv-high"
    if v >= 15: return "iv-mid"
    return "iv-low"

def rb_class(pct: int) -> str:
    if pct >= 70: return "rb-green"
    if pct >= 55: return "rb-blue"
    if pct >= 40: return "rb-amber"
    return "rb-red"

def rb_label(cls: str) -> str:
    return {"rb-green": "Bueno", "rb-blue": "Viable",
            "rb-amber": "Regular", "rb-red": "Malo"}[cls]

def rarity_pct(ivs: dict) -> int:
    """Fórmula de PokeOne: promedio de los 5 mejores IVs / 31."""
    top5 = sorted(ivs.values(), reverse=True)[:5]
    return round(sum(top5) / (31 * 5) * 100)

def rarity_css(pct: int) -> str:
    if pct >= 83: return "rarity-purple"
    if pct >= 65: return "rarity-blue"
    if pct >= 55: return "rarity-green"
    if pct >= 45: return "rarity-white"
    return "rarity-grey"

def ev_css(v: int) -> str:
    return "ev-set" if v > 0 else "ev-zero"

def sprite_url(icon: str) -> str:
    name = icon.replace(".png", "")
    return f"https://img.pokemondb.net/sprites/black-white/normal/{name}.png"

def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "-", name.lower()).strip("-")

# ── base stats & rol de combate ───────────────────────────────────────────────
# HP / Atk / Def / SpA / SpD / Spe  (Gen IV–V estándar)
BASE_STATS: dict[int, tuple] = {
    #  ID    HP   Atk  Def  SpA  SpD  Spe
    # ── Gen I ──────────────────────────────────────────────────────────────────
    6:   (78,  84,   78, 109,  85, 100),  # Charizard
    9:   (79,  83,  100,  85, 105,  78),  # Blastoise
    10:  (45,  30,   35,  20,  20,  45),  # Caterpie
    11:  (50,  20,   55,  25,  25,  30),  # Metapod
    12:  (60,  45,   50,  90,  80,  70),  # Butterfree
    13:  (40,  35,   30,  20,  20,  50),  # Weedle
    14:  (45,  25,   50,  25,  25,  35),  # Kakuna
    15:  (65,  90,   40,  45,  80,  75),  # Beedrill
    16:  (40,  45,   40,  35,  35,  56),  # Pidgey
    18:  (83,  80,   75,  70,  70, 101),  # Pidgeot
    19:  (30,  56,   35,  25,  35,  72),  # Rattata
    20:  (55,  81,   60,  50,  70,  97),  # Raticate
    21:  (40,  60,   30,  31,  31,  70),  # Spearow
    22:  (65,  90,   65,  61,  61, 100),  # Fearow
    23:  (35,  60,   44,  40,  54,  55),  # Ekans
    24:  (60,  95,   69,  65,  79,  58),  # Arbok
    25:  (35,  55,   40,  50,  50,  90),  # Pikachu
    27:  (50,  75,   85,  20,  30,  40),  # Sandshrew
    28:  (75, 100,  110,  45,  55,  65),  # Sandslash
    29:  (55,  47,   52,  40,  40,  41),  # Nidoran♀
    30:  (70,  62,   67,  55,  55,  56),  # Nidorina
    31:  (90,  92,   87,  75,  85,  76),  # Nidoqueen
    32:  (46,  57,   40,  40,  40,  50),  # Nidoran♂
    33:  (61,  72,   57,  55,  55,  65),  # Nidorino
    34:  (81, 102,   77,  85,  75,  85),  # Nidoking
    36:  (95,  70,   73,  95,  90,  60),  # Clefable
    37:  (38,  41,   40,  50,  65,  65),  # Vulpix
    38:  (73,  76,   75,  81, 100, 100),  # Ninetales
    39:  (115,  45,   20,  45,  25,  20),  # Jigglypuff
    40:  (140,  70,   45,  85,  50,  45),  # Wigglytuff
    41:  (40,  45,   35,  30,  40,  55),  # Zubat
    42:  (75,  80,   70,  65,  75,  90),  # Golbat
    43:  (45,  50,   55,  75,  65,  30),  # Oddish
    44:  (60,  65,   70,  85,  75,  40),  # Gloom
    45:  (75,  80,   85, 110,  90,  50),  # Vileplume
    46:  (35,  70,   55,  45,  55,  25),  # Paras
    47:  (60,  95,   80,  60,  80,  30),  # Parasect
    48:  (60,  55,   50,  40,  55,  45),  # Venonat
    49:  (70,  65,   60,  90,  75,  90),  # Venomoth
    50:  (10,  55,   25,  35,  45,  95),  # Diglett
    51:  (35,  80,   50,  50,  70, 120),  # Dugtrio
    52:  (40,  45,   35,  40,  40,  90),  # Meowth
    54:  (50,  52,   48,  65,  50,  55),  # Psyduck
    55:  (80,  82,   78,  95,  80,  85),  # Golduck
    56:  (40,  80,   35,  35,  45,  70),  # Mankey
    57:  (65, 105,   60,  60,  70,  95),  # Primeape
    58:  (55,  70,   45,  70,  50,  60),  # Growlithe
    59:  (90, 110,   80, 100,  80,  95),  # Arcanine
    60:  (40,  50,   40,  40,  40,  90),  # Poliwag
    61:  (65,  65,   65,  50,  50,  90),  # Poliwhirl
    62:  (90,  95,   95,  70,  90,  70),  # Poliwrath
    63:  (25,  20,   15, 105,  55,  90),  # Abra
    65:  (55,  50,   45, 135,  95, 120),  # Alakazam
    66:  (70,  80,   50,  35,  35,  35),  # Machop
    68:  (90, 130,   80,  65,  85,  55),  # Machamp
    69:  (50,  75,   35,  70,  30,  40),  # Bellsprout
    70:  (65,  90,   50,  85,  45,  55),  # Weepinbell
    71:  (80, 105,   65, 100,  60,  70),  # Victreebel
    72:  (40,  40,   35,  50,  100,  70),  # Tentacool
    73:  (80,  70,   65,  80, 120, 100),  # Tentacruel
    74:  (40,  80, 100,  30,  30,  20),   # Geodude
    76:  (80, 120, 130,  55,  65,  45),   # Golem
    77:  (50,  85,   55,  65,  65,  90),  # Ponyta
    79:  (90,  65,   65,  40,  40,  15),  # Slowpoke
    80:  (95,  75,  110, 100,  80,  30),  # Slowbro
    81:  (25,  35,   70,  95,  55,  45),  # Magnemite
    82:  (50,  60,   95, 120,  70,  70),  # Magneton
    84:  (35,  85,   45,  35,  35,  75),  # Doduo
    85:  (60, 110,   70,  60,  60, 110),  # Dodrio
    86:  (65,  45,   55,  45,  70,  45),  # Seel
    87:  (90,  70,   80,  70,  95,  70),  # Dewgong
    88:  (80,  80,   50,  40,  50,  25),  # Grimer
    89:  (105, 105,  75,  65,  100,  50),  # Muk
    90:  (30,  65,  100,  45,  25,  40),  # Shellder
    92:  (30,  35,   30,  100,  35,  80),  # Gastly
    94:  (60,  65,   60, 130,  75,  110),  # Gengar
    95:  (35,  45,  160,  30,  45,  70),  # Onix
    96:  (60,  48,   45,  43,  90,  42),  # Drowzee
    97:  (85,  73,   70,  73, 115,  67),  # Hypno
    98:  (30,  105,  90,  25,  25,  50),  # Krabby
    99:  (55,  130, 115,  50,  50,  75),  # Kingler
    100: (40,  30,   50,  55,  55, 100),  # Voltorb
    101: (60,  50,   70,  80,  80, 140),  # Electrode
    103: (95,  95,   85, 125,  75,  55),  # Exeggutor
    106: (50, 120,   53,  35,  110, 87),  # Hitmonlee
    107: (50,  105,  79,  35,  110,  76),  # Hitmonchan
    109: (40,  65,   95,  60,  45,  35),  # Koffing
    110: (65,  90,  120,  85,  70,  60),  # Weezing
    111: (80,  85,  95,  30,  30,  25),   # Rhyhorn
    113: (250,  5,   5,  35, 105,  50),   # Chansey
    114: (65,  55,  115,  100, 40,  60),  # Tangela
    116: (45,  67,   60,  65,  55,  58),  # Horsea
    117: (55,  65,   95,  95,  45,  85),  # Seadra
    118: (45,  67,   60,  35,  50,  63),  # Goldeen
    119: (80,  92,   65,  65,  80,  68),  # Seaking
    120: (30,  45,   55,  70,  55,  85),  # Staryu
    123: (70, 110,   80,  55,  80, 105),  # Scyther
    125: (65,  83,   57,  95,  85, 105),  # Electabuzz
    127: (65, 125, 100,  55,  70,  85),   # Pinsir
    128: (75, 100,  95,  40,  70, 110),   # Tauros
    129: (20,  10,   55,  15,  20,  80),  # Magikarp
    130: (95, 125,  79,  60, 100,  81),   # Gyarados
    132: (48,  48,   48,  48,  48,  48),  # Ditto
    133: (55,  55,   50,  45,  65,  55),  # Eevee
    135: (65,  65,   60, 110,  95, 130),  # Jolteon
    138: (35,  40,  100,  90,  55,  35),  # Omanyte
    140: (30,  80,   90,  55,  45,  55),  # Kabuto
    142: (80, 105,  65,  60,  75, 130),   # Aerodactyl
    143: (160, 110,  65,  65,  110, 30),  # Snorlax
    144: (90,  85,  100, 95, 125,  85),   # Articuno
    145: (90,  90,  85, 125,  90, 100),   # Zapdos
    146: (90, 100,  90, 125,  85,  90),   # Moltres
    147: (41,  64,   45,  50,  50,  50),  # Dratini
    # ── Gen II ─────────────────────────────────────────────────────────────────
    153: (60,  62,   80,  63,  80,  60),  # Bayleef
    156: (58,  64,   58,  80,  65,  80),  # Quilava
    161: (35,  46,   34,  35,  45,  20),  # Sentret
    162: (85,  76,   64,  45,  55,  90),  # Furret
    163: (60,  30,   30,  36,  56,  50),  # Hoothoot
    164: (100, 50,   50,  76,  96,  70),  # Noctowl
    165: (40,  20,   30,  40,  80,  55),  # Ledyba
    166: (55,  35,   50,  55,  110, 85),  # Ledian
    167: (40,  60,   40,  40,  40,  30),  # Spinarak
    168: (70,  90,   70,  60,  60,  40),  # Ariados
    170: (75,  38,   38,  56,  56,  67),  # Chinchou
    171: (125, 58,   58,  76,  76,  67),  # Lanturn
    175: (35,  20,   65,  40,  65,  20),  # Togepi
    179: (55,  40,   40,  65,  45,  35),  # Mareep
    187: (35,  45,   35,  35,  45,  50),  # Hoppip
    188: (55,  45,   50,  45,  65,  80),  # Skiploom
    194: (55,  45,   45,  25,  25,  15),  # Wooper
    195: (95,  85,   85,  65,  65,  35),  # Quagsire
    198: (60,  85,   42,  85,  42,  91),  # Murkrow
    209: (60,  80,   50,  40,  40,  30),  # Snubbull
    210: (90, 120,  75,  60,  60,  45),   # Granbull
    211: (65,  95,   75,  55,  55,  85),  # Qwilfish
    217: (90, 130,   75,  75,  75,  55),  # Ursaring
    218: (40,  40,   40,  70,  40,  20),  # Slugma
    228: (45,  60,   30,  80,  50,  65),  # Houndour
    229: (75,  90,   50, 110,  80,  95),  # Houndoom
    232: (90, 120,  120,  60,  60,  50),  # Donphan
    316: (70,  43,   53,  43,  53,  40),  # Gulpin
    # ── Gen III ────────────────────────────────────────────────────────────────
    302: (50,  75,   75,  65,  65,  50),  # Sableye
    # ── Gen IV ─────────────────────────────────────────────────────────────────
    401: (37,  25,   41,  25,  41,  25),  # Kricketot
    466: (75, 123,   67,  95,  85,  95),  # Electivire
}

# Naturalezas idóneas por rol
IDEAL_NATURES: dict[str, list] = {
    "Atacante Físico":   ["Adamant (+Atk/-SpA)", "Jolly (+Spe/-SpA)"],
    "Atacante Especial": ["Modest (+SpA/-Atk)", "Timid (+Spe/-Atk)"],
    "Mixto":             ["Naive (+Spe/-SpD)", "Hasty (+Spe/-Def)", "Rash (+SpA/-SpD)", "Naughty (+Atk/-SpD)"],
    "Wall Físico":       ["Bold (+Def/-Atk)", "Impish (+Def/-SpA)", "Relaxed (+Def/-Spe)"],
    "Wall Especial":     ["Calm (+SpD/-Atk)", "Careful (+SpD/-SpA)", "Sassy (+SpD/-Spe)"],
    "Tanque Mixto":      ["Bold (+Def/-Atk)", "Calm (+SpD/-Atk)", "Impish (+Def/-SpA)"],
    "Soporte":           ["Timid (+Spe/-Atk)", "Bold (+Def/-Atk)", "Calm (+SpD/-Atk)"],
}

# Descripción de cada naturaleza
NATURE_DESC: dict[str, str] = {
    "Hardy":   "Neutra — no modifica ningún stat.",
    "Lonely":  "+Atk / −Def — agresiva pero frágil físicamente.",
    "Brave":   "+Atk / −Spe — más daño físico, pero más lento.",
    "Adamant": "+Atk / −SpA — ideal para atacantes físicos puros.",
    "Naughty": "+Atk / −SpD — agresiva, pero vulnerable a ataques especiales.",
    "Bold":    "+Def / −Atk — defensiva, ideal para walls físicos.",
    "Docile":  "Neutra — no modifica ningún stat.",
    "Relaxed": "+Def / −Spe — más defensa física, pero más lento.",
    "Impish":  "+Def / −SpA — defensiva sin sacrificar velocidad.",
    "Lax":     "+Def / −SpD — más defensa física, peor defensa especial.",
    "Timid":   "+Spe / −Atk — velocidad máxima, ideal para sweepers especiales.",
    "Hasty":   "+Spe / −Def — rápido pero frágil físicamente.",
    "Serious": "Neutra — no modifica ningún stat.",
    "Jolly":   "+Spe / −SpA — velocidad máxima, ideal para sweepers físicos.",
    "Naive":   "+Spe / −SpD — rápido pero vulnerable a ataques especiales.",
    "Modest":  "+SpA / −Atk — ideal para atacantes especiales puros.",
    "Mild":    "+SpA / −Def — más poder especial, pero frágil físicamente.",
    "Quiet":   "+SpA / −Spe — más poder especial, pero más lento.",
    "Bashful": "Neutra — no modifica ningún stat.",
    "Rash":    "+SpA / −SpD — ofensiva especial, vulnerable a ataques especiales.",
    "Calm":    "+SpD / −Atk — defensiva especial, ideal para walls especiales.",
    "Gentle":  "+SpD / −Def — más defensa especial, frágil físicamente.",
    "Sassy":   "+SpD / −Spe — defensiva especial, pero más lento.",
    "Careful": "+SpD / −SpA — defensiva especial sin sacrificar ataque físico.",
    "Quirky":  "Neutra — no modifica ningún stat.",
}

# Descripción de habilidades
ABILITY_DESC: dict[str, str] = {
    "Adaptability":   "Aumenta el multiplicador STAB de 1.5× a 2×.",
    "Blaze":          "Potencia ataques Fire en ×1.5 cuando el HP cae al 33% o menos.",
    "Chlorophyll":    "Dobla la velocidad bajo sol.",
    "Clear Body":     "Impide que los rivales bajen los stats propios.",
    "Compound Eyes":  "Aumenta la precisión propia en un 30%.",
    "Damp":           "Impide el uso de Explosión y Autodestrucción en el campo.",
    "Early Bird":     "Despierta del sueño en la mitad de turnos.",
    "Effect Spore":   "30% de chance de paralizar/envenenar/adormecer al hacer contacto.",
    "Flash Fire":     "Inmune a ataques Fire; los absorbe para potenciar los propios.",
    "Guts":           "Sube Atk en ×1.5 cuando hay estado alterado.",
    "Hustle":         "Sube Atk en ×1.5 pero reduce precisión de ataques físicos.",
    "Hyper Cutter":   "Impide que bajen el stat de Ataque.",
    "Intimidate":     "Al entrar, baja el Ataque del rival 1 etapa.",
    "Keen Eye":       "Impide que bajen la Precisión propia.",
    "Leaf Guard":     "Inmune a estados alterados bajo sol.",
    "Levitate":       "Inmune a ataques Ground.",
    "Lightning Rod":  "Inmune a ataques Electric; absorbe para subir SpAtk.",
    "Limber":         "Inmune a parálisis.",
    "Natural Cure":   "Cura el estado alterado al cambiar de combate.",
    "No Guard":       "Todos los ataques (propios y rivales) tienen precisión perfecta.",
    "Oblivious":      "Inmune a Atracción y Provocación.",
    "Overgrow":       "Potencia ataques Grass en ×1.5 cuando el HP cae al 33% o menos.",
    "Own Tempo":      "Inmune a confusión.",
    "Pickup":         "Puede recoger objetos del suelo después del combate.",
    "Poison Point":   "30% de chance de envenenar al rival al hacer contacto físico.",
    "Pressure":       "El rival gasta 2 PP por movimiento en vez de 1.",
    "Regenerator":    "Recupera 1/3 del HP máximo al retirarse del combate.",
    "Rock Head":      "No recibe daño de retroceso propio.",
    "Run Away":       "Garantiza huida de combates contra salvajes.",
    "Serene Grace":   "Duplica la probabilidad de efectos secundarios (flinch, estados…).",
    "Shed Skin":      "33% de probabilidad por turno de curar el estado alterado.",
    "Shell Armor":    "Impide golpes críticos rivales.",
    "Static":         "30% de chance de paralizar al rival al hacer contacto físico.",
    "Steadfast":      "Sube Velocidad 1 etapa al sufrir flinch.",
    "Stench":         "10% de chance de causar flinch al atacar.",
    "Sticky Hold":    "Impide que el rival robe o tire el objeto propio.",
    "Storm Drain":    "Inmune a ataques Water; absorbe para subir SpAtk.",
    "Swift Swim":     "Dobla la velocidad bajo lluvia.",
    "Synchronize":    "Transmite al rival el estado alterado propio (veneno, quemadura, parálisis).",
    "Technician":     "Multiplica por 1.5 los movimientos con potencia base ≤60.",
    "Thick Fat":      "Reduce a la mitad el daño recibido de ataques Fire e Ice.",
    "Torrent":        "Potencia ataques Water en ×1.5 cuando el HP cae al 33% o menos.",
    "Trace":          "Copia la habilidad del rival al entrar en combate.",
    "Truant":         "Solo puede atacar un turno de cada dos.",
    "Unaware":        "Ignora los cambios de stat del rival al calcular daño.",
    "Vital Spirit":   "Inmune a sueño.",
    "Volt Absorb":    "Inmune a ataques Electric; los absorbe para recuperar HP.",
    "Water Absorb":   "Inmune a ataques Water; los absorbe para recuperar HP.",
    "White Smoke":    "Impide que los rivales bajen los stats propios.",
}

# Qué stats sube/baja cada naturaleza  (None = neutro)
NATURE_MOD: dict[str, tuple] = {
    "Hardy":   (None, None), "Docile":  (None, None), "Serious": (None, None),
    "Bashful": (None, None), "Quirky":  (None, None),
    "Lonely":  ("Atk", "Def"),  "Brave":   ("Atk", "Spe"),
    "Adamant": ("Atk", "SpA"),  "Naughty": ("Atk", "SpD"),
    "Bold":    ("Def", "Atk"),  "Relaxed": ("Def", "Spe"),
    "Impish":  ("Def", "SpA"),  "Lax":     ("Def", "SpD"),
    "Modest":  ("SpA", "Atk"),  "Mild":    ("SpA", "Def"),
    "Rash":    ("SpA", "SpD"),  "Quiet":   ("SpA", "Spe"),
    "Calm":    ("SpD", "Atk"),  "Gentle":  ("SpD", "Def"),
    "Careful": ("SpD", "SpA"),  "Sassy":   ("SpD", "Spe"),
    "Timid":   ("Spe", "Atk"),  "Hasty":   ("Spe", "Def"),
    "Jolly":   ("Spe", "SpA"),  "Naive":   ("Spe", "SpD"),
}

# Etiquetas de rol: (icono, texto_es, css_class)
ROLE_META: dict[str, tuple] = {
    "Atacante Especial": ("✦", "Atk Esp",  "role-special"),
    "Atacante Físico":   ("⚔", "Atk Fís",  "role-physical"),
    "Mixto":             ("⇌", "Mixto",     "role-mixed"),
    "Wall Físico":       ("🛡", "Wall Fís",  "role-wall-p"),
    "Wall Especial":     ("🔰", "Wall Esp",  "role-wall-s"),
    "Tanque Mixto":      ("⬡", "Tanque",    "role-tank"),
    "Soporte":           ("♦", "Soporte",   "role-support"),
}

def infer_role(pokemon_id: int, nature: str, evs: dict) -> str:
    """
    Clasifica el rol de combate combinando base stats, naturaleza y EVs.
    Devuelve una clave de ROLE_META.
    """
    bs = BASE_STATS.get(pokemon_id)
    if bs is None:
        return "Mixto"

    _, b_atk, b_def, b_spa, b_spd, b_spe = bs
    b_bulk = (b_def + b_spd) / 2

    # Puntuación ofensiva ajustada por naturaleza
    nat_up, nat_dn = NATURE_MOD.get(nature, (None, None))
    atk_score = b_atk * (1.1 if nat_up == "Atk" else 0.9 if nat_dn == "Atk" else 1.0)
    spa_score = b_spa * (1.1 if nat_up == "SpA" else 0.9 if nat_dn == "SpA" else 1.0)

    # EVs confirman orientación si ya están asignados
    ev_atk = evs.get("Atk", 0)
    ev_spa = evs.get("SpAtk", 0)
    ev_def = evs.get("Def", 0)
    ev_spd = evs.get("SpDef", 0)
    ev_hp  = evs.get("HP", 0)
    ev_off = ev_atk + ev_spa
    ev_def_total = ev_def + ev_spd + ev_hp

    # Si hay EVs significativos, dejan que hablen
    if ev_off > 100:
        if ev_atk > ev_spa * 1.5:
            return "Atacante Físico"
        if ev_spa > ev_atk * 1.5:
            return "Atacante Especial"
    if ev_def_total > ev_off and ev_def_total > 150:
        if ev_def > ev_spd:
            return "Wall Físico"
        return "Wall Especial"

    # Sin EVs claros → base stats + naturaleza
    off_diff  = atk_score - spa_score          # >0 más físico, <0 más especial
    bulk_high = b_bulk >= 70                   # buen bulk base

    if bulk_high and b_bulk >= (max(atk_score, spa_score) - 10):
        # El bulk es tan relevante como la ofensa
        if b_def >= b_spd + 15:
            return "Wall Físico"
        if b_spd >= b_def + 15:
            return "Wall Especial"
        return "Tanque Mixto"

    if abs(off_diff) < 10:
        return "Mixto"
    if off_diff >= 10:
        return "Atacante Físico"
    return "Atacante Especial"

# ── card builder ──────────────────────────────────────────────────────────────

# IV_LABELS en el mismo orden que IV_ORDER para la conversión label→key del JSON
IV_LABEL_TO_KEY = dict(zip(IV_LABELS, IV_ORDER))  # HP→HP, Atk→Atk, SpA→SpAtk, etc.

def stat_row(label: str, stats: list, css_fn, relevant_keys: list | None = None) -> str:
    cells = ""
    for lbl, val in zip(IV_LABELS, stats):
        css = css_fn(val) if callable(css_fn) else css_fn
        display = str(val) if val != 0 or css_fn == ev_css else "0"
        # atenúa celdas de IVs no relevantes para el rol
        dim = (relevant_keys is not None
               and IV_LABEL_TO_KEY.get(lbl) not in relevant_keys)
        cell_extra = ' iv-dim' if dim else ''
        cells += (
            f'<div class="sr-cell{cell_extra}">'
            f'<span class="sr-s">{lbl}</span>'
            f'<span class="sr-v {css}">{display}</span>'
            f'</div>'
        )
    return (
        f'<div class="stat-row-line">'
        f'<span class="sr-lbl">{label}</span>'
        f'<div class="sr-cells">{cells}</div>'
        f'</div>'
    )

# ── análisis del equipo ───────────────────────────────────────────────────────

# Efectividad ofensiva por tipo atacante → tipos que cubre bien (×2 o más)
TYPE_OFFENSE: dict[str, list] = {
    "Fire":     ["Grass","Bug","Ice","Steel"],
    "Water":    ["Fire","Ground","Rock"],
    "Grass":    ["Water","Ground","Rock"],
    "Electric": ["Water","Flying"],
    "Ice":      ["Grass","Ground","Flying","Dragon"],
    "Fighting": ["Normal","Ice","Rock","Dark","Steel"],
    "Poison":   ["Grass","Fairy"],
    "Ground":   ["Fire","Electric","Poison","Rock","Steel"],
    "Flying":   ["Grass","Fighting","Bug"],
    "Psychic":  ["Fighting","Poison"],
    "Bug":      ["Grass","Psychic","Dark"],
    "Rock":     ["Fire","Ice","Flying","Bug"],
    "Ghost":    ["Psychic","Ghost"],
    "Dragon":   ["Dragon"],
    "Dark":     ["Psychic","Ghost"],
    "Steel":    ["Ice","Rock","Fairy"],
    "Fairy":    ["Fighting","Dragon","Dark"],
    "Normal":   [],
}

# Debilidades defensivas por tipo del Pokémon (simplificado, sin inmunidades)
TYPE_WEAKNESS: dict[str, list] = {
    "Fire":     ["Water","Ground","Rock"],
    "Water":    ["Grass","Electric"],
    "Grass":    ["Fire","Ice","Poison","Flying","Bug"],
    "Electric": ["Ground"],
    "Ice":      ["Fire","Fighting","Rock","Steel"],
    "Fighting": ["Flying","Psychic","Fairy"],
    "Poison":   ["Ground","Psychic"],
    "Ground":   ["Water","Grass","Ice"],
    "Flying":   ["Electric","Ice","Rock"],
    "Psychic":  ["Bug","Ghost","Dark"],
    "Bug":      ["Fire","Flying","Rock"],
    "Rock":     ["Water","Grass","Fighting","Ground","Steel"],
    "Ghost":    ["Ghost","Dark"],
    "Dragon":   ["Ice","Dragon","Fairy"],
    "Dark":     ["Fighting","Bug","Fairy"],
    "Steel":    ["Fire","Fighting","Ground"],
    "Fairy":    ["Poison","Steel"],
    "Normal":   ["Fighting"],
}

# Habilidades con sinergias notables
ABILITY_SYNERGY: dict[str, str] = {
    "Serene Grace":  "Serene Grace duplica la prob. de efectos secundarios (flinch, parálisis…)",
    "Blaze":         "Blaze potencia movimientos Fire al 33% HP — combo con Eruption invertido",
    "Overgrow":      "Overgrow potencia movimientos Grass al 33% HP",
    "Torrent":       "Torrent potencia movimientos Water al 33% HP",
    "Swarm":         "Swarm potencia movimientos Bug al 33% HP",
    "Hyper Cutter":  "Hyper Cutter impide que bajen el Ataque — ideal en atacante físico",
    "Static":        "Static tiene 30% de paralizar al contacto — sinergia defensiva/soporte",
    "Intimidate":    "Intimidate baja Atk rival al entrar — sinergia defensiva",
    "Shed Skin":     "Shed Skin cura estados alterados 33% por turno — sustain pasivo",
    "Damp":          "Damp impide explosiones — nicho anti-Selfdestruct/Explosion",
    "Sticky Hold":   "Sticky Hold impide robo de objeto — poco impacto en story",
    "Leaf Guard":    "Leaf Guard inmune a estados bajo sol — situacional",
}

# Tipos «clave» para la progresión de Kanto/Johto
COVERAGE_TARGETS = ["Rock","Ground","Water","Flying","Psychic","Ghost","Dragon","Dark","Steel"]

def analyse_team(slots: list) -> dict:
    """
    Analiza el equipo y devuelve un dict con:
      score, iv_avg, roles, type_coverage, shared_weaknesses,
      synergies, combos, gaps, replaceable, notes
    """
    members = []
    for s in slots:
        pk = s["Pokemon"]
        p  = pk["Payload"]
        sd = pk["StaticData"]
        pid    = p["PokemonID"]
        nature = p["NatureName"]
        evs    = p["EVs"]
        ivs    = p["IVs"]
        rol    = infer_role(pid, nature, evs)
        pct    = iv_pct(ivs, rol)
        types  = [t["name"] for t in sd.get("Types", [])]
        bs     = BASE_STATS.get(pid)
        obj    = MOVESETS.get(slug(sd["Name"]), [])
        members.append({
            "name":    sd["Name"],
            "pid":     pid,
            "level":   p["Level"],
            "types":   types,
            "ability": pk.get("Ability") or "",
            "rol":     rol,
            "pct":     pct,
            "bs":      bs,
            "obj_moves": [m["name"] for m in obj],
            "cur_moves": [m["Name"] for m in p["Moves"] if m],
            "nature":  nature,
        })

    # ── IVs medio ─────────────────────────────────────────────────────────────
    iv_avg = round(sum(m["pct"] for m in members) / len(members)) if members else 0

    # ── roles ─────────────────────────────────────────────────────────────────
    from collections import Counter
    role_counts = Counter(m["rol"] for m in members)

    # ── cobertura ofensiva (tipos que cubre el equipo con moveset objetivo) ───
    covered = set()
    for m in members:
        all_moves = set(m["obj_moves"] + m["cur_moves"])
        for t in m["types"]:
            covered.update(TYPE_OFFENSE.get(t, []))
        # bonus por STAB implícito del moveset objetivo
        for mv_name in m["obj_moves"]:
            for t, targets in TYPE_OFFENSE.items():
                if any(t.lower() in mv_name.lower() for _ in [1]):
                    pass  # no podemos inferir tipo del movimiento por nombre

    # cobertura real = tipos del equipo
    team_types = set()
    for m in members:
        team_types.update(m["types"])
    for t in team_types:
        covered.update(TYPE_OFFENSE.get(t, []))

    gaps = [t for t in COVERAGE_TARGETS if t not in covered]

    # ── debilidades compartidas ───────────────────────────────────────────────
    weakness_count: dict[str, int] = {}
    for m in members:
        seen = set()
        for t in m["types"]:
            for w in TYPE_WEAKNESS.get(t, []):
                if w not in seen:
                    weakness_count[w] = weakness_count.get(w, 0) + 1
                    seen.add(w)
    shared_weaknesses = {t: n for t, n in weakness_count.items() if n >= 3}

    # ── sinergias de habilidades ──────────────────────────────────────────────
    synergies = []
    for m in members:
        ab = m["ability"]
        if ab in ABILITY_SYNERGY:
            synergies.append(f"{m['name']} ({ab}): {ABILITY_SYNERGY[ab]}")

    # ── combos detectados ─────────────────────────────────────────────────────
    combos = []
    names  = {m["name"] for m in members}
    types_all = {t for m in members for t in m["types"]}
    obj_all   = {mv for m in members for mv in m["obj_moves"]}
    cur_all   = {mv for m in members for mv in m["cur_moves"]}

    # Serene Grace + Air Slash / Thunder Wave
    sg = next((m for m in members if m["ability"] == "Serene Grace"), None)
    if sg:
        if "Air Slash" in sg["obj_moves"]:
            combos.append(f"{sg['name']} Serene Grace + Air Slash → 60% flinch, control de turno")
        if "Thunder Wave" in sg["obj_moves"] + sg["cur_moves"]:
            combos.append(f"{sg['name']} Thunder Wave + Serene Grace → parálisis + flinch combo")
        if "Nasty Plot" in sg["obj_moves"]:
            combos.append(f"{sg['name']} Nasty Plot + STAB Fairy → sweeper setup especial")

    # Blaze + Eruption
    bl = next((m for m in members if m["ability"] == "Blaze"), None)
    if bl and "Eruption" in bl["obj_moves"]:
        combos.append(f"{bl['name']} Blaze + Eruption: máximo daño a HP alto, Blaze como seguro a HP bajo")

    # Static paraliza al hacer contacto → ralentiza rivales físicos
    st = next((m for m in members if m["ability"] == "Static"), None)
    if st:
        combos.append(f"{st['name']} Static → paralización pasiva al recibir ataques de contacto")

    # Coberturas complementarias Water+Ground (Wooper/Quagsire)
    if "Water" in types_all and "Ground" in types_all:
        combos.append("Water + Ground en equipo → cobertura cruzada Fire/Rock/Electric")

    # Grass + Poison cubre Fairy y Water
    if "Grass" in types_all and "Poison" in types_all:
        combos.append("Grass + Poison → STAB cubre Water, Rock, Ground, Fairy")

    # ── Pokémon reemplazables ─────────────────────────────────────────────────
    replaceable = []
    for m in members:
        bs = m["bs"]
        if not bs: continue
        bst = sum(bs)
        reasons = []
        if bst < 300:
            reasons.append(f"BST {bst} muy bajo — base stats pobres a largo plazo")
        if m["pct"] < 40:
            reasons.append(f"IVs relevantes solo al {m['pct']}%")
        if m["rol"] == "Mixto" and bst < 350:
            reasons.append("stats equilibrados sin especialización clara")
        if reasons:
            replaceable.append({"name": m["name"], "reasons": reasons})

    # ── puntuación compuesta ──────────────────────────────────────────────────
    score = 5.0

    # IVs medios
    if iv_avg >= 70:   score += 1.5
    elif iv_avg >= 55: score += 0.8
    elif iv_avg < 40:  score -= 1.0

    # diversidad de roles (penaliza equipo muy mono-rol)
    if len(role_counts) >= 3: score += 0.5
    if role_counts.most_common(1)[0][1] >= 4: score -= 0.5  # >66% mismo rol

    # huecos de cobertura
    score -= len(gaps) * 0.2

    # debilidades compartidas graves
    score -= len(shared_weaknesses) * 0.3

    # combos y sinergias
    score += min(len(combos) * 0.2, 1.0)

    # Pokémon reemplazables
    score -= len(replaceable) * 0.3

    score = max(1.0, min(10.0, score))

    return {
        "score":             round(score, 1),
        "iv_avg":            iv_avg,
        "role_counts":       dict(role_counts),
        "covered_types":     sorted(covered),
        "gaps":              gaps,
        "shared_weaknesses": shared_weaknesses,
        "synergies":         synergies,
        "combos":            combos,
        "replaceable":       replaceable,
        "members":           members,
    }


def build_team_analysis(slots: list) -> tuple:
    """Devuelve (summary_html, detail_html) para colocarlos separados en la página."""
    a = analyse_team(slots)
    score = a["score"]

    if score >= 7:   sc, sl = "#3fb950", "Bueno"
    elif score >= 5: sc, sl = "#d29922", "Regular"
    else:            sc, sl = "#f85149", "Débil"

    role_pills = "".join(
        f'<span class="ta-pill">{rol} <b>{n}</b></span>'
        for rol, n in sorted(a["role_counts"].items(), key=lambda x: -x[1])
    )
    iv_avg   = a["iv_avg"]
    iv_color = "#3fb950" if iv_avg >= 65 else "#d29922" if iv_avg >= 45 else "#f85149"

    summary_html = f"""
<div class="team-analysis ta-summary">
  <div class="ta-score-wrap">
    <div class="ta-score" style="color:{sc}">{score}</div>
    <div class="ta-score-label" style="color:{sc}">{sl}</div>
    <div class="ta-score-sub">/ 10</div>
  </div>
  <div class="ta-overview">
    <div class="ta-row">
      <span class="ta-label">IVs medios</span>
      <div class="ta-bar-wrap">
        <div class="ta-bar" style="width:{iv_avg}%;background:{iv_color}"></div>
      </div>
      <span class="ta-bar-val" style="color:{iv_color}">{iv_avg}%</span>
    </div>
    <div class="ta-row">
      <span class="ta-label">Roles</span>
      <div class="ta-pills">{role_pills}</div>
    </div>
  </div>
</div>"""

    covered_html = "".join(
        f'<span class="ta-type-ok">{t}</span>' for t in a["covered_types"]
    )
    gaps_html = "".join(
        f'<span class="ta-type-gap">{t}</span>' for t in a["gaps"]
    ) or '<span class="ta-none">Ninguno destacado</span>'
    sw_html = "".join(
        f'<span class="ta-weak">{t} ×{n}</span>'
        for t, n in sorted(a["shared_weaknesses"].items(), key=lambda x: -x[1])
    ) or '<span class="ta-none">Sin debilidades graves compartidas</span>'
    syn_html = "".join(
        f'<li>{s}</li>' for s in a["synergies"]
    ) or '<li class="ta-none">Sin sinergias de habilidad destacadas</li>'
    combo_html = "".join(
        f'<li>{c}</li>' for c in a["combos"]
    ) or '<li class="ta-none">Sin combos detectados</li>'
    repl_html = "".join(
        f'<li><b>{r["name"]}</b>: {" · ".join(r["reasons"])}</li>'
        for r in a["replaceable"]
    ) or '<li class="ta-none">Ninguno — equipo sólido en su conjunto</li>'

    detail_html = f"""
<div class="team-analysis ta-detail">
  <div class="ta-grid">
    <div class="ta-block">
      <div class="ta-block-title">Cobertura ofensiva</div>
      <div class="ta-types">{covered_html}</div>
    </div>
    <div class="ta-block">
      <div class="ta-block-title">Huecos de cobertura</div>
      <div class="ta-types">{gaps_html}</div>
    </div>
    <div class="ta-block">
      <div class="ta-block-title">Debilidades compartidas (≥3 miembros)</div>
      <div class="ta-types">{sw_html}</div>
    </div>
    <div class="ta-block ta-block-full">
      <div class="ta-block-title">Sinergias de habilidad</div>
      <ul class="ta-list">{syn_html}</ul>
    </div>
    <div class="ta-block ta-block-full">
      <div class="ta-block-title">Combos y estrategias</div>
      <ul class="ta-list">{combo_html}</ul>
    </div>
    <div class="ta-block ta-block-full">
      <div class="ta-block-title">Pokémon reemplazables</div>
      <ul class="ta-list">{repl_html}</ul>
    </div>
  </div>
</div>"""

    return summary_html, detail_html


def build_top_html(team_slots: list, raw_boxes: list, top_n: int = 30) -> str:
    """Lista plana con los top_n Pokémon de todo el almacenamiento (equipo + cajas),
    ordenados por % IVs por rol de mayor a menor."""

    # Recopilar todos los slots con su ubicación
    all_entries = []
    for slot in team_slots:
        if slot:
            all_entries.append(("equipo", slot))
    for i, box in enumerate(raw_boxes):
        if not box or i == 0:
            continue
        for slot in box:
            if slot:
                all_entries.append((i, slot))

    # Calcular pct por rol para cada uno y ordenar
    def entry_pct(entry):
        _, slot = entry
        p = slot["Pokemon"]["Payload"]
        return iv_pct(p["IVs"], infer_role(p["PokemonID"], p["NatureName"], p["EVs"]))

    all_entries.sort(key=entry_pct, reverse=True)
    top = all_entries[:top_n]

    rows = ""
    for rank, (location, slot) in enumerate(top, 1):
        pk      = slot["Pokemon"]
        payload = pk["Payload"]
        sd      = pk["StaticData"]
        ivs     = payload["IVs"]
        nature  = payload["NatureName"]
        ability = pk.get("Ability") or "—"
        evs     = payload["EVs"]
        pid     = payload["PokemonID"]
        level   = payload["Level"]
        nick    = payload.get("Nickname") or ""
        shiny   = payload.get("Shiny", False)

        rol_key    = infer_role(pid, nature, evs)
        _, rol_text, rol_css = ROLE_META[rol_key]
        rel_keys   = ROLE_IV_KEYS.get(rol_key)
        pct        = iv_pct(ivs, rol_key)
        pct_global = rarity_pct(ivs)
        rbc        = rb_class(pct)
        rar        = rarity_css(pct_global)
        icon       = sprite_url(sd["Icon"])
        name       = sd["Name"]
        display    = f'{"★ " if shiny else ""}{name}{f" ({nick})" if nick else ""}'

        # badge de ubicación
        if location == "equipo":
            loc_html = '<span class="top-loc top-loc-team">Equipo</span>'
        else:
            loc_html = f'<span class="top-loc top-loc-box">C{location}</span>'

        # rank medal para top 3
        if rank == 1:   rank_html = '<span class="top-rank rank-gold">1</span>'
        elif rank == 2: rank_html = '<span class="top-rank rank-silver">2</span>'
        elif rank == 3: rank_html = '<span class="top-rank rank-bronze">3</span>'
        else:           rank_html = f'<span class="top-rank">{rank}</span>'

        types = sd.get("Types", [])
        type_badges = "".join(
            f'<span class="type-badge" style="background:{t["color"]}22;color:{t["color"]};'
            f'border:1px solid {t["color"]}44">{t["name"]}</span>'
            for t in types
        )

        iv_cells = ""
        for json_key, lbl in zip(IV_ORDER, IV_LABELS):
            v   = ivs.get(json_key, 0)
            css = iv_css(v)
            dim = " iv-dim" if rel_keys and json_key not in rel_keys else ""
            iv_cells += (
                f'<div class="sr-cell{dim}">'
                f'<span class="sr-s">{lbl}</span>'
                f'<span class="sr-v {css}">{v}</span>'
                f'</div>'
            )

        mdata = modal_data(slot)
        rows += (
            f'<div class="box-list-row">'
            f'{rank_html}'
            f'{loc_html}'
            f'<img class="bls-spr" src="{icon}" alt="{name}">'
            f'<div class="bls-info">'
            f'<span class="bls-name {rar}">{display}</span>'
            f'<div class="bls-meta">Lv.{level}</div>'
            f'</div>'
            f'<span class="combat-role {rol_css} top-rol">{rol_text}</span>'
            f'<div class="bls-ivs sr-cells">{iv_cells}</div>'
            f'<div class="role-badge {rbc}" onclick="openRbModal(this)" data-modal=\'{mdata}\' style="cursor:pointer">'
            f'<span class="rb-score">{pct}%</span>'
            f'<span class="rb-label">{rb_label(rbc)}</span>'
            f'</div>'
            f'</div>'
        )

    total = len(all_entries)
    return f"""
<div style="font-size:0.75em;color:#8b949e;margin-bottom:14px">
  Top {top_n} de {total} Pokémon totales ordenados por % IVs relevantes al rol
</div>
<div class="box-section-list">{rows}</div>"""


def modal_data(slot: dict) -> str:
    """Genera el JSON embebido en data-modal para openRbModal()."""
    import json as _json
    pk      = slot["Pokemon"]
    payload = pk["Payload"]
    sd      = pk["StaticData"]
    ivs     = payload["IVs"]
    evs     = payload["EVs"]
    pid     = payload["PokemonID"]
    nature  = payload["NatureName"]
    ability = pk.get("Ability") or ""
    level   = payload["Level"]
    nick    = payload.get("Nickname") or ""
    shiny   = payload.get("Shiny", False)

    rol_key  = infer_role(pid, nature, evs)
    _, rol_text, _ = ROLE_META[rol_key]
    pct      = iv_pct(ivs, rol_key)
    rbc      = rb_class(pct)
    rel_keys = ROLE_IV_KEYS.get(rol_key, [])

    iv_list = [
        {"s": lbl, "v": ivs.get(k, 0), "dim": k not in rel_keys}
        for k, lbl in zip(IV_ORDER, IV_LABELS)
    ]

    d = {
        "name":         (f"★ " if shiny else "") + sd["Name"] + (f" ({nick})" if nick else ""),
        "level":        level,
        "nature":       nature,
        "nature_desc":  NATURE_DESC.get(nature, ""),
        "ability":      ability,
        "ability_desc": ABILITY_DESC.get(ability, ""),
        "rol":          rol_key,
        "rol_text":     rol_text,
        "pct":          pct,
        "rbc":          rbc,
        "ivs":          iv_list,
        "ideal_natures": IDEAL_NATURES.get(rol_key, []),
    }
    return _json.dumps(d, ensure_ascii=False).replace("'", "&#39;")


def build_card(slot: dict) -> str:
    pk      = slot["Pokemon"]
    payload = pk["Payload"]
    sd      = pk["StaticData"]

    name    = sd["Name"].upper()
    key     = slug(sd["Name"])
    icon    = sprite_url(sd["Icon"])
    level   = payload["Level"]
    nature  = payload["NatureName"]
    ability = pk["Ability"] or "—"
    shiny   = payload.get("Shiny", False)
    nick    = payload.get("Nickname") or ""

    ivs   = payload["IVs"]
    evs   = payload["EVs"]
    moves = payload["Moves"]
    pid   = payload["PokemonID"]

    iv_vals = [ivs.get(k, 0) for k in IV_ORDER]
    ev_vals = [evs.get(k, 0) for k in IV_ORDER]

    # rol de combate — debe calcularse antes que el % de IVs
    rol_key  = infer_role(pid, nature, evs)
    rol_icon, rol_text, rol_css = ROLE_META[rol_key]

    pct        = iv_pct(ivs, rol_key)          # % por rol → badge de calidad
    pct_global = rarity_pct(ivs)  # top-5 IVs/31 → color del nombre (fórmula PokeOne)
    rbc   = rb_class(pct)
    rbl   = rb_label(rbc)
    rar   = rarity_css(pct_global)

    # card header color — toma el color del primer tipo
    types       = sd.get("Types", [])
    accent      = types[0]["color"] if types else "#8b949e"
    bg_r, bg_g, bg_b = int(accent[1:3],16), int(accent[3:5],16), int(accent[5:7],16)
    header_bg   = f"linear-gradient(135deg, rgba({bg_r},{bg_g},{bg_b},0.15), #161b22)"

    type_badges = "".join(
        f'<span class="type-badge" style="background:{t["color"]}22;color:{t["color"]};border:1px solid {t["color"]}44">'
        f'{t["name"]}</span>'
        for t in types
    )

    display_name = f'{"★ " if shiny else ""}{name}{f" ({nick})" if nick else ""}'

    # stat rows — IVs irrelevantes para el rol se atenúan
    rel_keys = ROLE_IV_KEYS.get(rol_key)
    iv_row   = stat_row("IV", iv_vals, iv_css, relevant_keys=rel_keys)
    ev_row   = stat_row("EV", ev_vals, ev_css)

    # moveset actual
    move_items = ""
    for i, m in enumerate(moves, 1):
        if m is None:
            continue
        move_items += (
            f'<li>'
            f'<div class="move-num">{i}</div>'
            f'<span class="move-name">{m["Name"]}</span>'
            f'<span class="move-desc">{move_name_es(m["Name"])}</span>'
            f'</li>'
        )

    # moveset objetivo desde movesets.json
    obj_moves = MOVESETS.get(key)
    if obj_moves:
        obj_items = "".join(
            f'<li>'
            f'<div class="move-num">{i}</div>'
            f'<span class="move-name">{m["name"]}</span>'
            f'<span class="move-desc">{m["desc"]}</span>'
            f'</li>'
            for i, m in enumerate(obj_moves, 1)
        )
        obj_panel = f'<ul class="moves-list">{obj_items}</ul>'
    else:
        obj_panel = '<div class="alert alert-info" style="margin-top:6px">Sin moveset objetivo definido — añádelo en movesets.json.</div>'

    mdata = modal_data(slot)
    return f"""
    <!-- {name} -->
    <div class="card">
      <div class="card-header" style="background:{header_bg};border-bottom:2px solid {accent}">
        <img class="pokemon-icon" src="{icon}" alt="{sd['Name']}">
        <div class="header-info">
          <h2 class="{rar}">{display_name}</h2>
          <div class="meta">Lv.{level} &bull; {nature} &bull; {ability}</div>
          <div class="types">
            {type_badges}
            <span class="combat-role {rol_css}" title="{rol_key}">{rol_icon} {rol_text}</span>
          </div>
        </div>
        <div class="role-badge {rbc}" onclick="openRbModal(this)" data-modal='{mdata}'>
          <span class="rb-score">{pct}%</span>
          <span class="rb-label">{rbl}</span>
        </div>
      </div>
      <div class="card-body">
        <div class="stitle">IVs / EVs</div>
        <div class="stat-rows">
          {iv_row}
          {ev_row}
        </div>
        <div class="moveset-tabs">
          <div class="mv-tab-bar">
            <button class="mv-tab-btn active" onclick="mvTab(this,'mv-{key}-actual')">Actual</button>
            <button class="mv-tab-btn" onclick="mvTab(this,'mv-{key}-obj')">Objetivo</button>
          </div>
          <div id="mv-{key}-actual" class="mv-panel active">
            <ul class="moves-list">{move_items}</ul>
          </div>
          <div id="mv-{key}-obj" class="mv-panel">
            {obj_panel}
          </div>
        </div>
      </div>
    </div>"""

# ── box Pokémon builders ──────────────────────────────────────────────────────

def build_box_grid_slot(slot: dict, box_num: int) -> str:
    """Slot compacto para la vista grid (sprite + badge %)."""
    pk      = slot["Pokemon"]
    payload = pk["Payload"]
    sd      = pk["StaticData"]
    ivs     = payload["IVs"]
    nature  = payload["NatureName"]
    evs     = payload["EVs"]
    pid     = payload["PokemonID"]
    level   = payload["Level"]
    pos     = slot.get("Position", 0)

    rol_key    = infer_role(pid, nature, evs)
    _, rol_text, rol_css = ROLE_META[rol_key]
    pct        = iv_pct(ivs, rol_key)
    pct_global = rarity_pct(ivs)
    rbc        = rb_class(pct)
    rar        = rarity_css(pct_global)
    icon       = sprite_url(sd["Icon"])
    name       = sd["Name"]
    uid        = f"box{box_num}p{pos}"

    return (
        f'<div class="box-grid-slot {rbc}" title="{name} Lv.{level} • {nature} • {pct}% ({rol_text})">'
        f'<img class="bgs-spr" src="{icon}" alt="{name}">'
        f'<span class="bgs-name {rar}">{name}</span>'
        f'<span class="bgs-pct">{pct}%</span>'
        f'<span class="combat-role {rol_css} bgs-role">{rol_text}</span>'
        f'</div>'
    )

def build_box_list_row(slot: dict, box_num: int) -> str:
    """Fila expandida para la vista lista con IVs coloreados por rol."""
    pk      = slot["Pokemon"]
    payload = pk["Payload"]
    sd      = pk["StaticData"]
    ivs     = payload["IVs"]
    nature  = payload["NatureName"]
    ability = pk.get("Ability") or "—"
    evs     = payload["EVs"]
    pid     = payload["PokemonID"]
    level   = payload["Level"]
    pos     = slot.get("Position", 0)
    nick    = payload.get("Nickname") or ""
    shiny   = payload.get("Shiny", False)

    rol_key    = infer_role(pid, nature, evs)
    _, rol_text, rol_css = ROLE_META[rol_key]
    rel_keys   = ROLE_IV_KEYS.get(rol_key)
    pct        = iv_pct(ivs, rol_key)
    pct_global = rarity_pct(ivs)
    rbc        = rb_class(pct)
    rar        = rarity_css(pct_global)
    icon       = sprite_url(sd["Icon"])
    name       = sd["Name"]
    display    = f'{"★ " if shiny else ""}{name}{f" ({nick})" if nick else ""}'

    # celdas IV
    iv_cells = ""
    for json_key, lbl in zip(IV_ORDER, IV_LABELS):
        v   = ivs.get(json_key, 0)
        css = iv_css(v)
        dim = " iv-dim" if rel_keys and json_key not in rel_keys else ""
        iv_cells += (
            f'<div class="sr-cell{dim}">'
            f'<span class="sr-s">{lbl}</span>'
            f'<span class="sr-v {css}">{v}</span>'
            f'</div>'
        )

    types = sd.get("Types", [])
    type_badges = "".join(
        f'<span class="type-badge" style="background:{t["color"]}22;color:{t["color"]};'
        f'border:1px solid {t["color"]}44">{t["name"]}</span>'
        for t in types
    )

    mdata = modal_data(slot)
    return (
        f'<div class="box-list-row">'
        f'<span class="bls-box">C{box_num}</span>'
        f'<img class="bls-spr" src="{icon}" alt="{name}">'
        f'<div class="bls-info">'
        f'<span class="bls-name {rar}">{display}</span>'
        f'<div class="bls-meta">Lv.{level} &bull; {nature} &bull; {ability}</div>'
        f'<div class="bls-types">{type_badges}'
        f'<span class="combat-role {rol_css}">{rol_text}</span></div>'
        f'</div>'
        f'<div class="bls-ivs sr-cells">{iv_cells}</div>'
        f'<div class="role-badge {rbc}" onclick="openRbModal(this)" data-modal=\'{mdata}\' style="cursor:pointer">'
        f'<span class="rb-score">{pct}%</span>'
        f'<span class="rb-label">{rb_label(rbc)}</span>'
        f'</div>'
        f'</div>'
    )

def _slot_pct(slot: dict) -> int:
    """Devuelve el % de IVs por rol de un slot, para ordenación."""
    pk = slot["Pokemon"]
    p  = pk["Payload"]
    return iv_pct(p["IVs"], infer_role(p["PokemonID"], p["NatureName"], p["EVs"]))

def build_boxes_html(raw_boxes: list) -> str:
    """Genera el HTML completo de la sección de cajas (grid + lista)."""
    non_empty = [(i, b) for i, b in enumerate(raw_boxes) if b and i > 0]

    # ── vista grid: agrupada por caja ──────────────────────────────────────────
    grid_boxes = ""
    for box_num, box in non_empty:
        grid_slots = "".join(build_box_grid_slot(s, box_num) for s in box if s)
        label = f"Caja {box_num}"
        grid_boxes += (
            f'<div class="box-block">'
            f'<div class="box-label">{label} <span class="box-count">{len(box)}</span></div>'
            f'<div class="box-grid-row">{grid_slots}</div>'
            f'</div>'
        )

    # ── vista lista: plana, ordenada de mayor a menor % ────────────────────────
    all_slots = [
        (box_num, s)
        for box_num, box in non_empty
        for s in box if s
    ]
    all_slots.sort(key=lambda x: _slot_pct(x[1]), reverse=True)
    list_rows = "".join(build_box_list_row(s, box_num) for box_num, s in all_slots)

    return f"""
<div id="view-grid" class="box-view active">
  <div class="box-section-grid">{grid_boxes}</div>
</div>
<div id="view-list" class="box-view">
  <div class="box-section-list">{list_rows}</div>
</div>
"""

# ── page builder ──────────────────────────────────────────────────────────────

CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: #0d1117; color: #e6edf3; font-family: 'Segoe UI', sans-serif; padding: 20px; }

.site-header { padding: 24px 28px; background: linear-gradient(135deg, #161b22, #0d1117);
  border-bottom: 2px solid #f3d327; margin-bottom: 30px; border-radius: 12px; }
.trainer-name { font-size: 1.8em; font-weight: 700; color: #f3d327; letter-spacing: 2px; }
.trainer-sub  { font-size: 0.8em; color: #8b949e; margin-top: 5px; letter-spacing: 1px; text-transform: uppercase; }

.section { max-width: 1300px; margin: 0 auto 40px; }
.section-header { display: flex; align-items: center; gap: 12px; margin-bottom: 20px; }
.section-header h2 { font-size: 1.3em; color: #f3d327; }
.section-header .badge { background: #f3d327; color: #000; border-radius: 12px;
  padding: 2px 10px; font-size: 0.75em; font-weight: 700; }
.divider { flex: 1; height: 1px; background: #21262d; }

.team-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(340px, 1fr)); gap: 18px; }

.card { background: #161b22; border-radius: 12px; overflow: hidden; border: 1px solid #30363d; }
.card-header { padding: 14px 18px 10px; display: flex; align-items: center; gap: 12px; }
.pokemon-icon { width: 52px; height: 52px; object-fit: contain; image-rendering: pixelated;
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.6)); }
.header-info h2 { font-size: 1.15em; font-weight: 700; letter-spacing: 1px; }
.header-info .meta { font-size: 0.75em; color: #8b949e; margin-top: 2px; }
.types { display: flex; gap: 4px; margin-top: 4px; }
.type-badge { padding: 1px 7px; border-radius: 8px; font-size: 0.65em; font-weight: 700; text-transform: uppercase; }
.card-body { padding: 0 18px 18px; }

.stitle { font-size: 0.68em; text-transform: uppercase; letter-spacing: 1px; color: #8b949e;
  margin: 12px 0 6px; border-bottom: 1px solid #21262d; padding-bottom: 3px; }

.stat-rows { display: flex; flex-direction: column; gap: 3px; }
.stat-row-line { display: flex; align-items: center; gap: 5px; }
.sr-lbl { font-size: 0.58em; font-weight: 700; color: #484f58; text-transform: uppercase;
  width: 16px; flex-shrink: 0; text-align: right; }
.sr-cells { display: flex; gap: 3px; flex: 1; }
.sr-cell { flex: 1; background: #0d1117; border-radius: 5px; padding: 3px 2px; text-align: center; min-width: 0; }
.sr-s { font-size: 0.52em; color: #8b949e; text-transform: uppercase; display: block; letter-spacing: 0.3px; }
.sr-v { font-size: 0.88em; font-weight: 700; display: block; }
.iv-high { color: #3fb950; }
.iv-mid  { color: #d29922; }
.iv-low  { color: #f85149; }
.ev-zero { color: #30363d; }
.ev-set  { color: #f3d327; }
.sr-cell.iv-dim { opacity: 0.3; }

.rarity-purple { color: #bf88ff; }
.rarity-blue   { color: #58a6ff; }
.rarity-green  { color: #3fb950; }
.rarity-white  { color: #e6edf3; }
.rarity-grey   { color: #8b949e; }

.combat-role { padding: 1px 7px; border-radius: 8px; font-size: 0.65em; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.3px; white-space: nowrap; }
.role-special  { background: #1a002d; color: #bf88ff; border: 1px solid #bf88ff44; }
.role-physical { background: #2d0a00; color: #ff7043; border: 1px solid #ff704344; }
.role-mixed    { background: #1a1500; color: #d29922; border: 1px solid #d2992244; }
.role-wall-p   { background: #001a2d; color: #58a6ff; border: 1px solid #58a6ff44; }
.role-wall-s   { background: #001d10; color: #3fb950; border: 1px solid #3fb95044; }
.role-tank     { background: #1a1a2d; color: #8b949e; border: 1px solid #8b949e44; }
.role-support  { background: #2d1a00; color: #f3d327; border: 1px solid #f3d32744; }

/* ── Team analysis panel ── */
.team-analysis { background: #161b22; border: 1px solid #30363d; border-radius: 12px;
  padding: 20px; margin-bottom: 24px; }
.ta-summary { display: flex; align-items: center; gap: 24px; }
.ta-detail { margin-top: 0; }
.ta-score-wrap { text-align: center; flex-shrink: 0; min-width: 64px; }
.ta-score { font-size: 2.8em; font-weight: 900; line-height: 1; }
.ta-score-label { font-size: 0.7em; font-weight: 700; text-transform: uppercase;
  letter-spacing: 1px; margin-top: 2px; }
.ta-score-sub { font-size: 0.65em; color: #484f58; }
.ta-overview { flex: 1; display: flex; flex-direction: column; gap: 8px; padding-top: 4px; }
.ta-row { display: flex; align-items: center; gap: 10px; font-size: 0.78em; }
.ta-label { color: #8b949e; min-width: 80px; flex-shrink: 0; }
.ta-bar-wrap { flex: 1; height: 6px; background: #21262d; border-radius: 3px; overflow: hidden; max-width: 200px; }
.ta-bar { height: 100%; border-radius: 3px; transition: width 0.3s; }
.ta-bar-val { font-weight: 700; min-width: 36px; }
.ta-pills { display: flex; flex-wrap: wrap; gap: 5px; }
.ta-pill { background: #21262d; border-radius: 20px; padding: 2px 10px;
  font-size: 0.72em; color: #8b949e; }
.ta-pill b { color: #e6edf3; }
.ta-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; }
.ta-block { background: #0d1117; border-radius: 8px; padding: 12px 14px; }
.ta-block-full { grid-column: 1 / -1; }
.ta-block-title { font-size: 0.65em; text-transform: uppercase; letter-spacing: 1px;
  color: #484f58; margin-bottom: 8px; font-weight: 700; }
.ta-types { display: flex; flex-wrap: wrap; gap: 5px; }
.ta-type-ok  { padding: 2px 8px; border-radius: 6px; font-size: 0.68em; font-weight: 700;
  background: #001d0e; color: #3fb950; border: 1px solid #3fb95033; }
.ta-type-gap { padding: 2px 8px; border-radius: 6px; font-size: 0.68em; font-weight: 700;
  background: #2d1117; color: #f85149; border: 1px solid #f8514933; }
.ta-weak { padding: 2px 8px; border-radius: 6px; font-size: 0.68em; font-weight: 700;
  background: #2d2200; color: #d29922; border: 1px solid #d2992233; }
.ta-list { list-style: none; display: flex; flex-direction: column; gap: 5px; }
.ta-list li { font-size: 0.78em; color: #c9d1d9; line-height: 1.5;
  padding-left: 10px; border-left: 2px solid #30363d; }
.ta-list li b { color: #f3d327; }
.ta-none { color: #484f58 !important; font-style: italic; border-left-color: #21262d !important; }

.role-badge { margin-left: auto; flex-shrink: 0; border-radius: 8px; padding: 4px 8px;
  cursor: pointer; text-align: center; transition: filter 0.15s; min-width: 52px; }
.role-badge:hover { filter: brightness(1.25); }
.rb-score { font-size: 1em; font-weight: 700; display: block; }
.rb-label { font-size: 0.62em; text-transform: uppercase; letter-spacing: 0.5px; display: block; }
.rb-green  { background: #001d0e; color: #3fb950; border: 1px solid #3fb95066; }
.rb-blue   { background: #001d2d; color: #58a6ff; border: 1px solid #58a6ff66; }
.rb-amber  { background: #2d2200; color: #d29922; border: 1px solid #d2992266; }
.rb-red    { background: #2d1117; color: #f85149; border: 1px solid #f8514966; }

.moveset-tabs { margin-top: 12px; }
.mv-tab-bar { display: flex; border-bottom: 1px solid #21262d; margin-bottom: 0; }
.mv-tab-btn { padding: 5px 12px; font-size: 0.67em; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.8px; color: #484f58; cursor: pointer; border-bottom: 2px solid transparent;
  margin-bottom: -1px; transition: color 0.15s; background: none;
  border-top: none; border-left: none; border-right: none; }
.mv-tab-btn:hover { color: #8b949e; }
.mv-tab-btn.active { color: #f3d327; border-bottom-color: #f3d327; }
.mv-panel { display: none; padding-top: 6px; }
.mv-panel.active { display: block; }

.moves-list { list-style: none; }
.moves-list li { display: flex; align-items: center; gap: 8px; padding: 4px 0;
  border-bottom: 1px solid #21262d; font-size: 0.82em; }
.moves-list li:last-child { border-bottom: none; }
.move-num { width: 18px; height: 18px; border-radius: 50%; background: #21262d;
  display: flex; align-items: center; justify-content: center; font-size: 0.65em;
  font-weight: 700; flex-shrink: 0; }
.move-name { font-weight: 600; min-width: 130px; }
.move-desc { color: #8b949e; font-size: 0.85em; flex: 1; }

.alert { border-radius: 6px; padding: 7px 10px; font-size: 0.78em; margin-top: 8px; line-height: 1.5; }
.alert-info    { background: #001d2d; border-left: 3px solid #388bfd; color: #79c0ff; }

/* ── Tabs de sección (Equipo / Cajas) ── */
.section-tabs { display: flex; gap: 0; border-bottom: 2px solid #21262d;
  margin-bottom: 24px; max-width: 1300px; margin-left: auto; margin-right: auto; }
.section-tab-btn { padding: 10px 22px; font-size: 0.9em; font-weight: 700;
  letter-spacing: 0.5px; color: #484f58; cursor: pointer; background: none;
  border: none; border-bottom: 3px solid transparent; margin-bottom: -2px;
  transition: color 0.15s; }
.section-tab-btn:hover { color: #8b949e; }
.section-tab-btn.active { color: #f3d327; border-bottom-color: #f3d327; }
.section-panel { display: none; max-width: 1300px; margin: 0 auto 40px; }
.section-panel.active { display: block; }

/* ── Controles vista Cajas ── */
.box-controls { display: flex; align-items: center; gap: 10px; margin-bottom: 18px; }
.view-btn { padding: 6px 14px; font-size: 0.78em; font-weight: 700; border-radius: 20px;
  cursor: pointer; border: 1px solid #30363d; background: #161b22; color: #8b949e;
  transition: all 0.15s; }
.view-btn:hover { border-color: #f3d327; color: #f3d327; }
.view-btn.active { background: #f3d327; color: #000; border-color: #f3d327; }
.box-view { display: none; }
.box-view.active { display: block; }
.box-count-badge { background: #f3d327; color: #000; border-radius: 12px;
  padding: 2px 10px; font-size: 0.75em; font-weight: 700; margin-left: auto; }

/* ── Caja: cabecera ── */
.box-block { margin-bottom: 20px; }
.box-label { font-size: 0.72em; font-weight: 700; color: #484f58; text-transform: uppercase;
  letter-spacing: 1px; padding: 6px 2px; border-bottom: 1px solid #21262d;
  margin-bottom: 8px; display: flex; align-items: center; gap: 8px; }
.box-count { background: #21262d; border-radius: 8px; padding: 1px 7px;
  font-size: 0.9em; color: #8b949e; }

/* ── Vista Grid ── */
.box-grid-row { display: flex; flex-wrap: wrap; gap: 6px; }
.box-grid-slot { display: flex; flex-direction: column; align-items: center;
  width: 80px; padding: 6px 4px; border-radius: 8px; border: 1px solid #21262d;
  background: #161b22; cursor: default; transition: border-color 0.15s; gap: 2px; }
.box-grid-slot:hover { border-color: #484f58; }
.box-grid-slot.rb-green { border-color: #3fb95033; }
.box-grid-slot.rb-blue  { border-color: #58a6ff33; }
.box-grid-slot.rb-amber { border-color: #d2992233; }
.box-grid-slot.rb-red   { border-color: #f8514933; }
.bgs-spr  { width: 40px; height: 40px; image-rendering: pixelated; }
.bgs-name { font-size: 0.55em; font-weight: 700; text-align: center;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 76px; }
.bgs-pct  { font-size: 0.7em; font-weight: 700; color: #8b949e; }
.bgs-role { font-size: 0.52em !important; padding: 1px 4px !important; }

/* ── Vista Lista ── */
.box-list-row { display: flex; align-items: center; gap: 10px; padding: 6px 10px;
  border-bottom: 1px solid #21262d; border-radius: 6px; }
.box-list-row:last-child { border-bottom: none; }
.box-list-row:hover { background: #161b22; }
.bls-box  { font-size: 0.62em; font-weight: 700; color: #484f58; min-width: 24px;
  text-align: center; flex-shrink: 0; }

/* TOP tab */
.top-rank { font-size: 0.7em; font-weight: 700; color: #484f58; min-width: 22px;
  text-align: center; flex-shrink: 0; }
.rank-gold   { color: #ffd700; }
.rank-silver { color: #c0c0c0; }
.rank-bronze { color: #cd7f32; }
.top-loc { font-size: 0.6em; font-weight: 700; border-radius: 5px;
  padding: 1px 6px; flex-shrink: 0; white-space: nowrap; }
.top-loc-team { background: #001d2d; color: #58a6ff; border: 1px solid #58a6ff44; }
.top-loc-box  { background: #21262d; color: #8b949e; border: 1px solid #30363d; }
.top-rol { flex-shrink: 0; font-size: 0.62em !important; }
.bls-spr  { width: 36px; height: 36px; image-rendering: pixelated; flex-shrink: 0; }
.bls-info { min-width: 160px; flex-shrink: 0; }
.bls-name { font-size: 0.88em; font-weight: 700; display: block; }
.bls-meta { font-size: 0.68em; color: #8b949e; margin-top: 1px; }
.bls-types { display: flex; gap: 3px; margin-top: 3px; flex-wrap: wrap; }
.bls-ivs  { flex: 1; display: flex; gap: 3px; }
.bls-ivs .sr-cell { flex: 1; background: #0d1117; border-radius: 5px;
  padding: 3px 2px; text-align: center; min-width: 0; }
.box-section-list { background: #161b22; border-radius: 10px;
  border: 1px solid #30363d; padding: 0 10px; }

/* Modal */
#rb-modal-overlay { display:none; position:fixed; inset:0; background:rgba(0,0,0,0.75);
  z-index:1000; align-items:center; justify-content:center; }
#rb-modal-overlay.open { display:flex; }
#rb-modal-box { background:#161b22; border:1px solid #30363d; border-radius:12px;
  padding:24px; max-width:480px; width:90%; max-height:85vh; overflow-y:auto;
  position:relative; }
#rb-modal-close { position:absolute; top:12px; right:14px; background:none; border:none;
  color:#8b949e; font-size:1.2em; cursor:pointer; }
#rb-modal-close:hover { color:#e6edf3; }
#rb-modal-content h3 { color:#f3d327; margin-bottom:8px; }
.rb-modal-bar { height:8px; border-radius:4px; margin:8px 0 12px;
  background:linear-gradient(90deg,#f85149,#d29922,#3fb950); position:relative; }
.rb-modal-marker { position:absolute; top:-3px; width:14px; height:14px;
  background:#fff; border-radius:50%; transform:translateX(-50%); box-shadow:0 0 6px #000; }
.rb-modal-ivs { display:grid; grid-template-columns:repeat(6,1fr); gap:4px; margin:8px 0; }
.rb-iv-cell { background:#0d1117; border-radius:5px; padding:4px 2px; text-align:center; }
.rb-iv-s { font-size:0.55em; color:#8b949e; text-transform:uppercase; display:block; }
.rb-iv-v { font-size:0.95em; font-weight:700; display:block; }
.modal-section { background:#0d1117; border-radius:8px; padding:10px 12px; }
.modal-section-title { font-size:0.62em; text-transform:uppercase; letter-spacing:1px;
  color:#484f58; font-weight:700; margin-bottom:5px; }
.modal-section-desc { font-size:0.78em; color:#c9d1d9; line-height:1.5; }
.modal-nature-name { font-size:0.9em; font-weight:700; color:#f3d327; }
.modal-nature-ideals { display:flex; flex-wrap:wrap; gap:5px; margin-top:5px; }
.modal-nature-ideal { background:#161b22; border:1px solid #30363d; border-radius:6px;
  padding:2px 8px; font-size:0.7em; color:#8b949e; }
"""

JS = """
function sectionTab(btn, panelId) {
  document.querySelectorAll('.section-tab-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.section-panel').forEach(p => p.classList.remove('active'));
  btn.classList.add('active');
  document.getElementById(panelId).classList.add('active');
}

function boxView(btn, viewId) {
  document.querySelectorAll('.view-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.box-view').forEach(v => v.classList.remove('active'));
  btn.classList.add('active');
  document.getElementById(viewId).classList.add('active');
}

function mvTab(btn, panelId) {
  const tabs = btn.closest('.moveset-tabs');
  tabs.querySelectorAll('.mv-tab-btn').forEach(b => b.classList.remove('active'));
  tabs.querySelectorAll('.mv-panel').forEach(p => p.classList.remove('active'));
  btn.classList.add('active');
  document.getElementById(panelId).classList.add('active');
}

function openRbModal(el) {
  const raw = el.getAttribute('data-modal');
  if (!raw) return;
  const d = JSON.parse(raw);

  const colorMap = {
    'rb-green':'#3fb950','rb-blue':'#58a6ff','rb-amber':'#d29922','rb-red':'#f85149'
  };
  const color = colorMap[d.rbc] || '#8b949e';

  // grid de IVs
  let ivGrid = '';
  d.ivs.forEach(iv => {
    const dimStyle = iv.dim ? 'opacity:0.3;' : '';
    const vClass = iv.v >= 25 ? 'iv-high' : iv.v >= 15 ? 'iv-mid' : 'iv-low';
    ivGrid += `<div class="rb-iv-cell" style="${dimStyle}">` +
              `<span class="rb-iv-s">${iv.s}</span>` +
              `<span class="rb-iv-v ${vClass}">${iv.v}</span></div>`;
  });

  // naturalezas ideales
  const ideals = d.ideal_natures.map(n =>
    `<span class="modal-nature-ideal">${n}</span>`
  ).join('');

  // check si la naturaleza actual es óptima
  const isIdeal = d.ideal_natures.some(n => n.startsWith(d.nature));
  const natureStatus = isIdeal
    ? `<span style="color:#3fb950;font-size:0.72em">✓ Óptima para ${d.rol_text}</span>`
    : `<span style="color:#d29922;font-size:0.72em">⚠ No ideal para ${d.rol_text}</span>`;

  document.getElementById('rb-modal-content').innerHTML = `
    <h3>${d.name}</h3>
    <div style="font-size:0.78em;color:#8b949e;margin-bottom:12px">Lv.${d.level}</div>

    <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px">
      <span class="role-badge ${d.rbc}" style="cursor:default">
        <span class="rb-score">${d.pct}%</span>
        <span class="rb-label">${d.rbc.replace('rb-','').replace('green','Bueno').replace('blue','Viable').replace('amber','Regular').replace('red','Malo')}</span>
      </span>
      <span style="font-size:0.78em;color:#8b949e">IVs relevantes al rol</span>
    </div>
    <div class="rb-modal-bar" style="margin-bottom:14px">
      <div class="rb-modal-marker" style="left:${d.pct}%;background:${color}"></div>
    </div>
    <div class="rb-modal-ivs" style="margin-bottom:16px">${ivGrid}</div>

    <div class="modal-section">
      <div class="modal-section-title">Naturaleza</div>
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">
        <span class="modal-nature-name">${d.nature}</span>
        ${natureStatus}
      </div>
      <div class="modal-section-desc">${d.nature_desc}</div>
      <div class="modal-section-title" style="margin-top:8px">Naturalezas ideales para ${d.rol_text}</div>
      <div class="modal-nature-ideals">${ideals || '<span style="color:#484f58">No definidas</span>'}</div>
    </div>

    <div class="modal-section" style="margin-top:12px">
      <div class="modal-section-title">Habilidad — ${d.ability}</div>
      <div class="modal-section-desc">${d.ability_desc || '<span style="color:#484f58">Sin descripción registrada</span>'}</div>
    </div>
  `;
  document.getElementById('rb-modal-overlay').classList.add('open');
}

document.addEventListener('DOMContentLoaded', () => {
  const overlay = document.getElementById('rb-modal-overlay');
  overlay.addEventListener('click', e => {
    if (e.target === overlay) overlay.classList.remove('open');
  });
  document.getElementById('rb-modal-close').addEventListener('click', () => {
    overlay.classList.remove('open');
  });
});
"""

MODAL_HTML = """
<div id="rb-modal-overlay">
  <div id="rb-modal-box">
    <button id="rb-modal-close">&times;</button>
    <div id="rb-modal-content"></div>
  </div>
</div>
"""

def build_page(team_name: str, slots: list, trainer: str, raw_boxes: list) -> str:
    count                    = len(slots)
    cards                    = "\n".join(build_card(s) for s in slots)
    analysis_summary, analysis_detail = build_team_analysis(slots)
    boxes_html               = build_boxes_html(raw_boxes)
    top_html                 = build_top_html(slots, raw_boxes)
    box_total  = sum(len(b) for i, b in enumerate(raw_boxes) if b and i > 0)
    box_count  = sum(1 for i, b in enumerate(raw_boxes) if b and i > 0)

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PokeOne — {team_name}</title>
<style>
{CSS}
</style>
</head>
<body>

<div class="site-header">
  <div class="trainer-name">{team_name}</div>
  <div class="trainer-sub">PokeOne &bull; Entrenador: {trainer} &bull; {count} en equipo &bull; {box_total} en cajas</div>
</div>

<div class="section-tabs">
  <button class="section-tab-btn active" onclick="sectionTab(this,'panel-equipo')">&#9876; Equipo activo</button>
  <button class="section-tab-btn" onclick="sectionTab(this,'panel-cajas')">&#128230; Cajas PC</button>
  <button class="section-tab-btn" onclick="sectionTab(this,'panel-top')">&#11088; TOP 30</button>
</div>

<div id="panel-equipo" class="section-panel active">
  {analysis_summary}
  <div class="team-grid">
{cards}
  </div>
  {analysis_detail}
</div>

<div id="panel-cajas" class="section-panel">
  <div class="box-controls">
    <button class="view-btn active" onclick="boxView(this,'view-grid')">&#9632; Grid</button>
    <button class="view-btn" onclick="boxView(this,'view-list')">&#9776; Lista</button>
    <span class="box-count-badge">{box_total} Pokémon &bull; {box_count} cajas</span>
  </div>
  {boxes_html}
</div>

<div id="panel-top" class="section-panel">
  {top_html}
</div>

{MODAL_HTML}

<script>
{JS}
</script>
</body>
</html>"""

# ── main ──────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Uso: python generate_team.py <ruta_al_json>")
        sys.exit(1)

    json_path = Path(sys.argv[1])
    if not json_path.exists():
        print(f"ERROR: no se encuentra el archivo {json_path}")
        sys.exit(1)

    raw = json_path.read_bytes().lstrip(b'\xe2\x80\x8b')
    data = json.loads(raw)

    trainer    = data["data"]["user_info"].get("userName", "unknown")
    raw_pokemon = data["data"]["pokemon"]
    team_slots  = [s for s in raw_pokemon[0] if s is not None]
    box_total   = sum(len(b) for i, b in enumerate(raw_pokemon) if b and i > 0)

    if not team_slots:
        print("ERROR: el equipo activo está vacío en el JSON.")
        sys.exit(1)

    print(f"\nJSON cargado: {len(team_slots)} Pokémon en equipo activo, {box_total} en cajas (entrenador: {trainer})")
    team_name = input("Nombre del equipo (ej: jsolerca, dani): ").strip()
    if not team_name:
        print("ERROR: el nombre no puede estar vacío.")
        sys.exit(1)

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    out_path = output_dir / f"{team_name}.html"

    action = "sobreescrito" if out_path.exists() else "creado"
    html = build_page(team_name, team_slots, trainer, raw_pokemon)
    out_path.write_text(html, encoding="utf-8")

    print(f"OK: {out_path} {action} — {len(team_slots)} equipo + {box_total} cajas.")

if __name__ == "__main__":
    main()
