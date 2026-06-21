# Hebrew Word of the Day

A small, installable **Progressive Web App** that teaches one **Biblical Hebrew**
word each day — with its transliteration, a plain-English pronunciation, a
definition, and the word shown in a verse from the Hebrew Bible.

Pure HTML, CSS, and vanilla JavaScript. No build step, no dependencies, no
tracking. Works offline once loaded.

## Features

- **Word of the day** — deterministic from the calendar date, so the word is the
  same for everyone on a given day and changes at local midnight.
- **Transliteration + definition** for every word, plus a fuller note on nuance.
- **Pronounce it** — taps the browser's speech synthesis (uses a Hebrew voice
  when one is installed).
- **Browse** — prev / next / today, a "surprise me" shuffle, arrow-key and swipe
  navigation.
- **A verse in context** — each word appears in a short, well-known passage with
  its reference and an English rendering.
- **Installable & offline** — full PWA with a manifest and a service worker that
  caches the app shell.
- Strong's numbers and approximate occurrence counts for further study.

## Run it locally

The app is fully static. Service workers require `http(s)`, so use a tiny local
server rather than opening the file directly:

```bash
python3 -m http.server 8000
# then visit http://localhost:8000
```

Then use your browser's **Install** option (or the in-app **Install** button on
supported browsers) to add it to your home screen / desktop.

## Project layout

```
index.html              markup + app shell
styles.css              styling (indigo + gold, glassy card)
app.js                  word-of-the-day logic, navigation, speech, install, SW
words.js                the word bank (edit/extend here)
manifest.webmanifest    PWA metadata
service-worker.js       offline caching
icons/                  generated PNG app icons (Torah scroll)
tools/make_icons.py     regenerate the icons (pure-Python PNG encoder)
```

## Adding or editing words

Open `words.js` and add an object to the `WORDS` array:

```js
{
  hebrew: "שָׁלוֹם",
  translit: "šālôm",        // academic transliteration
  pron: "sha-LOME",          // plain-English pronunciation
  pos: "noun (m.)",
  gloss: "peace, wholeness", // short definition
  meaning: "Completeness, welfare, harmony — not just absence of conflict.",
  strongs: "H7965",
  occurrences: 237,
  verse: { ref: "Numbers 6:26", he: "וְיָשֵׂם לְךָ שָׁלוֹם", en: "…and give you peace." }
}
```

## Regenerating icons

```bash
python3 tools/make_icons.py
```

## A note on the data

Glosses, Strong's numbers, and occurrence counts are standard lexical reference
data and are meant as a learning aid; occurrence counts are approximate. For
serious study, consult a full lexicon (e.g. BDB or HALOT).
