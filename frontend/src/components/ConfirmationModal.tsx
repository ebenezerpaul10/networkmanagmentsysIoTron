import React from "react";
import { AlertCircle, ArrowRight, X } from "lucide-react";

interface ConfirmationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  description: string;
  currentSsid: string;
  currentBssid: string;
  targetSsid: string;
  targetBssid: string;
  targetChannel: number;
  isLoading: boolean;
}

export const ConfirmationModal: React.FC<ConfirmationModalProps> = ({
  isOpen,
  onClose,
  onConfirm,
  title,
  description,
  currentSsid,
  currentBssid,
  targetSsid,
  targetBssid,
  targetChannel,
  isLoading,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-xs animate-in fade-in duration-150">
      <div className="w-full max-w-md bg-[#FFFFFF] rounded-xl border border-[#E5E5E5] shadow-lg p-6 space-y-4">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-[#F5F5F5] border border-[#E5E5E5] flex items-center justify-center text-[#111111]">
              <AlertCircle size={18} strokeWidth={1.75} />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-[#111111]">{title}</h3>
              <p className="text-xs text-[#737373] mt-0.5">{description}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            disabled={isLoading}
            className="text-[#737373] hover:text-[#111111] p-1 rounded-md transition-colors"
          >
            <X size={16} strokeWidth={1.75} />
          </button>
        </div>

        {/* Transition Preview Card */}
        <div className="p-3.5 rounded-lg border border-[#E5E5E5] bg-[#F5F5F5] space-y-3">
          <div className="text-[11px] font-semibold text-[#737373] uppercase tracking-wider">
            Connection Handover Details
          </div>

          <div className="grid grid-cols-2 gap-3 items-center">
            {/* Current */}
            <div className="p-2.5 rounded border border-[#E5E5E5] bg-[#FFFFFF]">
              <div className="text-[10px] text-[#737373]">Current AP</div>
              <div className="text-xs font-semibold text-[#111111] truncate">
                {currentSsid || "Unknown"}
              </div>
              <div className="text-[10px] font-mono text-[#737373] mt-0.5 truncate">
                {currentBssid || "N/A"}
              </div>
            </div>

            {/* Target */}
            <div className="p-2.5 rounded border border-[#111111] bg-[#FFFFFF]">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-medium text-[#111111]">Target AP</span>
                <span className="text-[9px] font-mono px-1 py-0.2 bg-[#111111] text-[#FFFFFF] rounded">
                  Ch {targetChannel}
                </span>
              </div>
              <div className="text-xs font-semibold text-[#111111] truncate">
                {targetSsid || currentSsid || "Cleanest Candidate"}
              </div>
              <div className="text-[10px] font-mono text-[#111111] mt-0.5 truncate font-medium">
                {targetBssid || "Auto-Candidate"}
              </div>
            </div>
          </div>

          <p className="text-[11px] text-[#737373] leading-relaxed">
            NetShield will perform an intelligent zero-downtime handshake to steer your connection to this cleaner BSSID. Handshake safety rollback is actively monitored.
          </p>
        </div>

        {/* Actions */}
        <div className="flex items-center justify-end gap-2.5 pt-2">
          <button
            onClick={onClose}
            disabled={isLoading}
            className="px-3.5 py-1.5 text-xs font-medium rounded-lg border border-[#E5E5E5] bg-[#FFFFFF] text-[#111111] hover:bg-[#F0F0F0] transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            disabled={isLoading}
            className="inline-flex items-center gap-1.5 px-4 py-1.5 text-xs font-medium rounded-lg bg-[#111111] text-[#FFFFFF] hover:bg-[#262626] transition-colors disabled:opacity-50"
          >
            {isLoading ? (
              <span>Steering Link...</span>
            ) : (
              <>
                <span>Confirm Handover</span>
                <ArrowRight size={13} strokeWidth={1.75} />
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

