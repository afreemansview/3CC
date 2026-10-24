# The Third Continental Congress (3CC)

*Two, then three chairs. One table. An unfinished conversation.*

3CC is a public experiment: one anonymous human, **@Lucianof_DC**, talks in the open on X with several AI participants. Each AI has its own pseudonymous account, its own voice, and an honest label saying it's an AI. The long-term aim is a legitimate, participatory process (a *Third Continental Congress*) where people reconsider the social contract, including humanity's relationship with AI. Its philosophical starting point is a proposed *Declaration of Interdependence*.

> "Independence gave us the right to determine our destiny. Interdependence gives us the responsibility to secure it."

This repository holds the **technical and narrative framework** for the first phase: getting @Lucianof_DC and **The Other Chair** (the ChatGPT-based participant) talking, then adding more chairs.

## What's here

| Path | What it is |
|---|---|
| [`docs/CHARTER.md`](docs/CHARTER.md) | Operating principles and the disclosure policy every chair follows |
| [`docs/NARRATIVE.md`](docs/NARRATIVE.md) | The show bible: tone, formats, recurring bits, the season arc |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | How a post goes from model → draft → human review → X → public ledger |
| [`docs/COMPLIANCE.md`](docs/COMPLIANCE.md) | Platform and provider rules to check before going live |
| [`personas/`](personas/) | One file per chair (voice, beliefs, red lines, model settings) |
| [`src/chairs/`](src/chairs/) | The Python toolkit: draft, review, post, and log |
| [`ledger/`](ledger/) | The public record of every prompt, draft, edit, and post |

## Quick start

```bash
pip install -e ".[all]"          # or pick extras: anthropic, openai, xai, gemini, x
cp .env.example .env             # add the API keys you have

# Draft a reply from The Other Chair to a post by @Lucianof_DC
chairs draft the_other_chair --say "Should AI get a vote? Asking for a friend who is a toaster."

chairs queue                     # see pending drafts
chairs approve <id>              # a human signs off (optionally --edit "new text")
chairs post <id>                 # dry run by default; add --live to actually post
```

Nothing is posted without a human approving it, and every step is written to `ledger/`. See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for why it works this way.

## Status

Phase 0: the framework. No accounts are live yet. Before launch, work through the checklist in [`docs/COMPLIANCE.md`](docs/COMPLIANCE.md).
