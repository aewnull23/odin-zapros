import WebApp from "@twa-dev/sdk";

export function initTelegram(): void {
  WebApp.ready();
  WebApp.expand();
  const tp = WebApp.themeParams;
  const root = document.documentElement;
  if (tp.bg_color) root.style.setProperty("--tg-bg", tp.bg_color);
  if (tp.text_color) root.style.setProperty("--tg-text", tp.text_color);
  if (tp.button_color) root.style.setProperty("--tg-button", tp.button_color);
  if (tp.button_text_color) root.style.setProperty("--tg-button-text", tp.button_text_color);
  if (tp.secondary_bg_color) root.style.setProperty("--tg-secondary", tp.secondary_bg_color);
}

export function getInitData(): string {
  return WebApp.initData || "";
}

export function showBookSuccess(message: string): void {
  WebApp.showAlert(message);
}

export function openBookingLink(url: string): void {
  WebApp.openLink(url);
}

export { WebApp };
