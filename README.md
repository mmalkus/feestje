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
