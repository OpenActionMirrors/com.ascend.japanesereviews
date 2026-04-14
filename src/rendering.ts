import { createCanvas, loadImage, GlobalFonts } from "@napi-rs/canvas";
import path from "node:path";
import url from "node:url";

const __dirname = path.dirname(url.fileURLToPath(import.meta.url));
const imagesDir = path.resolve(__dirname, "../static/imgs/actions/review");

/**
 * Renders a review count overlay on top of a site icon.
 * Matches the existing visual style:
 * - Trebuchet MS 22px white text
 * - Black semi-transparent blurred rectangle background
 * - Centered horizontally, positioned at y=24
 * - 12px per character + 4px padding width
 *
 * Returns a base64 data URI (image/png).
 */
export async function renderReviewIcon(
  iconFilename: string,
  text: string
): Promise<string> {
  const iconPath = path.join(imagesDir, iconFilename);
  const image = await loadImage(iconPath);

  const canvas = createCanvas(image.width, image.height);
  const ctx = canvas.getContext("2d");

  // Draw the base site icon
  ctx.drawImage(image, 0, 0);

  const textStr = text.toString();
  const charWidth = 12;
  const padding = 4;
  const boxWidth = charWidth * textStr.length + padding;
  const boxX = Math.floor(image.width / 2 - boxWidth / 2);
  const boxY = 24;
  const boxHeight = 26;

  // Draw blurred black semi-transparent background
  // Matches the original JS version: blur(4px) + shadowBlur(5)
  ctx.fillStyle = "#000a";
  ctx.shadowColor = "#000";
  ctx.shadowBlur = 5;
  ctx.filter = "blur(4px)";
  ctx.fillRect(boxX, boxY, boxWidth, boxHeight);

  // Reset filters for text
  ctx.filter = "none";
  ctx.shadowBlur = 0;

  // Draw white text
  ctx.fillStyle = "#fff";
  ctx.font = '22px "Trebuchet MS"';
  ctx.fillText(textStr, boxX + 2, 45);

  // Return as base64 data URI
  const buffer = canvas.toBuffer("image/png");
  return `data:image/png;base64,${buffer.toString("base64")}`;
}
