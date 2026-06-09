import * as en from "./languages/en.json";

import IntlMessageFormat from "intl-messageformat";
import { AVAILABLE_LANGUAGES, LANG_BASE_URL } from "../src/const";

// Only English is bundled (built-in fallback). Every other supported language
// is fetched once from the integration's static path and cached here, so the
// frontend bundles no longer carry all 8 languages. `localize()` falls back to
// English for any language or key not (yet) loaded.
const languages: Record<string, any> = { en };
const loaders: Record<string, Promise<void>> = {};

/** Normalize an HA language code ("de-DE") to a supported base code ("de"). */
function baseLang(language: string): string {
  return language
    .replace(/['"]+/g, "")
    .split(/[-_]/)[0]
    .toLowerCase();
}

/**
 * True when the active language is ready to render: English (built in), an
 * already-fetched language, or an unsupported code (which renders as English).
 */
export function isTranslationLoaded(language: string): boolean {
  const lang = baseLang(language);
  return (
    lang in languages || !AVAILABLE_LANGUAGES.includes(lang) // unsupported -> en
  );
}

/**
 * Ensure the active language's strings are available. Resolves immediately for
 * English / already-loaded / unsupported languages; otherwise fetches the JSON
 * once and caches it. On failure it keeps English as the fallback. The returned
 * promise lets callers re-render once the strings are in.
 */
export function ensureTranslations(language: string): Promise<void> {
  const lang = baseLang(language);
  if (isTranslationLoaded(language)) return Promise.resolve();
  if (!loaders[lang]) {
    loaders[lang] = fetch(`${LANG_BASE_URL}/${lang}.json`)
      .then((r) => (r.ok ? r.json() : Promise.reject(r.status)))
      .then((data) => {
        languages[lang] = data;
      })
      .catch(() => {
        // Keep English as the fallback; cache so we don't refetch on re-render.
        languages[lang] = languages["en"];
      });
  }
  return loaders[lang];
}

export function localize(
  string: string,
  language: string,
  ...args: any[]
): string {
  const lang = baseLang(language);
  let translated: string;

  try {
    translated = string.split(".").reduce((o, i) => o[i], languages[lang]);
  } catch (e) {
    translated = string.split(".").reduce((o, i) => o[i], languages["en"]);
  }

  if (translated === undefined)
    translated = string.split(".").reduce((o, i) => o[i], languages["en"]);

  if (!args.length) return translated;

  const argObject = {};
  for (let i = 0; i < args.length; i += 2) {
    let key = args[i];
    key = key.replace(/^{([^}]+)?}$/, "$1");
    argObject[key] = args[i + 1];
  }

  try {
    const message = new IntlMessageFormat(translated, language);
    return message.format(argObject) as string;
  } catch (err) {
    return "Translation " + err;
  }
}
