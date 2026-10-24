# Speurtocht PWA

Installable, offline version of "De Verdwenen Verjaardagstaart".

## Deploy (pick one)
- **Netlify Drop**: drag this folder onto https://app.netlify.com/drop
- **GitHub Pages**: repo Settings → Pages → Source: "Deploy from a branch", branch `main`, folder `/ (root)`. The game then lives at https://mmalkus.github.io/feestje/
- **Local test**: `python -m http.server 8000` and open http://localhost:8000
  (service workers need HTTPS or localhost; a LAN IP over plain http will not install).

## Install on the tablet
Open the URL → Safari: Share → "Zet op beginscherm"; Chrome/Android: menu → "App installeren".

## Setup
Tap "Ouders" (bottom right), answer the sum, edit spots/riddles/codes/suspects, Save.
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
  - with an OpenAI API key (Ouders → Detective-foto's met AI): a picture-book illustration of the group as detectives,
    made with the image edit API. The key is stored only in that browser's localStorage and is not included in the copy/paste export.
    Use a dedicated key with a spending limit. The photo is sent to OpenAI.

Photos are stored in IndexedDB on the device and are not part of the copy/paste export.
