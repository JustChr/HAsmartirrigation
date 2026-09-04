import { describe, it, expect } from "vitest";
import {
  cToF,
  mmToIn,
  msToMph,
  hpaToInHg,
  litersToGallons,
  convertWeather,
  formatWeather,
  formatVolume,
} from "./units";

describe("units scalar conversions", () => {
  it("cToF", () => {
    expect(cToF(0)).toBe(32);
    expect(cToF(100)).toBe(212);
    expect(cToF(-40)).toBe(-40);
  });
  it("mmToIn", () => {
    expect(mmToIn(25.4)).toBeCloseTo(1, 6);
  });
  it("msToMph", () => {
    expect(msToMph(1)).toBeCloseTo(2.2369, 3);
  });
  it("hpaToInHg", () => {
    expect(hpaToInHg(1000)).toBeCloseTo(29.53, 2);
  });
});

describe("convertWeather", () => {
  it("passes through metric unchanged with the metric label", () => {
    expect(convertWeather(20, "temperature", true)).toEqual({
      value: 20,
      unit: "°C",
    });
  });
  it("converts to imperial with the imperial label", () => {
    expect(convertWeather(20, "temperature", false)).toEqual({
      value: 68,
      unit: "°F",
    });
  });
  it("returns null for missing/NaN", () => {
    expect(convertWeather(null, "precipitation", true)).toBeNull();
    expect(convertWeather(undefined, "windspeed", false)).toBeNull();
    expect(convertWeather(NaN, "pressure", true)).toBeNull();
  });
});

describe("formatWeather", () => {
  it("metric temperature, 1 decimal", () => {
    expect(formatWeather(18.25, "temperature", true)).toBe("18.3 °C");
  });
  it("imperial precipitation uses 2 decimals", () => {
    expect(formatWeather(25.4, "precipitation", false)).toBe("1.00 in");
  });
  it("metric pressure 0 decimals, imperial 2", () => {
    expect(formatWeather(1013, "pressure", true)).toBe("1013 hPa");
    expect(formatWeather(1013, "pressure", false)).toBe("29.91 inch Hg");
  });
  it("missing value renders a dash", () => {
    expect(formatWeather(null, "temperature", true)).toBe("-");
  });
});

describe("formatVolume", () => {
  it("metric liters, no decimals", () => {
    expect(formatVolume(1234.2, true)).toBe("1234 L");
  });
  it("imperial gallons", () => {
    expect(litersToGallons(100)).toBeCloseTo(26.42, 2);
    expect(formatVolume(100, false)).toBe("26.4 gal");
  });
  it("missing renders a dash", () => {
    expect(formatVolume(undefined, false)).toBe("-");
  });
});
