# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A personal web dashboard for tracking Pokémon team progress in the PokeOne online game. Two parallel dashboards exist for two players:
- `pokeone_equipo.html` — jsolerca's team
- `dani_equipo.html` — CarroCarrillo's team

## No Build System

There are no dependencies, no `package.json`, no bundler, and no build step. Open the HTML files directly in a browser. Changes take effect immediately on reload.

## Architecture

Each dashboard is a **single self-contained HTML file** with all CSS in a `<style>` block and all JavaScript in a `<script>` block at the bottom. There are no external files or imports.

### Page Sections (in order)
1. **Equipo activo** — 6 Pokémon cards in a responsive grid (`.team-grid` / `.card`)
2. **Farmeo** — EV training targets per Pokémon (which wild Pokémon to battle and where)
3. **Capturas recientes** — Recently caught Pokémon with IV ratings
4. **Top Boxes** — Best Pokémon in storage, ranked
5. **A borrar** — Pokémon queued for release

### Card Structure (each `.card`)
- Header: name, level, nature, ability, type badges, role badge
- Stats: IV/EV/Objetivo columns (color-coded cells)
- Moveset: current moves + target moves with acquisition method
- Milestones and alert boxes

### Role Badge System
Badges (`.role-badge`) show a 1–10 quality score with color tiers:
- `rb-green` = Bueno (7–10)
- `rb-blue` = Viable (5–6)
- `rb-amber` = Regular (3–4)
- `rb-red` = Malo (1–2)

Clicking a badge calls `openRbModal(pokemonName)`, which opens a modal overlay explaining the score breakdown. Modal HTML lives inside each card and is shown/hidden via JS.

### IV Color Coding
Stat cells use inline classes for rarity tiers: grey (worst) → white → green → blue → purple → gold (31 IVs).

### Alert Boxes
`.alert.danger / .warning / .info / .good` — contextual notes inside cards about risks, goals, or status.

## Typical Edits

All data is hardcoded HTML. Common tasks:
- **Update a stat**: find the relevant `<td>` or stat cell inside the correct card and change the value
- **Change a role score**: update the badge class (`rb-green`, etc.), the displayed number, and the modal content for that Pokémon
- **Add a move**: edit the `.moves-list` inside the card
- **Add a capture**: add a new entry in the Capturas section
- **Reorder team**: move entire `.card` blocks within `.team-grid`
