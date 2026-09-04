/**
 * Small date/time helpers built on the platform `Intl` API and plain `Date`
 * math, replacing the former `moment` dependency.
 *
 * All formatting uses the browser's local time zone (matching the previous
 * `moment(value)` behaviour). Numeric formats are hand-padded so output is
 * deterministic across locales; weekday names and relative ("x ago") strings
 * are localized via `Intl` using the caller-provided HA language.
 */

const pad = (n: number): string => String(n).padStart(2, "0");

/** Parse anything `moment(value)` accepted into a `Date` (or an invalid Date). */
export function toDate(value: string | number | Date): Date {
  return value instanceof Date ? value : new Date(value);
}

/** True when the value parses to a real date (mirrors `moment().isValid()`). */
export function isValidDate(value: string | number | Date): boolean {
  return !Number.isNaN(toDate(value).getTime());
}

/** `HH:mm`, 24-hour, local time (was `moment(d).format("HH:mm")`). */
export function formatTime(value: string | number | Date): string {
  const d = toDate(value);
  return `${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

/** `YYYY-MM-DD HH:mm`, local time. */
export function formatDateTime(value: string | number | Date): string {
  const d = toDate(value);
  return (
    `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ` +
    `${pad(d.getHours())}:${pad(d.getMinutes())}`
  );
}

/** `MM-DD HH:mm`, local time (compact weather-record stamp). */
export function formatMonthDayTime(value: string | number | Date): string {
  const d = toDate(value);
  return `${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(
    d.getMinutes(),
  )}`;
}

/** Localized short weekday + time, e.g. `Mon 06:00` (was `format("ddd HH:mm")`). */
export function formatWeekdayTime(
  value: string | number | Date,
  lang: string,
): string {
  const d = toDate(value);
  const weekday = new Intl.DateTimeFormat(lang, { weekday: "short" }).format(d);
  return `${weekday} ${formatTime(d)}`;
}

/** True when both instants fall on the same local calendar day. */
export function isSameDay(a: Date, b: Date): boolean {
  return (
    a.getFullYear() === b.getFullYear() &&
    a.getMonth() === b.getMonth() &&
    a.getDate() === b.getDate()
  );
}

/** A new `Date` shifted by `n` whole days (negative to go back). */
export function addDays(d: Date, n: number): Date {
  const out = new Date(d.getTime());
  out.setDate(out.getDate() + n);
  return out;
}

/**
 * Localized relative time, e.g. "2 hours ago" / "in 3 days"
 * (was `moment(d).fromNow()`). Picks the largest sensible unit.
 */
export function fromNow(value: string | number | Date, lang: string): string {
  const diffMs = toDate(value).getTime() - Date.now();
  const rtf = new Intl.RelativeTimeFormat(lang, { numeric: "auto" });
  const sec = Math.round(diffMs / 1000);
  const abs = Math.abs(sec);
  if (abs < 60) return rtf.format(sec, "second");
  const min = Math.round(sec / 60);
  if (Math.abs(min) < 60) return rtf.format(min, "minute");
  const hr = Math.round(min / 60);
  if (Math.abs(hr) < 24) return rtf.format(hr, "hour");
  const day = Math.round(hr / 24);
  if (Math.abs(day) < 30) return rtf.format(day, "day");
  const month = Math.round(day / 30);
  if (Math.abs(month) < 12) return rtf.format(month, "month");
  return rtf.format(Math.round(month / 12), "year");
}
