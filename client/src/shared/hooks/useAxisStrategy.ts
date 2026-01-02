import { ONE_HOUR, ONE_DAY, ONE_MONTH, ONE_YEAR } from "@/lib/utils";

export interface TickStrategy {
  unit: "hour" | "day" | "month" | "year";
  step: number; // e.g., 2 means "Every 2nd hour"
  format: string; // e.g., "HH:mm"
  secondaryFormat: string; // The bracket label (e.g., "16th May 2024")
  showSecondary: boolean; // Should we show the bracket layer?
}

export const useAxisStrategy = (scale: number): TickStrategy => {
  const pxPerHour = ONE_HOUR * scale;
  const pxPerDay = ONE_DAY * scale;
  const pxPerMonth = ONE_MONTH * scale;
  const pxPerYear = ONE_YEAR * scale;

  // --- STAGE 1: HOURS (Zoomed In) ---
  // We want at least 60px between ticks to read "10 am"
  if (pxPerHour > 60) {
    return {
      unit: "hour",
      step: 1,
      format: "h a",
      secondaryFormat: "do MMMM yyyy",
      showSecondary: true,
    };
  }
  if (pxPerHour > 30) {
    return {
      unit: "hour",
      step: 2,
      format: "h a",
      secondaryFormat: "do MMMM yyyy",
      showSecondary: true,
    };
  }
  if (pxPerHour > 15) {
    return {
      unit: "hour",
      step: 4,
      format: "h a",
      secondaryFormat: "do MMMM yyyy",
      showSecondary: true,
    };
  }
  if (pxPerHour > 10) {
    return {
      unit: "hour",
      step: 6,
      format: "h a",
      secondaryFormat: "do MMMM yyyy",
      showSecondary: true,
    };
  }
  if (pxPerHour > 5) {
    return {
      unit: "hour",
      step: 12,
      format: "h a",
      secondaryFormat: "do MMMM yyyy",
      showSecondary: true,
    };
  }

  // --- STAGE 2: DAYS ---
  // We want at least 40px between days
  if (pxPerDay > 200) {
    return {
      unit: "day",
      step: 1,
      format: "d",
      secondaryFormat: "MMMM yyyy",
      showSecondary: true,
    };
  }
  if (pxPerDay > 100) {
    return {
      unit: "day",
      step: 2,
      format: "d",
      secondaryFormat: "MMMM yyyy",
      showSecondary: true,
    };
  }
  if (pxPerDay > 50) {
    return {
      unit: "day",
      step: 5,
      format: "d",
      secondaryFormat: "MMMM yyyy",
      showSecondary: true,
    };
  }
  if (pxPerDay > 25) {
    return {
      unit: "day",
      step: 10,
      format: "d",
      secondaryFormat: "MMMM yyyy",
      showSecondary: true,
    };
  }

  // --- STAGE 3: MONTHS ---
  // We want at least 50px between months
  if (pxPerMonth > 150) {
    return {
      unit: "month",
      step: 1,
      format: "MMM",
      secondaryFormat: "yyyy",
      showSecondary: true,
    };
  }
  if (pxPerMonth > 70) {
    return {
      unit: "month",
      step: 3,
      format: "MMM",
      secondaryFormat: "yyyy",
      showSecondary: true,
    };
  }

  // --- STAGE 4: YEARS (Zoomed Out) ---
  // Step 21-32: Years become the primary tick, Brackets disappear
  if (pxPerYear > 100) {
    return {
      unit: "year",
      step: 1,
      format: "yyyy",
      secondaryFormat: "",
      showSecondary: false,
    };
  }
  if (pxPerYear > 50) {
    return {
      unit: "year",
      step: 2,
      format: "yyyy",
      secondaryFormat: "",
      showSecondary: false,
    };
  }
  if (pxPerYear > 25) {
    return {
      unit: "year",
      step: 5,
      format: "yyyy",
      secondaryFormat: "",
      showSecondary: false,
    };
  }

  // Decades
  return {
    unit: "year",
    step: 10,
    format: "yyyy",
    secondaryFormat: "",
    showSecondary: false,
  };
};
