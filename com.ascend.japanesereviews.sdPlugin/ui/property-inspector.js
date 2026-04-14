let websocket = null;
let uuid = null;
let actionInfo = {};

const placeholders = {
  bunpro: "Bunpro API Token",
  wanikani: "Wanikani V2 API Token (read-only)",
  "marumori-vocab": "MaruMori API Key",
  "marumori-grammar": "MaruMori API Key",
};

function showFieldsBySelectedWebsite() {
  const website = document.getElementById("websiteSelect").value;
  const apiKeyGroup = document.getElementById("apiKeyGroup");
  const credentialsGroup = document.getElementById("credentialsGroup");
  const apiKeyField = document.getElementById("apiKey");

  if (website === "kitsun") {
    apiKeyGroup.style.display = "none";
    credentialsGroup.style.display = "";
  } else {
    apiKeyGroup.style.display = "";
    credentialsGroup.style.display = "none";
    apiKeyField.placeholder = placeholders[website] || "API Token";
  }
}

function refreshSettings(settings) {
  const apiKeyField = document.getElementById("apiKey");
  const websiteField = document.getElementById("websiteSelect");
  const usernameField = document.getElementById("username");
  const passwordField = document.getElementById("password");

  if (settings) {
    apiKeyField.value = settings.apiKey ?? "";
    websiteField.value = settings.website ?? "bunpro";
    usernameField.value = settings.username ?? "";
    passwordField.value = settings.password ?? "";

    showFieldsBySelectedWebsite();
  }

  apiKeyField.disabled = false;
  websiteField.disabled = false;
  usernameField.disabled = false;
  passwordField.disabled = false;
}

function updateSettings() {
  const payload = {
    apiKey: document.getElementById("apiKey").value,
    website: document.getElementById("websiteSelect").value,
    username: document.getElementById("username").value,
    password: document.getElementById("password").value,
  };

  const setSettings = {
    event: "setSettings",
    context: uuid,
    payload: payload,
  };

  websocket.send(JSON.stringify(setSettings));
}

function onWebsiteChange() {
  showFieldsBySelectedWebsite();
  updateSettings();
}

function connectElgatoStreamDeckSocket(
  inPort,
  inUUID,
  inRegisterEvent,
  info,
  inActionInfo
) {
  uuid = inUUID;
  actionInfo = JSON.parse(inActionInfo);
  websocket = new WebSocket("ws://localhost:" + inPort);

  refreshSettings(actionInfo.payload.settings);

  websocket.onopen = function () {
    websocket.send(
      JSON.stringify({
        event: inRegisterEvent,
        uuid: inUUID,
      })
    );
  };

  websocket.onmessage = function (evt) {
    const jsonObj = JSON.parse(evt.data);
    switch (jsonObj.event) {
      case "didReceiveSettings":
        refreshSettings(jsonObj.payload.settings);
        break;
      case "propertyInspectorDidDisappear":
        updateSettings();
        break;
      default:
        break;
    }
  };
}
