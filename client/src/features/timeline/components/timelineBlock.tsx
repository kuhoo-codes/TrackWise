import React from "react";
import { useMemo } from "react";
import { ChildNode } from "@/features/timeline/components/childNode";
import { getTextWidth } from "@/lib/utils";
import type { TimelineNode } from "@/services/types";

interface TimelineBlockProps {
  data: TimelineNode;
  style: React.CSSProperties;
  width: number;
  onAddChild: (parentId: number) => void;
  onEditNode: (node: TimelineNode) => void;
}

export const TimelineBlock: React.FC<TimelineBlockProps> = ({
  data,
  style,
  width,
  onAddChild,
  onEditNode,
}) => {
  const isCompactMode = useMemo(() => {
    const padding = 32;
    const titleColumnWidth = width * 0.3 - padding;
    const textWidth = getTextWidth(
      data.title,
      "bold 15px ui-sans-serif, system-ui, sans-serif",
    );
    return titleColumnWidth < 40 || textWidth > titleColumnWidth;
  }, [width, data.title]);

  return (
    <div
      style={
        {
          ...style,
          "--lane-height": style.height,
        } as React.CSSProperties
      }
      className="absolute group"
    >
      {/* 1. CAPTION TITLE (Only shows if block is too small) 
          We position this absolute TOP of the block
      */}
      {isCompactMode && (
        <div
          className="absolute -top-7 left-0 w-max max-w-[300px] z-20 cursor-pointer"
          onClick={(e) => {
            e.stopPropagation();
            onEditNode(data);
          }}
        >
          <span className="text-xs font-bold text-gray-700 bg-white/80 px-1.5 py-0.5 rounded border border-gray-200 shadow-sm backdrop-blur-sm hover:text-blue-600">
            {data.title}
          </span>
        </div>
      )}

      {/* 2. THE ACTUAL BLOCK */}
      <div
        className={`
            w-full h-full
            rounded-lg
            border border-white/10 shadow-lg 
            ${data.color}
            overflow-hidden
            hover:shadow-2xl hover:brightness-105 hover:scale-[1.005]
            cursor-copy
            flex
        `}
      >
        {/* LEFT SIDE (Title) - Only render if NOT compact mode */}
        {!isCompactMode && (
          <>
            <div
              onClick={(e) => {
                e.stopPropagation();
                onEditNode(data);
              }}
              className="
                  w-[30%] 
                  h-full 
                  flex flex-col justify-center 
                  px-4
                  border-r border-white/10 
                  bg-black/5 
                  cursor-pointer 
                  hover:bg-black/10
                  transition-colors
              "
              title="Click to Edit"
            >
              <h3
                className="text-white font-bold leading-tight truncate"
                style={{
                  fontSize: "max(14px, calc(var(--lane-height) * 0.15))",
                }}
              >
                {data.title}
              </h3>
              <span
                className="text-white/70 font-medium mt-1 block"
                style={{
                  fontSize: "max(10px, calc(var(--lane-height) * 0.10))",
                }}
              >
                {new Date(data.startDate || "").getFullYear()} -{" "}
                {new Date(data.endDate || "").getFullYear()}
              </span>
            </div>

            {/* RIGHT SIDE (Children) - Only render if NOT compact mode  */}
            <div
              onClick={(e) => {
                e.stopPropagation();
                onAddChild(data.id);
              }}
              className={`
              h-full 
              flex items-center 
              px-6 gap-15 
              overflow-x-auto no-scrollbar
              cursor-copy
              ${isCompactMode ? "w-full" : "w-[70%]"}
          `}
            >
              {data.children?.map((child) => (
                <ChildNode
                  key={child.id}
                  node={child}
                  onEditNode={onEditNode}
                />
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
};
