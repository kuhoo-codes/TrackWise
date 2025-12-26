import * as Dialog from "@radix-ui/react-dialog";
import * as Label from "@radix-ui/react-label";
import {
  X,
  Briefcase,
  GraduationCap,
  Code,
  Award,
  Image as ImageIcon,
  Trash2,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import React, { useState, useEffect } from "react";
import {
  timelineNodeSchema,
  type TimelineNodeFormValues,
} from "@/features/timeline/components/types";

interface NodeModalProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (data: TimelineNodeFormValues) => Promise<void>;
  onDelete?: (id: number) => void;
  availableParents?: { id: number; title: string }[];
  initialData?: Partial<TimelineNodeFormValues> & { id?: number };
  timelineId: number;
}

const formatDateForInput = (date?: Date | null) => {
  if (!date) return "";
  try {
    return date.toISOString().split("T")[0];
  } catch (e) {
    console.error("Date formatting error:", e);
    return "";
  }
};

export const TimelineNodeModal: React.FC<NodeModalProps> = ({
  isOpen,
  onOpenChange,
  onSubmit,
  onDelete,
  availableParents = [],
  initialData,
}) => {
  const [activeTab, setActiveTab] = useState<
    "essentials" | "details" | "media"
  >("essentials");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const isEditing = !!initialData?.id;

  const defaultState = React.useMemo<Partial<TimelineNodeFormValues>>(
    () => ({
      title: "",
      type: "work",
      parentId: 0,
      isCurrent: false,
      shortSummary: "",
      description: "",
      privateNotes: "",
      media: [],
      startDate: new Date(),
    }),
    [],
  );

  const NODE_TYPE_OPTIONS: {
    id: TimelineNodeFormValues["type"];
    icon: LucideIcon;
    label: string;
  }[] = [
    { id: "work", icon: Briefcase, label: "Work" },
    { id: "education", icon: GraduationCap, label: "Education" },
    { id: "project", icon: Code, label: "Project" },
    { id: "certification", icon: Award, label: "Cert" },
    { id: "blog", icon: Code, label: "Blog" },
    { id: "milestone", icon: Award, label: "Milestone" },
  ];

  const [formData, setFormData] =
    useState<Partial<TimelineNodeFormValues>>(defaultState);

  useEffect(() => {
    if (isOpen) {
      setErrors({});
      setFormData({ ...defaultState, ...initialData });
      setActiveTab("essentials");
    }
  }, [isOpen, initialData, defaultState]);

  const handleChange = <K extends keyof TimelineNodeFormValues>(
    field: K,
    value: TimelineNodeFormValues[K],
  ): void => {
    setFormData((prev) => ({ ...prev, [field]: value }));

    if (errors[field]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  const handleValidationAndSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setErrors({});

    const result = timelineNodeSchema.safeParse(formData);

    if (!result.success) {
      const newErrors: Record<string, string> = {};
      result.error.errors.forEach((err) => {
        const path = err.path[0] as string;
        newErrors[path] = err.message;
      });
      setErrors(newErrors);
      setIsSubmitting(false);

      if (newErrors.shortSummary || newErrors.description) {
        setActiveTab("details");
      } else {
        setActiveTab("essentials");
      }
      return;
    }

    try {
      await onSubmit(result.data as TimelineNodeFormValues);
    } catch (error) {
      console.error("Submit error", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog.Root open={isOpen} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 transition-opacity" />

        {/* Modal Content */}
        <Dialog.Content className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-2xl max-h-[90vh] bg-white rounded-2xl shadow-2xl z-50 flex flex-col focus:outline-none overflow-hidden">
          <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100 bg-white sticky top-0 z-10">
            <Dialog.Title className="text-xl font-bold text-gray-900">
              {isEditing ? "Edit Node" : "Add Timeline Node"}
            </Dialog.Title>
            <Dialog.Close asChild>
              <button className="p-2 hover:bg-gray-100 rounded-full transition-colors text-gray-500">
                <X className="w-5 h-5" />
              </button>
            </Dialog.Close>
          </div>

          {/* Tabs */}
          <div className="flex px-6 border-b border-gray-100 bg-gray-50/50">
            {(["essentials", "details", "media"] as const).map((tab) => (
              <button
                key={tab}
                type="button"
                onClick={() => setActiveTab(tab)}
                className={`
                  px-4 py-3 text-sm font-medium border-b-2 transition-colors capitalize
                  ${
                    activeTab === tab
                      ? "border-blue-600 text-blue-600"
                      : "border-transparent text-gray-500 hover:text-gray-700"
                  }
                `}
              >
                {tab}
              </button>
            ))}
          </div>

          {/* Form Body */}
          <form
            onSubmit={(e) => void handleValidationAndSubmit(e)}
            className="flex-1 overflow-y-auto p-6"
          >
            {activeTab === "essentials" && (
              <div className="space-y-6">
                <div className="space-y-2">
                  <Label.Root className="text-sm font-medium text-gray-700">
                    Node Type
                  </Label.Root>
                  <div className="grid grid-cols-4 gap-3">
                    {NODE_TYPE_OPTIONS.map((type) => (
                      <div
                        key={type.id}
                        onClick={() => handleChange("type", type.id)}
                        className={`
                          flex flex-col items-center justify-center p-3 rounded-xl border cursor-pointer transition-all select-none
                          ${
                            formData.type === type.id
                              ? "border-blue-600 bg-blue-50 text-blue-700 ring-1 ring-blue-600"
                              : "border-gray-200 hover:border-blue-300 hover:bg-gray-50"
                          }
                        `}
                      >
                        <type.icon className="w-5 h-5 mb-1" />
                        <span className="text-xs font-medium">
                          {type.label}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Title Input */}
                <div className="space-y-2">
                  <Label.Root
                    htmlFor="title"
                    className="text-sm font-medium text-gray-700"
                  >
                    Title <span className="text-red-500">*</span>
                  </Label.Root>
                  <input
                    id="title"
                    value={formData.title}
                    onChange={(e) => handleChange("title", e.target.value)}
                    className="w-full px-4 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 outline-none transition"
                    placeholder="e.g. Senior Frontend Engineer"
                  />
                  {errors.title && (
                    <span className="text-red-500 text-xs">{errors.title}</span>
                  )}
                </div>

                {/* Parent Block Selector */}
                <div className="space-y-2">
                  <Label.Root
                    htmlFor="parentId"
                    className="text-sm font-medium text-gray-700"
                  >
                    Belongs To (Block)
                  </Label.Root>
                  <div className="relative">
                    <select
                      id="parentId"
                      value={formData.parentId || ""}
                      onChange={(e) => {
                        const val = e.target.value;
                        handleChange(
                          "parentId",
                          val === "" ? null : Number(val),
                        );
                      }}
                      className="w-full px-4 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 outline-none appearance-none bg-white cursor-pointer"
                    >
                      <option value="">None (Create New Parent Block)</option>
                      {availableParents.map((p) => (
                        <option key={p.id} value={p.id}>
                          {p.title}
                        </option>
                      ))}
                    </select>
                    <div className="absolute inset-y-0 right-0 flex items-center px-2 pointer-events-none">
                      <svg
                        className="w-4 h-4 text-gray-500"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth="2"
                          d="M19 9l-7 7-7-7"
                        />
                      </svg>
                    </div>
                  </div>
                  <p className="text-xs text-gray-500">
                    Leave empty to create a new main timeline block. Select a
                    block to add this as a child event.
                  </p>
                </div>

                {/* Date Inputs */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label.Root
                      htmlFor="startDate"
                      className="text-sm font-medium text-gray-700"
                    >
                      Start Date <span className="text-red-500">*</span>
                    </Label.Root>
                    <input
                      id="startDate"
                      type="date"
                      value={formatDateForInput(formData.startDate)}
                      onChange={(e) => {
                        if (e.target.valueAsDate) {
                          handleChange("startDate", e.target.valueAsDate);
                        }
                      }}
                      className="w-full px-4 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 outline-none"
                    />
                    {errors.startDate && (
                      <span className="text-red-500 text-xs">
                        {errors.startDate}
                      </span>
                    )}
                  </div>

                  <div
                    className={`space-y-2 ${formData.isCurrent ? "opacity-50 pointer-events-none" : ""}`}
                  >
                    <Label.Root
                      htmlFor="endDate"
                      className="text-sm font-medium text-gray-700"
                    >
                      End Date
                    </Label.Root>
                    <input
                      id="endDate"
                      type="date"
                      value={formatDateForInput(formData.endDate)}
                      onChange={(e) => {
                        handleChange("endDate", e.target.valueAsDate);
                      }}
                      className="w-full px-4 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 outline-none"
                    />
                    {errors.endDate && (
                      <span className="text-red-500 text-xs">
                        {errors.endDate}
                      </span>
                    )}
                  </div>
                </div>

                {/* Is Current Checkbox */}
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="isCurrent"
                    checked={formData.isCurrent}
                    onChange={(e) =>
                      handleChange("isCurrent", e.target.checked)
                    }
                    className="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500 cursor-pointer"
                  />
                  <Label.Root
                    htmlFor="isCurrent"
                    className="text-sm text-gray-700 cursor-pointer select-none"
                  >
                    I am currently working on this
                  </Label.Root>
                </div>
              </div>
            )}

            {/* --- TAB: DETAILS --- */}
            {activeTab === "details" && (
              <div className="space-y-6">
                <div className="space-y-2">
                  <Label.Root
                    htmlFor="shortSummary"
                    className="text-sm font-medium text-gray-700"
                  >
                    Short Summary
                  </Label.Root>
                  <input
                    id="shortSummary"
                    value={formData.shortSummary || ""}
                    onChange={(e) =>
                      handleChange("shortSummary", e.target.value)
                    }
                    className="w-full px-4 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 outline-none"
                    placeholder="e.g. Led the migration to Next.js"
                  />
                  {errors.shortSummary && (
                    <span className="text-red-500 text-xs">
                      {errors.shortSummary}
                    </span>
                  )}
                </div>

                <div className="space-y-2">
                  <Label.Root
                    htmlFor="description"
                    className="text-sm font-medium text-gray-700"
                  >
                    Full Description
                  </Label.Root>
                  <textarea
                    id="description"
                    rows={6}
                    value={formData.description || ""}
                    onChange={(e) =>
                      handleChange("description", e.target.value)
                    }
                    className="w-full px-4 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 outline-none resize-none"
                    placeholder="Tell the story..."
                  />
                </div>

                <div className="space-y-2">
                  <Label.Root
                    htmlFor="privateNotes"
                    className="text-sm font-medium text-gray-700"
                  >
                    Private Notes
                  </Label.Root>
                  <textarea
                    id="privateNotes"
                    rows={3}
                    value={formData.privateNotes || ""}
                    onChange={(e) =>
                      handleChange("privateNotes", e.target.value)
                    }
                    className="w-full px-4 py-2 rounded-lg border border-amber-200 bg-amber-50 focus:ring-2 focus:ring-amber-400 outline-none resize-none"
                    placeholder="Notes only visible to you..."
                  />
                </div>
              </div>
            )}

            {/* --- TAB: MEDIA --- */}
            {activeTab === "media" && (
              <div className="flex flex-col items-center justify-center h-48 border-2 border-dashed border-gray-300 rounded-xl bg-gray-50">
                <div className="text-center">
                  <ImageIcon className="w-10 h-10 text-gray-400 mx-auto mb-2" />
                  <p className="text-gray-500 text-sm font-medium">
                    Media Upload
                  </p>
                  <p className="text-gray-400 text-xs">
                    Drag and drop or click to upload
                  </p>
                </div>
              </div>
            )}

            <button type="submit" className="hidden" />
          </form>

          {/* Footer Actions */}
          <div className="p-6 border-t border-gray-100 bg-gray-50 flex justify-between gap-3 sticky bottom-0">
            <div>
              {isEditing && onDelete && initialData?.id && (
                <button
                  type="button"
                  onClick={() => {
                    if (
                      window.confirm(
                        "Are you sure you want to delete this node?",
                      )
                    ) {
                      onDelete(initialData.id!);
                    }
                  }}
                  className="px-4 py-2 text-sm font-medium text-red-600 bg-red-50 border border-red-200 rounded-lg hover:bg-red-100 transition-colors flex items-center gap-2"
                >
                  <Trash2 className="w-4 h-4" />
                  Delete
                </button>
              )}
            </div>

            <div className="flex gap-3">
              <Dialog.Close asChild>
                <button
                  type="button"
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
              </Dialog.Close>
              <button
                onClick={(e) => {
                  void handleValidationAndSubmit(e);
                }}
                disabled={isSubmitting}
                className="px-6 py-2 text-sm font-medium text-white bg-black rounded-lg hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isSubmitting
                  ? "Saving..."
                  : isEditing
                    ? "Update Node"
                    : "Save Node"}
              </button>
            </div>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
};
