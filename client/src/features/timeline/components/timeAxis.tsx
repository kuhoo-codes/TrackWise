import { addMonths, differenceInMonths, format } from "date-fns";
import { getXPosition } from "@/lib/utils";

interface TimeAxisProps {
  startDate: Date;
  endDate: Date;
}

export const TimeAxis: React.FC<TimeAxisProps> = ({ startDate, endDate }) => {
  const totalMonths = differenceInMonths(endDate, startDate);
  const months = Array.from({ length: totalMonths + 1 }).map((_, i) =>
    addMonths(startDate, i),
  );

  return (
    <div className="relative w-full h-12 border-b border-gray-300 bg-gray-50/50">
      {months.map((date, i) => {
        const left = getXPosition(startDate, date);
        const isYearStart = date.getMonth() === 0;

        return (
          <div
            key={i}
            className="absolute bottom-0 flex flex-col items-start pointer-events-none"
            style={{ left: `${left}px` }}
          >
            <div
              className={`w-px ${isYearStart ? "h-6 bg-gray-800" : "h-3 bg-gray-400"}`}
            />

            <span
              className={`ml-1 text-xs ${isYearStart ? "font-bold text-gray-900" : "text-gray-500"}`}
            >
              {isYearStart ? format(date, "yyyy") : format(date, "MMM")}
            </span>
          </div>
        );
      })}
    </div>
  );
};
