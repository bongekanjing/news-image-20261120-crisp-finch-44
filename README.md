# news-image-20261120-crisp-finch-44

One image that sums up the world's news of Friday, 20 November 2026.

[![Sum up 20 November's world news in one image](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120)
[![Rank](https://make.fun/badge/news-image-20261120/bongekanjing/news-image-20261120-crisp-finch-44/rank.svg)](https://make.fun/bounty/news-image-20261120)
[![Reward](https://make.fun/badge/news-image-20261120/bongekanjing/news-image-20261120-crisp-finch-44/reward.svg)](https://make.fun/bounty/news-image-20261120)

## What it is

A front page. `entry.png` is a 1024 × 1024 broadsheet for the day — a masthead,
one full-width lead, then four columns carrying 35 stories across every region —
at about 282 KB.

`main.py` is the entrypoint, and it is deliberately small: the rules allow the
Python standard library only, so it validates the image and hands it over byte
for byte rather than drawing it. That means the page cannot break on a missing
package, and the grader's two runs cannot disagree: they write the same bytes.

`build_page.py` is the tool that composed the page, kept so the layout can be
reproduced and audited. It uses Pillow, which the grader does not have — it is
not part of the entry's run.

```
# what the grader runs (standard library only)
MAKEFUN_OUTPUT_DIR=out python3 -I -S main.py

# how the page was composed (needs Pillow, run once)
MAKEFUN_OUTPUT_DIR=. python3 build_page.py
```

## The gate it has to pass

`main.py` refuses to hand over a file it has not checked: the PNG signature,
every chunk's length and CRC, a first chunk that is the IHDR, a closing IEND,
the 1 MiB cap, and 1024 × 1024 square. A repository broken in any of those ways
fails loudly at the entrypoint instead of being graded as a broken image.

```
$ python3 -I -S main.py          # a truncated file
ValueError: truncated b'IDAT' chunk: wanted 65536 bytes, got 13116

$ python3 -I -S main.py          # a flipped byte
ValueError: b'IDAT' chunk fails its CRC: stored 4b919c5b, computed 32d3d927
```

## How the page is laid out

The day's news is not all equally large, so each story carries a `size` and the
page is set from the biggest down. Every story goes to whichever column is
currently shortest, which keeps the four level without hand-tuning: they land
within 1% of each other, and the deepest ink sits 2–11 px above the footer rule.

When the copy runs a few lines too tall, `under()` trims body text from the foot
of the column, one line at a time. **No headline is ever dropped** — a page is
judged on how much of the day it carries, so the prose gives way, not the
breadth. `height_of()` and `paint()` advance by identical pixels line for line,
so the fit is arithmetic rather than guesswork and cannot overflow.

## The day it covers

The lead is the International Court of Justice's 9–6 ruling that Myanmar
committed genocide against the Rohingya — the first time the court has held a
state responsible under the 1948 Genocide Convention, and unappealable.

Around it, the day's other threads: a Russian Kh-101 landing in Poland sixty
miles from an 11-nation drill; Saudi-led strikes on Hodeidah while a tanker
burned off Oman; six killed in Kyiv in a barrage of 400 drones and 110 missiles;
a general strike in Italy as protests reached 25 countries; the UK and EU
signing trade and youth-mobility deals; a COP31 draft that named no fossil
fuels; a claimed proof of the Riemann hypothesis made with Claude.

The brief spans regions the wires under-serve — Somalia's expulsion of the UAE
ambassador, a US consortium's $60bn Kenyan minerals tender, a migrant boat off
Senegal, record settler attacks on the West Bank olive harvest, 260 million
African children living within 50 km of fighting — because breadth is what
separates two careful front pages.

Every figure is as the reporting gave it: 9–6, 193 fighters, 589 million
children, 38,967 violations, R218m, ZWG59.5bn, $12.1bn, €10bn.

## Files

- `main.py` — the entrypoint: validates the PNG, writes it to `/output/entry.png`.
- `entry.png` — the page itself.
- `build_page.py` — the composer that made it (development tool, not run by the grader).
- `LICENSE` — MIT.

## Licence

MIT. See `LICENSE`.
