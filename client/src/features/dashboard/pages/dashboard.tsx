import { Plus, Trash2 } from "lucide-react";
import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ROUTES } from "@/app/router/routes";
import {
  CreateTimelineModal,
  type CreateTimelineFormValues,
} from "@/features/dashboard/components/createTimelineModal";
import { DeleteConfirmationModal } from "@/features/dashboard/components/deleteConfirmationModal";
import { TimelineService } from "@/services/timeline";
import type { TimelineSummary, TimelineCreateRequest } from "@/services/types";
import { useAuth } from "@/shared/hooks/useAuth";

export const Dashboard: React.FC = () => {
  const { token } = useAuth();
  const [timelines, setTimelines] = useState<TimelineSummary[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [timelineToDelete, setTimelineToDelete] = useState<number | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const fetchTimelines = async () => {
    if (!token) return;
    try {
      const data = await TimelineService.getTimelines();
      setTimelines(data);
    } catch (error) {
      console.error("Failed to load timelines", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    void fetchTimelines();
  }, [token]);

  const handleCreateTimeline = async (data: CreateTimelineFormValues) => {
    if (!token) return;
    try {
      const payload: TimelineCreateRequest = {
        title: data.title,
        description: data.description ?? "",
        isPublic: data.isPublic,
        defaultZoomLevel: data.defaultZoomLevel,
      };
      await TimelineService.createTimeline(payload);
      await fetchTimelines();
      setIsCreateModalOpen(false);
    } catch (error) {
      console.error("Failed to create timeline", error);
    }
  };

  const handleDeleteClick = (e: React.MouseEvent, id: number) => {
    e.preventDefault();
    e.stopPropagation();
    setTimelineToDelete(id);
  };

  const confirmDelete = async () => {
    if (!token || !timelineToDelete) return;

    setIsDeleting(true);
    try {
      await TimelineService.deleteTimeline(timelineToDelete);
      setTimelines((prev) => prev.filter((t) => t.id !== timelineToDelete));
      setTimelineToDelete(null);
    } catch (error) {
      console.error("Failed to delete timeline", error);
      alert("Failed to delete timeline");
    } finally {
      setIsDeleting(false);
    }
  };

  if (isLoading) return <div>Loading Dashboard...</div>;
  return (
    <div className="max-w-5xl mx-auto px-6 py-10">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900">My Timelines</h1>
        <button
          onClick={() => setIsCreateModalOpen(true)}
          className="flex items-center gap-2 bg-black text-white px-4 py-2 rounded-lg hover:bg-gray-800 transition"
        >
          <Plus className="w-4 h-4" />
          Create New
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {timelines.map((timeline) => (
          <Link
            key={timeline.id}
            to={`${ROUTES.TIMELINE}/${timeline.id}`}
            className="block group"
          >
            <div className="relative border border-gray-200 rounded-xl p-6 hover:shadow-lg transition-all bg-white h-full flex flex-col">
              {/* --- DELETE BUTTON (Visible on Hover) --- */}
              <button
                onClick={(e) => handleDeleteClick(e, timeline.id)}
                className="absolute top-0.5 right-4 p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-full opacity-0 group-hover:opacity-100 transition-all duration-200 z-10"
                title="Delete Timeline"
              >
                <Trash2 className="w-4 h-4" />
              </button>
              <h2 className="text-xl font-bold text-gray-900 group-hover:text-blue-600 mb-2">
                {timeline.title}
              </h2>
              <p className="text-gray-500 text-sm flex-1">
                {timeline.description || "No description provided."}
              </p>
              <div className="mt-4 pt-4 border-t border-gray-50 flex justify-between text-xs text-gray-400">
                <span>{timeline.isPublic ? "Public" : "Private"}</span>
                <span>
                  Last updated {timeline.updatedAt.toLocaleDateString()}
                </span>
              </div>
            </div>
          </Link>
        ))}
      </div>

      {timelines.length === 0 && (
        <div className="text-center py-20 bg-gray-50 rounded-2xl border-2 border-dashed border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">
            No timelines yet
          </h3>
          <p className="text-gray-500 mb-4">
            Create your first timeline to get started tracking your journey.
          </p>
        </div>
      )}

      {/* Render Modals */}
      <CreateTimelineModal
        isOpen={isCreateModalOpen}
        onOpenChange={setIsCreateModalOpen}
        onSubmit={handleCreateTimeline}
      />

      <DeleteConfirmationModal
        isOpen={!!timelineToDelete}
        onOpenChange={(open) => !open && setTimelineToDelete(null)}
        onConfirm={confirmDelete}
        isDeleting={isDeleting}
      />
    </div>
  );
};
