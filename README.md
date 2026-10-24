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
  With "Maak er detectives van" on, they can turn it into a detective picture:
  - without an API key: a sepia "case file" print with a TOPDETECTIVES stamp, made on the device;
  - with an API key (Ouders → Detective-foto's met AI): a picture-book illustration of the group as detectives.
    Pick a service (OpenAI, OpenRouter, Mistral, or "Anders" with your own endpoint URL), tap "Modellen ophalen" to load
    the model list from `<endpoint>/models` (🖼 marks image models) and choose one. Supported API styles:
    - *Foto bewerken*: OpenAI-style `POST /images/edits` (OpenAI `gpt-image-1`, compatible servers);
    - *Chat met plaatje terug*: `POST /chat/completions` with image output (e.g. OpenRouter `google/gemini-2.5-flash-image`);
    - *Mistral agent*: creates an agent with the `image_generation` tool and runs it via `/conversations`. Mistral can't edit
      photos, so it draws a new picture from what it sees and faces will resemble the kids less.
    Keys are stored per service only in that browser's localStorage and are not in the copy/paste export.
    Use a dedicated key with a spending limit. The photo is sent to the chosen service. The service must allow calls
    from a browser (CORS); if it doesn't, the button falls back to the on-device version and shows a message.

Photos are stored in IndexedDB on the device and are not part of the copy/paste export.
