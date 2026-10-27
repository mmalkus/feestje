# Speurtocht PWA

Installable, offline version of "De Verdwenen Verjaardagstaart".

## Deploy (pick one)
- **Netlify Drop**: drag this folder onto https://app.netlify.com/drop
- **GitHub Pages**: repo Settings → Pages → Source: "Deploy from a branch", branch `main`, folder `/ (root)`. The game then lives at https://mmalkus.github.io/feestje/
- **Local test**: `python -m http.server 8000` and open http://localhost:8000
  (service workers need HTTPS or localhost; a LAN IP over plain http will not install).

## Install on the tablet
Open the URL → Safari: Share → "Zet op beginscherm"; Chrome/Android: menu → "App installeren".
The game goes fullscreen when the kids tap "Start het onderzoek" (and via the ⛶ button bottom-left). iPhone Safari has no fullscreen for web pages: add it to the home screen there to hide the browser bars. iPad and Android support it.

## Setup
Tap "Ouders" (bottom right), answer the sum (two digits × two digits, e.g. 12 × 45), edit the steps/suspects, Save.
The menu has two tabs: **Opdrachten** (story, steps, suspects; tap a step to fold it open or closed, drag ⠿ to reorder) and **Instellingen** (lock, AI, voice, transfer).
The menu asks for the sum or PIN **every** time it is opened. Under "Toegang tot dit menu" you can switch to a 4–8 digit PIN
(stored as a salted SHA-256 hash on the device). Forgot it? "Pincode vergeten?" lets you in with a two-digit × two-digit sum, then set a new PIN.
After 5 wrong tries the gate waits 30 seconds.

The screen stays awake while the game is open (Wake Lock API, re-requested whenever the page comes back or is tapped;
needs iOS 16.4+ / a recent Chrome).
Settings are stored in localStorage on that device. Use the copy/paste box to move them to another device.

## Soorten opdrachten
Each step in the setup has a type:
- **Raadsel + briefje**: riddle → find the note → type its code (the original game).
- **Waar is dit? (foto)**: upload a close-up of the hiding spot; kids first see it zoomed in and can zoom out as a hint, then type the note's code.
- **Fotopuzzel**: a photo of the hiding spot cut into 9 tiles; tap two tiles to swap them. Once it's solved they go there and type the code.
- **Letterpuzzel**: put the shuffled letters of a word in order, all on the tablet.
- **Foto-opdracht**: the kids take a photo (e.g. a team photo). It ends up in the photo album on the final screen.
  The camera opens right inside the game (live viewfinder, "📸 Klik!", a 3-2-1 self-timer and a front/back switch).
  The browser asks for camera permission once; if it's refused or not available, the button opens the device's own camera instead.
  With "Maak er detectives van" on, they can turn it into a detective picture:
  - without an API key: a sepia "case file" print with a TOPDETECTIVES stamp, made on the device;
  - with an API key (Ouders → Instellingen → Detective-foto's met AI): a picture-book illustration of the group as detectives.
    Pick a service (OpenAI, OpenRouter, Mistral, or "Anders" with your own endpoint URL), tap "Modellen ophalen" to load
    the model list from `<endpoint>/models` (🖼 marks image models) and choose one. Supported API styles:
    - *Foto bewerken*: OpenAI-style `POST /images/edits` (OpenAI `gpt-image-1`, compatible servers);
    - *Chat met plaatje terug*: `POST /chat/completions` with image output (e.g. OpenRouter `google/gemini-2.5-flash-image`);
    - *Mistral agent*: creates an agent with the `image_generation` tool and runs it via `/conversations`. Mistral can't edit
      photos, so it draws a new picture from what it sees and faces will resemble the kids less.
    Keys are stored per service only in that browser's localStorage and are not in the copy/paste export.
    Use a dedicated key with a spending limit. The photo is sent to the chosen service. The service must allow calls
    from a browser (CORS); if it doesn't, the button falls back to the on-device version and shows a message.

- **Zoek deze plek (foto-match)**: upload a photo of a spot (take it at the kids' eye height). The kids see a pencil drawing of it
  (or the real photo, if you tick that), find the spot and photograph it with the back camera.
  - A **warmer/colder meter** under the viewfinder compares the live camera image with your photo a few times a second
    (❄️ IJskoud → 🔥 HEET!) and ticks when they get warmer.
  - "📸 Is het hier?" checks the photo **on the device, offline**: it finds corners in both photos, matches them and counts how many
    agree on one camera move (ORB-style features + RANSAC, no library). "Hoe precies" sets how many must agree:
    Makkelijk 12, Normaal 18, Streng 30. In tests, unrelated photos reached 5–11 and photos of the same spot 17–270.
  - If the device rejects it and an API key is set, an **AI second opinion** is asked (Ouders → Instellingen → "Zoek deze plek: AI kijkt mee"):
    both photos go to `POST /chat/completions` of the chosen service with a vision model (default `gpt-4.1-mini`,
    `google/gemini-2.5-flash` on OpenRouter, `mistral-medium-latest` on Mistral). Its tip is shown when it says no.
  - After two misses a "👻 Spiekplaatje" button lays the drawing over the camera image.
  - "Ouders: plek goedkeuren" (sum or PIN) always lets a parent pass the step.
  - In the setup, the app rates how recognisable the spot is, and "🧪 Probeer uit" lets you take a test photo to see the score
    (and the AI's answer). Plain walls and doors are hard to recognise; pick spots with things and patterns.
  - Found spots end up in the photo album on the final screen.
  - **Verrassing** (optional, needs the image key from "Detective-foto's met AI"): write what the AI should add to your photo
    (e.g. "modderige voetstappen die om de hoek verdwijnen") and tap "✨ Maak verrassingsfoto". The edited photo is made in the setup
    and stored on the device, so no internet is needed while playing. The kids see it only once they've found the spot, on the
    "PLEK GEVONDEN!" screen. A new photo of the spot drops the old surprise. Mistral draws a new picture instead of editing the photo.
    Also works for a Kompastocht step that has a photo.

- **Kompastocht (GPS)**: the kids walk to a point outdoors. An on-screen compass arrow points at it, with the distance
  ("Nog 120 meter"), 🔥 Warmer / ❄️ Kouder, and a warm/cold bar. Put several of these steps in a row to make a trail.
  - In the setup, tap the map (OpenStreetMap) to place the point, tap "📍 Ik sta er nu" while standing there, or paste
    coordinates or a Google Maps link. The map shows the whole trail and the distance from the previous point.
    "Gevonden binnen" (10–50 m) sets how close counts as there; 20 m works well for phone GPS.
  - Optional photo: once they're there, the step continues as **Zoek deze plek** (drawing, warmer/colder camera, photo check).
  - The arrow follows the phone's compass (iPhone asks for permission when they tap "🧭 Op pad!"). Without a compass it
    uses the walking direction from the GPS. "Ouders: we zijn er" (sum or PIN) always lets a parent pass the point.
  - Needs location permission and HTTPS (GitHub Pages / Netlify are fine). The game works offline outdoors; only the map in
    the setup needs internet.

## Voorlezen (text-to-speech)
Ouders → Instellingen → "Voorlezen": a voice reads the story, riddles, tips, evidence and the ending aloud. Every line is spoken
**before the game starts** and stored in IndexedDB, so no internet is needed while playing. "🎙 Alles nu inspreken"
does it in the setup; anything still missing (e.g. the closing line with the team name, or lines changed since) is
spoken when the kids tap Start, behind a progress screen. If that fails, they can retry or "Start zonder stem".
Clips are reused as long as the text and the voice settings stay the same. A "🔊 Nog een keer" button replays a line.
- **ElevenLabs** (default, best Dutch): custom voices via Voice Cloning (clone your own voice), Voice Design, or the
  Voice Library. "Stemmen ophalen" lists your voices (★ = your own). Models: `eleven_multilingual_v2`, `eleven_flash_v2_5`, `eleven_v3`.
- **OpenAI** `gpt-4o-mini-tts`: fixed voices, but you can describe how it should sound (narrator style).
- **Anders**: any server with an OpenAI-style `POST /audio/speech` (e.g. a self-hosted voice-cloning server); must allow CORS.
Keys are stored per service only in that browser's localStorage, like the image key.

Photos are stored in IndexedDB on the device and are not part of the copy/paste export.

## Tests
Run on every pull request to `main` (GitHub Actions, `.github/workflows/tests.yml`). Locally:
```
pip install -r tests/requirements.txt && python -m playwright install chromium
pytest tests
```
`test_static.py` checks that `VERSION` in index.html matches the cache name in sw.js, that the manifest and precached files exist, and that the scripts parse.
`test_gps.py` walks a compass trail with a simulated GPS and sets a point in the parents' menu.
`test_smoke.py` opens the game in Chromium at phone size: start screen, starting the hunt, the parent gate (wrong and right answer) and offline reload via the service worker.
