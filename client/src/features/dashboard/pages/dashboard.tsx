import { Plus, Trash2, ChevronDown, Github, Clock } from "lucide-react";
import React, { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { ROUTES } from "@/app/router/routes";
import { ConnectGithubButton } from "@/features/dashboard/components/connectGithubButton";
import { CreateFromGithubModal } from "@/features/dashboard/components/createFromGithubModal";
import {
  CreateTimelineModal,
  type CreateTimelineFormValues,
} from "@/features/dashboard/components/createTimelineModal";
import { DeleteConfirmationModal } from "@/features/dashboard/components/deleteConfirmationModal";
import { useGithubConnect } from "@/shared/hooks/useGithubConnect";
import { useTimelines } from "@/shared/hooks/useTimelines";

export const Dashboard: React.FC = () => {
  const { timelines, isLoading, isDeleting, createTimeline, deleteTimeline } =
    useTimelines();
  const { isConnected } = useGithubConnect(); // Check if GitHub is connected

  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isGithubModalOpen, setIsGithubModalOpen] = useState(false); // <-- New state
  const [timelineToDelete, setTimelineToDelete] = useState<number | null>(null);

  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setIsDropdownOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleCreateTimeline = async (data: CreateTimelineFormValues) => {
    const success = await createTimeline(data);
    if (success) {
      setIsCreateModalOpen(false);
    }
  };

  const handleDeleteClick = (e: React.MouseEvent, id: number) => {
    e.preventDefault();
    e.stopPropagation();
    setTimelineToDelete(id);
  };

  const confirmDelete = async () => {
    if (!timelineToDelete) return;
    const success = await deleteTimeline(timelineToDelete);
    if (success) {
      setTimelineToDelete(null);
    }
  };

  if (isLoading) return <div>Loading Dashboard...</div>;
  return (
    <div className="max-w-6xl mx-auto px-8 py-12">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-12">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-primary">
            My Timelines
          </h1>
          <p className="text-muted-foreground mt-1">
            Manage and edit your developer journeys.
          </p>
        </div>

        <div className="flex items-center gap-2">
          {/* 1. Simplified Sync Action */}
          <ConnectGithubButton />

          {/* 2. Primary Action Dropdown */}
          <div className="relative" ref={dropdownRef}>
            <button
              onClick={() => setIsDropdownOpen(!isDropdownOpen)}
              className="flex items-center gap-2 bg-primary text-white px-4 py-2 rounded-lg hover:opacity-90 transition-all text-sm font-medium shadow-sm"
            >
              <Plus className="w-4 h-4" />
              <span>Create New</span>
              <ChevronDown
                className={`w-3.5 h-3.5 opacity-60 transition-transform duration-200 ${isDropdownOpen ? "rotate-180" : ""}`}
              />
            </button>

            {isDropdownOpen && (
              <div className="absolute right-0 mt-2 w-52 bg-white border border-border rounded-xl shadow-lg z-50 overflow-hidden animate-in fade-in zoom-in-95 duration-100">
                <div className="p-1.5">
                  <button
                    onClick={() => {
                      setIsDropdownOpen(false);
                      setIsCreateModalOpen(true);
                    }}
                    className="w-full flex items-center gap-3 px-3 py-2 text-sm text-muted-foreground hover:text-primary hover:bg-secondary/50 rounded-lg transition-colors text-left"
                  >
                    <Clock className="w-4 h-4" />
                    Empty Timeline
                  </button>

                  {isConnected && (
                    <button
                      onClick={() => {
                        setIsDropdownOpen(false);
                        setIsGithubModalOpen(true);
                      }}
                      className="w-full flex items-center gap-3 px-3 py-2 text-sm text-muted-foreground hover:text-primary hover:bg-secondary/50 rounded-lg transition-colors text-left border-t border-border/40 mt-1 pt-2"
                    >
                      <Github className="w-4 h-4" />
                      From GitHub Repos
                    </button>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
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

      <CreateFromGithubModal
        isOpen={isGithubModalOpen}
        onOpenChange={setIsGithubModalOpen}
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
