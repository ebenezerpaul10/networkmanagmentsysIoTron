import React, { useState } from "react";
import { Activity, AlertCircle, Info, Radio, Layers } from "lucide-react";
import type { NetShieldStats } from "../types";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
} from "recharts";

interface SpectrumAnalyzerViewProps {
  stats: NetShieldStats | null;
  advancedMode: boolean;
}

export const SpectrumAnalyzerView: React.FC<SpectrumAnalyzerViewProps> = ({
  stats,
  advancedMode,
}) => {
  const [chartType, setChartType] = useState<"line" | "bar">("line");

  if (!stats) {
    return (
      <div className="flex items-center justify-center h-64 text-sm text-[#737373]">
        Awaiting Spectrum telemetry...
      </div>
    );
  }

  const {
    ch1,
    ch6,
    ch11,
    total_aps,
    spectrum_history,
    highway,
    current_channel,
    esp_connected,
    radar_source,
  } = stats;

  const chartHistoryData = (spectrum_history || []).map((pt, i) => ({
    time: `t-${spectrum_history.length - i}s`,
    "Channel 1 (2.412 GHz)": pt.ch1 ?? 0,
    "Channel 6 (2.437 GHz)": pt.ch6 ?? 0,
    "Channel 11 (2.462 GHz)": pt.ch11 ?? 0,
  }));

  const barData = [
    { channel: "Ch 1", aps: ch1, frequency: "2.412 GHz" },
    { channel: "Ch 6", aps: ch6, frequency: "2.437 GHz" },
    { channel: "Ch 11", aps: ch11, frequency: "2.462 GHz" },
  ];

  return (
    <div className="space-y-6">
      {/* Honest Hardware Notice Banner */}
      <div className="p-4 rounded-xl border border-[#E5E5E5] bg-[#FFFFFF] shadow-xs flex items-start gap-3">
        <div className="p-1.5 rounded-lg bg-[#F5F5F5] border border-[#E5E5E5] text-[#111111] shrink-0">
          <Info size={16} strokeWidth={1.75} />
        </div>
        <div>
          <div className="text-xs font-semibold text-[#111111]">
            Hardware Radio Architecture Disclosure
          </div>
          <p className="text-xs text-[#737373] mt-0.5 leading-relaxed">
            RF Hardware Sensor: ESP32 2.4 GHz (Channels 1–13). 5 GHz / 6 GHz scanning is not supported by current radio hardware.
          </p>
        </div>
      </div>

      {/* 3 Lane Highway Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {/* Lane 1 */}
        <div
          className={`p-5 rounded-xl border bg-[#FFFFFF] shadow-xs space-y-3 transition-all ${
            current_channel === 1 ? "border-[#111111] ring-1 ring-[#111111]" : "border-[#E5E5E5]"
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-[#737373]">
              Highway Lane 1
            </span>
            <span className="text-xs font-mono px-2 py-0.5 rounded bg-[#F5F5F5] border border-[#E5E5E5] text-[#111111]">
              Ch 1 · 2.412 GHz
            </span>
          </div>

          <div className="flex items-baseline justify-between">
            <div>
              <div className="text-2xl font-bold font-mono text-[#111111]">
                {ch1} <span className="text-xs font-normal text-[#737373]">AP beacons</span>
              </div>
              <div className="text-xs text-[#737373] mt-1">{highway.lane1.desc}</div>
            </div>
          </div>

          <div className="pt-2 border-t border-[#E5E5E5] flex items-center justify-between">
            <span className="text-xs font-medium text-[#111111]">{highway.lane1.status}</span>
            {current_channel === 1 && (
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#111111] text-[#FFFFFF]">
                Active Client
              </span>
            )}
            {highway.best_lane === 1 && current_channel !== 1 && (
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#F5F5F5] border border-[#E5E5E5] text-[#10B981] font-semibold">
                Cleanest Lane
              </span>
            )}
          </div>
        </div>

        {/* Lane 6 */}
        <div
          className={`p-5 rounded-xl border bg-[#FFFFFF] shadow-xs space-y-3 transition-all ${
            current_channel === 6 ? "border-[#111111] ring-1 ring-[#111111]" : "border-[#E5E5E5]"
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-[#737373]">
              Highway Lane 6
            </span>
            <span className="text-xs font-mono px-2 py-0.5 rounded bg-[#F5F5F5] border border-[#E5E5E5] text-[#111111]">
              Ch 6 · 2.437 GHz
            </span>
          </div>

          <div className="flex items-baseline justify-between">
            <div>
              <div className="text-2xl font-bold font-mono text-[#111111]">
                {ch6} <span className="text-xs font-normal text-[#737373]">AP beacons</span>
              </div>
              <div className="text-xs text-[#737373] mt-1">{highway.lane6.desc}</div>
            </div>
          </div>

          <div className="pt-2 border-t border-[#E5E5E5] flex items-center justify-between">
            <span className="text-xs font-medium text-[#111111]">{highway.lane6.status}</span>
            {current_channel === 6 && (
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#111111] text-[#FFFFFF]">
                Active Client
              </span>
            )}
            {highway.best_lane === 6 && current_channel !== 6 && (
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#F5F5F5] border border-[#E5E5E5] text-[#10B981] font-semibold">
                Cleanest Lane
              </span>
            )}
          </div>
        </div>

        {/* Lane 11 */}
        <div
          className={`p-5 rounded-xl border bg-[#FFFFFF] shadow-xs space-y-3 transition-all ${
            current_channel === 11 ? "border-[#111111] ring-1 ring-[#111111]" : "border-[#E5E5E5]"
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-[#737373]">
              Highway Lane 11
            </span>
            <span className="text-xs font-mono px-2 py-0.5 rounded bg-[#F5F5F5] border border-[#E5E5E5] text-[#111111]">
              Ch 11 · 2.462 GHz
            </span>
          </div>

          <div className="flex items-baseline justify-between">
            <div>
              <div className="text-2xl font-bold font-mono text-[#111111]">
                {ch11} <span className="text-xs font-normal text-[#737373]">AP beacons</span>
              </div>
              <div className="text-xs text-[#737373] mt-1">{highway.lane11.desc}</div>
            </div>
          </div>

          <div className="pt-2 border-t border-[#E5E5E5] flex items-center justify-between">
            <span className="text-xs font-medium text-[#111111]">{highway.lane11.status}</span>
            {current_channel === 11 && (
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#111111] text-[#FFFFFF]">
                Active Client
              </span>
            )}
            {highway.best_lane === 11 && current_channel !== 11 && (
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#F5F5F5] border border-[#E5E5E5] text-[#10B981] font-semibold">
                Cleanest Lane
              </span>
            )}
          </div>
        </div>
      </div>

      {/* RF Spectrum Occupancy History Graph */}
      <div className="p-5 rounded-xl border border-[#E5E5E5] bg-[#FFFFFF] shadow-xs space-y-4">
        <div className="flex items-center justify-between flex-wrap gap-3">
          <div>
            <h3 className="text-sm font-semibold text-[#111111]">
              Real-Time RF Channel Occupancy Telemetry
            </h3>
            <p className="text-xs text-[#737373] mt-0.5">
              Live non-overlapping channel beacon occupancy stream ({radar_source}).
            </p>
          </div>

          {/* Chart Controls */}
          <div className="flex items-center gap-1.5 p-0.5 rounded-lg border border-[#E5E5E5] bg-[#F5F5F5]">
            <button
              onClick={() => setChartType("line")}
              className={`px-3 py-1 text-xs font-medium rounded-md transition-colors ${
                chartType === "line"
                  ? "bg-[#FFFFFF] text-[#111111] shadow-xs"
                  : "text-[#737373] hover:text-[#111111]"
              }`}
            >
              Time Series Wave
            </button>
            <button
              onClick={() => setChartType("bar")}
              className={`px-3 py-1 text-xs font-medium rounded-md transition-colors ${
                chartType === "bar"
                  ? "bg-[#FFFFFF] text-[#111111] shadow-xs"
                  : "text-[#737373] hover:text-[#111111]"
              }`}
            >
              Channel Bar Distribution
            </button>
          </div>
        </div>

        {/* Chart Container */}
        <div className="h-72 w-full pt-2">
          {chartType === "line" ? (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartHistoryData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#F0F0F0" vertical={false} />
                <XAxis dataKey="time" tick={{ fontSize: 10, fill: "#737373" }} hide />
                <YAxis
                  domain={[0, "auto"]}
                  tick={{ fontSize: 10, fill: "#737373" }}
                  allowDecimals={false}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#FFFFFF",
                    borderColor: "#E5E5E5",
                    fontSize: "12px",
                    fontFamily: "monospace",
                    borderRadius: "8px",
                    boxShadow: "0 2px 4px rgba(0,0,0,0.05)",
                  }}
                />
                <Legend
                  wrapperStyle={{ fontSize: "11px", paddingTop: "12px", fontFamily: "sans-serif" }}
                />
                <Line
                  type="monotone"
                  dataKey="Channel 1 (2.412 GHz)"
                  stroke="#737373"
                  strokeWidth={1.75}
                  dot={false}
                  isAnimationActive={false}
                />
                <Line
                  type="monotone"
                  dataKey="Channel 6 (2.437 GHz)"
                  stroke="#111111"
                  strokeWidth={2}
                  dot={false}
                  isAnimationActive={false}
                />
                <Line
                  type="monotone"
                  dataKey="Channel 11 (2.462 GHz)"
                  stroke="#A3A3A3"
                  strokeDasharray="4 4"
                  strokeWidth={1.75}
                  dot={false}
                  isAnimationActive={false}
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={barData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#F0F0F0" vertical={false} />
                <XAxis dataKey="channel" tick={{ fontSize: 11, fill: "#111111" }} />
                <YAxis tick={{ fontSize: 10, fill: "#737373" }} allowDecimals={false} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#FFFFFF",
                    borderColor: "#E5E5E5",
                    fontSize: "12px",
                    borderRadius: "8px",
                  }}
                />
                <Bar dataKey="aps" name="Detected Access Points" fill="#111111" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>
    </div>
  );
};
