import type { ToastNotification } from "../types";
import { CheckCircle2, Info, AlertTriangle, AlertCircle, X } from "lucide-react";

interface ToastContainerProps {
  toasts: ToastNotification[];
  onDismiss: (id: string) => void;
}

export const ToastContainer: React.FC<ToastContainerProps> = ({ toasts, onDismiss }) => {
  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 max-w-sm w-full pointer-events-none">
      {toasts.map((toast) => {
        let Icon = Info;
        let dotColor = "bg-[#737373]";

        if (toast.type === "success") {
          Icon = CheckCircle2;
          dotColor = "bg-[#10B981]";
        } else if (toast.type === "warning") {
          Icon = AlertTriangle;
          dotColor = "bg-[#F59E0B]";
        } else if (toast.type === "error") {
          Icon = AlertCircle;
          dotColor = "bg-[#EF4444]";
        }

        return (
          <div
            key={toast.id}
            className="pointer-events-auto p-3.5 rounded-xl border border-[#E5E5E5] bg-[#FFFFFF] shadow-md flex items-start gap-3 transition-all animate-in slide-in-from-bottom-2 duration-200"
          >
            <div className="mt-0.5 shrink-0 flex items-center justify-center">
              <Icon size={14} strokeWidth={1.75} className="text-[#111111]" />
            </div>

            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between gap-2">
                <span className="text-xs font-semibold text-[#111111] truncate">
                  {toast.title}
                </span>
                <span className="text-[10px] text-[#A3A3A3] font-mono shrink-0">
                  {toast.timestamp}
                </span>
              </div>
              <p className="text-xs text-[#737373] mt-0.5 leading-snug break-words">
                {toast.message}
              </p>
            </div>

            <button
              onClick={() => onDismiss(toast.id)}
              className="text-[#A3A3A3] hover:text-[#111111] shrink-0 p-1"
            >
              <X size={13} strokeWidth={1.75} />
            </button>
          </div>
        );
      })}
    </div>
  );
};
