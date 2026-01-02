import {
  addHours,
  addDays,
  addMonths,
  addYears,
  startOfHour,
  startOfDay,
  startOfMonth,
  startOfYear,
  endOfDay,
  endOfMonth,
  endOfYear,
  format,
} from "date-fns";
import React, { useMemo } from "react";
import { getXPosition, getWidth } from "@/lib/utils";
import { useAxisStrategy } from "@/shared/hooks/useAxisStrategy";

interface TimeAxisProps {
  // Global boundaries (used for calculating absolute 'left' position)
  timelineStart: Date;

  // Visible boundaries (used for the loop - what we actually draw)
  visibleStartDate: Date;
  visibleEndDate: Date;

  scale: number;
}

export const TimeAxis: React.FC<TimeAxisProps> = ({
  timelineStart,
  visibleStartDate,
  visibleEndDate,
  scale,
}) => {
  const strategy = useAxisStrategy(scale);

  // 1. Generate Primary Ticks
  // CRITICAL FIX: We only loop from visibleStartDate to visibleEndDate
  const ticks = useMemo(() => {
    const items: Date[] = [];

    // Start generating ticks from the visible start, not 50 years ago
    let current = new Date(visibleStartDate);

    // Snap to nearest unit (so ticks don't "swim" as you scroll)
    if (strategy.unit === "hour") current = startOfHour(current);
    else if (strategy.unit === "day") current = startOfDay(current);
    else if (strategy.unit === "month") current = startOfMonth(current);
    else if (strategy.unit === "year") current = startOfYear(current);

    // Loop until we hit the right side of the screen
    while (current < visibleEndDate) {
      items.push(current);

      if (strategy.unit === "hour") {
        current = addHours(current, strategy.step);
      } else if (strategy.unit === "day") {
        current = addDays(current, strategy.step);
      } else if (strategy.unit === "month") {
        current = addMonths(current, strategy.step);
      } else if (strategy.unit === "year") {
        current = addYears(current, strategy.step);
      }
    }
    return items;
  }, [visibleStartDate, visibleEndDate, strategy]);

  // 2. Generate Secondary Brackets
  const secondaryGroups = useMemo(() => {
    if (!strategy.showSecondary) return [];

    const groups: { start: Date; end: Date; label: string }[] = [];

    // Snap start for brackets
    let current = new Date(visibleStartDate);
    if (strategy.unit === "hour") current = startOfDay(current);
    else if (strategy.unit === "day") current = startOfMonth(current);
    else if (strategy.unit === "month") current = startOfYear(current);

    while (current < visibleEndDate) {
      let end: Date;
      let nextStart: Date;

      if (strategy.unit === "hour") {
        end = endOfDay(current);
        nextStart = addDays(current, 1);
      } else if (strategy.unit === "day") {
        end = endOfMonth(current);
        nextStart = addMonths(current, 1);
      } else {
        end = endOfYear(current);
        nextStart = addYears(current, 1);
      }

      groups.push({
        start: current,
        end,
        label: format(current, strategy.secondaryFormat),
      });

      current = nextStart;
    }
    return groups;
  }, [visibleStartDate, visibleEndDate, strategy]);

  return (
    <div className="relative w-full h-14 border-b border-gray-300 bg-gray-50/90 backdrop-blur select-none">
      {/* Brackets */}
      {secondaryGroups.map((group, i) => {
        // NOTE: We still calculate position relative to timelineStart (Global Zero)
        const left = getXPosition(timelineStart, group.start, scale);
        const width = getWidth(group.start, group.end, scale);

        return (
          <div
            key={`sec-${i}`}
            className="absolute top-1 flex justify-center items-center border-l border-r border-t border-gray-400/50"
            style={{ left: `${left}px`, width: `${width}px`, height: "20px" }}
          >
            <span className="text-[10px] font-bold text-gray-500 bg-gray-50 px-2 -mt-6 whitespace-nowrap">
              {group.label}
            </span>
          </div>
        );
      })}

      {/* Ticks */}
      {ticks.map((date, i) => {
        const left = getXPosition(timelineStart, date, scale);
        return (
          <div
            key={`prim-${i}`}
            className="absolute bottom-0 flex flex-col items-center pointer-events-none"
            style={{ left: `${left}px`, transform: "translateX(-50%)" }}
          >
            <div className="h-2 w-px bg-gray-400" />
            <span className="mt-1 text-[10px] text-gray-500 font-medium whitespace-nowrap">
              {format(date, strategy.format)}
            </span>
          </div>
        );
      })}
    </div>
  );
};
