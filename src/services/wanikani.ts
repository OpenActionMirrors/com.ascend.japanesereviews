import type { ReviewSettings, SiteConfig } from "./types";

export const wanikani: SiteConfig = {
  reviewUrl: "https://www.wanikani.com/review",
  icon: "wanikani.png",
  authType: "apiKey",

  async getReviewCount(settings: ReviewSettings): Promise<number> {
    const response = await fetch("https://api.wanikani.com/v2/summary", {
      headers: {
        "Wanikani-Revision": "20170710",
        Authorization: `Bearer ${settings.apiKey}`,
        Pragma: "no-cache",
        "Cache-Control": "no-cache",
      },
    });

    const body = await response.json() as {
      data: { reviews: Array<{ subject_ids: string[] }> };
    };

    return body.data.reviews[0].subject_ids.length;
  },
};
