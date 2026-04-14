import streamDeck from "@elgato/streamdeck";
import { ReviewAction } from "./actions/review-action";

streamDeck.actions.registerAction(new ReviewAction());
streamDeck.connect();
