# Quest Map Generator

A browser-only HeroQuest-style quest map editor. Open `index.html` (or host it anywhere static).

The entire map – floor, walls, doors, secret doors, furniture, monsters, traps, quest number, title,
intro and Zargon's secret notes – is encoded in the URL **hash**. Nothing is saved or sent anywhere;
copy the link and anyone opening it sees the same map. The hash updates live as you edit.

- Paint floor and walls are drawn automatically around it; click near a square edge to place doors.
- `R` rotates, `Del` removes the selected item, browser back/forward steps through edits.
- Format: 26×19 grid, bit-packed, deflate-compressed, base64url, with a version byte (see `index.html`).
