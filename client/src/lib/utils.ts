import { clsx, type ClassValue } from "clsx";
import { differenceInMilliseconds } from "date-fns";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export const LANE_HEIGHT = 150;
export const LANE_GAP = 20;

// Time Constants (ms)
export const ONE_HOUR = 3600000;
export const ONE_DAY = 86400000;
export const ONE_MONTH = 2629800000;
export const ONE_YEAR = 31557600000;

export const MIN_SCALE = 10 / ONE_YEAR;

export const MAX_SCALE = 100 / ONE_HOUR;

export const DEFAULT_SCALE = 100 / ONE_MONTH;

export const getWidth = (start: Date, end: Date, scale: number) => {
  const ms = differenceInMilliseconds(end, start);
  return Math.max(ms * scale, 0);
};

export const getXPosition = (
  viewStartDate: Date,
  itemDate: Date,
  scale: number,
) => {
  const ms = differenceInMilliseconds(itemDate, viewStartDate);
  return ms * scale;
};

export const getDateFromX = (viewStartDate: Date, x: number, scale: number) => {
  const msToAdd = x / scale;
  return new Date(viewStartDate.getTime() + msToAdd);
};
