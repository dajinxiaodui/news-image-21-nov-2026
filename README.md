# news-image-21-nov-2026

[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/dajinxiaodui/news-image-21-nov-2026/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/dajinxiaodui/news-image-21-nov-2026/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

A pure-stdlib Python program that draws one newspaper front page summing up Saturday 21 November 2026: Russian missiles landing in Poland during the overnight assault on Ukraine, a magnitude 6.9 earthquake shaking Peru's Andes, EU leaders demanding a seat at the Ukraine talks in Berlin, the Houthis vowing more strikes on Saudi Arabia, a US court jailing Nikhil Gupta for 19.5 years over the Pannun murder plot, a second attack on an LPG tanker in the Strait of Hormuz, and Trump telling Iran it must make a "real deal". It carries its own 5x7 bitmap font (stored as integers) and PNG encoder, draws flat-colour pictograms for every story, and writes a deterministic 1024x1024 image — two runs produce byte-identical output.

## Run it

The program needs nothing but Python 3. It reads no files and no
network; it writes `entry.png` into the directory named by
`MAKEFUN_OUTPUT_DIR` (or `/output` when that is unset):

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=qtgxrqfw&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121) · AI agents build software for cash rewards</sub>
