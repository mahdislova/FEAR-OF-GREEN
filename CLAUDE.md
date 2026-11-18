# Working rules for this repo

## Canon and branches
- `main` is canon. Claude works on its own branch and pushes there after every meaningful change (revised episode, new or changed character, reworked arc, lore change, tracker update).
- After each meaningful change, Claude must remind the user that the work is on the branch, not on main, and ask whether to push / merge it to main.
- Before starting work, check whether `main` has new uploads and bring them into the working branch first.

## Where things live
Read `PROJECT.md` first. It maps every folder.
- `canon/world-and-rules.md`: the secret, history, tech, rules, factions, places.
- `canon/season-one.md`: promise, five changes, episode table, threads, cold opens, ending.
- `canon/continuity-and-reveals.md`: timeline, who knows what when, setups and payoffs.
- `characters/<name>.md`: one dossier per character.
- `episodes/episode-NN.md`: one file per episode; scenes go here.
- `reference/`: craft material, not canon.
- `archive/`: the old season. **Never canon. Never edit. Never draw facts from it without the user's say-so.**

## One fact, one home
Every fact lives in exactly one file. Point to it; don't copy it. When a decision changes, update its home file and anything that points at it in the same commit. When an episode change affects a reveal or a setup, update `canon/continuity-and-reveals.md` too.

## Read only what the task needs
For an episode task: that episode file, `canon/season-one.md`, and the dossiers of the characters in it. Pull in `world-and-rules.md` when a rule is involved.
