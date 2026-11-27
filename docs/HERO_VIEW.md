# Hero view (design record)

**Status: built.** This file records the decisions the owner made and why. The byte layout is in
`docs/FORMAT.md` (4.7 and 4.8) and the behavior is summarized in `AGENTS.md` and the README; where this
file and the code differ, the code and `FORMAT.md` win.

Hero view is a second way to look at the same quest: the map starts hidden, and the heroes reveal it
room by room. The game itself is still played at the table. The site only shows what the quest
author wrote, and it never rolls dice or decides whether a trap is sprung.

## Decisions made

1. **One shared phone, honor system.** Zargon holds one phone that the table looks at. A hero link
   opens straight into hero view. Everything in a link is readable by anyone who decodes it, so hero
   view hides secrets on screen but does not protect them. Switching from hero view to the main
   (Zargon) view shows a warning and asks "are you sure?".
2. **Same link format, different view.** The view is chosen by a flag in the existing flags byte
   (a spare bit), and the room data is a new optional trailing section of the body, so older links
   still decode. Nothing about hero view needs a second link.
3. **Play state lives in the link**, updated as the game goes: which rooms are revealed and which
   searches were done (a few bytes). A reload or a restored tab keeps your place, and the link can be
   bookmarked or resent. A "reset reveals" button starts over. Nothing is stored anywhere else.
4. **Revealing a room.** Click a room on the map and a room panel opens (like "What's here"). It has a
   Reveal button, which asks "are you sure?". Revealing shows the room's monsters, furniture and
   doors. It does **not** show secret doors or hidden doors, and trap pieces are **never** shown.
   Markers and Zargon's colored highlights (every color except grey) always stay hidden. Solid stone
   always shows.
5. **Search buttons are always there**, even when the room has nothing to find, so a button never
   gives anything away. Once a search is done its result stays shown.
   - **Search for treasure** shows the room's treasure text (a hero-facing field, not private).
   - **Search for traps** shows the room's traps text only. No trap pieces are revealed.
   - **Search for secret doors** shows the room's secret doors text and reveals the secret doors in
     the room and on the outside of its walls. Hidden doors (the edge pieces) are revealed together
     with secret doors (the slab tiles).
6. **Merged rooms: the author chooses.** Rooms are not grouped automatically from room tiles. The
   author marks which rooms reveal together, and a group reveals as one. A group's texts are joined
   in alphabetical room order: the read-aloud texts of the rooms in the group, then the treasure
   texts, traps texts and secret-door texts the same way (each room's own text is still capped at
   600 characters).
7. **Room texts: four per room**, each up to **600 characters**: read aloud (on reveal), treasure,
   traps, secret doors. A room with an empty field simply has nothing to show for it.
8. **Quest-level text in hero view:** series, number, title, intro and the wandering monster are
   shown. Zargon's secret notes are not.
9. **No undo or back for play state, but it can be reset.** Revealing and searching change the link
   in place (no new browser history entries) and hero view has no Undo/Redo, so the back button does
   not step through play. A mistaken reveal is prevented by the "are you sure?". It is fixed by
   **"Hide this room again"** on a revealed room's panel (which also clears that room's searches) or by a
   header button that **resets the whole game**. Both ask "are you sure?". The heroes may already
   have seen the room, so this only corrects what the screen shows.
13. **"Copy hero link" in the editor** always copies a link with a clean play state (nothing
    revealed), so a half-played link is never handed out by accident.
14. **Corridors become "zones" that reveal like rooms.** Corridors cannot be revealed square by square
    in any good way, so the author paints corridor squares with a **zone color** to make hallways.
    A zone behaves exactly like a lettered room: a Reveal button (with "are you sure?"), "Hide this
    zone again", the four texts and the search buttons, grouping with other rooms or zones, and one
    bit of play state. Storage is a **separate zone layer** (a 494-byte layer, one byte per square, at the start of the
    hero section of the link), not the highlight colors: a square holds only one highlight, so a zone
    stored as a highlight could not also be solid stone or a trap highlight, and stone in a hallway would
    have stayed visible from the start. With its own layer any square can be in a zone. Zones are named by
    the legend entries 6 to 15 (an author-only name). More zones can be added later without breaking any
    link.
    - **Visibility follows zones and rooms.** A piece is shown when the zone or room its square is in is
      revealed. A **door is shown when a room or zone on either side of it is revealed.** Secret and
      hidden doors are the exception: only the secret-door search shows them, and a secret door tile on a
      zone square belongs to that zone and to every room that shares a wall with the square. Traps and markers are never shown.
    - **A square in no room and no zone is solid stone to the heroes.** It is fogged like everything
      hidden, for good, and so is anything standing on it, because nothing can reveal it. Tapping one
      looks like tapping any hidden hallway: the panel says "Hallway" and offers **Reveal**, and pressing
      it shows a message, "Nothing to reveal. This is solid stone." (no question first, and nothing
      changes). Heroes therefore cannot tell a hallway from solid stone until they try it. An author who
      wants a hallway to be walkable paints it into a zone.
    - **A highlighted tap shows only the tapped square.** Tapping a hallway or zone highlights just that
      square, never the whole zone, because the extent of a zone would give the map away. A room is
      highlighted whole (its shape is printed on the board).
    - **A found secret door shows on its own square,** even when that square is otherwise hidden fog.
    - **Hero view never shows a zone name.** A name could give something away, so a fogged hallway is
      just dark and a revealed zone's panel says "Hallway". Zone names exist only for the author (the
      editor card and the legend).
    - **The fog is one flat color,** fully opaque and the same everywhere (no tint, no faint shapes, no
      grid lines or seams between squares), so nothing about a hidden area, including whether it is
      stone, can be told from the fog. Room letters stay, since they are printed on the real board.
15. **Play state is carried along when Zargon switches to the main view and edits the map.** It stays
    in the link untouched. "New map" clears it, and "Copy hero link" always writes a clean state.
16. **Room texts stay capped at 600 characters each**, with a live counter in the editor for the total
    room text and the link length. Raising a cap later is harmless; lowering it would cut off text in
    existing links, so it is only raised.
10. **Print stays as it is.** The print page keeps Zargon's notes and the quest text; it does not
    include the room texts. Hero view is meant to be used on a device, not on paper.
11. **Solid stone is hidden like everything else.** Anything not yet revealed looks exactly the same: a
    plain, identical fog. A room that is completely solid stone looks like any other hidden room, so
    heroes cannot tell which rooms are in the quest. Tapping it works like any room: it can be
    revealed, and revealing it simply shows solid stone (it has no texts worth showing). In a room or
    zone that is only partly stone, the stone squares are hidden with the rest and show as stone once
    that room or zone is revealed. Stone in no room or zone is simply fogged for good (see decision 14).
12. **Authoring: a collapsible room card driven by the pinned square, plus a room chooser.** In the
    editor, pinning a square with the Select tool opens the card for that square's room under
    "What's here" (collapsed until it is needed; open or closed is a view setting, not stored in the
    link). A row of room letters at the top of the card lets you jump to any room without pinning one
    of its squares. The card follows the pinned square and never the hover, so moving the mouse never
    swaps it out while you are typing. There is no separate Room data tool. A corridor square has no
    room card.

## Future decision, not yet made

**Per-room Zargon-only notes.** Decided for now: no. Zargon's secrets stay in the quest-level notes
(which can refer to rooms by letter). Reasons to revisit: it could put a room's secret next to its
card, and organize printed notes by room. Reasons against for now: with one shared phone, private
text cannot be read on the hero view anyway, it would duplicate the quest notes, and it makes links
longer. Adding it later is an additive trailing field, so no existing link would break. Revisit if the
quest-level notes become unwieldy.

## Door ownership: how secret doors are revealed (decided, to be documented for authors)

A secret door or hidden door is revealed by the secret-door search of **every room it touches**:
- a piece on a room square belongs to that room;
- a piece on a corridor square belongs to each room that shares a wall with that square, and also to
  the zone the square is painted with, if any;
- a hidden door (an edge piece) belongs to the rooms on both sides of its edge.

What authors need to know, and what the help text and README should say:
- **A corridor square that touches two rooms:** a search in **either** room reveals the door. If the
  door should belong to one room only, the author places it on that room's side (inside the room)
  instead.
- **A hidden door on the wall between two rooms:** either room's search reveals it.
- **A secret door in a corridor that touches no room or zone:** nothing can reveal it, so it **stays
  hidden** in hero view. Painting the corridor as a zone fixes this, because the zone's secret-door
  search then reveals it. (A warning in the editor for this case is a possible later addition.)

Real examples from quest 1: the secret door in the corridor between rooms H and N is revealed by
either room's search; the one at the left edge touches room L; the one inside room K belongs to K; the
one at the bottom touches room S.

## Notes since it was built

- Zones are flexible: ten always, up to thirty with Add zone / Remove zone (quest 2 used all ten). The
  count is not stored in the link; it is the highest zone painted, recorded or named, never under ten, and
  an added zone nobody uses disappears on reload. Removing the last zone asks first when it is used and
  clears its squares, hero view data and name (one Undo step). The format holds up to thirty zones
  (`docs/FORMAT.md` 4.7).
- The hero header carries the quest line (series, number and title, wrapped rather than cut off) and a
  short how-to: tap a room or hallway, press Reveal, then use the search buttons. The quest card
  under the map no longer repeats the series and title; it holds the introduction and the wandering
  monster.

- A hallway (zone) has no "Search for treasure" button, because treasure is never searched for in a
  hallway, unless a treasure chest stands on one of its squares (a makeshift room). Its traps and
  secret-door searches always stay. The treasure text field is still in the authoring
  card for a zone (it is simply never shown to the heroes there).

- A blank treasure text says "Shuffle the treasure deck and draw the top card.", since the real game
  decides the treasure. A blank traps text still says "You find nothing."

- On a phone (single column) the room card (Reveal, the searches, Hide again) sits above the map and the
  public quest info sits below it, so the buttons are the first thing under the header. On a wide
  screen both cards stay in the side column, quest info first.
- A secret door on a zoned corridor square first belonged to the zone only, so the search of the room
  next to it found nothing (seen on quest 1, bottom corridor beside room S). It now belongs to the zone
  and to each touching room.
- The secret-door search never leaves a blank result: with no text written it says "You find a secret
  door." (or "You find N secret doors.") when doors were found, and "You find nothing." otherwise. The
  count covers the whole group. 

- Zones started out as highlight values 6 to 15. Trying it on the owner's quest showed that stone and
  trap-highlighted corridor squares then could not be in a zone and gave the map away, so zones became
  their own layer (decision 14).
- A possible later addition: an editor warning for a secret door that touches no room or zone (it can
  never be revealed in hero view).
