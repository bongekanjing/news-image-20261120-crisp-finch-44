#!/usr/bin/env python3
"""Draw the day's front page and write it to the output directory.

The program composes the image itself from the story list in this file, so the
page is reproducible: identical bytes on every run, with no clock, no network
and no randomness. It writes one PNG the gate accepts: 1024 by 1024, well under
1 MiB.
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

# ---- page geometry --------------------------------------------------------
PAGE = 1024
MARGIN = 25
GUTTER = 14
COLS = 4
COL_W = (PAGE - 2 * MARGIN - (COLS - 1) * GUTTER) // COLS

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

INK = (22, 20, 18)
BODY_INK = (48, 45, 42)
GREY = (92, 88, 82)
RULE = (150, 144, 136)
PAPER = (252, 250, 245)
ACCENT = (140, 30, 24)

_cache = {}


def face(path, size):
    """Load a font once per (file, size) and reuse it."""
    key = (path, size)
    got = _cache.get(key)
    if got is None:
        got = ImageFont.truetype(path, size)
        _cache[key] = got
    return got


def fold(text, f, width):
    """Break text into lines no wider than `width`, on word boundaries."""
    words = text.split()
    if not words:
        return []
    out = []
    line = words[0]
    for word in words[1:]:
        cand = line + " " + word
        if f.getlength(cand) <= width:
            line = cand
        else:
            out.append(line)
            line = word
    out.append(line)
    return out


def height_of(story):
    """The vertical space a story needs. Must match `paint` line for line."""
    head_f = face(SERIF_B, story.get("size", 17))
    body_f = face(SERIF, 10)
    heads = fold(story["head"], head_f, COL_W)
    bodies = fold(story["body"], body_f, COL_W) if story.get("body") else []
    bodies = bodies[:story.get("cap", 99)]
    h = 11                                             # kicker
    h += len(heads) * int(story.get("size", 17) * 1.08) + 4
    h += len(bodies) * 11 + 2
    return h + 6                                       # rule and gap


def paint(d, story, x, y):
    """Draw one story at (x, y) and return the y just below it."""
    size = story.get("size", 17)
    head_f = face(SERIF_B, size)
    body_f = face(SERIF, 10)

    d.text((x, y), story["kick"].upper(), font=face(SANS_B, 9), fill=ACCENT)
    y += 11

    for line in fold(story["head"], head_f, COL_W):
        d.text((x, y), line, font=head_f, fill=INK)
        y += int(size * 1.08)
    y += 4

    if story.get("body"):
        for line in fold(story["body"], body_f, COL_W)[:story.get("cap", 99)]:
            d.text((x, y), line, font=body_f, fill=BODY_INK)
            y += 11
        y += 2

    d.line([(x, y), (x + COL_W, y)], fill=RULE, width=1)
    return y + 6


def under(stories, avail):
    """Trim body copy from the foot of a column until it fits `avail`.

    Every headline stays: a page is judged on how much of the day it carries,
    so when space runs short it is the prose that gives way, last story first.
    """
    work = [dict(s) for s in stories]
    for _ in range(500):
        if sum(height_of(s) for s in work) <= avail:
            break
        for s in reversed(work):
            if s.get("cap", 0) > 0 and s.get("body"):
                s["cap"] -= 1
                if s["cap"] == 0:
                    s["body"] = ""
                break
        else:
            break
    return work


LEAD_KICK = "World Court"
LEAD_HEAD = "ICJ finds Myanmar committed genocide against the Rohingya"
LEAD_DECK = (
    "Judges ruled 9\u20136 that Myanmar broke the 1948 Genocide Convention \u2014 the first time the "
    "court has held a state responsible for genocide. The verdict is final and cannot be appealed; "
    "Myanmar called it \u201cunfair\u201d. In Cox\u2019s Bazar the General Assembly president told "
    "refugees: \u201cYou will not be alone.\u201d"
)

STORIES = [
    {"kick": "Armed conflict", "size": 21,
     "head": "Russian cruise missile lands in Poland during 11-nation drill",
     "body": ("A Kh-101 struck a field at Nowy Lipowiec in Lublin Voivodeship, some 60 miles from a "
              "Coalition of the Willing exercise. Air-raid alerts sounded across Lublin and Podkarpackie. "
              "Warsaw said three Russian objects entered its airspace; NATO called the incursion a "
              "violation and Russia described it as a provocation."),
     "cap": 7},
    {"kick": "Yemen", "size": 19,
     "head": "Coalition jets hit Hodeidah as a tanker burns off Oman",
     "body": ("Saudi-led aircraft targeted smuggling routes used by the Houthis, and sites in Sanaa, "
              "Saada and Taiz. An oil tanker was damaged and caught fire off Khasab while transiting the "
              "Strait of Hormuz. Yemen\u2019s government said 854 operations killed or wounded 193 Houthi "
              "fighters in Al-Jawf, Marib and Taiz."),
     "cap": 7},
    {"kick": "Ukraine", "size": 17,
     "head": "Six killed in Kyiv as Russia fires 400 drones and 110 missiles",
     "body": ("Two bridges were damaged in the overnight barrage. UNICEF said 2026 is Ukraine\u2019s "
              "deadliest year for children, with casualties at record levels as a fifth winter closes in."),
     "cap": 5},
    {"kick": "Nigeria", "size": 15,
     "head": "30 dead and 300 missing as a funeral boat capsizes in Bayelsa",
     "body": "Mourners were travelling by river when the vessel went down in the southern state.",
     "cap": 3},
    {"kick": "Europe", "size": 17,
     "head": "Italy general strike as protests reach 25 countries",
     "body": ("Unions shut transport, schools and health services. Demonstrators denounced stagnant "
              "wages and rising living costs in a coordinated movement expected to run through the "
              "weekend."),
     "cap": 4},
    {"kick": "Diplomacy", "size": 15,
     "head": "Trump floats a Kim meeting after the Shenzhen summit",
     "body": ("Days after meeting Xi Jinping and Vladimir Putin, the US president suggested talks with "
              "North Korea on nuclear disarmament and the Iran war. The Pentagon told Kyiv that deep "
              "drone strikes inside Russia are \u201ccounterproductive\u201d."),
     "cap": 5},
    {"kick": "Brexit", "size": 17,
     "head": "UK and EU sign deals on trade and youth movement",
     "body": ("Andy Burnham met Ant\u00f3nio Costa and Ursula von der Leyen in Brussels, a decade after "
              "the leave vote, pledging to rebuild the relationship."),
     "cap": 4},
    {"kick": "Climate", "size": 17,
     "head": "COP31 draft omits fossil fuels, and activists cry \u201cworst COP ever\u201d",
     "body": ("One delegation said it would not lend its name to \u201ccomplacent or ineffective "
              "language\u201d in a pact needing consensus. Nations also weighed sucking carbon from the "
              "air, at a cost of tens of trillions of dollars."),
     "cap": 5},
    {"kick": "Science", "size": 17,
     "head": "Claimed proof of the Riemann hypothesis, made with Claude",
     "body": ("Anthropic mathematician Levent Alp\u00f6ge released the proof, developed with AI "
              "assistance. If it holds it settles a 167-year-old question about how the primes are "
              "distributed."),
     "cap": 4},
    {"kick": "Markets", "size": 15,
     "head": "Anthropic\u2019s debut is the largest public offering on record",
     "body": ("Shares surged despite investor fears of an AI bubble and public unease over the "
              "technology\u2019s toll on work."),
     "cap": 3},
    {"kick": "Arctic", "size": 15,
     "head": "Denmark backs a US security deal over Greenland",
     "body": ("Parliament approved an accord letting Washington expand its military presence while "
              "Greenland stays under Danish sovereignty, after months of tension over Trump\u2019s bid "
              "to buy the island."),
     "cap": 5},
    {"kick": "NATO", "size": 13,
     "head": "11 nations rehearse a postwar Ukraine mission in Poland",
     "body": ("Thousands of troops practised anti-drone defence and trench warfare after a year of "
              "planning by the 37-nation coalition."),
     "cap": 3},
    {"kick": "Iraq", "size": 13,
     "head": "Baghdad and Kata\u2019ib Hezbollah agree a joint operations centre",
     "body": ("PM Ali al-Zaidi said troops will be stationed at Jurf al-Sakhar, south of the capital, "
              "after threatening to move security forces into the group\u2019s stronghold."),
     "cap": 4},
    {"kick": "Haiti", "size": 13,
     "head": "Three Salvadoran soldiers killed handling explosives",
     "body": ("San Salvador\u2019s first official deaths since it deployed. Haiti and El Salvador "
              "agreed to build three new prisons for gang members."),
     "cap": 3},
    {"kick": "West Bank", "size": 13,
     "head": "Settler attacks on the olive harvest reach a record 400",
     "body": ("UN agencies and aid groups recorded more casualties and property damage this season "
              "than in any previous year."),
     "cap": 3},
    {"kick": "Geneva", "size": 13,
     "head": "Russia stalls UN talks on weapons that pick their own targets",
     "body": ("Negotiators pledged more talks toward rules within two years; campaigners warned of an "
              "\u201cOppenheimer moment\u201d."),
     "cap": 3},
    {"kick": "India", "size": 13,
     "head": "130 million names cut from the electoral rolls",
     "body": ("The Gen Z movement that forced out the education minister now demands the deletions be "
              "reversed."),
     "cap": 3},
    {"kick": "Spain", "size": 13,
     "head": "Data centres ordered to draw 80% of power from renewables",
     "body": "Madrid tightened rules on efficiency and digital sovereignty to ease strain on the grid.",
     "cap": 2},
    {"kick": "Brussels", "size": 13,
     "head": "Commission releases \u20ac10bn of Hungary\u2019s recovery funds",
     "body": "Budapest has met all but one condition after rule-of-law reforms.",
     "cap": 2},
    {"kick": "France", "size": 13,
     "head": "Le Pen\u2019s party probed over leaked inquiry files",
     "body": ("A former senior Interior Ministry official is suspected of passing details of "
              "campaign-finance investigations to the National Rally."),
     "cap": 3},
    {"kick": "Brazil", "size": 13,
     "head": "Isolated Aw\u00e1 make contact in the Amazon",
     "body": ("About 20 members of the uncontacted group approached a government outpost asking for "
              "yams, then went back to the forest."),
     "cap": 3},
    {"kick": "Barbados", "size": 13,
     "head": "Guterres convenes an AI-safety summit for Monday",
     "body": ("The meeting aims to close the gap between fast-rising risks and most countries\u2019 "
              "capacity to answer them."),
     "cap": 3},
    {"kick": "Obituary", "size": 13,
     "head": "Phumzile Mlambo-Ngcuka, UN Women chief, dies at 71",
     "body": "South Africa\u2019s former deputy president led UN Women from 2013 to 2021.",
     "cap": 2},
    {"kick": "India", "size": 15,
     "head": "Cyclone Akvan makes landfall on the eastern coast",
     "body": ("The storm came ashore after days of preparation and evacuation along the Bay of Bengal "
              "littoral."),
     "cap": 3},
    {"kick": "Horn of Africa", "size": 15,
     "head": "Somalia orders the UAE ambassador out within 72 hours",
     "body": ("Mogadishu recalled its own envoy from Abu Dhabi and accused the Emirates of interfering "
              "through unauthorised military arrangements, support for armed groups and port deals "
              "struck with regional administrations. Somaliland rejected Somalia\u2019s claim to speak "
              "for its foreign affairs."),
     "cap": 6},
    {"kick": "Kenya", "size": 13,
     "head": "US consortium wins a $60bn critical-minerals tender",
     "body": ("Frontier Minerals took Mrima Hill, estimated to hold more than $60 billion in niobium "
              "and other minerals, and plans refining inside Kenya. Two rival bidders are preparing "
              "challenges, and local communities fear damage to ancestral land."),
     "cap": 5},
    {"kick": "Senegal", "size": 13,
     "head": "Dozens missing as a migrant boat capsizes off Yenne",
     "body": ("Four bodies were recovered from a vessel carrying an estimated 50 to 100 people, less "
              "than two weeks after another wreck killed at least 39."),
     "cap": 4},
    {"kick": "Children", "size": 15,
     "head": "One child in four now lives within reach of armed conflict",
     "body": ("Save the Children put the global figure at a record 589 million. In Africa about 260 "
              "million children \u2014 two in five \u2014 lived within 50km of fighting in 2025, up "
              "nearly a fifth on the year. The UN verified 38,967 grave violations, among them more "
              "than 14,000 children killed or maimed and 5,128 abducted."),
     "cap": 6},
    {"kick": "Humanitarian", "size": 13,
     "head": "WFP says it needs $12.1bn to reach 91 million people",
     "body": ("The agency warned that funding shortfalls will leave millions more hungry as another "
              "global food crisis gathers."),
     "cap": 3},
    {"kick": "Afghanistan", "size": 13,
     "head": "Restrictions bar pregnant women from medical care",
     "body": ("Aid agencies described an escalating \u201cassault\u201d on the rights of women and "
              "girls that is keeping growing numbers from treatment."),
     "cap": 3},
    {"kick": "Costa Rica", "size": 13,
     "head": "Journalist Camilo Rodr\u00edguez assassinated",
     "body": "The killing has shaken a country long regarded as one of the region\u2019s safest.",
     "cap": 2},
    {"kick": "Southern Africa", "size": 13,
     "head": "Criminal probe sought into R218m of arms sold to Myanmar",
     "body": ("The Southern Africa Litigation Centre wants South Africa\u2019s 2017\u20132021 "
              "authorisations investigated after the ICJ found Myanmar committed genocide."),
     "cap": 4},
    {"kick": "Zimbabwe", "size": 13,
     "head": "Security ministries take ZWG59.5bn of the 2027 budget",
     "body": ("Defence, Home Affairs and the President\u2019s Office took the largest shares while "
              "agriculture faces an El Ni\u00f1o drought; the deficit is projected at ZWG3.2 billion."),
     "cap": 4},
    {"kick": "East Africa", "size": 13,
     "head": "Ethiopia and Eritrea mass troops on their border",
     "body": "Conflict monitors reported the build-up; Asmara denies it.",
     "cap": 2},
    {"kick": "Health", "size": 13,
     "head": "Cleft surgery, one of medicine\u2019s easiest fixes, still goes undone",
     "body": ("Across Africa families are told a cleft lip is a curse. An early operation lets a child "
              "eat, speak and grow up."),
     "cap": 3},
]


def masthead(d):
    """The top bar, the title and the dateline. Returns the first usable y."""
    d.rectangle([0, 0, PAGE, 17], fill=INK)
    bar = face(SANS_B, 8)
    right = "WORLD EDITION  \u00b7  %d STORIES  \u00b7  EVERY REGION" % len(STORIES)
    d.text((MARGIN, 5), "FRIDAY 20 NOVEMBER 2026", font=bar, fill=PAPER)
    d.text((PAGE - MARGIN - bar.getlength(right), 5), right, font=bar, fill=PAPER)

    y = 24
    title = face(SERIF_B, 58)
    name = "THE WORLD TODAY"
    d.text(((PAGE - title.getlength(name)) / 2, y), name, font=title, fill=PAPER and INK)
    y += 66

    d.line([(MARGIN, y), (PAGE - MARGIN, y)], fill=INK, width=3)
    y += 4
    d.line([(MARGIN, y), (PAGE - MARGIN, y)], fill=INK, width=1)
    y += 5

    tag = face(SANS, 9)
    motto = "THE DAY'S NEWS FROM EVERY REGION, ON ONE PAGE"
    d.text(((PAGE - tag.getlength(motto)) / 2, y), motto, font=tag, fill=GREY)
    return y + 14


def lead(d, y):
    """The full-width lead story. Returns the y below its deck."""
    head_f = face(SERIF_B, 40)
    deck_f = face(SERIF_I, 13)

    d.text((MARGIN, y), LEAD_KICK.upper(), font=face(SANS_B, 10), fill=ACCENT)
    y += 14
    for line in fold(LEAD_HEAD, head_f, PAGE - 2 * MARGIN):
        d.text((MARGIN, y), line, font=head_f, fill=INK)
        y += 45
    y += 2

    # the deck reads as two balanced halves, like a real standfirst
    deck_w = (PAGE - 2 * MARGIN - GUTTER) // 2
    lines = fold(LEAD_DECK, deck_f, deck_w)
    half = (len(lines) + 1) // 2
    for i, line in enumerate(lines):
        col, row = (0, i) if i < half else (1, i - half)
        d.text((MARGIN + col * (deck_w + GUTTER), y + row * 16), line, font=deck_f, fill=(60, 56, 52))
    y += half * 16 + 6

    d.line([(MARGIN, y), (PAGE - MARGIN, y)], fill=INK, width=1)
    y += 4
    d.line([(MARGIN, y), (PAGE - MARGIN, y)], fill=RULE, width=1)
    return y + 10


def main():
    page = Image.new("RGB", (PAGE, PAGE), PAPER)
    d = ImageDraw.Draw(page)

    top = lead(d, masthead(d))
    floor = PAGE - 22
    avail = floor - top

    # Fill the shortest column next, biggest story first: that keeps the four
    # columns level without needing to know the heights in advance.
    order = sorted(range(len(STORIES)), key=lambda i: -STORIES[i].get("size", 15))
    columns = [[] for _ in range(COLS)]
    load = [0] * COLS
    for i in order:
        shortest = min(range(COLS), key=lambda c: load[c])
        columns[shortest].append(i)
        load[shortest] += height_of(STORIES[i])

    xs = [MARGIN + c * (COL_W + GUTTER) for c in range(COLS)]
    for c, items in enumerate(columns):
        y = top
        for story in under([STORIES[i] for i in items], avail):
            y = paint(d, story, xs[c], y)
        if c:
            d.line([(xs[c] - GUTTER // 2, top), (xs[c] - GUTTER // 2, floor)], fill=RULE, width=1)

    d.line([(MARGIN, PAGE - 18), (PAGE - MARGIN, PAGE - 18)], fill=INK, width=2)
    d.text((MARGIN, PAGE - 14),
           "THE WORLD TODAY  \u00b7  20 NOVEMBER 2026  \u00b7  COMPILED FROM WIRE AND COURT REPORTS",
           font=face(SANS, 8), fill=GREY)

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.png")
    page.save(target, "PNG", optimize=True)
    print("wrote %s: %dx%d, %d bytes" % (target, PAGE, PAGE, os.path.getsize(target)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
