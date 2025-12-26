import { clsx, type ClassValue } from "clsx";
import { differenceInDays } from "date-fns";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export const LANE_HEIGHT = 150;
export const LANE_GAP = 20;
export const PIXELS_PER_DAY = 2;

export const getWidth = (start: Date, end: Date) => {
  const days = differenceInDays(end, start);
  return Math.max(days * PIXELS_PER_DAY, 100);
};

export const getXPosition = (viewStartDate: Date, itemDate: Date) => {
  const days = differenceInDays(itemDate, viewStartDate);
  return days * PIXELS_PER_DAY;
};
