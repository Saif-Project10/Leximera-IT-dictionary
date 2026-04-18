# Leximera IT Dictionary

Leximera is a static, search-first dictionary website for advanced English and technical terminology. It runs entirely in the browser using HTML, CSS, JavaScript, and a local `data.json` dataset.

## Overview

The website is designed to help students and learners explore difficult vocabulary with:

- fast keyword search
- live suggestions
- alphabet filtering
- detailed word pages
- synonyms, antonyms, and collocations
- example sentences and usage tips
- bookmarks saved in `localStorage`
- recently viewed words
- dark mode
- text-to-speech for word pronunciation

## Pages

- `index.html` - home page with search, suggestions, stats, word of the day, and recent words
- `word.html` - full detail page for a selected word
- `bookmarks.html` - saved words page
- `about.html` - project background
- `contact.html` - contact information
- `disclaimer.html` - AI-content disclaimer

## Project Structure

```text
.
|-- index.html
|-- word.html
|-- bookmarks.html
|-- about.html
|-- contact.html
|-- disclaimer.html
|-- style.css
|-- script.js
`-- data.json
```

## How It Works

- `script.js` loads `data.json` in the browser using `fetch()`
- the dataset is normalized and indexed client-side for search and filtering
- bookmarks, theme preference, and recent history are stored in browser `localStorage`
- word detail pages use query parameters such as `word.html?term=example`

## Run Locally

Because the site loads `data.json` with `fetch()`, it should be served from a local web server instead of opening the HTML files directly with `file://`.

### Option 1: Python

```powershell
python -m http.server 8000
```

Then open:

```text
http://localhost:8000
```

### Option 2: VS Code Live Server

Open the project in VS Code and run the site with the Live Server extension.

## Notes

- `data.json` is the main dictionary dataset and is the largest file in the project.
- The website is fully front-end based and does not require a backend.
- Content on the site includes AI-assisted material, as stated on the disclaimer page.

## Customization

To update the dictionary:

1. Edit or replace `data.json`
2. Keep the expected fields consistent, such as `word`, `meaning`, `shortMeaning`, `synonyms`, `antonyms`, `collocations`, and examples
3. Refresh the browser after changes

## Author

Built for Leximera as a student-focused terminology reference website.
