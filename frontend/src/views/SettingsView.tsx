import React, { useState } from "react";
import {
  Settings as SettingsIcon,
  Server,
  Clock,
  SlidersHorizontal,
  CheckCircle2,
  RefreshCw,
  Cpu,
  Layers,
} from "lucide-react";
import { API_BASE_URL, setApiBaseUrl } from "../api";
import type { NetShieldStats } from "../types";

interface SettingsViewProps {
  stats: NetShieldStats | null;
  advancedMode: boolean;
  onToggleAdvancedMode: () => void;
  pollIntervalMs: number;
  onChangePollInterval: (ms: number) => void;
  onRefreshNow: () => void;
}

export const SettingsView: React.FC<SettingsViewProps> = ({
  stats,
  advancedMode,
  onToggleAdvancedMode,
  pollIntervalMs,
  onChangePollInterval,
  onRefreshNow,
}) => {
  const [endpointInput, setEndpointInput] = useState(API_BASE_URL || "http://localhost:8080");
  const [savedSuccess, setSavedSuccess] = useState(false);

  const handleSaveEndpoint = (e: React.FormEvent) => {
    e.preventDefault();
    setApiBaseUrl(endpointInput);
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 2000);
    onRefreshNow();
  };

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Settings Header */}
      <div className="p-5 rounded-xl border border-[#E5E5E5] bg-[#FFFFFF] shadow-xs">
        <h2 className="text-base font-semibold text-[#111111]">
          Enterprise Controller Settings
        </h2>
        <p className="text-xs text-[#737373] mt-1">
          Configure backend daemon telemetry endpoints, real-time polling cadence, and visualization modes.
        </p>
      </div>

      {/* Backend API Configuration */}
      <div className="p-5 rounded-xl border border-[#E5E5E5] bg-[#FFFFFF] shadow-xs space-y-4">
        <div className="flex items-center gap-2.5">
          <Server size={16} strokeWidth={1.75} className="text-[#111111]" />
          <h3 className="text-sm font-semibold text-[#111111]">
            Daemon Telemetry Endpoint
          </h3>
        </div>

        <form onSubmit={handleSaveEndpoint} className="space-y-3">
          <div>
            <label className="text-xs font-medium text-[#737373]">
              NetShield HTTP API URL
            </label>
            <div className="mt-1 flex gap-2">
              <input
                type="text"
                value={endpointInput}
                onChange={(e) => setEndpointInput(e.target.value)}
                placeholder="http://localhost:8080"
                className="flex-1 px-3 py-1.5 text-xs font-mono rounded-lg border border-[#E5E5E5] bg-[#F5F5F5] focus:bg-[#FFFFFF] focus:outline-none focus:border-[#111111] transition-colors"
              />
              <button
                type="submit"
                className="px-4 py-1.5 text-xs font-medium rounded-lg bg-[#111111] text-[#FFFFFF] hover:bg-[#262626] transition-colors"
              >
                Apply
              </button>
            </div>
            <p className="text-[11px] text-[#A3A3A3] mt-1">
              Leave default when running locally on port 8080 or when Vite proxy is active.
            </p>
          </div>

          {savedSuccess && (
            <div className="p-2.5 rounded-lg border border-[#E5E5E5] bg-[#F5F5F5] flex items-center gap-2 text-xs font-medium text-[#111111]">
              <CheckCircle2 size={14} strokeWidth={1.75} className="text-[#10B981]" />
              Telemetry endpoint updated successfully.
            </div>
          )}
        </form>
      </div>

      {/* Polling Interval Selection */}
      <div className="p-5 rounded-xl border border-[#E5E5E5] bg-[#FFFFFF] shadow-xs space-y-4">
        <div className="flex items-center gap-2.5">
          <Clock size={16} strokeWidth={1.75} className="text-[#111111]" />
          <h3 className="text-sm font-semibold text-[#111111]">
            Telemetry Polling Frequency
          </h3>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {[
            { ms: 1000, label: "Real-Time (1,000 ms)", desc: "Lowest latency RF wave updates" },
            { ms: 2000, label: "Balanced (2,000 ms)", desc: "Optimal network efficiency" },
            { ms: 5000, label: "Conservative (5,000 ms)", desc: "Minimal CPU & background overhead" },
          ].map((item) => (
            <button
              key={item.ms}
              type="button"
              onClick={() => onChangePollInterval(item.ms)}
              className={`p-3.5 rounded-xl border text-left transition-all ${
                pollIntervalMs === item.ms
                  ? "border-[#111111] bg-[#FFFFFF] ring-1 ring-[#111111]"
                  : "border-[#E5E5E5] bg-[#F5F5F5] hover:bg-[#F0F0F0]"
              }`}
            >
              <div className="text-xs font-semibold text-[#111111]">{item.label}</div>
              <div className="text-[11px] text-[#737373] mt-1">{item.desc}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Mode Toggle */}
      <div className="p-5 rounded-xl border border-[#E5E5E5] bg-[#FFFFFF] shadow-xs flex items-center justify-between">
        <div className="flex items-start gap-3">
          <SlidersHorizontal size={18} strokeWidth={1.75} className="text-[#111111] mt-0.5" />
          <div>
            <div className="text-sm font-semibold text-[#111111]">
              Telemetry Density Mode
            </div>
            <div className="text-xs text-[#737373] mt-0.5 max-w-md">
              Toggle between Standard Mode (simplified indicators) and Advanced Mode (extended hardware registers, raw BSSID, and packet metrics).
            </div>
          </div>
        </div>

        <button
          onClick={onToggleAdvancedMode}
          type="button"
          role="switch"
          aria-checked={advancedMode}
          className={`relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
            advancedMode ? "bg-[#111111]" : "bg-[#D4D4D4]"
          }`}
        >
          <span
            className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
              advancedMode ? "translate-x-5" : "translate-x-0"
            }`}
          />
        </button>
      </div>

      {/* System Hardware Diagnostics Info */}
      <div className="p-5 rounded-xl border border-[#E5E5E5] bg-[#FFFFFF] shadow-xs space-y-3">
        <div className="flex items-center gap-2.5">
          <Cpu size={16} strokeWidth={1.75} className="text-[#111111]" />
          <h3 className="text-sm font-semibold text-[#111111]">
            Connected Daemon Hardware
          </h3>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs pt-1">
          <div className="p-2.5 rounded border border-[#E5E5E5] bg-[#F5F5F5]">
            <div className="text-[10px] text-[#737373] uppercase">ESP32 Status</div>
            <div className="font-mono font-semibold text-[#111111] mt-0.5">
              {stats?.esp_connected ? "Connected" : "Disconnected"}
            </div>
          </div>
          <div className="p-2.5 rounded border border-[#E5E5E5] bg-[#F5F5F5]">
            <div className="text-[10px] text-[#737373] uppercase">Serial Port</div>
            <div className="font-mono font-semibold text-[#111111] mt-0.5 truncate">
              {stats?.esp_port || "N/A"}
            </div>
          </div>
          <div className="p-2.5 rounded border border-[#E5E5E5] bg-[#F5F5F5]">
            <div className="text-[10px] text-[#737373] uppercase">Secondary Wi-Fi</div>
            <div className="font-mono font-semibold text-[#111111] mt-0.5">
              {stats?.wlan1_detected ? "Detected" : "None"}
            </div>
          </div>
          <div className="p-2.5 rounded border border-[#E5E5E5] bg-[#F5F5F5]">
            <div className="text-[10px] text-[#737373] uppercase">DNS Port</div>
            <div className="font-mono font-semibold text-[#111111] mt-0.5">
              UDP 5353
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
