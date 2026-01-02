import { addYears } from "date-fns/addYears";
import { Plus, Minus } from "lucide-react";
import React, {
  useEffect,
  useLayoutEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { TimeAxis } from "@/features/timeline/components/timeAxis";
import { TimelineBlock } from "@/features/timeline/components/timelineBlock";
import { TimelineNodeModal } from "@/features/timeline/components/timelineNodeModal";
import type { TimelineNodeFormValues } from "@/features/timeline/components/types";
import {
  getWidth,
  getXPosition,
  LANE_HEIGHT,
  LANE_GAP,
  DEFAULT_SCALE,
  MIN_SCALE,
  MAX_SCALE,
  getDateFromX,
} from "@/lib/utils";
import type { TimelineNode } from "@/services/types";
import { useTimeline } from "@/shared/hooks/useTimeline";

interface TimelineProps {
  timelineId: number;
}

export const Timeline: React.FC<TimelineProps> = ({ timelineId }) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [scale, setScale] = useState(DEFAULT_SCALE);
  const [scrollLeft, setScrollLeft] = useState(0);
  const [modalInitialData, setModalInitialData] = useState<
    Partial<TimelineNodeFormValues> & { id?: number }
  >({});

  const containerRef = useRef<HTMLDivElement>(null);
  const hasInitializedScroll = useRef(false);
  const zoomAnchorRef = useRef<{ time: Date; offsetFromLeft: number } | null>(
    null,
  );

  const { nodes, isLoading, error, createNode, updateNode, deleteNode } =
    useTimeline(timelineId);

  const uiItems = useMemo(
    () =>
      nodes.map((node) => ({
        ...node,
        startDate: node.startDate,
        endDate: node.endDate ?? new Date(),
      })),
    [nodes],
  );

  const handleOpenAddModal = (parentId = 0) => {
    setModalInitialData({
      parentId,
    });
    setIsModalOpen(true);
  };

  const handleOpenEditModal = (node: TimelineNode) => {
    setModalInitialData({
      id: node.id,
      title: node.title,
      type: node.type,
      parentId: node.parentId,
      startDate: node.startDate,
      endDate: node.endDate,
      isCurrent: node.isCurrent,
      shortSummary: node.shortSummary,
      description: node.description,
      privateNotes: node.privateNotes,
    });
    setIsModalOpen(true);
  };

  const handleBackgroundClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      handleOpenAddModal(0);
    }
  };

  const handleModalSubmit = async (data: TimelineNodeFormValues) => {
    try {
      if (modalInitialData.id) {
        await updateNode(modalInitialData.id, data);
      } else {
        await createNode(data);
      }

      setIsModalOpen(false);
    } catch (err) {
      console.error("Failed to save node:", err);
    }
  };

  const handleDeleteNode = async (id: number) => {
    if (confirm("Delete this node?")) {
      await deleteNode(id);
      setIsModalOpen(false);
    }
  };

  const { viewStartDate, viewEndDate } = useMemo(() => {
    let start = new Date();
    let end = new Date();

    if (uiItems.length > 0) {
      const startTimes = uiItems.map((i) => i.startDate.getTime());
      const endTimes = uiItems.map((i) => i.endDate.getTime());
      start = new Date(Math.min(...startTimes));
      end = new Date(Math.max(...endTimes));
    }

    return {
      viewStartDate: addYears(start, -50),
      viewEndDate: addYears(end, 50),
    };
  }, [uiItems]);

  // 2. VIRTUALIZATION ENGINE
  const { visibleStart, visibleEnd } = useMemo(() => {
    const containerWidth = containerRef.current?.clientWidth || 0;

    const bufferPixels = containerWidth;

    const startPixel = Math.max(0, scrollLeft - bufferPixels);
    const endPixel = scrollLeft + containerWidth + bufferPixels;

    const vStart = getDateFromX(viewStartDate, startPixel, scale);
    const vEnd = getDateFromX(viewStartDate, endPixel, scale);

    return { visibleStart: vStart, visibleEnd: vEnd };
  }, [scrollLeft, scale, viewStartDate]);

  // 3. SCROLL LISTENER
  const onScroll = () => {
    if (containerRef.current) {
      // We use requestAnimationFrame to prevent thrashing
      requestAnimationFrame(() => {
        if (containerRef.current) {
          setScrollLeft(containerRef.current.scrollLeft);
        }
      });
    }
  };

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const handleWheel = (e: WheelEvent) => {
      if (e.ctrlKey) {
        e.preventDefault();
        const rect = container.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const absoluteX = container.scrollLeft + mouseX;

        const timeUnderMouse = getDateFromX(viewStartDate, absoluteX, scale);

        zoomAnchorRef.current = {
          time: timeUnderMouse,
          offsetFromLeft: mouseX,
        };

        const zoomFactor = e.deltaY < 0 ? 1.05 : 0.95;
        const newScale = Math.min(
          Math.max(scale * zoomFactor, MIN_SCALE),
          MAX_SCALE,
        );

        setScale(newScale);
      }
    };

    container.addEventListener("wheel", handleWheel, { passive: false });
    return () => container.removeEventListener("wheel", handleWheel);
  }, [scale, isLoading, viewStartDate]);

  useLayoutEffect(() => {
    const container = containerRef.current;

    // Safety check: If container isn't ready, we can't scroll
    if (!container) return;

    // --- CASE 1: HANDLE ZOOMING (Priority) ---
    // If we have an anchor, the user is actively zooming.
    // We must respect this position to prevent "jumping".
    if (zoomAnchorRef.current) {
      const anchor = zoomAnchorRef.current;
      const newAbsoluteX = getXPosition(viewStartDate, anchor.time, scale);

      container.scrollLeft = newAbsoluteX - anchor.offsetFromLeft;

      // Reset the anchor now that we've handled it
      zoomAnchorRef.current = null;
      return; // Stop here. We don't want to init-scroll if we are zooming.
    }

    // --- CASE 2: HANDLE INITIAL LOAD (Secondary) ---
    // If we haven't zoomed, and we haven't initialized the view yet...
    if (!hasInitializedScroll.current && !isLoading && nodes.length > 0) {
      const clientWidth = container.clientWidth;

      // Center on "Today"
      const targetDate = new Date();
      const xPos = getXPosition(viewStartDate, targetDate, scale);
      const initialScroll = xPos - clientWidth / 2;

      container.scrollLeft = initialScroll;
      hasInitializedScroll.current = true;
    }
  }, [scale, viewStartDate, isLoading, nodes.length]);

  const handleManualZoom = (direction: "in" | "out") => {
    const container = containerRef.current;
    if (!container) return;

    const clientWidth = container.clientWidth;
    const centerOffset = clientWidth / 2;
    const centerPixelAbsolute = container.scrollLeft + centerOffset;

    const timeAtCenter = getDateFromX(
      viewStartDate,
      centerPixelAbsolute,
      scale,
    );

    zoomAnchorRef.current = {
      time: timeAtCenter,
      offsetFromLeft: centerOffset,
    };

    const factor = direction === "in" ? 1.5 : 0.6;
    const newScale = Math.min(Math.max(scale * factor, MIN_SCALE), MAX_SCALE);

    setScale(newScale);
  };

  const itemsWithLanes = useMemo(() => {
    const sorted = [...uiItems].sort(
      (a, b) => a.startDate.getTime() - b.startDate.getTime(),
    );
    const lanes: Date[] = [];

    return sorted.map((item) => {
      let laneIndex = lanes.findIndex(
        (laneEnd) => item.startDate.getTime() > laneEnd.getTime(),
      );
      if (laneIndex === -1) {
        laneIndex = lanes.length;
        lanes.push(item.endDate);
      } else {
        lanes[laneIndex] = item.endDate;
      }
      return { ...item, laneIndex };
    });
  }, [uiItems]);

  const availableParents = useMemo(
    () =>
      uiItems
        .filter((i) => !i.parentId)
        .map((i) => ({ id: i.id, title: i.title })),
    [uiItems],
  );

  const containerWidth = getXPosition(viewStartDate, viewEndDate, scale);
  const maxLaneIndex = Math.max(...itemsWithLanes.map((i) => i.laneIndex), 0);
  const containerHeight = (maxLaneIndex + 1) * (LANE_HEIGHT + LANE_GAP) + 100;

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  // --- RENDER ---
  return (
    <div className="w-full h-screen flex flex-col bg-gray-50 overflow-hidden">
      {/* --- ZOOM CONTROLS UI --- */}
      <div className="absolute bottom-8 right-8 z-50 flex flex-col gap-2 shadow-xl rounded-lg bg-white p-1 border border-gray-200">
        <button
          onClick={() => handleManualZoom("in")}
          className="p-2 hover:bg-gray-100 rounded text-gray-700 transition-colors"
          title="Zoom In"
        >
          <Plus size={20} />
        </button>
        <div className="h-px w-full bg-gray-200" />
        <button
          onClick={() => handleManualZoom("out")}
          className="p-2 hover:bg-gray-100 rounded text-gray-700 transition-colors"
          title="Zoom Out"
        >
          <Minus size={20} />
        </button>
      </div>
      <div
        ref={containerRef}
        onScroll={onScroll}
        className="flex-1 overflow-auto relative cursor-default"
        title="Click empty space to add a new Timeline Block"
      >
        <div
          className="relative"
          style={{
            width: `${containerWidth}px`,
            height: `${containerHeight}px`,
          }}
          onClick={handleBackgroundClick}
        >
          {/* 1. The Blocks Layer */}
          <div className="relative mt-8 h-full pointer-events-none">
            {itemsWithLanes.map((item) => {
              const left = getXPosition(viewStartDate, item.startDate, scale);
              const width = getWidth(item.startDate, item.endDate, scale);
              const bottom = item.laneIndex * (LANE_HEIGHT + LANE_GAP);

              return (
                <div key={item.id} className="pointer-events-auto">
                  <TimelineBlock
                    data={item}
                    width={width}
                    style={{
                      left: `${left}px`,
                      width: `${width}px`,
                      height: `${LANE_HEIGHT}px`,
                      bottom: `${bottom}px`,
                    }}
                    onAddChild={() => handleOpenAddModal(item.id)} // Rule #4
                    onEditNode={handleOpenEditModal} // Rule #3 & #1
                  />
                </div>
              );
            })}
          </div>

          {/* 2. The Time Axis Layer (Sticky Top) */}
          <div className="sticky top-0 z-20 bg-gray-50/95 backdrop-blur pt-5 border-b pointer-events-auto">
            <TimeAxis
              timelineStart={viewStartDate} // The global anchor (0px)
              visibleStartDate={visibleStart} // The loop start
              visibleEndDate={visibleEnd} // The loop end
              scale={scale}
            />
          </div>
        </div>
      </div>

      {/* --- THE MODAL --- */}
      <TimelineNodeModal
        isOpen={isModalOpen}
        onOpenChange={setIsModalOpen}
        onSubmit={handleModalSubmit}
        onDelete={(id) => {
          void handleDeleteNode(id);
        }}
        availableParents={availableParents}
        timelineId={timelineId}
        initialData={modalInitialData}
      />
    </div>
  );
};
