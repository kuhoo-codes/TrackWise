import React, { useMemo, useState } from "react";
import { TimeAxis } from "@/features/timeline/components/timeAxis";
import { TimelineBlock } from "@/features/timeline/components/timelineBlock";
import { TimelineNodeModal } from "@/features/timeline/components/timelineNodeModal";
import type { TimelineNodeFormValues } from "@/features/timeline/components/types";
import { getWidth, getXPosition, LANE_HEIGHT, LANE_GAP } from "@/lib/utils";
import type { TimelineNode } from "@/services/types";
import { useTimeline } from "@/shared/hooks/useTimeline";

interface TimelineProps {
  timelineId: number;
}

export const Timeline: React.FC<TimelineProps> = ({ timelineId }) => {
  const [isModalOpen, setIsModalOpen] = useState(false);

  const [modalInitialData, setModalInitialData] = useState<
    Partial<TimelineNodeFormValues> & { id?: number }
  >({});
  const { nodes, isLoading, error, createNode, updateNode, deleteNode } =
    useTimeline(timelineId);

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

  const uiItems = useMemo(
    () =>
      nodes.map((node) => ({
        ...node,
        startDate: node.startDate,
        endDate: node.endDate ?? new Date(),
      })),
    [nodes],
  );

  const { viewStartDate, viewEndDate } = useMemo(() => {
    if (uiItems.length === 0) {
      const viewEndDate = new Date();
      const viewStartDate = new Date();
      viewStartDate.setFullYear(viewStartDate.getFullYear() - 1);
      viewEndDate.setFullYear(viewEndDate.getFullYear() + 1);

      return { viewStartDate, viewEndDate };
    }

    const sorted = [...uiItems].sort(
      (a, b) => a.startDate.getTime() - b.startDate.getTime(),
    );
    const endSorted = [...uiItems].sort(
      (a, b) => b.endDate.getTime() - a.endDate.getTime(),
    );

    if (!sorted[0] || !endSorted[0]) {
      return { viewStartDate: new Date(), viewEndDate: new Date() };
    }

    return {
      viewStartDate: new Date(sorted[0].startDate.getTime() - 2592000000), // -1 Month padding
      viewEndDate: new Date(endSorted[0].endDate.getTime() + 2592000000), // +1 Month padding
    };
  }, [uiItems]);

  const itemsWithLanes = useMemo(() => {
    const sortedItems = [...uiItems].sort(
      (a, b) => a.startDate.getTime() - b.startDate.getTime(),
    );
    const lanes: Date[] = [];

    return sortedItems.map((item) => {
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

  const maxLaneIndex = Math.max(...itemsWithLanes.map((i) => i.laneIndex), 0);
  const containerHeight = (maxLaneIndex + 1) * (LANE_HEIGHT + LANE_GAP) + 100;
  const containerWidth = getXPosition(viewStartDate, viewEndDate);

  const availableParents = useMemo(
    () =>
      uiItems
        .filter((i) => !i.parentId)
        .map((i) => ({ id: i.id, title: i.title })),
    [uiItems],
  );

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  // --- RENDER ---
  return (
    <div className="w-full h-screen flex flex-col bg-gray-50 overflow-hidden">
      <div
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
              const left = getXPosition(viewStartDate, item.startDate);
              const width = getWidth(item.startDate, item.endDate);

              const bottom = item.laneIndex * (LANE_HEIGHT + LANE_GAP);

              return (
                <div key={item.id} className="pointer-events-auto">
                  <TimelineBlock
                    data={item}
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
            <TimeAxis startDate={viewStartDate} endDate={viewEndDate} />
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
