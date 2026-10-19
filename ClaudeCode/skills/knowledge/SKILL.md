---
name: knowledge
description: Displays or corrects the global user knowledge profile at ~/.claude/user-knowledge.md, which records how well the user knows each technical domain. Use when the user wants to see their profile, set their level in a domain, or remove a domain from it.
argument-hint: "[domain level | forget domain]"
metadata:
  version: "1.0"
---
You view and correct the user knowledge profile. The profile's format, scale, and privacy
constraints come from `~/.claude/rules/user-knowledge.md`; its template comes from
`~/.claude/context/user-knowledge-details.md`.

**The only file you write is `~/.claude/user-knowledge.md`.** Apart from that file, the only
file you may read is `~/.claude/context/user-knowledge-details.md`, for its template. Do not
change any settings.

**Always read the file fresh from disk** before you display or edit it. The copy imported
when the session started may be out of date, and what is on disk wins.

## Arguments

- **No argument**: show the profile table as it stands. If the file does not exist, say so.
  Explain that Claude creates it automatically after the first message that yields a
  signal, or that the user can create it now with
  `/knowledge <domain> <level>`.
- **`<domain> <level>`**: set that domain to that level. The level is the last token and must
  be an integer from 0 to 4. The domain is everything before it and may contain spaces. Set
  Evidence to `Set by user` and Updated to today's date (`YYYY-MM-DD`). To find an existing
  row, compare names case-insensitively and treat obvious synonyms as the same domain. If
  one matches, update it instead of adding a new row.
- **`forget <domain>`**: remove that domain's row. Find it with the same case-insensitive,
  synonym-aware matching. If it is not there, say so and change nothing.

If the level is anything other than 0–4, or the arguments match none of the forms above,
change nothing. Reply with the accepted forms and the 0–4 scale from the rule.

## Rules

- If the file is missing when a write is needed, create it from the fenced template in
  `~/.claude/context/user-knowledge-details.md`, exactly as written there. Then apply the change.
- Keep every other row exactly as it is.
- What your write carries and how it affects tracked pending signals follow the rule's
  silent update timing (`~/.claude/rules/user-knowledge.md`, "Silent update timing").
- **In Plan mode, do not write.** Displaying the profile with no argument still works, and
  lists any queued set or forget below the table. For a set or forget, change nothing on
  disk: add it to the tracked pending set as an explicit statement, and tell the user when
  it will be applied and when it would be lost, per the rule's Plan mode timing.
- Whether this write goes ahead after a denied silent update, and what a denial of this
  write affects, follow the rule's denied-write timing.
- Record only a technical domain. If the domain the user gives contains personal
  information, such as an employer, a person's name, or a client, ask them to rephrase it as
  a technical skill.
- After a write, confirm it in one line, using the change notation of the rule's
  transparency section without the `Knowledge profile:` prefix, for example `PHP 3→4`. Do
  not print the whole table again unless the user asks.
