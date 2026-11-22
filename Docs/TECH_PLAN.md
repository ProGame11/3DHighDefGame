# Hiking Horror — Technical Plan (Unity 6.3 LTS, URP)

Status: **design only, no Unity code written yet.** Done so far: the trail theme music
(`Music/`, `Assets/HikingHorror/Resources/Music/trail_*.ogg`). This plan is what the previous
chat intended to build; adjust freely.

## Project setup
- Create the project in Unity Hub with the **Universal 3D** template (URP configured, Input
  System package installed). Repo layout: everything lives in `Assets/HikingHorror/`.
- No asmdef files (scripts compile into Assembly-CSharp, which sees URP + Input System).
  Editor-only code goes in `Assets/HikingHorror/Editor/`.
- Input: the template enables the **new Input System**; `UnityEngine.Input` throws when
  `activeInputHandler` is 1. Wrap input in one class with `#if ENABLE_INPUT_SYSTEM`
  (`Keyboard.current`, `Mouse.current.delta`) and a legacy fallback.
- Unity 6.3: use `FindAnyObjectByType` (FindObjectOfType is obsolete). Don't use `?.`/`??`
  on UnityEngine.Object.
- Useful skills: the owner has the **awesome-gamedev-agent-skills** plugin installed locally.
  Route with its `router`; relevant skills: `unity-csharp-scripting`, `unity-input-system`,
  `camera-systems` (first-person look), `procedural-gen` (terrain/scatter), `level-design`,
  `audio-design` (adaptive music, ducking), `game-ai` (monster), `save-systems`,
  `game-ui-ux`, `survival-crafting` (food), `performance-optimization`.

## The owner wants an EDITABLE world
Build it once with editor tools into saved scenes, then the owner edits by hand:
- **Unity Terrain**: heightmap (raise/lower/smooth brushes), 4 terrain layers painted
  (leaf litter, green grass, dry tan grass, dirt), **trees and bushes as terrain tree
  prototypes** (paintable), grass as terrain **detail** prototypes (waves in wind).
- **Trail** = a `TrailPath` component (`[ExecuteAlways]`, list of points, Catmull-Rom) with
  scene-view handles to drag points. It generates the path ribbon mesh (gravel/dirt texture
  with noisy alpha-clipped edges, slightly above the terrain) and scattered fallen-leaf
  cards on and near the path, live in the editor (meshes not saved: rebuilt from points).
  Button "Fit terrain to trail": flattens terrain along the path, paints dirt + green grass
  strips at the edges (photo 1), removes trees on the path.
- **One scene per day** (`Day01.unity` …). Landmarks (the leaning forked tree, campsite,
  food-hang tree) are normal GameObjects. Story moments are visible `StoryTrigger` boxes
  with a list of actions editable in the Inspector (play voice line, play sound, show
  figure, set dread, set music state, give objective).
- Menu **Hiking Horror/**: Build Day 1 Scene, Add Scare/Story Trigger, Add Campsite, Add
  Trail Marker, Fit Terrain to Trail, Capture Screenshots.
- Code-generated art first (textures + tree meshes baked to assets so terrain can use them);
  slots to swap in free Asset Store trees/textures later.

## Day 1 scene layout (from the 3 photos)
Terrain ~512×512 m, trail ~800–1000 m, all three photo looks in order:
1. **Section A — gravel trail (photo 1)**: gentle S-curves, gravel ribbon ~1.2 m wide, green
   grass strips 0.6–1.8 m from center, brown leaf litter beyond, very dense thin saplings
   (3–8 cm trunks, 5–9 m tall) both sides, green/yellow/rust honeysuckle-like bushes
   mostly on the right.
2. **Section B — uphill dirt (photo 2)**: climbs ~8–10 m, dirt path with leaves, tan dry
   grass verges, more open canopy, the **leaning forked tree** landmark on the left,
   tangled bare brush on the right, some trees holding dead brown leaves.
3. **Section C — long straight (photo 3)**: very long straight path, leaves covering it,
   tightly packed straight thin trunks both sides.
4. Campsite clearing at the end (flat, fire ring, tent spot, a food-hang tree nearby).
- Overcast: high soft sun (intensity ~0.5–0.8), Trilight ambient (light grey sky, grey-brown
  equator, brown ground), exponential-squared fog (visibility ~60–100 m, grey), custom
  overcast cloud skybox shader (CG skybox shaders work in URP), URP Volume: ACES/Neutral
  tonemapping, saturation −15, slight contrast, subtle vignette + film grain. A second
  "dread" Volume whose weight rises over the week (desaturate, darker, more grain).
- Camera: SMAA, far clip ~250 m, near clip 0.03 (so Ben's body is visible).
- Performance: tree LODGroups (LOD0 ≤ ~50 m, LOD1 trunk + main branches, cull ~120 m), shadow
  distance ~40 m (overcast shadows are faint anyway), terrain detail distance ~60 m.

## Player
- `CharacterController`; walk ~2.3 m/s, sprint ~4.6 m/s with stamina; mouse look with pitch
  −80..85° (looking down at feet is a key shot); head bob; footsteps from bob phase; surface
  type from distance to `TrailPath` (gravel / dirt / leaves / snow later).
- Procedural Ben body (tapered capsule meshes): torso (green), arms with two-bone IK for the
  held item, legs with a procedural walk cycle, shoes; head renders shadows only.

## Gameplay systems (Day 1 + Night 1)
- Hotbar: hands, flashlight (spot light + cookie, battery, flicker), camera (photos via
  `ScreenCapture.CaptureScreenshotAsTexture` after `WaitForEndOfFrame`, flash light, album on
  Tab; "photo-only" monster renderers switched on for the capture frame so photos show
  things Ben can't see), food, walkie (Alex), compass.
- Hunger, food inventory, eat; campfire (particles + flickering point light); tent pitch
  and pack as multi-step "hold E" interactions; food bag hang spot.
- Day flow: hiking → dusk at campsite (time of day tied to trail progress) → camp tasks →
  night choice UI (Sleep / Go into the dark) → night event → morning → pack up → next day.
- Night 1 sleep: monster circles the tent; its shadow crosses the tent wall. Trick: the tent
  fabric has an inner mesh facing inward but with **outward normals**, so from inside you
  see the outside lighting and the monster's shadow cast by the fire light.
- Monster ("Figure"): procedural tall humanoid; modes WalkAhead (along the trail), StandWatch,
  CircleTent, Rush → JumpScare (face fills the screen, stinger, cut to black, wake in tent).
- UI in IMGUI (prompts, hotbar, hunger/stamina, subtitles, fades, night choice, pause menu).
- Audio: procedural SFX at startup (footsteps on leaves/gravel/dirt, wind, birds, fire
  crackle, drone, stinger, heartbeat, zipper, stake hammer, shutter) until real files exist;
  music director plays `Resources/Music/<name>` with layer fades (PlayScheduled for sync);
  voice system reads a CSV from `Resources/` and plays `Resources/Voice/<ID>`.
- Save: day number, inventory, clues found, photos (PlayerPrefs/JSON).

## Screenshots for the owner (Unity on his Mac)
Run Unity in batch mode with graphics (not `-nographics`) and an editor method that builds
the scene and renders cameras at the three photo viewpoints to PNG, e.g.
`/Applications/Unity/Hub/Editor/<version>/Unity.app/Contents/MacOS/Unity -batchmode
-projectPath <project> -executeMethod HikingHorror.EditorTools.ScreenshotTool.CaptureAll -quit
-logFile -`.
Viewpoints: (1) standing on the gravel path looking along it (photo 1); (2) portrait shot up
the dirt path with the forked tree on the left (photo 2); (3) looking down ~50° at Ben's
arm, leg and shoe on the long straight trail (photo 3); plus an overview.
