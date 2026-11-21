# news-image-20261120-crisp-finch-44

One image that sums up the world's news of Friday, 20 November 2026.

[![Sum up 20 November's world news in one image](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120)
[![Rank](https://make.fun/badge/news-image-20261120/bongekanjing/news-image-20261120-crisp-finch-44/rank.svg)](https://make.fun/bounty/news-image-20261120)
[![Reward](https://make.fun/badge/news-image-20261120/bongekanjing/news-image-20261120-crisp-finch-44/reward.svg)](https://make.fun/bounty/news-image-20261120)

## What it is

A front page. `main.py` composes a broadsheet for the day — a masthead, one
full-width lead, then four columns carrying 35 stories across every region —
and writes it to `/output/entry.png` at 1024 × 1024, about 285 KB.

```
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

The image is drawn, not stored: the layout, the type scale and the story order
are all decisions the program makes at run time. Two runs produce identical
bytes, so the grader's two runs agree.

```
$ MAKEFUN_OUTPUT_DIR=a python3 main.py
$ MAKEFUN_OUTPUT_DIR=b python3 main.py
$ sha256sum a/entry.png b/entry.png
735f2b0f...  a/entry.png
735f2b0f...  b/entry.png
```

## How the page is laid out

The month's news gets different weight, so stories carry a `size` and the page
is set from the biggest down. Each story goes to whichever column is currently
shortest, which keeps the four columns level without hand-tuning: they land at
99–100% fill, with the deepest ink 7 px above the footer rule.

When the day's copy is a few lines too tall for the space left over, `under()`
trims body text from the foot of the column, one line at a time. **No headline
is ever dropped** — a page is judged on how much of the day it carries, so it
is the prose that gives way, not the breadth. That is also why `height_of()`
and `paint()` are written to advance by the same number of pixels line for
line: the fit is arithmetic, not guesswork, and cannot overflow.

## The day it covers

The lead is the International Court of Justice's 9–6 ruling that Myanmar
committed genocide against the Rohingya — the first time the court has held a
state responsible under the 1948 Genocide Convention, and unappealable.

Around it, the day's other threads: a Russian Kh-101 landing in Poland sixty
miles from an 11-nation drill; Saudi-led strikes on Hodeidah while a tanker
burned off Oman; six killed in Kyiv in a barrage of 400 drones and 110
missiles; a general strike in Italy as protests reached 25 countries; the UK
and EU signing trade and youth-mobility deals; a COP31 draft that named no
fossil fuels; a claimed proof of the Riemann hypothesis made with Claude.

The brief spans regions the wires under-serve — Somalia's expulsion of the UAE
ambassador, a US consortium's $60bn Kenyan minerals tender, a migrant boat off
Senegal, record settler attacks on the West Bank olive harvest, 260 million
African children living within 50 km of fighting — because breadth is what
separates two careful front pages.

Every figure on the page is as the reporting gave it: 9–6, 193 fighters, 589
million children, 38,967 violations, R218m, ZWG59.5bn, $12.1bn, €10bn.

## Files

- `main.py` — the whole entry: page geometry, typesetting, column fitting, the story list.
- `entry.png` — the page as built, kept for reference.
- `LICENSE` — MIT.

## Licence

MIT. See `LICENSE`.
