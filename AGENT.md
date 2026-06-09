# AGENT.md — Instrucciones para actualizar el dashboard desde JSON

Este documento explica cómo actualizar `pokeone_equipo.html` (o `dani_equipo.html`) usando un archivo JSON de la API de PokeOne.

---

## Cómo invocar al agente

Di algo como:
> "Actualiza `pokeone_equipo.html` con los datos de `input/input_jsolerca_20260609.json`"

El agente leerá ambos archivos y aplicará los cambios siguiendo las reglas de este documento.

---

## Estructura del JSON

```
data.user_info          → datos del entrenador
data.pokemon[0]         → Box 0 = equipo activo (6 Pokémon, Position 1–6)
data.pokemon[1..N]      → Box 1, 2, 3... = cajas de almacenamiento
```

Cada entrada de Pokémon tiene esta forma:
```json
{
  "Position": 1,
  "Box": 0,
  "Pokemon": {
    "StaticData": { "Name": "Arcanine", "Icon": "arcanine.png", "Types": [...] },
    "Ability": "Flash Fire",
    "Payload": {
      "Level": 32,
      "NatureName": "Modest",
      "IVs": { "HP": 22, "Atk": 13, "Def": 3, "SpAtk": 27, "SpDef": 14, "Speed": 14 },
      "EVs": { "HP": 0, "Atk": 0, "Def": 0, "SpAtk": 0, "SpDef": 0, "Speed": 0 },
      "Moves": [
        { "Name": "Leer" }, { "Name": "Odor Sleuth" }, { "Name": "Helping Hand" }, { "Name": "Flame Wheel" }
      ]
    }
  }
}
```

---

## Qué actualizar automáticamente (datos objetivos del JSON)

Estos campos se leen directamente del JSON sin interpretación. Actualízalos siempre que difieran:

### Header del sitio

| Campo HTML | Fuente JSON |
|---|---|
| `Trainer Lv <span>` | `user_info.kantoTrainerLevel` |
| `Badges <span>X/8` | `user_info.badges.length` + `/8` |
| `Pokedex <span>X` capturados | `user_info.pokedexCaught` |
| `PokeDollar <span>` | `user_info.pokeDollar` (formato `69,180`) |
| `PVP <span>XW / YL` | `user_info.pvpWins` + `W / ` + `user_info.pvpLosses` + `L` |
| Fecha en `Ultima actualizacion:` | Fecha del archivo JSON (del nombre o `CaughtDateUtc` más reciente) |

### Cards del equipo activo (Box 0)

Para cada Pokémon en `data.pokemon[0]` (Position 1–6):

**Encabezado de la card:**
- Nivel: `Payload.Level`
- Nature: `Payload.NatureName`
- Ability: `Pokemon.Ability`

**Fila de IVs** — valores `Payload.IVs.{HP,Atk,Def,SpAtk,SpDef,Speed}`:
- `iv-high` (verde): IV ≥ 25
- `iv-mid` (naranja): IV 15–24
- `iv-low` (rojo): IV ≤ 14

**Fila de EVs** — valores `Payload.EVs.{HP,Atk,Def,SpAtk,SpDef,Speed}`:
- `ev-set` (amarillo): EV > 0
- `ev-zero` (gris, muestra `0`): EV = 0

**Moveset actual** — `Payload.Moves[0..3].Name` en orden. Actualiza solo los nombres de los 4 movimientos. Conserva los textos descriptivos y etiquetas existentes; si un movimiento cambió, actualiza también su descripción brevemente.

**Progreso de farmeo** — Si los EVs actuales (`Payload.EVs`) ya superaron algún objetivo de la sección Farmeo, actualiza el contador restante. Si un stat está completo (EV actual = OBJ), marca como `✓` con `style="color:#3fb950"`.

### Sección Farmeo (cuentas pendientes)

Para cada Pokémon cuya fila de farmeo muestre "X batallas", calcula el restante:
- Si `OBJ = 252` y `EV_actual = 53` → mostrar `"199 más (53 hechos)"` 
- Si `EV_actual >= OBJ` → mostrar `"✓ completado"` en verde

---

## Qué NO actualizar automáticamente (requiere criterio)

Estos campos los mantiene el dueño del dashboard o requieren análisis:

- **Valoraciones (role badge, score X/10, label)** — No cambies salvo que el dueño lo indique explícitamente. La valoración refleja opinión sobre el potencial, no solo stats.
- **Moveset objetivo** — No cambiar. Es el plan a futuro, no el estado actual.
- **Milestones** — Si un hito ya fue alcanzado (nivel actual ≥ nivel del hito), marca el `milestone-lv` con `✓` delante. No elimines ni muevas los hitos.
- **Alerts** — No modificar a menos que el dueño lo pida.
- **Modal `RB_DATA`** — No cambiar el contenido de los modales de valoración.
- **Secciones Capturas, Top Cajas, A borrar** — Son curadas manualmente. No tocar salvo instrucción explícita.

---

## Reglas de clases CSS para IVs

| Valor IV | Clase CSS | Color |
|---|---|---|
| 25–31 | `iv-high` | verde `#3fb950` |
| 15–24 | `iv-mid` | naranja `#d29922` |
| 0–14 | `iv-low` | rojo `#f85149` |

---

## Orden de los Pokémon en el equipo

El orden en el HTML no siempre coincide con `Position` en el JSON. Respeta el orden visual actual del HTML (basado en valoración descendente, decidido por el dueño). No reordenes las cards salvo instrucción explícita.

---

## Proceso de actualización paso a paso

1. Lee el JSON de entrada.
2. Compara `data.pokemon[0]` con las cards del HTML, identificando cada card por el nombre del Pokémon en `StaticData.Name`.
3. Para cada card, actualiza los campos objetivos de la tabla anterior.
4. Actualiza el header del sitio.
5. Actualiza los contadores de farmeo pendiente.
6. Reporta un resumen de qué cambió y qué quedó sin tocar (valoraciones, objetivos, etc.).

---

## Ejemplo de actualización típica

Si el JSON muestra que Golem subió de Lv.42 a Lv.44:
- Actualiza `Lv.42 → Lv.44` en la meta del card.
- Comprueba si alcanzó algún milestone (Lv.44 = Explosion) y márcalo con `✓`.
- Si los EVs de Atk pasaron de 50 a 252, actualiza la fila EV y marca el farmeo como completado.

---

## Formato de nombre de archivo de entrada

`input/input_{jugador}_{YYYYMMDD}.json`

El jugador se mapea al dashboard así:
- `jsolerca` → `pokeone_equipo.html`
- `CarroCarrillo` → `dani_equipo.html`
