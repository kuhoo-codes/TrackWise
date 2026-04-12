import * as Dialog from "@radix-ui/react-dialog";
import { AlertTriangle } from "lucide-react";
import React from "react";
import { GithubInvertocat } from "@/shared/components/ui/asset/githubLogo";

interface DisconnectConfirmationModalProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  onConfirm: () => Promise<void>;
  isDisconnecting: boolean;
}

export const DisconnectConfirmationModal: React.FC<
  DisconnectConfirmationModalProps
> = ({ isOpen, onOpenChange, onConfirm, isDisconnecting }) => (
  <Dialog.Root open={isOpen} onOpenChange={onOpenChange}>
    <Dialog.Portal>
      <Dialog.Overlay className="fixed inset-0 bg-black/40 backdrop-blur-sm z-[100] transition-opacity" />
      <Dialog.Content className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-md bg-white rounded-2xl shadow-2xl z-[101] p-8 focus:outline-none">
        <div className="flex flex-col items-center text-center">
          {/* Icon Stack */}
          <div className="relative mb-6">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center">
              <GithubInvertocat className="w-8 h-8 text-gray-900" />
            </div>
            <div className="absolute -bottom-1 -right-1 w-7 h-7 bg-red-100 border-4 border-white rounded-full flex items-center justify-center">
              <AlertTriangle className="w-3.5 h-3.5 text-red-600" />
            </div>
          </div>

          <Dialog.Title className="text-xl font-bold text-gray-900 mb-3">
            Disconnect GitHub?
          </Dialog.Title>

          <div className="space-y-4 text-sm text-gray-600 mb-8 leading-relaxed">
            <p>
              Your existing{" "}
              <strong className="text-gray-900">
                timelines will remain untouched
              </strong>
              , but all synced repository data, commits, and issue history will
              be cleared from our database.
            </p>
            <div className="p-3 bg-amber-50 border border-amber-100 rounded-lg text-amber-800 text-xs">
              <strong>Note:</strong> If you reconnect in the future, you will
              have to wait for a full data synchronization again, which can be
              time-consuming.
            </div>
          </div>

          <div className="flex gap-3 w-full">
            <button
              onClick={() => onOpenChange(false)}
              className="flex-1 px-4 py-2.5 text-sm font-semibold text-gray-700 bg-white border border-gray-300 rounded-xl hover:bg-gray-50 transition-all active:scale-95"
            >
              Keep Connected
            </button>
            <button
              onClick={() => void onConfirm()}
              disabled={isDisconnecting}
              className="flex-1 px-4 py-2.5 text-sm font-semibold text-white bg-red-600 rounded-xl hover:bg-red-700 disabled:opacity-50 transition-all active:scale-95 shadow-sm shadow-red-200"
            >
              {isDisconnecting ? "Disconnecting..." : "Disconnect"}
            </button>
          </div>
        </div>
      </Dialog.Content>
    </Dialog.Portal>
  </Dialog.Root>
);
