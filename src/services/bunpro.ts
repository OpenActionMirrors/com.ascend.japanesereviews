import type { ReviewSettings, SiteConfig } from "./types";

export const bunpro: SiteConfig = {
  reviewUrl: "https://bunpro.jp/dashboard",
  icon: "bunpro.png",
  authType: "apiKey",

  async getReviewCount(settings: ReviewSettings): Promise<number> {
    const response = await fetch(
      `https://api.bunpro.jp/api/frontend/user/due?dangerously_authenticate_using_api_token=true`,
      {
        headers: {
          Pragma: "no-cache",
          "Cache-Control": "no-cache",
          "Authorization": "Bearer " + settings.apiKey
        },
      }
    );

    const body = await response.json() as {
      total_due_grammar: number,
      total_due_vocab: number
    };

    return body.total_due_grammar + body.total_due_vocab;
  },
};
