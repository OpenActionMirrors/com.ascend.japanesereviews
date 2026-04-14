import type { ReviewSettings, SiteConfig } from "./types";

export const bunpro: SiteConfig = {
  reviewUrl: "https://bunpro.jp/dashboard",
  icon: "bunpro.png",
  authType: "apiKey",

  async getReviewCount(settings: ReviewSettings): Promise<number> {
    const response = await fetch(
      `https://bunpro.jp/api/user/${settings.apiKey}/study_queue`,
      {
        headers: {
          Pragma: "no-cache",
          "Cache-Control": "no-cache",
        },
      }
    );

    const body = await response.json() as {
      requested_information: { reviews_available: number };
    };

    return body.requested_information.reviews_available;
  },
};
