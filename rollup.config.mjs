import resolve from "@rollup/plugin-node-resolve";
import typescript from "@rollup/plugin-typescript";
import path from "node:path";
import url from "node:url";

const isWatching = !!process.env.ROLLUP_WATCH;
const sdPlugin = "com.ascend.japanesereviews.sdPlugin";

/**
 * @type {import("rollup").RollupOptions}
 */
const config = {
  input: "src/plugin.ts",
  output: {
    file: `${sdPlugin}/bin/plugin.js`,
    format: "es",
    sourcemap: isWatching,
  },
  external: (id) =>
    id.startsWith("node:") ||
    ["@elgato/streamdeck", "@napi-rs/canvas", "ws"].includes(id) ||
    id.startsWith("@elgato/"),
  plugins: [
    {
      name: "emit-package-json",
      generateBundle() {
        this.emitFile({
          fileName: "package.json",
          source: JSON.stringify({ type: "module" }),
          type: "asset",
        });
      },
    },
    typescript({
      mapRoot: isWatching
        ? `./${path.relative(
            `./${sdPlugin}/bin`,
            path.dirname(url.fileURLToPath(import.meta.url))
          )}`
        : undefined,
    }),
    resolve({
      browser: false,
      exportConditions: ["node"],
      preferBuiltins: true,
    }),
  ],
};

export default config;
