import type { SiteConfig, Website } from "./types";
import { bunpro } from "./bunpro";
import { wanikani } from "./wanikani";
import { marumoriVocab, marumoriGrammar } from "./marumori";
import { kitsun } from "./kitsun";

export type { ReviewSettings, SiteConfig, Website } from "./types";

export const supportedSites: Record<Website, SiteConfig> = {
  bunpro,
  wanikani,
  "marumori-vocab": marumoriVocab,
  "marumori-grammar": marumoriGrammar,
  kitsun,
};
