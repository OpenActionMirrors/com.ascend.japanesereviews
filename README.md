# Stream Deck Japanese Reviews

A collection of review trackers for various Japanese review websites. The following sites are supported:

| Name     | Description     | Auth Method        | Website              |
| -------- | --------------- | ------------------ | -------------------- |
| Bunpro   | Grammar & Vocab | API Key            | https://bunpro.jp    |
| Wanikani | Kanji           | API Key            | https://wanikani.com |
| MaruMori | Grammar & Vocab | API Key            | https://marumori.io  |
| Kitsun   | Grammar & Vocab | Email & Password   | https://kitsun.io    |

Icons for each website are shown with a counter of the number of reviews currently waiting, which updates every 10 minutes. Updates are timed to 1 minute after the hour to ensure hourly updates (esp. Wanikani) are shown as soon as possible.

![Button Display](./docs/example.png)

![Property Inspector Example](./docs/pi-example.png)

Clicking on each button will open to the relevant website in your default browser, with reviews being one click away.

## Requirements

- **Stream Deck software 7.1+**
- **Node.js 24+** (for building from source)

## Getting Started

There are a few ways to utilize this Stream Deck plugin:

1. (Recommended) Download the latest released version from the Stream Deck store by searching for "Japanese Reviews"

2. Download the latest released version from Github and run `com.ascend.japanesereviews.streamDeckPlugin`.

3. Build from source and copy the `com.ascend.japanesereviews.sdPlugin` folder into the following folder:
    * On Windows: `%appdata%\Elgato\StreamDeck\Plugins\`
    * On macOS: `~/Library/Application Support/com.elgato.StreamDeck/Plugins/`

## Building

1. Install build dependencies from the project root:

   ```sh
   npm install
   ```

2. Compile the TypeScript source into the plugin bundle:

   ```sh
   npm run build
   ```

   This outputs `com.ascend.japanesereviews.sdPlugin/bin/plugin.js`.

3. Install the plugin's runtime dependencies:

   ```sh
   cd com.ascend.japanesereviews.sdPlugin
   npm install --omit=dev
   ```

4. Copy the entire `com.ascend.japanesereviews.sdPlugin` folder to the Stream Deck plugins directory (see paths above) and restart Stream Deck.

### Watch Mode

For development, you can use watch mode to automatically rebuild on changes:

```sh
npm run watch
```

### Packaging for Distribution

To package the plugin as a `.streamDeckPlugin` installer, install the [Elgato CLI](https://docs.elgato.com/streamdeck/sdk/introduction/getting-started/) and run:

```sh
npm install -g @elgato/cli@latest
streamdeck pack com.ascend.japanesereviews.sdPlugin
```

## Contributing

Feel free to suggest feature changes or add support for additional Japanese review sites by opening a pull request.

The plugin is written in TypeScript and built with Rollup. Source code is in `src/`, the Property Inspector UI is in `ui/`, and the compiled plugin lives in `com.ascend.japanesereviews.sdPlugin/`.
