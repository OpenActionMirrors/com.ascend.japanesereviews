import type { ReviewSettings, SiteConfig } from "./types";

export const kitsun: SiteConfig = {
  reviewUrl: "https://kitsun.io/dashboard",
  icon: "kitsun.png",
  authType: "credentials",

  async getReviewCount(settings: ReviewSettings): Promise<number> {
    // Step 1: Login with email/password to get session cookie
    const loginResponse = await fetch("https://api.kitsun.io/profile/login", {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email: settings.username,
        password: settings.password,
      }),
      redirect: "manual",
    });

    const setCookie = loginResponse.headers.get("set-cookie");
    if (!setCookie) {
      throw new Error("Kitsun login failed: no session cookie returned");
    }

    // Step 2: Use cookie to fetch review count
    const response = await fetch("https://api.kitsun.io/general/home", {
      headers: {
        Accept: "application/json",
        Cookie: setCookie,
      },
    });

    const body = await response.json() as {
      counts: { reviews: number };
    };

    return body.counts.reviews;
  },
};
