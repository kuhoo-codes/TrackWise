import { Globe, Trash2, Save } from "lucide-react";
import React, { useRef, useState } from "react";
import { toast } from "react-hot-toast";
import { SettingsSection } from "@/features/settings/components/settingsSection";
import { UserAvatar } from "@/shared/components/layout/userAvatar";
import { useAuth } from "@/shared/hooks/useAuth";
import { useAvatar } from "@/shared/hooks/useAvatar";

export const Settings: React.FC = () => {
  const [isSaving, setIsSaving] = useState(false);
  const { user, updateUser } = useAuth();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const { uploadAvatar, removeAvatar, isProcessing } = useAvatar();

  const [formData, setFormData] = useState({
    name: user?.name || "",
    headline: user?.headline || "",
  });

  const handleAvatarClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (
    event: React.ChangeEvent<HTMLInputElement>,
  ) => {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      await uploadAvatar(file);
      toast.success("Avatar updated successfully!");
    } catch (error) {
      toast.error("Failed to upload avatar.");
      console.error("Upload failed", error);
    }
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleRemoveAvatar = async () => {
    try {
      await removeAvatar();
      toast.success("Avatar removed successfully!");
    } catch (error) {
      toast.error("Failed to remove avatar.");
      console.error("Remove failed", error);
    }
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await updateUser(formData);
      toast.success("Profile updated successfully!");
    } catch (error) {
      console.error("Failed to save profile", error);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-8 py-12">
      <header className="flex items-center justify-between mb-12">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
          <p className="text-muted-foreground mt-1">
            Manage your account and portfolio preferences.
          </p>
        </div>
        <button
          onClick={() => void handleSave()}
          className="flex items-center gap-2 bg-primary text-white px-4 py-2 rounded-lg text-sm font-medium hover:opacity-90 transition-all shadow-sm"
        >
          {isSaving ? (
            <Save className="w-4 h-4 animate-pulse" />
          ) : (
            <Save className="w-4 h-4" />
          )}
          {isSaving ? "Saving..." : "Save Changes"}
        </button>
      </header>

      <div className="space-y-2">
        {/* 1. Personal Information */}
        <SettingsSection
          title="Profile"
          description="This information will be used by the AI to introduce you on your timeline."
        >
          <div className="flex items-center gap-6 mb-4">
            <div
              className="relative group cursor-pointer"
              onClick={() => void handleAvatarClick()}
            >
              <UserAvatar
                size="lg"
                className={isProcessing ? "opacity-50" : ""}
              />
              {isProcessing && (
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                </div>
              )}
            </div>

            <input
              type="file"
              ref={fileInputRef}
              className="hidden"
              accept="image/*"
              onChange={(e) => void handleFileChange(e)}
            />

            <button
              onClick={() => void handleAvatarClick()}
              disabled={isProcessing}
              className="text-sm font-medium border border-border px-3 py-1.5 rounded-md hover:bg-secondary transition-colors disabled:opacity-50"
            >
              {isProcessing ? "Processing..." : "Change Avatar"}
            </button>
            {/* Show Remove button only if user currently has an avatar */}
            {user?.hasAvatar && (
              <button
                onClick={() => void handleRemoveAvatar()}
                disabled={isProcessing}
                className="text-sm font-medium border border-red-100 text-red-600 px-3 py-1.5 rounded-md hover:bg-red-50 transition-colors disabled:opacity-50 flex items-center gap-2"
              >
                <Trash2 className="w-3.5 h-3.5" />
                Remove
              </button>
            )}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Full Name</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) =>
                  setFormData((prev) => ({ ...prev, name: e.target.value }))
                }
                className="w-full bg-white border border-border rounded-lg px-3 py-2 text-sm outline-none focus:ring-1 focus:ring-primary"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">
                Professional Headline
              </label>
              <input
                type="text"
                value={formData.headline}
                onChange={(e) =>
                  setFormData((prev) => ({ ...prev, headline: e.target.value }))
                }
                placeholder="e.g. Senior Backend Engineer"
                className="w-full bg-white border border-border rounded-lg px-3 py-2 text-sm focus:ring-1 focus:ring-primary outline-none transition-all"
              />
            </div>
          </div>
        </SettingsSection>

        {/* 2. Portfolio Visibility */}
        <SettingsSection
          title="Portfolio"
          description="Control how your career timeline is shared with the world."
        >
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 rounded-xl border border-border bg-white">
              <div className="flex gap-3">
                <Globe className="w-5 h-5 text-muted-foreground" />
                <div>
                  <p className="text-sm font-medium">Public Portfolio</p>
                  <p className="text-xs text-muted-foreground">
                    Allow anyone with the link to view your timeline.
                  </p>
                </div>
              </div>
              <input
                type="checkbox"
                className="w-10 h-5 bg-gray-200 rounded-full appearance-none checked:bg-primary transition-all relative cursor-pointer before:content-[''] before:absolute before:w-4 before:h-4 before:bg-white before:rounded-full before:top-0.5 before:left-0.5 checked:before:left-5 before:transition-all"
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Custom URL Slug</label>
              <div className="flex items-center">
                <span className="bg-secondary px-3 py-2 border border-r-0 border-border rounded-l-lg text-sm text-muted-foreground">
                  trackwise.ai/p/
                </span>
                <input
                  type="text"
                  placeholder="username"
                  className="flex-1 bg-white border border-border rounded-r-lg px-3 py-2 text-sm focus:ring-1 focus:ring-primary outline-none transition-all"
                />
              </div>
            </div>
          </div>
        </SettingsSection>

        {/* 3. GitHub Preferences */}
        <SettingsSection
          title="GitHub Sync"
          description="Fine-tune how the AI gathers your contribution data."
        >
          <div className="space-y-3">
            {[
              {
                id: "pr",
                label: "Include Pull Requests",
                desc: "Analyzes code quality and complexity.",
              },
              {
                id: "commit",
                label: "Include Commits",
                desc: "Tracks daily activity and consistency.",
              },
              {
                id: "private",
                label: "Include Private Metadata",
                desc: "Shows activity without revealing code.",
              },
            ].map((item) => (
              <label
                key={item.id}
                className="flex items-start gap-3 p-3 rounded-lg hover:bg-secondary/40 transition-colors cursor-pointer"
              >
                <input type="checkbox" defaultChecked className="mt-1" />
                <div>
                  <p className="text-sm font-medium">{item.label}</p>
                  <p className="text-xs text-muted-foreground">{item.desc}</p>
                </div>
              </label>
            ))}
          </div>
        </SettingsSection>

        {/* 4. Danger Zone */}
        <SettingsSection
          title="Danger Zone"
          description="Irreversible actions regarding your data."
        >
          <div className="p-4 rounded-xl border border-red-100 bg-red-50/30">
            <h4 className="text-sm font-semibold text-red-900">
              Delete Account
            </h4>
            <p className="text-xs text-red-700 mt-1 mb-4">
              Once deleted, all your timelines and AI-generated insights will be
              gone forever.
            </p>
            <button className="flex items-center gap-2 text-xs font-bold text-red-600 hover:text-red-700 transition-colors">
              <Trash2 className="w-3.5 h-3.5" />
              Delete my TrackWise account
            </button>
          </div>
        </SettingsSection>
      </div>
    </div>
  );
};
