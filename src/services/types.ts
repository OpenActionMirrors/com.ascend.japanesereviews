export type Website = "bunpro" | "wanikani" | "marumori-vocab" | "marumori-grammar" | "kitsun";

export interface ReviewSettings {
  website: Website;
  apiKey?: string;
  username?: string;
  password?: string;
  lastCount?: number;
  lastDateTime?: string;
}

export interface SiteConfig {
  reviewUrl: string;
  icon: string;
  authType: "apiKey" | "credentials";
  getReviewCount(settings: ReviewSettings): Promise<number>;
}
