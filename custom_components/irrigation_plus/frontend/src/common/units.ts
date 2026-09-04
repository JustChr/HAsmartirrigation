import {
  UNIT_DEGREES_C,
  UNIT_DEGREES_F,
  UNIT_MM,
  UNIT_INCH,
  UNIT_HPA,
  UNIT_INHG,
  UNIT_MS,
  UNIT_MH,
} from "../const";

/**
 * Weather value unit conversion. The backend always emits metric (°C, mm, m/s,
 * hPa); when the user selects imperial we convert the value AND swap the unit
 * label. Kept as pure functions (no Lit / no DOM) so they're unit-testable.
 */

export type Quantity =
  | "temperature"
  | "precipitation"
  | "windspeed"
  | "pressure";

export interface Converted {
  value: number;
  unit: string;
}

export const cToF = (c: number): number => (c * 9) / 5 + 32;
export const mmToIn = (mm: number): number => mm / 25.4;
export const msToMph = (ms: number): number => ms * 2.2369362920544;
export const hpaToInHg = (hpa: number): number => hpa * 0.0295299830714;
export const litersToGallons = (l: number): number => l * 0.264172052;

/** Convert a metric weather value to the user's unit system + label. */
export function convertWeather(
  value: number | null | undefined,
  quantity: Quantity,
  metric: boolean,
): Converted | null {
  if (value === null || value === undefined || Number.isNaN(value)) return null;
  switch (quantity) {
    case "temperature":
      return metric
        ? { value, unit: UNIT_DEGREES_C }
        : { value: cToF(value), unit: UNIT_DEGREES_F };
    case "precipitation":
      return metric
        ? { value, unit: UNIT_MM }
        : { value: mmToIn(value), unit: UNIT_INCH };
    case "windspeed":
      return metric
        ? { value, unit: UNIT_MS }
        : { value: msToMph(value), unit: UNIT_MH };
    case "pressure":
      return metric
        ? { value, unit: UNIT_HPA }
        : { value: hpaToInHg(value), unit: UNIT_INHG };
  }
}

/** Sensible decimal places per quantity/system (inches/inHg need more). */
function defaultDecimals(quantity: Quantity, metric: boolean): number {
  if (quantity === "pressure") return metric ? 0 : 2;
  if (quantity === "precipitation") return metric ? 1 : 2;
  return 1; // temperature, windspeed
}

/**
 * Format a metric weather value in the user's units as "<value> <unit>",
 * or "-" when the value is missing.
 */
export function formatWeather(
  value: number | null | undefined,
  quantity: Quantity,
  metric: boolean,
  decimals?: number,
): string {
  const c = convertWeather(value, quantity, metric);
  if (!c) return "-";
  const d = decimals ?? defaultDecimals(quantity, metric);
  return `${c.value.toFixed(d)} ${c.unit}`;
}

/**
 * Format a water volume (backend emits liters) in the user's units as
 * "<value> L" / "<value> gal", or "-" when missing.
 */
export function formatVolume(
  value: number | null | undefined,
  metric: boolean,
): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "-";
  return metric
    ? `${value.toFixed(0)} L`
    : `${litersToGallons(value).toFixed(1)} gal`;
}
