import React from "react";
import {
  Wifi,
  Radio,
  CheckCircle2,
  RefreshCw,
  Compass,
  ArrowRight,
  ShieldAlert,
} from "lucide-react";
import type { NetShieldStats } from "../types";

interface WifiManagerViewProps {
  stats: NetShieldStats | null;
  advancedMode: boolean;
  onRequestSwitch: () => void;
  isSwitching: boolean;
}

export const WifiManagerView: React.FC<WifiManagerViewProps> = ({
  stats,
  advancedMode,
  onRequestSwitch,
  isSwitching,
}) => {
  if (!stats) {
    return (
      <div className="flex items-center justify-center h-64 text-sm text-[#737373]">
        Awaiting Wi-Fi telemetry...
      </div>
    );
  }

  const {
    current_ssid,
    current_bssid,
    current_channel,
    current_signal,
    best_ssid,
    best_bssid,
    recommended_channel,
    best_rssi,
    congestion_score,
    total_aps,
    ch1,
    ch6,
    ch11,
  } = stats;

  const isCurrentOptimal = current_channel === recommended_channel && current_bssid === best_bssid;

  return (
    <div className="space-y-6">
      {/* Top Banner / Summary */}
      <div className="p-5 rounded-xl border border-[#E5E5E5] bg-[#FFFFFF] shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-base font-semibold text-[#111111]">
              Access Point Steering & BSSID Management
            </h2>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#F5F5F5] border border-[#E5E5E5] text-[#111111]">
              L2 Handover
            </span>
          </div>
          <p className="text-xs text-[#737373] mt-1 max-w-2xl leading-relaxed">
            NetShield continuously evaluates nearby radio beacons to prevent sticky-client degradation by steering your adapter to the cleanest, highest-throughput BSSID on your target SSID.
          </p>
        </div>

        <button
          onClick={onRequestSwitch}
          disabled={isSwitching}
          className="inline-flex items-center justify-center gap-2 px-4 py-2 text-xs font-medium rounded-lg bg-[#111111] text-[#FFFFFF] hover:bg-[#262626] transition-colors shrink-0 disabled:opacity-50"
        >
          {isSwitching ? (
            <RefreshCw size={14} strokeWidth={1.75} className="animate-spin text-white" />
          ) : (
            <Compass size={14} strokeWidth={1.75} className="text-white" />
          )}
          <span>Steer to Cleanest BSSID</span>
        </button>
      </div>

      {/* Grid: Active Link vs Recommended Target */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Active Connected Access Point */}
        <div className="p-5 rounded-xl border border-[#E5E5E5] bg-[#FFFFFF] shadow-xs space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-[#10B981]" />
              <span className="text-xs font-semibold uppercase tracking-wider text-[#737373]">
                Active Connection
              </span>
            </div>
            <span className="text-xs font-mono px-2 py-0.5 rounded bg-[#F5F5F5] border border-[#E5E5E5] text-[#111111]">
              Ch {current_channel || 1}
            </span>
          </div>

          <div>
            <div className="text-xl font-bold text-[#111111] tracking-tight">
              {current_ssid || "Scanning..."}
            </div>
            <div className="mt-1 flex items-center gap-2 text-xs text-[#737373]">
              <span>BSSID:</span>
              <span className="font-mono text-[#111111] font-medium">
                {current_bssid || "N/A"}
              </span>
            </div>
          </div>

          <div className="pt-3 border-t border-[#E5E5E5] grid grid-cols-2 gap-4">
            <div>
              <div className="text-[11px] text-[#737373]">Signal Strength</div>
              <div className="mt-1 flex items-baseline gap-1.5">
                <span className="text-lg font-semibold font-mono text-[#111111]">
                  {current_signal}%
                </span>
                <span className="text-xs font-mono text-[#737373]">
                  {best_rssi ? `${best_rssi} dBm` : ""}
                </span>
              </div>
            </div>
            <div>
              <div className="text-[11px] text-[#737373]">Channel Status</div>
              <div className="mt-1 flex items-baseline gap-1.5">
                <span className="text-sm font-semibold font-mono text-[#111111]">
                  Lane {current_channel || 1}
                </span>
                <span className="text-[11px] text-[#737373]">
                  ({current_channel === 1 ? ch1 : current_channel === 6 ? ch6 : ch11} APs)
                </span>
              </div>
            </div>
          </div>

          <div className="w-full bg-[#F5F5F5] h-1.5 rounded-full overflow-hidden">
            <div
              className="bg-[#111111] h-full transition-all duration-500"
              style={{ width: `${Math.min(100, Math.max(5, current_signal))}%` }}
            />
          </div>
        </div>

        {/* Cleanest Recommended Access Point */}
        <div className="p-5 rounded-xl border border-[#111111] bg-[#FFFFFF] shadow-xs space-y-4 relative">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-[#10B981]" />
              <span className="text-xs font-semibold uppercase tracking-wider text-[#111111]">
                Recommended Candidate AP
              </span>
            </div>
            <span className="text-xs font-mono px-2 py-0.5 rounded bg-[#111111] text-[#FFFFFF]">
              Ch {recommended_channel || 1}
            </span>
          </div>

          <div>
            <div className="text-xl font-bold text-[#111111] tracking-tight">
              {best_ssid || current_ssid || "Cleanest Candidate"}
            </div>
            <div className="mt-1 flex items-center gap-2 text-xs text-[#737373]">
              <span>Target BSSID:</span>
              <span className="font-mono text-[#111111] font-semibold">
                {best_bssid || "Auto-Candidate Selection"}
              </span>
            </div>
          </div>

          <div className="pt-3 border-t border-[#E5E5E5] grid grid-cols-2 gap-4">
            <div>
              <div className="text-[11px] text-[#737373]">Congestion Index</div>
              <div className="mt-1 flex items-baseline gap-1.5">
                <span className="text-lg font-semibold font-mono text-[#111111]">
                  {congestion_score}/100
                </span>
                <span className="text-xs text-[#10B981]">Clean Lane</span>
              </div>
            </div>
            <div>
              <div className="text-[11px] text-[#737373]">Status</div>
              <div className="mt-1 flex items-baseline gap-1.5">
                {isCurrentOptimal ? (
                  <span className="text-xs font-semibold text-[#10B981] flex items-center gap-1">
                    <CheckCircle2 size={13} strokeWidth={1.75} />
                    Connected to Best AP
                  </span>
                ) : (
                  <span className="text-xs font-semibold text-[#111111] flex items-center gap-1">
                    Candidate Ready
                  </span>
                )}
              </div>
            </div>
          </div>

          <div className="pt-1">
            <button
              onClick={onRequestSwitch}
              disabled={isSwitching || isCurrentOptimal}
              className={`w-full py-2 px-3 text-xs font-medium rounded-lg flex items-center justify-center gap-2 transition-colors ${
                isCurrentOptimal
                  ? "bg-[#F5F5F5] text-[#737373] border border-[#E5E5E5] cursor-default"
                  : "bg-[#111111] text-[#FFFFFF] hover:bg-[#262626]"
              }`}
            >
              <span>{isCurrentOptimal ? "Optimal BSSID Connected" : "Steer Connection Now"}</span>
              {!isCurrentOptimal && <ArrowRight size={13} strokeWidth={1.75} />}
            </button>
          </div>
        </div>
      </div>

      {/* Nearby Scan Summary Table */}
      <div className="p-5 rounded-xl border border-[#E5E5E5] bg-[#FFFFFF] shadow-xs space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-semibold text-[#111111]">
              Nearby RF Environmental Scan
            </h3>
            <p className="text-xs text-[#737373] mt-0.5">
              Discovered {total_aps} surrounding BSSIDs on 2.4 GHz non-overlapping channels.
            </p>
          </div>
          <span className="text-xs font-mono text-[#737373]">
            {stats.esp_connected ? "Antenna: ESP32 Hardware" : "Antenna: Host Adapter"}
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-[#E5E5E5] text-[#737373] uppercase tracking-wider text-[10px]">
                <th className="py-2.5 px-3 font-semibold">Channel</th>
                <th className="py-2.5 px-3 font-semibold">Frequency Band</th>
                <th className="py-2.5 px-3 font-semibold">Detected Beacons</th>
                <th className="py-2.5 px-3 font-semibold">Highway Congestion Rating</th>
                <th className="py-2.5 px-3 font-semibold text-right">Controller Advice</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#E5E5E5]">
              <tr className={current_channel === 1 ? "bg-[#F5F5F5]/60" : ""}>
                <td className="py-3 px-3 font-mono font-medium text-[#111111]">
                  Channel 1 {current_channel === 1 && <span className="text-[10px] text-[#737373]">(Active)</span>}
                </td>
                <td className="py-3 px-3 font-mono text-[#737373]">2.412 GHz</td>
                <td className="py-3 px-3 font-mono text-[#111111]">{ch1} APs</td>
                <td className="py-3 px-3">
                  <span className="inline-flex items-center gap-1.5">
                    <span className={`w-2 h-2 rounded-full ${ch1 >= 4 ? "bg-[#EF4444]" : ch1 >= 2 ? "bg-[#F59E0B]" : "bg-[#10B981]"}`} />
                    <span className="font-medium text-[#111111]">{stats.highway.lane1.status}</span>
                  </span>
                </td>
                <td className="py-3 px-3 text-right font-mono">
                  {recommended_channel === 1 ? (
                    <span className="text-[#10B981] font-semibold">Optimal</span>
                  ) : (
                    <span className="text-[#737373]">Standby</span>
                  )}
                </td>
              </tr>
              <tr className={current_channel === 6 ? "bg-[#F5F5F5]/60" : ""}>
                <td className="py-3 px-3 font-mono font-medium text-[#111111]">
                  Channel 6 {current_channel === 6 && <span className="text-[10px] text-[#737373]">(Active)</span>}
                </td>
                <td className="py-3 px-3 font-mono text-[#737373]">2.437 GHz</td>
                <td className="py-3 px-3 font-mono text-[#111111]">{ch6} APs</td>
                <td className="py-3 px-3">
                  <span className="inline-flex items-center gap-1.5">
                    <span className={`w-2 h-2 rounded-full ${ch6 >= 4 ? "bg-[#EF4444]" : ch6 >= 2 ? "bg-[#F59E0B]" : "bg-[#10B981]"}`} />
                    <span className="font-medium text-[#111111]">{stats.highway.lane6.status}</span>
                  </span>
                </td>
                <td className="py-3 px-3 text-right font-mono">
                  {recommended_channel === 6 ? (
                    <span className="text-[#10B981] font-semibold">Optimal</span>
                  ) : (
                    <span className="text-[#737373]">Standby</span>
                  )}
                </td>
              </tr>
              <tr className={current_channel === 11 ? "bg-[#F5F5F5]/60" : ""}>
                <td className="py-3 px-3 font-mono font-medium text-[#111111]">
                  Channel 11 {current_channel === 11 && <span className="text-[10px] text-[#737373]">(Active)</span>}
                </td>
                <td className="py-3 px-3 font-mono text-[#737373]">2.462 GHz</td>
                <td className="py-3 px-3 font-mono text-[#111111]">{ch11} APs</td>
                <td className="py-3 px-3">
                  <span className="inline-flex items-center gap-1.5">
                    <span className={`w-2 h-2 rounded-full ${ch11 >= 4 ? "bg-[#EF4444]" : ch11 >= 2 ? "bg-[#F59E0B]" : "bg-[#10B981]"}`} />
                    <span className="font-medium text-[#111111]">{stats.highway.lane11.status}</span>
                  </span>
                </td>
                <td className="py-3 px-3 text-right font-mono">
                  {recommended_channel === 11 ? (
                    <span className="text-[#10B981] font-semibold">Optimal</span>
                  ) : (
                    <span className="text-[#737373]">Standby</span>
                  )}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
