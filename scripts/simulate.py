#!/usr/bin/env python3
"""A rough playthrough simulator for a quest link: how hard is this quest for 2, 3 or 4 heroes?

It is a fights-only Monte Carlo, not a game engine. The heroes clear the rooms one after another in
a random order, with the dice rules of the base game. The program reports how often they survive,
how many body points (BP) they have left, and where the BP goes. There is no movement, line of
sight, doors, treasure or equipment, and special rules written in the quest text are not modeled
(only the stat blocks in Zargon's notes are read). Treat the numbers as a way to compare quests and
spot cliffs, not as a prediction. Nothing here touches the app or the link format.

    .venv/bin/python scripts/simulate.py docs/showcase/quest-1.txt
    .venv/bin/python scripts/simulate.py "https://.../#AdVX..." --runs 5000 --heroes 3,4

Python only, no third-party packages. It reads links with the decoder in tests/reference.py.
"""

from __future__ import annotations

import argparse
import copy
import json
import random
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tests"))
import reference as ref  # noqa: E402

# ---------------------------------------------------------------- the rules (base game)
# Combat dice: 3 of 6 faces are skulls, 2 are white shields (heroes block with these) and 1 is a
# black shield (monsters block with this).
SKULL, WHITE_SHIELD, BLACK_SHIELD = 1 / 2, 1 / 3, 1 / 6

# Body points, attack dice, defend dice, mind points (the monster chart of the base game).
HEROES = {
    "Barbarian": (8, 3, 2, 2),
    "Dwarf": (7, 2, 2, 3),
    "Elf": (6, 2, 2, 4),
    "Wizard": (4, 1, 2, 6),
}
MONSTERS = {
    "Goblin": (1, 2, 1, 1),
    "Skeleton": (1, 2, 2, 0),
    "Zombie": (1, 2, 3, 0),
    "Orc": (1, 3, 2, 2),
    "Abomination": (2, 3, 3, 3),
    "Mummy": (2, 3, 4, 0),
    "Dread Warrior": (3, 4, 4, 3),
    "Gargoyle": (3, 4, 5, 4),
}
TRAP_DAMAGE = {"Pit trap": 1, "Spear trap": 1, "Falling rock trap": 2}
CASTERS = {"Dread Warlock"}  # no chart row: their stats come from a stat block in the notes
PARTY_ORDER = ["Barbarian", "Dwarf", "Elf", "Wizard"]
HEAL_AMOUNT = 4  # a potion of healing, and the Wizard's Heal Body
MAX_ROUNDS = 60  # a fight that lasts longer is a stalemate and counts as a loss


@dataclass
class Hero:
    name: str
    bp: int
    max_bp: int
    attack: int
    defend: int

    @classmethod
    def named(cls, name: str) -> Hero:
        bp, attack, defend, _mind = HEROES[name]
        return cls(name, bp, bp, attack, defend)


@dataclass
class Monster:
    name: str
    bp: int
    attack: int
    defend: int
    caster: bool = False

    @classmethod
    def named(cls, kind: str) -> Monster:
        bp, attack, defend, _mind = MONSTERS[kind]
        return cls(kind, bp, attack, defend)


@dataclass
class Trap:
    kind: str
    damage: int


@dataclass
class Encounter:
    name: str
    monsters: list[Monster] = field(default_factory=list)
    traps: list[Trap] = field(default_factory=list)


@dataclass
class Quest:
    title: str
    encounters: list[Encounter]
    potions: int = 0


@dataclass
class Supplies:
    potions: int = 0
    heal_body: bool = False
    genie: bool = False


@dataclass
class Result:
    win_rate: float
    bp_left: float
    dead: float
    cost: dict[str, float]


@dataclass
class StatBlock:
    name: str
    bp: int
    mind: int
    attack: int
    defend: int


# ---------------------------------------------------------------- reading the notes and the link
def parse_stat_blocks(notes: str) -> list[StatBlock]:
    """Reads blocks like **Name** followed by a |BP|MP|Attack|Defense|Special| table."""
    lines = notes.split("\n")
    blocks = []
    for i, line in enumerate(lines):
        header = [c.strip().lower() for c in line.strip().strip("|").split("|")]
        if header[:4] != ["bp", "mp", "attack", "defense"] or not line.strip().startswith("|"):
            continue
        name = ""
        for back in range(i - 1, -1, -1):
            if lines[back].strip():
                name = lines[back].strip().strip("*").strip()
                break
        for row in lines[i + 1 : i + 4]:
            cells = [c.strip() for c in row.strip().strip("|").split("|")]
            if len(cells) >= 4 and all(c.isdigit() for c in cells[:4]):
                bp, mind, attack, defend = (int(c) for c in cells[:4])
                if name:
                    blocks.append(StatBlock(name, bp, mind, attack, defend))
                break
    return blocks


def load_link(text: str) -> dict:
    """The quest state from a link, a bare payload, or the path of a file that holds one."""
    path = Path(text)
    raw = path.read_text(encoding="utf-8") if path.is_file() else text
    payload = raw.strip().split("#")[-1].strip()
    if not re.fullmatch(r"[A-Za-z0-9_-]+", payload):
        raise ValueError("that is not a quest link (expected a link, its part after #, or a file)")
    try:
        return ref.decode(payload)
    except Exception as error:  # the reference decoder asserts on anything it cannot read
        raise ValueError(f"could not read this quest link ({type(error).__name__})") from error


def _board_rows() -> list[str]:
    lines = (ROOT / "src/board.txt").read_text(encoding="utf-8").splitlines()
    return [ln for ln in lines if ln and not ln.startswith("//")]


def _catalog() -> dict[int, dict]:
    return {p["id"]: p for p in json.loads((ROOT / "src/catalog.json").read_text(encoding="utf-8"))}


def build_quest(
    st: dict,
    *,
    notes_blocks: list[StatBlock] | None = None,
    wanderers: int = 1,
    corridor_group: int = 3,
    potions: int | None = None,
    boss_types: dict[str, str] | None = None,
) -> Quest:
    """Turns a decoded link into encounters: one per room, corridor monsters in small groups."""
    catalog, rows = _catalog(), _board_rows()
    blocks = parse_stat_blocks(st.get("notes", "")) if notes_blocks is None else notes_blocks
    pieces = [(catalog[i], x, y) for i, x, y, _r in st["items"] if i in catalog]
    monster_pieces = [p for p in pieces if p[0].get("monster")]
    stats = _boss_stats(monster_pieces, blocks, boss_types or {})

    rooms: dict[str, Encounter] = {}
    corridor_monsters: list[Monster] = []
    corridor_traps: list[Trap] = []
    for piece in pieces:
        cat, x, y = piece
        room = rows[y][x] if y < len(rows) and x < len(rows[y]) else "."
        is_room = room.isalpha()
        if cat.get("monster"):
            monster = stats.get(id(piece)) or _default_monster(cat["name"])
            if is_room:
                rooms.setdefault(room, Encounter(f"Room {room}")).monsters.append(monster)
            else:
                corridor_monsters.append(monster)
        elif cat["name"] in TRAP_DAMAGE:
            trap = Trap(cat["name"], TRAP_DAMAGE[cat["name"]])
            if is_room:
                rooms.setdefault(room, Encounter(f"Room {room}")).traps.append(trap)
            else:
                corridor_traps.append(trap)
    encounters = [rooms[k] for k in sorted(rooms)]
    groups = [
        corridor_monsters[i : i + corridor_group]
        for i in range(0, len(corridor_monsters), corridor_group)
    ]
    corridor = [Encounter(f"Corridor {n + 1}", monsters=g) for n, g in enumerate(groups)]
    if corridor_traps and not corridor:
        corridor = [Encounter("Corridor")]
    for n, trap in enumerate(corridor_traps):
        corridor[n % len(corridor)].traps.append(trap)
    encounters += corridor

    wm = catalog.get(st.get("wm_id", 0))
    if wm and wm.get("monster"):
        encounters += [
            Encounter(f"Wandering {wm['name']}", monsters=[_default_monster(wm["name"])])
            for _ in range(wanderers)
        ]
    found = len(re.findall(r"potion of healing", st.get("notes", ""), flags=re.IGNORECASE))
    return Quest(st.get("title", ""), encounters, found if potions is None else potions)


def _default_monster(name: str) -> Monster:
    if name in MONSTERS:
        monster = Monster.named(name)
    else:
        raise ValueError(
            f"No stats for {name}: add a stat block to Zargon's notes, for example "
            f"**{name}** followed by a |BP|MP|Attack|Defense|Special| table."
        )
    return monster


def _boss_stats(pieces, blocks: list[StatBlock], boss_types: dict[str, str]) -> dict[int, Monster]:
    """Gives each stat block to a monster piece: the --boss one, else the only piece of its type."""
    known = {b.name for b in blocks}
    for name in boss_types:
        if name not in known:
            raise ValueError(f"--boss {name}: there is no stat block with that name in the notes")
    by_id: dict[int, Monster] = {}
    counts: dict[str, int] = {}
    for cat, _x, _y in pieces:
        counts[cat["name"]] = counts.get(cat["name"], 0) + 1
    free = [
        p for p in pieces if counts[p[0]["name"]] == 1 and p[0]["name"] not in boss_types.values()
    ]
    for block in blocks:
        wanted = boss_types.get(block.name)
        if wanted:
            piece = next((p for p in pieces if p[0]["name"] == wanted and id(p) not in by_id), None)
        else:
            piece = free.pop(0) if free else None
        if piece is None:
            raise ValueError(
                f"The stat block for {block.name} has no monster to go with: it needs a monster "
                f"that is the only one of its type (or use --boss '{block.name}=<monster type>')."
            )
        monster = Monster(
            block.name, block.bp, block.attack, block.defend, piece[0]["name"] in CASTERS
        )
        by_id[id(piece)] = monster
    return by_id


# ---------------------------------------------------------------- one fight, and what happens after
def _skulls(n: int, rng) -> int:
    return sum(rng.random() < SKULL for _ in range(n))


def _hero_shields(n: int, rng) -> int:
    return sum(rng.random() < WHITE_SHIELD for _ in range(n))


def _monster_shields(n: int, rng) -> int:
    return sum(rng.random() < BLACK_SHIELD for _ in range(n))


def fight(
    heroes: list[Hero],
    monsters: list[Monster],
    rng,
    *,
    front: int,
    focus: bool,
    max_rounds: int = MAX_ROUNDS,
    supplies: Supplies | None = None,
    caster_damage: int = 0,
) -> int:
    """Plays rounds until one side is gone. front = how many fight at once (0 = everyone)."""
    rounds = 0
    while monsters and any(h.bp > 0 for h in heroes) and rounds < max_rounds:
        rounds += 1
        alive = [h for h in heroes if h.bp > 0]
        fighters = sorted(alive, key=lambda h: -h.attack)[: front or len(alive)]
        for hero in fighters:
            if not monsters:
                break
            target = min(monsters, key=lambda m: m.bp)  # the weakest monster first
            dice = hero.attack
            if (
                supplies
                and supplies.genie
                and hero.name == "Wizard"
                and (target.bp >= 2 or target.defend >= 4)
            ):
                supplies.genie, dice = False, 5  # the Wizard's Genie spell: 5 attack dice, once
            target.bp -= max(0, _skulls(dice, rng) - _monster_shields(target.defend, rng))
            if target.bp <= 0:
                monsters.remove(target)
        reach = monsters[: front or len(monsters)]
        for monster in reach:
            alive = [h for h in heroes if h.bp > 0]
            if not alive:
                break
            victim = min(alive, key=lambda h: h.bp) if focus else rng.choice(alive)
            hit = max(0, _skulls(monster.attack, rng) - _hero_shields(victim.defend, rng))
            victim.bp -= hit + (caster_damage if monster.caster else 0)
    return rounds


def heal_between_fights(heroes: list[Hero], supplies: Supplies) -> None:
    """A potion and then the Wizard's Heal Body go to the weakest hero who is nearly dead."""
    for available in ("potion", "spell"):
        weak = [h for h in heroes if 0 < h.bp <= 3]
        if not weak:
            return
        if available == "potion" and supplies.potions > 0:
            supplies.potions -= 1
        elif available == "spell" and supplies.heal_body:
            supplies.heal_body = False
        else:
            continue
        hero = min(weak, key=lambda h: h.bp)
        hero.bp = min(hero.max_bp, hero.bp + HEAL_AMOUNT)


# ---------------------------------------------------------------- many playthroughs
def simulate(
    quest: Quest,
    hero_names: list[str],
    *,
    front: int,
    focus: bool,
    runs: int,
    seed: int = 1,
    trap_chance: float = 0.35,
    spells: bool = True,
    caster_damage: int = 0,
) -> Result:
    rng = random.Random(seed)
    wins, left, dead = 0, 0.0, 0.0
    cost = {e.name: 0.0 for e in quest.encounters}
    for _ in range(runs):
        heroes = [Hero.named(n) for n in hero_names]
        wizard = spells and "Wizard" in hero_names
        supplies = Supplies(quest.potions, heal_body=wizard, genie=wizard)
        order = list(quest.encounters)
        rng.shuffle(order)
        cleared = True
        for enc in order:
            if not any(h.bp > 0 for h in heroes):
                cleared = False
                break
            before = [max(h.bp, 0) for h in heroes]
            monsters = copy.deepcopy(enc.monsters)
            fight(
                heroes,
                monsters,
                rng,
                front=front,
                focus=focus,
                supplies=supplies,
                caster_damage=caster_damage,
            )
            cleared = cleared and not monsters
            for trap in enc.traps:
                alive = [h for h in heroes if h.bp > 0]
                if alive and rng.random() < trap_chance:
                    rng.choice(alive).bp -= trap.damage
            cost[enc.name] += sum(before) - sum(max(h.bp, 0) for h in heroes)
            heal_between_fights(heroes, supplies)
        wins += cleared and any(h.bp > 0 for h in heroes)
        left += sum(max(h.bp, 0) for h in heroes)
        dead += sum(h.bp <= 0 for h in heroes)
    return Result(wins / runs, left / runs, dead / runs, {k: v / runs for k, v in cost.items()})


# ---------------------------------------------------------------- the report
ASSUMPTIONS = [
    "Heroes clear the rooms one at a time in a random order; no movement, line of sight or doors.",
    "Base-game dice and monster chart; hero stats without equipment (Mummy and Abomination: 2 BP).",
    "'Doorway' means two heroes and two monsters fight at once; 'open' means everyone does.",
    "Zargon 'random' hits a random hero; 'focus' always hits the hero with the fewest BP.",
    "A trap hurts a random hero with the chance below (pit and spear 1 BP, falling rock 2 BP).",
    "Healing: potions named in the notes, and the Wizard's Heal Body and Genie (once each).",
    "Special abilities in the notes (calling reinforcements, floors giving way) are not modeled.",
]


def report(quest: Quest, parties: list[int], args) -> str:
    total_monsters = sum(len(e.monsters) for e in quest.encounters)
    total_bp = sum(m.bp for e in quest.encounters for m in e.monsters)
    out = [
        f"{quest.title or 'Untitled quest'}: {total_monsters} monsters ({total_bp} BP) in "
        f"{len(quest.encounters)} encounters, {quest.potions} potion(s) of healing, "
        f"{args.runs} runs each.",
        "",
        f"{'party':9} {'tactic':8} {'Zargon':7} {'win %':>6} {'BP left':>8} {'heroes dead':>12}",
    ]
    detail: Result | None = None
    for size in parties:
        names = PARTY_ORDER[:size]
        for tactic, front in (("doorway", 2), ("open", 0)):
            for zargon, focus in (("random", False), ("focus", True)):
                res = simulate(
                    quest,
                    names,
                    front=front,
                    focus=focus,
                    runs=args.runs,
                    seed=args.seed,
                    trap_chance=args.trap_chance,
                    spells=not args.no_spells,
                    caster_damage=args.caster_damage,
                )
                out.append(
                    f"{size} heroes {tactic:8} {zargon:7} {res.win_rate * 100:6.0f} "
                    f"{res.bp_left:8.1f} "
                    f"{res.dead:12.1f}"
                )
                if size == max(parties) and tactic == "open" and zargon == "random":
                    detail = res
    if detail:
        worst = sorted(detail.cost.items(), key=lambda kv: -kv[1])[:8]
        out += [
            "",
            f"Where the BP goes ({max(parties)} heroes, open, random Zargon), average BP lost:",
        ]
        out += [f"  {name:22} {lost:5.1f}" for name, lost in worst if lost > 0]
    out += ["", "Assumptions:"] + [f"  - {a}" for a in ASSUMPTIONS]
    out.append(
        f"  - Traps trigger with chance {args.trap_chance}; casters add {args.caster_damage} BP "
        "of spell damage per round."
    )
    return "\n".join(out)


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Rough playthrough simulation of a quest link.")
    p.add_argument("quest", help="a quest link, its part after #, or a file that contains one")
    p.add_argument("--runs", type=int, default=2000, help="playthroughs per row (default 2000)")
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--heroes", default="2,3,4", help="party sizes, 1-4 (default 2,3,4)")
    p.add_argument("--trap-chance", type=float, default=0.35)
    p.add_argument("--wanderers", type=int, default=1, help="wandering monster appearances")
    p.add_argument("--corridor-group", type=int, default=3, help="corridor monsters per encounter")
    p.add_argument(
        "--potions", type=int, default=None, help="override the potions found in the notes"
    )
    p.add_argument(
        "--caster-damage", type=int, default=2, help="BP of spell damage a caster adds per round"
    )
    p.add_argument("--no-spells", action="store_true", help="the Wizard casts nothing")
    p.add_argument(
        "--boss",
        action="append",
        default=[],
        metavar="NAME=TYPE",
        help="give the stat block NAME to the monster piece of this TYPE",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        sizes = [int(s) for s in args.heroes.split(",")]
        if not sizes or any(s < 1 or s > 4 for s in sizes):
            raise ValueError("--heroes takes sizes from 1 to 4, such as 2,3,4")
        bosses = dict(b.split("=", 1) for b in args.boss)
        state = load_link(args.quest)
        quest = build_quest(
            state,
            wanderers=args.wanderers,
            corridor_group=args.corridor_group,
            potions=args.potions,
            boss_types=bosses,
        )
        print(report(quest, sizes, args))
    except (ValueError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
