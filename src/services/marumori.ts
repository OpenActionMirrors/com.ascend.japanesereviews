import type { ReviewSettings, SiteConfig } from "./types";

export const marumoriVocab: SiteConfig = {
  reviewUrl: "https://marumori.io/study-lists/reviews",
  icon: "marumori.png",
  authType: "apiKey",

  async getReviewCount(settings: ReviewSettings): Promise<number> {
    const response = await fetch("https://public-api.marumori.io/home", {
      headers: {
        Authorization: `Bearer ${settings.apiKey}`,
        Pragma: "no-cache",
        "Cache-Control": "no-cache",
      },
    });

    const body = await response.json() as {
      data: { counts: { reviews: number } };
    };

    return body.data.counts.reviews;
  },
};

export const marumoriGrammar: SiteConfig = {
  reviewUrl: "https://marumori.io/study-lists/reviews?grammar=true",
  icon: "marumori.png",
  authType: "apiKey",

  async getReviewCount(settings: ReviewSettings): Promise<number> {
    // MaruMori API has a rate limit of 1 request every 250ms.
    // When both vocab and grammar icons exist, add a delay to avoid 429.
    await new Promise((resolve) => setTimeout(resolve, 1000));

    const response = await fetch("https://public-api.marumori.io/home", {
      headers: {
        Authorization: `Bearer ${settings.apiKey}`,
        Pragma: "no-cache",
        "Cache-Control": "no-cache",
      },
    });

    const body = await response.json() as {
      data: { counts: { grammarReviews: number } };
    };

    return body.data.counts.grammarReviews;
  },
};
