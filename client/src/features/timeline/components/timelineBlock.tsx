import React from "react";
import { ChildNode } from "@/features/timeline/components/childNode";
import type { TimelineNode } from "@/services/types";

interface TimelineBlockProps {
  data: TimelineNode;
  style: React.CSSProperties;
  onAddChild: (parentId: number) => void;
  onEditNode: (node: TimelineNode) => void;
}

export const TimelineBlock: React.FC<TimelineBlockProps> = ({
  data,
  style,
  onAddChild,
  onEditNode,
}) => (
  <div
    style={
      {
        ...style,
        "--lane-height": style.height,
      } as React.CSSProperties & {
        "--lane-height": string | number | undefined;
      }
    }
    className={`
        absolute 
        rounded-lg
        border border-white/10 shadow-lg 
        ${data.color}
        transition-all duration-300
        overflow-hidden
        group
        hover:shadow-2xl hover:brightness-105 hover:scale-[1.005]
        cursor-copy
      `}
  >
    <div className="flex w-full h-full">
      {/* --- LEFT SIDE (30%) - RULE #3: Edit Parent --- */}
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
                cursor-pointer      /* Indicates clickable for edit */
                hover:bg-black/10   /* Feedback */
                transition-colors
            "
        title="Click to Edit this Block"
      >
        <h3
          className="text-white font-bold leading-tight truncate"
          style={{ fontSize: "max(14px, calc(var(--lane-height) * 0.15))" }}
        >
          {data.title}
        </h3>
        <span
          className="text-white/70 font-medium mt-1 block"
          style={{ fontSize: "max(10px, calc(var(--lane-height) * 0.10))" }}
        >
          {new Date(data.startDate || "").getFullYear()} -{" "}
          {new Date(data.endDate || "").getFullYear()}
        </span>
      </div>

      {/* --- RIGHT SIDE (70%) - RULE #4: Add Child --- */}
      <div
        onClick={(e) => {
          e.stopPropagation(); // Don't trigger background
          onAddChild(data.id); // Add child to THIS parent
        }}
        className="
                w-[70%] 
                h-full 
                flex items-center 
                px-6 gap-15 
                overflow-x-auto no-scrollbar
                cursor-copy /* Indicates adding something */
            "
        title="Click empty space to add a child node"
      >
        {data.children?.map((child) => (
          <ChildNode key={child.id} node={child} onEditNode={onEditNode} />
        ))}
      </div>
    </div>
  </div>
);
