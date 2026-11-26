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
   Markers and Zargon's colored highlights always stay hidden. Solid stone always shows.
5. **Search buttons are always there**, even when the room has nothing to find, so a button never
   gives anything away. Once a search is done its result stays shown.
   - **Search for treasure** shows the room's treasure text (a hero-facing field, not private).
   - **Search for traps** shows the room's traps text only. No trap pieces are revealed.
   - **Search for secret doors** shows the room's secret doors text and reveals the secret doors in
     the room and on the outside of its walls.
6. **Merged rooms: the author chooses.** Rooms are not grouped automatically from room tiles. The
   author marks which rooms reveal together, and a group reveals as one.
7. **Room texts: four per room**, each up to **600 characters**: read aloud (on reveal), treasure,
   traps, secret doors. A room with an empty field simply has nothing to show for it.
8. **Quest-level text in hero view:** series, number, title, intro and the wandering monster are
   shown. Zargon's secret notes are not.

## Future decision, not yet made

**Per-room Zargon-only notes.** Decided for now: no. Zargon's secrets stay in the quest-level notes
(which can refer to rooms by letter). Reasons to revisit: it could put a room's secret next to its
card, and organize printed notes by room. Reasons against for now: with one shared phone, private
text cannot be read on the hero view anyway, it would duplicate the quest notes, and it makes links
longer. Adding it later is an additive trailing field, so no existing link would break. Revisit if the
quest-level notes become unwieldy.

## Still open (assumptions to confirm, and details)

- Assumed, not yet confirmed: hidden doors (the edge pieces) are revealed together with secret doors
  by the secret-door search; markers always stay hidden; non-grey highlights always stay hidden.
- Which room's texts a merged group uses (each room's own texts in turn, or one set for the group).
- Exactly which door pieces count as being "on the outside of the room walls".
- How play state interacts with Undo and the browser's back button, and what it looks like in the
  editor (probably it is ignored there).
- The authoring screens: a Room tool and a room card in the editor, and how rooms are grouped.
- Whether the print page should include the room texts.
- Link length: worst case is 22 rooms x 4 texts x 600 characters, so the existing link-length warning
  matters. A tighter limit is possible if real quests get long.
