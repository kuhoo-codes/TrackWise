import * as Dialog from "@radix-ui/react-dialog";
import { X } from "lucide-react";
import React, { useState, useEffect } from "react";
import { toast } from "react-hot-toast";
import { GithubService } from "@/services/github";
import { useGithubConnect } from "@/shared/hooks/useGithubConnect";

interface CreateFromGithubModalProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
}

export const CreateFromGithubModal: React.FC<CreateFromGithubModalProps> = ({
  isOpen,
  onOpenChange,
}) => {
  const [repos, setRepos] = useState<{ id: number; fullName: string }[]>([]);
  const [selectedRepoIds, setSelectedRepoIds] = useState<Set<number>>(
    new Set(),
  );
  const [isLoadingRepos, setIsLoadingRepos] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { triggerSync } = useGithubConnect();

  useEffect(() => {
    if (isOpen) {
      void fetchRepos();
    } else {
      setSelectedRepoIds(new Set());
    }
  }, [isOpen]);

  const fetchRepos = async () => {
    setIsLoadingRepos(true);
    try {
      const data = await GithubService.getRepositories();
      setRepos(data);
    } catch (error) {
      toast.error("Failed to load repositories.");
      console.error("Error fetching repositories from GitHub:", error);
    } finally {
      setIsLoadingRepos(false);
    }
  };

  const toggleRepo = (id: number) => {
    const newSet = new Set(selectedRepoIds);
    if (newSet.has(id)) newSet.delete(id);
    else newSet.add(id);
    setSelectedRepoIds(newSet);
  };

  const handleSubmit = async () => {
    if (selectedRepoIds.size === 0) return;

    setIsSubmitting(true);
    try {
      await GithubService.generateTimelines(Array.from(selectedRepoIds));
      toast.success("Timeline generation started in the background!");
      onOpenChange(false);
    } catch (error) {
      toast.error("Failed to start timeline generation.");
      console.error("Error generating timelines from GitHub:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog.Root open={isOpen} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50" />
        <Dialog.Content className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-md bg-white rounded-2xl shadow-2xl z-50 p-6 focus:outline-none">
          <div className="flex justify-between items-center mb-6">
            <Dialog.Title className="text-xl font-bold text-gray-900">
              Create from GitHub Repos
            </Dialog.Title>
            <Dialog.Close asChild>
              <button className="text-gray-400 hover:text-gray-500 transition-colors">
                <X className="w-5 h-5" />
              </button>
            </Dialog.Close>
          </div>

          <div>
            {isLoadingRepos ? (
              <div className="text-center py-10 text-gray-500">
                <div className="w-6 h-6 border-2 border-gray-300 border-t-gray-600 rounded-full animate-spin mx-auto mb-3" />
                Loading repositories...
              </div>
            ) : repos.length === 0 ? (
              <div className="text-center py-10 bg-gray-50 rounded-xl border border-gray-200">
                <h3 className="font-medium text-gray-900 mb-2">
                  No repositories found
                </h3>
                <p className="text-sm text-gray-500 mb-6 px-6">
                  We couldn't find any repositories synced to your profile. You
                  may need to run a sync to fetch your latest data.
                </p>
                <button
                  onClick={() => void triggerSync()}
                  className="bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors shadow-sm"
                >
                  Sync GitHub Profile
                </button>
              </div>
            ) : (
              <div className="space-y-4">
                <p className="text-sm text-gray-500 mb-2">
                  Select the repositories you want to track. We will generate a
                  timeline for each one.
                </p>

                <div className="max-h-64 overflow-y-auto border border-gray-200 rounded-lg divide-y divide-gray-100">
                  {repos.map((repo) => (
                    <label
                      key={repo.id}
                      className="flex items-center gap-3 p-3 hover:bg-gray-50 cursor-pointer transition-colors"
                    >
                      <input
                        type="checkbox"
                        checked={selectedRepoIds.has(repo.id)}
                        onChange={() => toggleRepo(repo.id)}
                        className="w-4 h-4 text-black border-gray-300 rounded focus:ring-black focus:ring-2"
                      />
                      <span className="text-sm font-medium text-gray-900 truncate">
                        {repo.fullName}
                      </span>
                    </label>
                  ))}
                </div>

                <div className="flex justify-end gap-3 pt-4 mt-2">
                  <Dialog.Close asChild>
                    <button
                      type="button"
                      className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 rounded-lg transition-colors"
                    >
                      Cancel
                    </button>
                  </Dialog.Close>
                  <button
                    onClick={() => void handleSubmit()}
                    disabled={selectedRepoIds.size === 0 || isSubmitting}
                    className="px-4 py-2 text-sm font-medium text-white bg-black rounded-lg hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
                  >
                    {isSubmitting
                      ? "Starting..."
                      : `Generate ${
                          selectedRepoIds.size > 0
                            ? `(${selectedRepoIds.size})`
                            : ""
                        }`}
                  </button>
                </div>
              </div>
            )}
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
};
