"""Hero view rules as pure functions: regions, groups, play actions, visibility, secret doors, texts."""

from __future__ import annotations

# Board facts used below: room A is x 1-4 / y 1-3, H is x 5-8 / y 4-8, K is x 10-15 / y 7-12,
# N is x 7-8 / y 10-12. Row 0 and row 9 are corridor. Regions: A=0, H=7, K=10, N=13, zone 1=26.
A, H, K, N, Z1, Z2 = 0, 7, 10, 13, 26, 27
DOOR, HIDDEN_DOOR, SECRET_DOOR, GOBLIN, CHEST, PIT_TRAP, MARKER_1 = 1, 2, 4, 40, 30, 31, 80


def run(page, body, arg=None):
    """Runs JS with `st` (the app state, reset to a blank quest first) and `H` (QMG.hero) in scope."""
    return page.evaluate(
        "([body, arg]) => { const H = QMG.hero; const st = QMG.app.state;"
        " st.rooms = {}; st.play = null; st.items = []; st.hl.fill(0); st.zones.fill(0);"
        " return (new Function('H', 'st', 'arg', body))(H, st, arg); }",
        [body, arg],
    )


def test_a_group_reveals_together_and_a_loner_alone(page):
    r = run(
        page,
        """
        st.rooms = { 10: { start: false, group: 3, texts: ['', '', '', ''] },
                     13: { start: false, group: 3, texts: ['', '', '', ''] },
                     0: { start: false, group: 0, texts: ['', '', '', ''] } };
        return [H.groupMembers(st, 10), H.groupMembers(st, 13), H.groupMembers(st, 0), H.groupMembers(st, 5)];
        """,
    )
    assert r == [[10, 13], [10, 13], [0], [5]]


def test_the_start_state_reveals_the_start_regions_and_the_first_action_makes_play_explicit(page):
    r = run(
        page,
        """
        st.rooms = { 0: { start: true, group: 0, texts: ['', '', '', ''] } };
        const before = [H.isRevealed(st, 0), H.isRevealed(st, 10), st.play];
        H.revealRegion(st, 10);
        return [before, H.isRevealed(st, 0), H.isRevealed(st, 10), st.play !== null];
        """,
    )
    assert r == [[True, False, None], True, True, True]


def test_reveal_reveals_the_whole_group_and_reports_whether_anything_changed(page):
    r = run(
        page,
        """
        st.rooms = { 10: { start: false, group: 1, texts: ['', '', '', ''] },
                     13: { start: false, group: 1, texts: ['', '', '', ''] } };
        const first = H.revealRegion(st, 13);
        const again = H.revealRegion(st, 13);
        return [first, again, H.isRevealed(st, 10), H.isRevealed(st, 13), H.isRevealed(st, 0)];
        """,
    )
    assert r == [True, False, True, True, False]


def test_hiding_a_region_hides_its_group_and_clears_their_searches_even_for_a_start_region(page):
    r = run(
        page,
        """
        st.rooms = { 10: { start: true, group: 1, texts: ['', '', '', ''] },
                     13: { start: false, group: 1, texts: ['', '', '', ''] } };
        H.revealRegion(st, 13);
        H.searchRegion(st, 13, 'sd');
        H.revealRegion(st, 0);
        H.hideRegion(st, 13);
        return [H.isRevealed(st, 10), H.isRevealed(st, 13), H.isRevealed(st, 0), H.isSearched(st, 13, 'sd')];
        """,
    )
    assert r == [False, False, True, False]


def test_searching_needs_a_revealed_region_applies_to_the_group_and_repeats_harmlessly(page):
    r = run(
        page,
        """
        st.rooms = { 10: { start: false, group: 1, texts: ['', '', '', ''] },
                     13: { start: false, group: 1, texts: ['', '', '', ''] } };
        const hidden = H.searchRegion(st, 10, 't');
        H.revealRegion(st, 10);
        const first = H.searchRegion(st, 10, 't');
        const again = H.searchRegion(st, 10, 't');
        return [hidden, first, again, H.isSearched(st, 13, 't'), H.isSearched(st, 10, 'tr')];
        """,
    )
    assert r == [False, True, False, True, False]


def test_reset_game_goes_back_to_the_start_state(page):
    r = run(
        page,
        """
        st.rooms = { 0: { start: true, group: 0, texts: ['', '', '', ''] } };
        H.revealRegion(st, 10); H.hideRegion(st, 0);
        H.resetGame(st);
        return [st.play, H.isRevealed(st, 0), H.isRevealed(st, 10)];
        """,
    )
    assert r == [None, True, False]


def test_texts_of_a_group_are_joined_in_region_order_skipping_empty_ones(page):
    r = run(
        page,
        """
        st.rooms = { 13: { start: false, group: 1, texts: ['N reads', '', 'N traps', ''] },
                     10: { start: false, group: 1, texts: ['K reads', 'K gold', '', ''] },
                     0: { start: false, group: 0, texts: ['A alone', '', '', ''] } };
        return [H.regionTexts(st, 13), H.regionTexts(st, 0), H.regionTexts(st, 5)];
        """,
    )
    assert r[0] == {
        "readAloud": "K reads\n\nN reads",
        "treasure": "K gold",
        "traps": "N traps",
        "secretDoors": "",
    }
    assert r[1]["readAloud"] == "A alone"
    assert r[2] == {"readAloud": "", "treasure": "", "traps": "", "secretDoors": ""}


def test_squares_are_visible_only_in_a_revealed_region_and_unzoned_squares_never_are(page):
    r = run(
        page,
        """
        st.zones[0 * 26 + 5] = 1; // zone 1 on a corridor square in row 0
        const out = [H.squareVisible(st, 3, 0), H.squareVisible(st, 5, 0), H.squareVisible(st, 2, 2)];
        H.revealRegion(st, 26); H.revealRegion(st, 0);
        return out.concat([H.squareVisible(st, 5, 0), H.squareVisible(st, 2, 2)]);
        """,
    )
    assert r == [
        False,
        False,
        False,
        True,
        True,
    ]  # a square in no room or zone is solid stone: hidden for good


def piece_visibility(page, items, setup=""):
    return run(
        page,
        f"""
        {setup}
        st.items = arg.map(([id, x, y, r]) => ({{ id, x, y, r }}));
        return H.itemVisibility(st);
        """,
        items,
    )


def test_ordinary_pieces_follow_their_room_but_markers_and_traps_are_never_shown(page):
    items = [[GOBLIN, 2, 2, 0], [CHEST, 2, 3, 0], [MARKER_1, 3, 2, 0], [PIT_TRAP, 4, 3, 0]]
    assert piece_visibility(page, items) == [False, False, False, False]
    shown = piece_visibility(page, items, "H.revealRegion(st, 0);")
    assert shown == [True, True, False, False]


def test_pieces_in_an_unzoned_corridor_are_never_shown_and_zoned_ones_follow_the_zone(page):
    items = [[GOBLIN, 3, 0, 0]]
    assert piece_visibility(page, items) == [False]
    assert piece_visibility(page, items, "H.revealRegion(st, 0);") == [
        False
    ]  # revealing a room does not help
    zoned = "st.zones[3] = 1;"  # zone 1 on (3, 0)
    assert piece_visibility(page, items, zoned) == [False]
    assert piece_visibility(page, items, zoned + "H.revealRegion(st, 26);") == [True]


def test_a_door_shows_when_either_side_is_visible(page):
    west_door = [DOOR, 1, 2, 3]  # west edge of room A: between corridor (0, 2) and room A (1, 2)
    assert piece_visibility(page, [west_door]) == [
        False
    ]  # the corridor side is solid stone, the room hidden
    hidden_both = "st.zones[2 * 26 + 0] = 1;"  # make the corridor square a hidden zone
    assert piece_visibility(page, [west_door], hidden_both) == [False]
    assert piece_visibility(page, [west_door], hidden_both + "H.revealRegion(st, 0);") == [True]
    assert piece_visibility(page, [west_door], hidden_both + "H.revealRegion(st, 26);") == [True]


def test_a_secret_door_tile_in_a_room_is_found_only_by_that_rooms_secret_door_search(page):
    tile = [SECRET_DOOR, 2, 2, 0]
    assert piece_visibility(page, [tile], "H.revealRegion(st, 0);") == [False]
    assert piece_visibility(
        page, [tile], "H.revealRegion(st, 0); H.searchRegion(st, 0, 'tr');"
    ) == [False]
    assert piece_visibility(
        page, [tile], "H.revealRegion(st, 0); H.searchRegion(st, 0, 'sd');"
    ) == [True]


def test_a_secret_door_in_an_unzoned_corridor_belongs_to_each_room_it_touches(page):
    tile = [SECRET_DOOR, 7, 9, 0]  # corridor square between room H (above) and room N (below)
    owners = run(page, "return H.secretOwners(st, { id: 4, x: 7, y: 9, r: 0 });")
    assert owners == [H, N]
    for room in (H, N):
        found = f"H.revealRegion(st, {room}); H.searchRegion(st, {room}, 'sd');"
        assert piece_visibility(page, [tile], found) == [True]
    assert piece_visibility(page, [tile], "H.revealRegion(st, 7);") == [False]


def test_a_secret_door_on_a_zone_square_belongs_to_the_zone_and_to_each_room_it_touches(page):
    tile = [SECRET_DOOR, 7, 9, 0]  # between room H (above) and room N (below), painted as zone 1
    zoned = "st.zones[9 * 26 + 7] = 1;"
    owners = run(page, zoned + "return H.secretOwners(st, { id: 4, x: 7, y: 9, r: 0 });")
    assert owners == [H, N, Z1]
    for region in (H, N, Z1):
        found = zoned + f"H.revealRegion(st, {region}); H.searchRegion(st, {region}, 'sd');"
        assert piece_visibility(page, [tile], found) == [True]
    assert piece_visibility(page, [tile], zoned + "H.revealRegion(st, 26);") == [False]


def test_a_secret_door_in_a_zone_far_from_any_room_belongs_to_the_zone_only(page):
    owners = run(page, "st.zones[0] = 1; return H.secretOwners(st, { id: 4, x: 0, y: 0, r: 0 });")
    assert owners == [Z1]


def test_the_secret_doors_a_search_finds_are_counted_over_the_whole_group(page):
    body = (
        "st.items = [{ id: 4, x: 2, y: 2, r: 0 }, { id: 4, x: 7, y: 9, r: 0 },"
        " { id: 2, x: 7, y: 8, r: 2 }, { id: 4, x: 20, y: 0, r: 0 }];"
        " st.rooms[0] = { start: false, group: 1, texts: ['', '', '', ''] };"
        " st.rooms[7] = { start: false, group: 1, texts: ['', '', '', ''] };"
        " st.rooms[10] = { start: false, group: 0, texts: ['', '', '', ''] };"
        " return [0, 7, 10, 13].map((r) => H.secretDoorsFound(st, r));"
    )
    # group {A, H}: A's tile, the corridor tile and H's hidden door; K owns none; N owns the corridor tile
    assert run(page, body) == [3, 3, 0, 1]


def test_a_hidden_door_on_a_wall_belongs_to_the_regions_on_both_sides(page):
    # south edge of room H at (7, 8): between H (7, 8) and the corridor square (7, 9)
    owners = run(page, "return H.secretOwners(st, { id: 2, x: 7, y: 8, r: 2 });")
    assert owners == [H]  # the corridor side is unzoned, so only the room owns it
    both = run(
        page, "st.zones[9 * 26 + 7] = 1; return H.secretOwners(st, { id: 2, x: 7, y: 8, r: 2 });"
    )
    assert both == [H, Z1]


def test_stone_shows_only_where_its_square_is_visible(page):
    r = run(
        page,
        """
        st.hl[2 * 26 + 2] = 1; st.hl[0 * 26 + 3] = 1;
        const before = [H.stoneVisible(st, 2, 2), H.stoneVisible(st, 3, 0), H.stoneVisible(st, 6, 0)];  // 3,0 is unzoned
        H.revealRegion(st, 0);
        return before.concat([H.stoneVisible(st, 2, 2)]);
        """,
    )
    assert r == [False, False, False, True]  # stone shows only once its room or zone is revealed


def test_stone_and_a_trap_highlight_can_sit_in_a_zone_and_stay_hidden_with_it(page):
    r = run(
        page,
        """
        st.hl[0 * 26 + 5] = 1;      // corridor stone ...
        st.zones[0 * 26 + 5] = 1;   // ... that belongs to zone 1
        st.hl[0 * 26 + 6] = 2;      // a trap highlight on a zoned corridor square
        st.zones[0 * 26 + 6] = 1;
        const before = [H.stoneVisible(st, 5, 0), H.squareVisible(st, 6, 0)];
        H.revealRegion(st, 26);
        return before.concat([H.stoneVisible(st, 5, 0), H.squareVisible(st, 6, 0)]);
        """,
    )
    assert r == [False, False, True, True]


def test_a_found_secret_door_shows_even_where_the_square_is_hidden(page):
    tile = [SECRET_DOOR, 7, 9, 0]  # on an unzoned corridor square between rooms H and N
    found = f"H.revealRegion(st, {H}); H.searchRegion(st, {H}, 'sd');"
    assert piece_visibility(page, [tile], found) == [True]
    assert (
        run(
            page,
            found + " st.items = [{ id: 4, x: 7, y: 9, r: 0 }]; return H.squareVisible(st, 7, 9);",
        )
        is True
    )
    assert (
        run(page, "st.items = [{ id: 4, x: 7, y: 9, r: 0 }]; return H.squareVisible(st, 7, 9);")
        is False
    )
    other = run(
        page, found + " st.items = [{ id: 4, x: 7, y: 9, r: 0 }]; return H.squareVisible(st, 8, 9);"
    )
    assert other is False  # only the door's own square is shown, not the corridor around it


def test_treasure_can_be_searched_in_every_room_but_in_a_hallway_only_with_a_treasure_chest(page):
    body = (
        "st.zones[4] = 1; st.zones[5] = 2;"  # zone 1 on (4, 0), zone 2 on (5, 0)
        " st.items = [{ id: 30, x: 4, y: 0, r: 0 }, { id: 40, x: 5, y: 0, r: 0 }];"
        " return [0, 7, 26, 27, 28].map((r) => H.canSearchTreasure(st, r));"
    )
    # rooms A and H always; zone 1 holds a chest; zone 2 only a goblin; zone 3 is empty
    assert run(page, body) == [True, True, True, False, False]


def test_zones_up_to_thirty_are_regions_and_have_names(page):
    body = (
        "st.zones[0] = 17; st.zones[1] = 30; st.legend[22] = 'Long corridor';"
        " return [H.regionAt(st, 0, 0), H.regionAt(st, 1, 0), H.regionName(st, 42),"
        " H.regionName(st, 55), H.regionName(st, 26)];"
    )
    assert run(page, body) == [42, 55, "Long corridor", "Zone 30", "Zone 1"]


def test_a_zone_beyond_thirty_is_no_zone(page):
    assert run(page, "st.zones[0] = 31; return H.regionAt(st, 0, 0);") is None


def test_a_quest_always_has_ten_zones_and_more_only_when_they_are_used(page):
    body = """
        const counts = [H.zoneCount(st)];
        st.zones[5] = 12; counts.push(H.zoneCount(st)); st.zones[5] = 0;
        st.rooms[41] = { start: false, group: 0, texts: ['', '', '', 'x'] };
        counts.push(H.zoneCount(st)); delete st.rooms[41];
        st.legend[24] = 'named'; counts.push(H.zoneCount(st)); delete st.legend[24];
        st.zones[6] = 3; counts.push(H.zoneCount(st));
        return counts;
    """
    # none: 10; a square in zone 12: 12; a record for region 41 (zone 16): 16; a name in entry 24
    # (zone 19): 19; a zone 3 square alone: back to 10
    assert run(page, body) == [10, 12, 16, 19, 10]


def test_zones_above_the_tenth_have_separate_play_state_bits(page):
    body = """
        H.revealRegion(st, 5); H.revealRegion(st, 30); H.revealRegion(st, 55);
        return [H.isRevealed(st, 30), H.isRevealed(st, 55), H.isRevealed(st, 31)];
    """
    assert run(page, body) == [True, True, False]
