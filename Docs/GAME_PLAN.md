# Hiking Horror — Game Plan (everything decided so far)

Working title: none yet. Engine: **Unity 6 (6.3 LTS), URP** ("Universal 3D" template).
Owner's plan: Claude **Pro**. Budget rule from the owner: stop building at 100% of the weekly
usage limit; use Sonnet for small fixes, Opus for building new systems.

## Concept

A first-person hiking sim that slowly turns into horror. You play **Ben**, an expert hiker,
on a week-long hike through late-autumn woods. It starts relaxing (birds, wind, leaves) and
gets scarier every day and night. Slow-burn psychological horror, with jump scares at night.

## Characters (voices made by the owner in ElevenLabs)

| Character | Who | Notes |
|---|---|---|
| **Ben** (player) | Man, about 30, expert hiker | Talks to himself: trail commentary ("Those are deer tracks… no. Those aren't deer."), reactions, camp chatter. Calm on Day 1, shaky and exhausted by Day 14. |
| **Alex** | Man, park ranger | Heard over the walkie-talkie. Friendly check-ins → static → wrong directions in Week 2. |
| **The missing hiker** | Unknown | Voice memos found on their abandoned camera. |
| **The monster** | Tall figure, dark jacket, light pants | Looks like the hiker in the owner's 3rd photo. Mimics Ben's voice later in the week (same ElevenLabs voice, "off" + in-game distortion). |

## Ben's first-person body (match the owner's photo)

Visible arms, legs and shoes when looking down: **dark green sweatshirt**, **royal blue
sweatpants with an orange logo on the left leg**, **grey sneakers/hiking shoes**, light skin.
Arms swing while walking; the held item (flashlight, camera…) is in the right hand.

## Gear

Tent, headlamp/flashlight (batteries drain, flickers near the monster), **camera** (takes real
photos; later photos show things Ben didn't see; flash makes the monster back off briefly,
limited flash charges), map + compass (needle drifts in scary parts), fire kit, water,
food, first-aid kit, multitool, rope, walkie-talkie (Alex). Hotbar with number keys or a
backpack menu; items shown in hand.

## Food matters (survival-lite)

- Hunger bar drains with hiking.
- Food: trail mix, jerky, granola bars (snacks), freeze-dried meals (cooked on stove/fire,
  most filling), plus supplies found at night.
- **Hang the food bag** from a tree away from the tent each night (real expert skill). Skip
  it and food goes missing overnight — "and it wasn't a bear".
- Hot meal = more filling but the smell/fire draws the monster closer that night; cold
  trail mix = safer, hungrier.
- Hungry: slower, sprint stamina drains faster, shaky/blurry view, stomach growls.
  **Starving: hallucinations** (fake figures, fake footsteps) — you can't trust what you see.
  No instant death from hunger.
- Week 2: food runs short; fishing at the Day 8 creek; the monster raids the bag regardless.

## Daily loop

1. **Day:** hike the day's trail, take photos, read markers, eat, talk (Ben lines).
2. **Dusk:** pick the campsite, **pitch the tent step by step** (lay out, poles, stakes,
   rainfly), build fire, cook/eat, hang food bag.
3. **Night — choose:**
   - **Go to sleep:** safe; you hear/see that night's scare from inside the tent.
   - **Go into the dark:** explore with flashlight + camera; find clues, batteries, lost gear.
     If the monster gets you: **jump scare → cut to black → wake up in the tent in the
     morning** (no death, no game over), with one more item missing.
4. **Morning:** wake in the tent, **pack up the tent** (stakes, poles, roll it, into the
   pack), put out the fire, take a photo of the campsite (matters later). Next day.

On the **first night the monster comes right up to the tent**: footsteps circling in the
leaves, a tall shadow on the tent wall (lit by the fire), it stops outside the door.
Morning: long footprints around the tent, the map is gone, the fire pit is cold.

## The week (scare level out of 10)

### Week 1: The Trail
| Day | Day | Night: sleep | Night: go into the dark |
|---|---|---|---|
| 1 (1/10) | Gravel trail (photo 1), birds, wind. Photos for fun. A hiker far ahead. Pitch camp. | Footsteps slowly circle the tent. | Someone standing between the trees. Walk closer → jump scare. |
| 2 (2/10) | Uphill dirt trail (photo 2). Second set of footprints beside yours. Yesterday's photo: hiker in the background staring. | Tall shadow stops outside the tent door. | Abandoned campsite: torn tent, a camera left behind. |
| 3 (3/10) | Pass the leaning forked tree twice. Walkie static. Flash photo shows a figure you can't see. | Tapping on the tent pole. | Something calls to you in your own voice. |
| 4 (4/10) | Compass drifts, markers moved, trail loops. | Fire goes out; zipper opens a few inches. | It's sitting by your fire; only the camera flash makes it go away. |
| 5 (5/10) | Dead silence. Hiker stands still, closer each time you look away. Photos show it right behind you. | Footsteps matching yours; walkie says your name. | Fresh footprints in your boot size lead into the woods. |
| 6 (6/10) | Fog, dark by midday, batteries almost dead. | Its shadow is inside the tent with you. Don't turn the light on. | The woods are completely silent, until they aren't. |
| 7 (8/10) | Long straight trail (photo 3). It gets closer every time you look down at your feet; it turns; **run for the trailhead**. Reach the car; it stops at the treeline. | — | — |

**The choice at the car (Day 7):**
- **Leave → Ending 1: Early Exit.** Drive away. At home, the last photo on the camera —
  which you never took — shows you asleep in your tent.
- **Stay another week.** Walkie: Alex asks for help finding a missing hiker. Turn back in.

### Week 2: Deep Woods (only if you stay)
| Day | Day | Night: sleep | Night: go into the dark |
|---|---|---|---|
| Night 7 | (camp near the trailhead) | Car headlights flash on and off all night. | Your car is unlocked and the seat is warm. |
| 8 (5/10) | Calm; birdsong loops exactly. Creek crossing. Your name in the trail register in someone else's handwriting. | You wake with the tent pitched somewhere else. | Something wading slowly up the creek toward you. |
| 9 (6/10) | Ranger cabin + fire tower. Alex's directions are wrong. Photo: someone in the tower window. | Cabin lights flick on and off across the clearing. | Ranger's logbook: *"It copies whoever it follows."* |
| 10 (6/10) | Burned forest. In daylight it walks beside you through the trees, matching your pace. | Something lies down against the tent; breathing. | Dozens of tents in the burn — all yours. |
| 11 (7/10) | First snow. Two sets of tracks behind you, both your boots. Old photos: the figure has moved closer in each. | Snow crunching as it circles, closer every lap. | Tracks lead to it standing over your camp, wearing your gear. |
| 12 (8/10) | Whiteout. Markers lead to the missing hiker's last camp; their camera's last photo is you, asleep. | Walkie: "I'm outside," in your voice. | Flashlight dies; only the camera flash shows where it is. |
| 13 (9/10) | Its den under fallen trees, full of everything it took. Take your gear back. It hunts in daylight now. | No real sleep: keep the flashlight on the tent door until dawn. | The last clue is out there, and so is it. |
| 14 (10/10) | Final trail out through snow and darkness; the last chase. | — | — |

### Endings
1. **Early Exit** — leave at Day 7 (above).
2. **Out of the Woods** — escape after Day 14, but you're not sure what came out with you.
3. **Lost** — caught on Day 14. A new hiker starts the trail and far ahead is someone
   walking: Ben. (Ties back to the person in the owner's 3rd photo.)
4. **The Truth** — only if you went into the dark enough nights to find every clue. You
   learn what it is and end it.

## The three reference photos (in `Reference/`)
1. `photo1_gravel_trail.jpg` — narrow gravel path with green grass strips along both edges,
   brown leaf litter, dense thin bare saplings both sides; right side has green, yellow and
   rust-brown bushes (honeysuckle-like). Overcast grey sky. Late November.
2. `photo2_uphill_dirt.jpg` — dirt path going slightly uphill, leaf-covered, tan dry grass
   verges, a **leaning forked tree** on the left, tangled bare brush on the right, open grey
   sky, some trees still holding dead brown leaves.
3. `photo3_looking_down.jpg` — first-person looking down: green sleeve and hand reaching
   forward, blue sweatpants, grey shoe, on a **long straight** leaf-covered dirt path between
   very dense straight thin trunks; a dark-jacketed person far ahead (→ the monster idea).

## Voices (ElevenLabs workflow)
- A voice script spreadsheet: `ID, Who, Line, How it should sound, When it plays`.
- File name = ID, e.g. `D01_BEN_003`, `D01_ALEX_001`, `N01_BEN_002`, `D05_MONSTER_001`.
- Drop files into one folder; the game finds them by name. Until then each line shows as a
  subtitle with a short silence. Subtitles can be toggled.
- Example lines: `D01_BEN_003` "Nice. Gravel the whole first stretch." (relaxed);
  `D01_ALEX_001` "Ranger station. You checked in okay out there?" (friendly, radio);
  `N01_BEN_002` "…Just a deer. Probably just a deer." (whisper);
  `D05_MONSTER_001` "Nice. Gravel the whole first stretch." (Ben's voice, flat and wrong —
  the monster repeating Day 1).

## Music (Claude composes MIDI → owner produces in FL Studio)
- Everything is built from one 8-bar **trail motif** in D major that falls apart over the week.
- **Done:** the Trail Theme (layered) — owner liked it. Name not chosen yet (ideas: "The Way
  In", "Leaf Litter", "Seven Days Out", "Ben's Trail").
- **To do (12):** Main Menu; Night – In the Tent; Night – Into the Dark (layered: base +
  tension); Chase Day 7; Chase Day 14; Week 2 – Deep Woods; Endings 1–4; stingers (jump
  scare, photo reveal, low boom). All already written in `Music/Tools/compose.py` — just run
  `python3 compose.py --render` to render them.
- Music is adaptive: the trail theme is 5 synchronized 96 s loop layers (guitar, flute
  melody, wrong-note music box, dark pad, drone) faded by the dread level; the music drops
  to silence right before scares; stingers on events.
- Loudness: about -24 LUFS integrated, true peak ≤ -1 dBTP. Voices sit on top (duck music
  under dialogue).

## Build order (agreed)
1. **Day 1 + Night 1** (biggest chunk: world from the photos, Ben's body, walking, gear,
   tent pitch/pack, food, night choice, first scare) — owner wants to **see screenshots**.
2. Days 2–7 + the leave/stay choice.
3. Days 8–14 + all four endings.
4. Voice script, remaining music, polish.

With the Pro budget, the agreed split is: Claude builds all systems, editor tools, Days 1–3,
the endings, the voice script and the music MIDI; the owner can build Days 4–14 himself in
Unity with the editor tools ("Add scare", "Add campsite", trail editing, tree painting),
following a per-day checklist Claude writes.
