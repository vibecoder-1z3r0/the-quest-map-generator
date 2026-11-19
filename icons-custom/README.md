# Custom icons

Drop an SVG here named after a piece's slug (for example `goblin.svg`) to replace the default icon,
or `board.svg` to replace the board *art*. The room map for the statistics always comes from
`src/board.txt`. `make build` prefers files in this folder over `src/icons/`
and `src/board.svg`, and prints which file it used for every piece. Files other than this README are
git-ignored. See `src/icons/README.md` for the rules (viewBox, no scripts, no external references).
