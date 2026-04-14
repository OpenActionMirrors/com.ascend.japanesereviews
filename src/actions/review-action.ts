import streamDeck, {
  type DidReceiveSettingsEvent,
  type KeyUpEvent,
  SingletonAction,
  type WillAppearEvent,
  type WillDisappearEvent,
} from "@elgato/streamdeck";
import { supportedSites, type ReviewSettings, type Website } from "../services/index";
import { renderReviewIcon } from "../rendering";

const UPDATE_INTERVAL_MS = 10 * 60 * 1000; // 10 minutes
const CACHE_TTL_MS = 10 * 60 * 1000; // 10 minutes

/** Per-context state for each button instance. */
interface ActionState {
  settings: ReviewSettings;
  intervalTimer?: NodeJS.Timeout;
  initialTimer?: NodeJS.Timeout;
}

function toSettings(payload: Record<string, unknown>): ReviewSettings {
  return {
    website: (payload.website as Website) ?? "bunpro",
    apiKey: payload.apiKey as string | undefined,
    username: payload.username as string | undefined,
    password: payload.password as string | undefined,
    lastCount: payload.lastCount as number | undefined,
    lastDateTime: payload.lastDateTime as string | undefined,
  };
}

export class ReviewAction extends SingletonAction {
  override readonly manifestId = "com.ascend.japanesereviews.action";
  private states = new Map<string, ActionState>();

  override async onWillAppear(ev: WillAppearEvent): Promise<void> {
    const settings = toSettings(ev.payload.settings);
    const contextId = ev.action.id;

    streamDeck.logger.info(`onWillAppear: website=${settings.website}, hasApiKey=${!!settings.apiKey}, hasAuth=${this.hasAuth(settings)}`);

    this.clearTimers(contextId);
    this.states.set(contextId, { settings });

    if (this.hasAuth(settings)) {
      await this.scheduleReviews(contextId, ev);
    } else {
      await this.setIconWithText(ev, settings, "key?");
    }
  }

  override async onWillDisappear(ev: WillDisappearEvent): Promise<void> {
    this.clearTimers(ev.action.id);
    this.states.delete(ev.action.id);
  }

  override async onDidReceiveSettings(
    ev: DidReceiveSettingsEvent
  ): Promise<void> {
    const settings = toSettings(ev.payload.settings);
    const contextId = ev.action.id;

    this.clearTimers(contextId);
    this.states.set(contextId, { settings });

    if (this.hasAuth(settings)) {
      await this.scheduleReviews(contextId, ev);
    } else {
      await this.setIconWithText(ev, settings, "key?");
    }
  }

  override async onKeyUp(ev: KeyUpEvent): Promise<void> {
    const settings = toSettings(ev.payload.settings);
    const site = supportedSites[settings.website];

    if (site) {
      await streamDeck.system.openUrl(site.reviewUrl);
    }
  }

  private hasAuth(settings: ReviewSettings): boolean {
    if (!settings.website) return false;

    const site = supportedSites[settings.website];
    if (!site) return false;

    if (site.authType === "credentials") {
      return !!(settings.username && settings.password);
    }
    return !!settings.apiKey;
  }

  private async scheduleReviews(
    contextId: string,
    ev: WillAppearEvent | DidReceiveSettingsEvent
  ): Promise<void> {
    const state = this.states.get(contextId);
    if (!state) return;

    const { settings } = state;

    // Check if we have a recent cached value
    const lastDate = settings.lastDateTime
      ? new Date(settings.lastDateTime)
      : null;
    const cachedRecently =
      lastDate && Date.now() - lastDate.getTime() < CACHE_TTL_MS;

    if (cachedRecently && settings.lastCount !== undefined) {
      await this.setIconWithText(ev, settings, String(settings.lastCount));
    } else {
      await this.setIconWithText(ev, settings, "...");
      await this.updateReviews(contextId, ev);
    }

    // Schedule so it triggers every 10 minutes, starting 1 past the hour
    // to catch the typical hourly review updates.
    // Minimum 2 minutes, maximum 11 minutes until first scheduled update.
    const minutesTillFirst = 10 - (new Date().getMinutes() % 10) + 1;
    const firstDelayMs = minutesTillFirst * 60 * 1000;

    state.initialTimer = setTimeout(() => {
      this.updateReviews(contextId, ev);

      state.intervalTimer = setInterval(() => {
        this.updateReviews(contextId, ev);
      }, UPDATE_INTERVAL_MS);
    }, firstDelayMs);
  }

  private async updateReviews(
    contextId: string,
    ev: WillAppearEvent | DidReceiveSettingsEvent
  ): Promise<void> {
    const state = this.states.get(contextId);
    if (!state) return;

    const { settings } = state;
    const site = supportedSites[settings.website];
    if (!site) return;

    try {
      streamDeck.logger.info(`Fetching reviews for ${settings.website}...`);
      const count = await site.getReviewCount(settings);
      streamDeck.logger.info(`Got ${count} reviews for ${settings.website}`);
      await this.setIconWithText(ev, settings, String(count));

      // Cache the result in settings
      settings.lastCount = count;
      settings.lastDateTime = new Date().toISOString();
      await ev.action.setSettings({
        ...settings,
      });
    } catch (err) {
      streamDeck.logger.error(`Failed to fetch reviews for ${settings.website}: ${err}`);
      await this.setIconWithText(ev, settings, "?");
    }
  }

  private async setIconWithText(
    ev: { action: { setImage(image: string): Promise<void> } },
    settings: ReviewSettings,
    text: string
  ): Promise<void> {
    const site = supportedSites[settings.website];
    if (!site) return;

    try {
      streamDeck.logger.info(`Rendering icon: ${site.icon} with text "${text}"`);
      const dataUri = await renderReviewIcon(site.icon, text);
      streamDeck.logger.info(`Rendered icon, data URI length: ${dataUri.length}`);
      await ev.action.setImage(dataUri);
    } catch (err) {
      streamDeck.logger.error(`Failed to render icon: ${err}`);
    }
  }

  private clearTimers(contextId: string): void {
    const state = this.states.get(contextId);
    if (!state) return;

    if (state.intervalTimer) clearInterval(state.intervalTimer);
    if (state.initialTimer) clearTimeout(state.initialTimer);
  }
}
