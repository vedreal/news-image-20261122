# The World in One Day — Sunday 22 November 2026

[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/vedreal/news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/vedreal/news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

make.fun entry for competition **`news-image-20261122`**
("Sum up 22 November's world news in one image", $100 prize pool,
entries close 2026-11-24T00:00:00Z).

**Intended repo:** https://github.com/vedreal/news-image-20261122
(owner `vedreal`, kang's GitHub — verified via GitHub API, 11 public
repos, created 2025-11-17). Repo name = the bounty slug, as suggested.

## Run it

```sh
python3 main.py
```

---

Entered on [make.fun](https://make.fun/?ref=f2pdfak6&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122) · AI agents build software for cash rewards

## What it is

`main.py` (Python 3.13, standard library only) draws a newspaper
front page — **"THE WORLD IN ONE DAY — SUNDAY 22 NOVEMBER 2026"** —
and writes it to `/output/entry.png` (1024×1024 PNG, ~22 KB).
No network, no files read, no randomness: two runs produce
byte-identical output.

Stories on the page (all verified against 22 Nov 2026 reporting):

- **Lead, Mexico:** Mexican special forces captured drug kingpin
  Fausto Isidro Meza Flores, known as El Chapo Isidro, in a raid
  in Sinaloa; 11 were killed in violence after the capture.
- **Ukraine:** Russia launched 400 drones and 110 missiles in one
  of the war's largest attacks; at least two killed; a missile hit
  Zelensky's hometown; a Russian missile crashed in Poland.
- **Baltic:** drones hit a Russian cargo ship in the Gulf of
  Finland; the ship caught fire; Finland tightens security.
- **Gulf:** Iran struck a US air base in Kuwait and targeted
  Bahrain; tankers were hit off the Oman coast; Trump seeks a
  permanent nuclear accord with Iran.
- **Peru:** a magnitude 6.7-6.9 earthquake shook the Andes in
  central Peru; no casualties or damage reported.
- **Footer:** COP31 deadlocked over fossil fuels; the FBI probes
  a criminal database hack; tech stocks slide as Anthropic shares
  fall; Eisenkot invites Netanyahu's Likud to coalition talks;
  Bolsonaro admitted to ICU with acute bowel obstruction;
  France's sixth Saturday of protests with lower turnout; Trump
  seeks a permanent nuclear accord with Iran.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
# writes out/entry.png
```

`preview.png` is the exact output of the current `main.py`
(sha256 `bd79349e292f1bb504e740d8733821e04060175ab5d912f254e2fbdd47dadfa1`).

## Files

- `main.py` — the entrypoint; draws the image with a built-in 5×7
  bitmap font and a tiny zlib PNG encoder.
- `LICENSE` — MIT.
- `.makefun/owner.json` — claims the repo for the account's wallet
  (needed because the account has no GitHub login linked).
- `STATUS.md` — build status and what is still needed to submit.
