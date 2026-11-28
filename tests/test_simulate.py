"""The quest simulator (scripts/simulate.py): a rough fights-only Monte Carlo, never part of the app."""

from __future__ import annotations

import subprocess
import sys

import pytest
import reference as ref
from conftest import ROOT

sys.path.insert(0, str(ROOT / "scripts"))
import simulate as sim  # noqa: E402

CATALOG = {
    p["slug"]: p["id"] for p in __import__("json").loads((ROOT / "src/catalog.json").read_text())
}


class Const:
    """A 'random' source that always returns the same number, so dice are predictable."""

    def __init__(self, value: float):
        self.value = value

    def random(self) -> float:
        return self.value

    def shuffle(self, items) -> None:
        pass

    def choice(self, items):
        return items[0]


def put(st, slug, x, y, r=0):
    st["items"].append((CATALOG[slug], x, y, r))


def quest_state(notes=""):
    """Room K is x 10-15 / y 7-12, room S x 14-17 / y 13-17; row 0 is corridor (src/board.txt)."""
    st = ref.blank()
    st["title"] = "Test quest"
    st["notes"] = notes
    return st


BLOCK = """**Lumeloth**
|BP|MP|Attack|Defense|Special|
| :--- | :--- | :--- | :--- | :--- |
| 4 | 3 | 4 | 4 | When Lumeloth dies he lets out a shriek. |
"""


# ---------------------------------------------------------------- stat blocks in the notes
def test_a_stat_block_in_the_notes_is_read():
    blocks = sim.parse_stat_blocks("Intro text\n\n" + BLOCK + "\nG - more text")
    assert [(b.name, b.bp, b.mind, b.attack, b.defend) for b in blocks] == [
        ("Lumeloth", 4, 3, 4, 4)
    ]


def test_two_stat_blocks_are_read_in_order():
    other = BLOCK.replace("Lumeloth", "Uganoth Undead").replace(
        "| 4 | 3 | 4 | 4 |", "| 3 | 6 | 1 | 6 |"
    )
    blocks = sim.parse_stat_blocks(BLOCK + "\n" + other)
    assert [(b.name, b.bp, b.defend) for b in blocks] == [
        ("Lumeloth", 4, 4),
        ("Uganoth Undead", 3, 6),
    ]


def test_tables_that_are_not_stat_blocks_are_ignored():
    notes = "**Loot**\n|Item|Gold|\n|---|---|\n| Sword | 50 |\n"
    assert sim.parse_stat_blocks(notes) == []
    assert sim.parse_stat_blocks("no tables at all") == []


# ---------------------------------------------------------------- reading a quest
def test_monsters_are_grouped_by_room_and_corridor_monsters_by_threes():
    st = quest_state()
    for x in (11, 12):
        put(st, "goblin", x, 8)  # room K
    put(st, "abomination", 13, 9)  # room K
    for x in range(0, 4):
        put(st, "goblin", x, 0)  # four corridor goblins
    quest = sim.build_quest(st, notes_blocks=[], wanderers=0)
    sizes = {e.name: len(e.monsters) for e in quest.encounters}
    assert sizes["Room K"] == 3
    assert sorted(len(e.monsters) for e in quest.encounters if e.name.startswith("Corridor")) == [
        1,
        3,
    ]


def test_the_only_piece_of_a_monster_type_takes_the_notes_stat_block():
    st = quest_state(BLOCK)
    put(st, "abomination", 12, 9)
    put(st, "goblin", 11, 8)
    quest = sim.build_quest(st, wanderers=0)
    boss = next(m for e in quest.encounters for m in e.monsters if m.name == "Lumeloth")
    assert (boss.bp, boss.attack, boss.defend) == (4, 4, 4)
    goblin = next(m for e in quest.encounters for m in e.monsters if m.name == "Goblin")
    assert (goblin.bp, goblin.attack, goblin.defend) == (1, 2, 1)


def test_boss_types_say_which_monster_a_stat_block_belongs_to():
    st = quest_state(BLOCK)
    put(st, "orc", 11, 8)  # without a hint the first lone monster would take the block
    put(st, "abomination", 12, 9)
    quest = sim.build_quest(st, wanderers=0, boss_types={"Lumeloth": "Abomination"})
    names = sorted(m.name for e in quest.encounters for m in e.monsters)
    assert names == ["Lumeloth", "Orc"]


def test_a_boss_hint_for_a_stat_block_that_does_not_exist_is_an_error():
    st = quest_state(BLOCK)
    put(st, "abomination", 12, 9)
    with pytest.raises(ValueError, match="Nobody"):
        sim.build_quest(st, wanderers=0, boss_types={"Nobody": "Abomination"})


def test_a_stat_block_with_no_lone_monster_to_take_it_is_an_error():
    st = quest_state(BLOCK)
    put(st, "goblin", 11, 8)
    put(st, "goblin", 12, 8)  # two goblins: no monster is the only one of its type
    with pytest.raises(ValueError, match="Lumeloth"):
        sim.build_quest(st, wanderers=0)


def test_a_monster_without_known_stats_is_an_error_that_names_it():
    st = quest_state()
    put(st, "dread-warlock", 15, 14)  # BP varies by quest and the notes have no stat block
    with pytest.raises(ValueError, match="Dread Warlock"):
        sim.build_quest(st, wanderers=0)


def test_traps_belong_to_their_room_and_a_room_with_only_traps_is_an_encounter():
    st = quest_state()
    put(st, "pit-trap", 2, 2)  # room A
    put(st, "falling-rock-trap", 3, 2)
    quest = sim.build_quest(st, wanderers=0)
    room = next(e for e in quest.encounters if e.name == "Room A")
    assert room.monsters == [] and sorted(t.damage for t in room.traps) == [1, 2]


def test_potions_are_counted_from_the_notes_unless_given():
    st = quest_state("B - a Potion of Healing\n\nC - 100 gold and a potion of healing\n")
    assert sim.build_quest(st, wanderers=0).potions == 2
    assert sim.build_quest(st, wanderers=0, potions=0).potions == 0


def test_the_wandering_monster_becomes_extra_encounters():
    st = quest_state()
    st["wm_id"] = CATALOG["skeleton"]
    quest = sim.build_quest(st, wanderers=2)
    assert [e.name for e in quest.encounters].count("Wandering Skeleton") == 2


# ---------------------------------------------------------------- the dice and fights
def party(*names):
    return [sim.Hero.named(n) for n in names]


def goblins(n):
    return [sim.Monster.named("Goblin") for _ in range(n)]


def test_with_every_die_a_skull_and_a_shield_the_heroes_kill_goblins_and_take_no_damage():
    heroes = party("Barbarian", "Dwarf")
    sim.fight(heroes, goblins(3), Const(0.0), front=0, focus=False)
    assert [h.bp for h in heroes] == [8, 7]


def test_with_no_skulls_nothing_dies_and_the_fight_is_a_stalemate():
    heroes = party("Barbarian")
    monsters = goblins(2)
    sim.fight(heroes, monsters, Const(0.9), front=0, focus=False)
    assert len(monsters) == 2 and heroes[0].bp == 8


def test_monsters_that_get_through_the_shields_hurt_the_weakest_hero_when_focusing():
    heroes = party("Barbarian", "Wizard")
    monsters = [sim.Monster("Brute", bp=50, attack=6, defend=0)]
    # skulls always (0.2 < 0.5) but a hero shield needs < 1/3, so use 0.4: skull and no shield
    sim.fight(heroes, monsters, Const(0.4), front=0, focus=True, max_rounds=1)
    assert heroes[0].bp == 8 and heroes[1].bp == 4 - 6


def test_a_doorway_lets_only_two_monsters_attack_at_once():
    heroes = party("Barbarian", "Dwarf", "Elf", "Wizard")
    monsters = [sim.Monster("Brute", bp=50, attack=1, defend=0) for _ in range(6)]
    sim.fight(heroes, monsters, Const(0.4), front=2, focus=True, max_rounds=1)
    assert 25 - sum(h.bp for h in heroes) == 2  # two monsters, one skull each


def test_healing_goes_to_a_hero_who_is_nearly_dead_and_uses_up_a_potion():
    heroes = party("Barbarian", "Elf")
    heroes[1].bp = 2
    state = sim.Supplies(potions=1, heal_body=False, genie=False)
    sim.heal_between_fights(heroes, state)
    assert heroes[1].bp == 6 and state.potions == 0
    sim.heal_between_fights(heroes, state)  # nothing left to use
    assert heroes[1].bp == 6


# ---------------------------------------------------------------- running many playthroughs
def small_quest():
    st = quest_state()
    for i in range(8):
        put(st, "goblin", 11 + i % 3, 8 + i // 3)  # room K
    put(st, "orc", 15, 12)
    return sim.build_quest(st, wanderers=0)


def test_more_heroes_do_not_do_worse():
    quest = small_quest()
    wins = [
        sim.simulate(quest, heroes, front=0, focus=False, runs=300, seed=3).win_rate
        for heroes in (
            ["Barbarian", "Dwarf"],
            ["Barbarian", "Dwarf", "Elf"],
            ["Barbarian", "Dwarf", "Elf", "Wizard"],
        )
    ]
    assert wins[0] <= wins[1] <= wins[2]


def test_the_same_seed_gives_the_same_answer():
    quest = small_quest()
    one = sim.simulate(quest, ["Barbarian", "Elf"], front=0, focus=True, runs=50, seed=9)
    two = sim.simulate(quest, ["Barbarian", "Elf"], front=0, focus=True, runs=50, seed=9)
    assert (one.win_rate, one.bp_left, one.cost) == (two.win_rate, two.bp_left, two.cost)


def test_a_trap_that_always_triggers_costs_exactly_its_damage():
    st = quest_state()
    put(st, "pit-trap", 2, 2)
    quest = sim.build_quest(st, wanderers=0)
    result = sim.simulate(
        quest, ["Barbarian", "Dwarf"], front=0, focus=False, runs=20, seed=1, trap_chance=1.0
    )
    assert result.win_rate == 1.0 and result.bp_left == 15 - 1
    assert result.cost["Room A"] == 1


def test_the_cost_of_a_room_is_the_bp_the_heroes_lose_in_it():
    quest = small_quest()
    result = sim.simulate(
        quest, ["Barbarian", "Dwarf", "Elf"], front=0, focus=False, runs=100, seed=2
    )
    assert result.cost["Room K"] > 0
    assert result.bp_left == pytest.approx(21 - sum(result.cost.values()), abs=0.01)  # no healing


# ---------------------------------------------------------------- the command line
def run_cli(*args):
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts/simulate.py"), *args],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )


def test_the_command_line_reads_a_link_file_and_prints_a_report(tmp_path):
    st = quest_state()
    put(st, "goblin", 11, 8)
    put(st, "goblin", 12, 8)
    path = tmp_path / "quest.txt"
    path.write_text("https://example.test/app/#" + ref.encode(st) + "\n")
    done = run_cli(str(path), "--runs", "30", "--seed", "1")
    assert done.returncode == 0, done.stderr
    assert "Test quest" in done.stdout
    for text in ("4 heroes", "3 heroes", "2 heroes", "Room K", "Assumptions"):
        assert text in done.stdout


def test_the_command_line_refuses_something_that_is_not_a_link(tmp_path):
    path = tmp_path / "junk.txt"
    path.write_text("not a link at all!!")
    done = run_cli(str(path))
    assert done.returncode != 0
    assert "link" in done.stderr.lower()


def test_the_command_line_says_which_monster_has_no_stats(tmp_path):
    st = quest_state()
    put(st, "dread-warlock", 15, 14)
    path = tmp_path / "quest.txt"
    path.write_text(ref.encode(st))
    done = run_cli(str(path))
    assert done.returncode != 0 and "Dread Warlock" in done.stderr
