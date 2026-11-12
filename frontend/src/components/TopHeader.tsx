import React from "react";
import { Radio, RefreshCw, Gauge, BookmarkCheck } from "lucide-react";
import type { NetShieldStats } from "../types";

interface TopHeaderProps {
  stats: NetShieldStats | null;
  activeTabTitle: string;
  onToggleAutoRoam: () => void;
  onCaptureBaseline: () => void;
  onRunBenchmark: () => void;
  isBenchmarking: boolean;
  isCapturingBaseline: boolean;
  isTogglingRoam: boolean;
}

export const TopHeader: React.FC<TopHeaderProps> = ({
  stats,
  activeTabTitle,
  onToggleAutoRoam,
  onCaptureBaseline,
  onRunBenchmark,
  isBenchmarking,
  isCapturingBaseline,
  isTogglingRoam,
}) => {
  const isOnline = stats && stats.latency_ms >= 0;
  const isEspConnected = Boolean(stats?.esp_connected);
  const latency = stats?.latency_ms ?? 0;
  const autoRoam = Boolean(stats?.auto_roam_enabled);

  return (
    <header className="h-16 bg-[#FFFFFF] border-b border-[#E5E5E5] px-6 flex items-center justify-between sticky top-0 z-10">
      {/* Title & Network Status Badge */}
      <div className="flex items-center gap-4">
        <h1 className="text-base font-semibold text-[#111111] tracking-tight">
          {activeTabTitle}
        </h1>

        <div className="h-4 w-px bg-[#E5E5E5]" />

        {/* Live Network Status Badge */}
        <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-md bg-[#F5F5F5] border border-[#E5E5E5] text-xs font-medium text-[#111111]">
          <span
            className={`w-2 h-2 rounded-full ${
              isOnline
                ? latency < 50
                  ? "bg-[#10B981]"
                  : "bg-[#F59E0B]"
                : "bg-[#EF4444]"
            }`}
          />
          <span className="font-mono text-[11px] font-medium tracking-tight">
            {isOnline ? `ONLINE · ${latency.toFixed(0)}ms` : "OFFLINE / TIMEOUT"}
          </span>
        </div>

        {/* Hardware Indicator Badge */}
        <div className="hidden lg:inline-flex items-center gap-2 px-2.5 py-1 rounded-md bg-[#F5F5F5] border border-[#E5E5E5] text-xs font-medium text-[#737373]">
          <Radio size={13} strokeWidth={1.75} className={isEspConnected ? "text-[#10B981]" : "text-[#737373]"} />
          <span className="font-mono text-[11px] text-[#111111]">
            {stats?.radar_source || "Detecting Hardware..."}
          </span>
        </div>
      </div>

      {/* Quick Action Controls */}
      <div className="flex items-center gap-3">
        {/* Auto-Pilot Roam Toggle */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-[#E5E5E5] bg-[#FFFFFF]">
          <div className="text-right">
            <div className="text-xs font-medium text-[#111111] leading-none">
              Auto-Pilot Roam
            </div>
            <div className="text-[10px] text-[#737373] mt-0.5 font-mono">
              {autoRoam ? "ACTIVE" : "STANDBY"}
            </div>
          </div>
          <button
            onClick={onToggleAutoRoam}
            disabled={isTogglingRoam}
            type="button"
            role="switch"
            aria-checked={autoRoam}
            className={`relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none disabled:opacity-50 ${
              autoRoam ? "bg-[#111111]" : "bg-[#D4D4D4]"
            }`}
          >
            <span
              className={`pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                autoRoam ? "translate-x-4" : "translate-x-0"
              }`}
            />
          </button>
        </div>

        {/* Capture Baseline Button */}
        <button
          onClick={onCaptureBaseline}
          disabled={isCapturingBaseline}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg border border-[#E5E5E5] bg-[#FFFFFF] text-[#111111] hover:bg-[#F0F0F0] transition-colors disabled:opacity-50"
          title="Save current state as baseline reference snapshot"
        >
          {isCapturingBaseline ? (
            <RefreshCw size={13} strokeWidth={1.75} className="animate-spin text-[#111111]" />
          ) : (
            <BookmarkCheck size={13} strokeWidth={1.75} className="text-[#111111]" />
          )}
          <span>Capture Baseline</span>
        </button>

        {/* Run Benchmark Button */}
        <button
          onClick={onRunBenchmark}
          disabled={isBenchmarking}
          className="inline-flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-medium rounded-lg bg-[#111111] text-[#FFFFFF] hover:bg-[#262626] transition-colors disabled:opacity-50 shadow-sm"
        >
          {isBenchmarking ? (
            <RefreshCw size={13} strokeWidth={1.75} className="animate-spin text-white" />
          ) : (
            <Gauge size={13} strokeWidth={1.75} className="text-white" />
          )}
          <span>{isBenchmarking ? "Benchmarking..." : "Run Benchmark"}</span>
        </button>
      </div>
    </header>
  );
};
