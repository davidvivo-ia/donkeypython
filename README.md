# 🫏 DONKEY.PY — DONKEY.BAS Remake in Python

> **The legendary IBM PC DOS game from 1981, rewritten in Python + Pygame.**
> DONKEY.BAS was the first game ever shipped with the IBM Personal Computer, written by **Bill Gates** and **Neil Konzen** at 4 AM in a locked closet. Now runs on your modern machine.

[
[
[
[
[

***

## 🕹️ What is DONKEY.BAS?

**DONKEY.BAS** is the first video game ever included with the **IBM Personal Computer (PC DOS 1.00, 1981)**.
It was written by **Bill Gates** (Microsoft co-founder) and **Neil Konzen** during an all-night session
in a tiny locked closet at IBM — the only room with a lock they could use.

> *"It was myself and Neil Konzen at four in the morning with this prototype IBM PC…  
> we wrote late at night a little application to show what the BASIC built into the IBM PC could do.  
> And so that was DONKEY.BAS. It was, at the time, very thrilling."*
> — **Bill Gates**, TechEd 2001 Keynote

The Apple Macintosh team famously called it *"the most embarrassing game"* when they first saw an IBM PC —
and were shocked to discover Bill Gates had put his name on it.

**This project is a faithful Python remake** of that legendary game, using `pygame` and modern Python idioms.

***

## 🎮 Gameplay

You drive a car down a two-lane road. A donkey randomly appears in one of the lanes and moves toward you.

- **Press `SPACE`** to switch lanes and avoid the donkey
- If you **hit the donkey** → `BOOM!` → Donkey scores a point
- If the **donkey passes you** without collision → `Donkey loses!` → Driver scores a point
- Your car slowly **creeps upward** — the closer you are to the top, the less reaction time you have
- The donkey gets **faster** as your score increases (up to 8× speed)

> Original mechanic preserved: the only input is a **single key** (spacebar), exactly as in the 1981 BASIC version.

***

## ✨ Features

| Feature | Original DONKEY.BAS (1981) | This Python Remake |
|---|---|---|
| Language | IBM BASIC (GW-BASIC / BASICA) | Python 3 + Pygame |
| Graphics | CGA 4-color mode (320×200) | 640×480 with CGA palette |
| Sprites | Block pixel art | Vector shapes (no external files) |
| Controls | Spacebar only | Spacebar + ESC |
| Sound | PC speaker BEEP | *(optional, extensible)* |
| Difficulty | Fixed speed | Progressive (×1 to ×8) |
| Explosion | Pieces fly to corners | Particle system |
| Platform | MS-DOS / PC DOS | Windows, macOS, Linux |
| Title screen | IBM box-drawing characters | Faithful recreation |

***

## 📦 Installation

### Requirements

- Python 3.8 or higher
- pygame 2.x

### Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/donkey-py.git
cd donkey-py

# 2. Install dependencies
pip install pygame

# 3. Run the game
python donkey.py
```

No extra assets needed — all sprites are drawn with pure Pygame code.

***

## 🎯 Controls

| Key | Action |
|---|---|
| `SPACE` | Switch lane / Start game from title screen |
| `ESC` | Exit the game |

***

## 🏗️ Project Structure

```
donkey-py/
│
├── donkey.py          # Main game file (single file, zero dependencies beyond pygame)
├── README.md          # This file
└── LICENSE            # MIT License
```

The entire game fits in a single file (`donkey.py`) following the spirit of the original BASIC program.

***

## 🧱 Technical Architecture

The game uses a clean **finite state machine** pattern:

```
TITLE ──[SPACE]──▶ PLAYING
                      │
               [collision]──▶ BOOM (2s) ──▶ PLAYING
                      │
               [donkey passes]──▶ MISS (1.5s) ──▶ PLAYING
```

### Key classes

| Class | Responsibility |
|---|---|
| `DonkeyGame` | Main loop, state machine, event handling |
| `Car` | Player entity — lane switching, smooth interpolation |
| `Donkey` | Enemy entity — random lane, progressive speed |
| `Renderer` | All drawing logic isolated from game logic |
| `GameState` | Enum: `TITLE`, `PLAYING`, `BOOM`, `MISS` |

### Design principles applied

- **`@dataclass`** for `Car` and `Donkey` entities
- **`Enum`** for game states — no magic integers or booleans
- **Delta-time movement** (`dt`) — frame-rate independent physics
- **Pure-code sprites** — `make_car_surface()` and `make_donkey_surface()` draw to `pygame.Surface` without image files
- **Particle system** — `make_explosion_particles()` for the BOOM! effect
- **PEP 484 type hints** throughout
- **`if __name__ == "__main__":` guard** for clean imports

***

## 📖 Historical Context

### The IBM PC and DONKEY.BAS (1981)

DONKEY.BAS shipped with **PC DOS 1.00** in August 1981, bundled inside `BASIC.COM` on the original
**IBM Personal Computer Model 5150**. It was designed to demonstrate the CGA graphics adapter's
ability to render color graphics and to show off the BASIC interpreter Microsoft had licensed to IBM.

The game runs in **CGA Palette 1** (cyan, magenta, white, black) — the only color graphics mode
available on the original IBM PC hardware.

### Why it matters

- First commercial PC game in history to ship preinstalled with an IBM personal computer
- Directly tied to the founding story of Microsoft's dominance of the PC market
- The `.BAS` extension simply denotes it was written in BASIC — all BASIC programs used it
- Version 1.10 (the version in this repo's source reference) fixed minor bugs from 1.00
- Apple's Macintosh team cited it as evidence that IBM's PC was technically inferior

### Original authors

- **Bill Gates** — Microsoft co-founder, later CEO and Chairman
- **Neil Konzen** — Early Microsoft employee, later worked on the original Macintosh port of Microsoft software

***

## 🔗 Related Resources

- 📺 [DONKEY.BAS running in PCjs browser emulator](https://www.pcjs.org/software/pcx86/app/ibm/basic/1.00/donkey/) — play the original in your browser
- 📖 [DONKEY.BAS — Wikipedia](https://en.wikipedia.org/wiki/DONKEY.BAS)
- 🎙️ [Bill Gates talks about DONKEY.BAS at TechEd 2001](https://blog.codinghorror.com/bill-gates-and-donkey-bas/)
- 📦 [Original DONKEY.BAS source on Internet Archive](https://archive.org/details/donkey-v1.1.0)
- 🖥️ [LaunchBox Games Database entry](https://gamesdb.launchbox-app.com/games/details/154401-donkey)

***

## 🤝 Contributing

Contributions welcome! Ideas for improvement:

- [ ] Add PC speaker sound effects via `pygame.mixer`
- [ ] Pixel-art sprites using `pygame.Surface` arrays
- [ ] High score persistence with `json` / `sqlite3`
- [ ] Multiplayer mode (two donkeys simultaneously)
- [ ] Faithful 320×200 CGA resolution mode
- [ ] Web version via [Pygbag](https://pygame-web.github.io/) (Python + WebAssembly)

***

## 📄 License

This project is released under the **MIT License** — see the [`LICENSE`](LICENSE) file. Free to use, modify, and distribute.

This is an independent, clean-room reimplementation written from scratch in Python.
It contains no original DONKEY.BAS code or assets, and it is not affiliated with, sponsored by, or endorsed by IBM or Microsoft.
Any product names mentioned are used for historical reference only and belong to their respective owners.

***

## 🔍 Search Keywords

*For discoverability: donkey.bas python, DONKEY BAS remake, IBM PC DOS game python, bill gates first game python,
donkey game pygame, retro DOS game python, PC DOS 1981 game clone, donkey.bas clone pygame,
IBM personal computer game remake, gwbasic game python, basica game python, classic PC game python*

***

<div align="center">

**Made with Python 🐍 + Pygame 🎮**

*"It was, at the time, very thrilling."* — Bill Gates, 1981

⭐ Star this repo if it brought you nostalgia (or curiosity)

</div>
