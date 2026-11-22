# Start here (handoff to a new Claude chat)

This folder is a handoff from an earlier Claude chat. It has everything decided so far for a
**hiking horror game in Unity 6**.

## What's inside
- `Docs/GAME_PLAN.md` — the full game design: story, characters, the 14 days and nights,
  food, gear, endings, voices, music.
- `Docs/TECH_PLAN.md` — how to build it in Unity 6.3 LTS (URP), and how to render screenshots.
- `Reference/` — the 3 trail photos the game is based on.
- `Music/` — the finished **trail theme**: MIDI for FL Studio (`Music/MIDI/trail.mid`), a
  preview (`Music/Preview/trail_theme_preview.mp3`) and the composer script that writes
  the other 12 tracks (`Music/Tools/compose.py`).
- `Assets/HikingHorror/Resources/Music/` — the trail theme's 5 game layers (Ogg).

The same files are on GitHub: `progame11/3dhighdefgame`, branch
`claude/3d-hiking-sim-scenes-btzgee` (the photos are only in this zip).

## How to use it
1. Unzip this somewhere normal (e.g. `Documents/HikingHorror-handoff`).
2. In Unity Hub, create a project with the **Universal 3D** template (Unity 6.3 LTS), e.g.
   `Documents/HikingHorror`.
3. Copy the `Assets/HikingHorror` folder from this zip into the project's `Assets` folder.
4. Open a new Claude Code session **on your Mac** (Claude desktop app → Code tab) in the
   Unity project folder, and paste the message below.

## Message to paste into the new chat

```
I'm making a hiking horror game in Unity 6 (URP). An earlier Claude chat planned it with me.
Please read these files first (they're in the handoff folder I unzipped at
<PUT THE PATH HERE>): Docs/START_HERE.md, Docs/GAME_PLAN.md and Docs/TECH_PLAN.md, and look
at the 3 photos in Reference/.

Use my gamedev plugin (awesome-gamedev-agent-skills): start with its router and load only
the skills each step needs.

First task: build the Day 1 scene in this Unity project to look like my 3 photos (gravel
trail, uphill dirt trail with the leaning forked tree, long straight leafy trail), with
Ben's first-person body (green sweatshirt, blue pants, grey shoes) and walking. Keep the
world editable (Terrain, a draggable trail, one scene per day, a "Hiking Horror" menu).
Then run Unity on my Mac to render screenshots from the same viewpoints as my photos and
show them to me.

I'm on the Pro plan, so work efficiently and commit as you go.
```
