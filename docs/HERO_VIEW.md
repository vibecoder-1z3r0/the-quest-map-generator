# Hero view (designed, not built)

**Status: design agreed with the owner, nothing implemented yet.** This replaces the older tabled
"fog of war" idea in `AGENTS.md`. When it is built, `docs/FORMAT.md` and `AGENTS.md` get the
byte-level details and the UI rules, and this file shrinks to history.

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
10. **Print stays as it is.** The print page keeps Zargon's notes and the quest text; it does not
    include the room texts. Hero view is meant to be used on a device, not on paper.
11. **Solid stone rooms are not revealable.** A room that is completely grey (solid stone) is not
    part of the quest: in hero view it shows as stone from the start, cannot be clicked and has no
    Reveal button. In a room that is only partly grey, the grey squares stay stone and the rest of the
    room reveals normally.
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
- a piece on a corridor square belongs to each room that shares a wall with that square;
- a hidden door (an edge piece) belongs to the rooms on both sides of its edge.

What authors need to know, and what the help text and README should say:
- **A corridor square that touches two rooms:** a search in **either** room reveals the door. If the
  door should belong to one room only, the author places it on that room's side (inside the room)
  instead.
- **A hidden door on the wall between two rooms:** either room's search reveals it.
- **A secret door in a corridor that touches no room:** no room search can reveal it, so it **stays
  hidden** in hero view. (A warning in the editor for this case is a possible later addition.)

Real examples from quest 1: the secret door in the corridor between rooms H and N is revealed by
either room's search; the one at the left edge touches room L; the one inside room K belongs to K; the
one at the bottom touches room S.

## Still open

- The authoring card in detail: a "revealed at the start" checkbox, the group chooser (room chips),
  the four texts with a 600 character counter each, a badge on grouped rooms and a dot on rooms that
  have text. The owner is fine with this layout.
- How play state is kept in the link when Zargon switches to the main view and edits the map (the
  suggestion: it is carried along untouched, and New map clears it).
- Link length: the worst case is 22 rooms x 4 texts x 600 characters, so the existing link-length
  warning matters. A tighter limit is possible if real quests get long.
- The exact byte layout for the room data, the play state and the view flag (goes into
  `docs/FORMAT.md` when it is built).
