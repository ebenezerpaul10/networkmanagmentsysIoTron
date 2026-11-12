import React from "react";
import {
  Activity,
  Wifi,
  Shield,
  Cpu,
  ArrowUpRight,
  TrendingDown,
  TrendingUp,
  Bot,
  Zap,
} from "lucide-react";
import type { NetShieldStats } from "../types";
import {
  AreaChart,
  Area,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

interface OverviewViewProps {
  stats: NetShieldStats | null;
  advancedMode: boolean;
  onNavigateTab: (tab: any) => void;
  onRunBenchmark: () => void;
  onTriggerSwitch: () => void;
}

export const OverviewView: React.FC<OverviewViewProps> = ({
  stats,
  advancedMode,
  onNavigateTab,
  onRunBenchmark,
  onTriggerSwitch,
}) => {
  if (!stats) {
    return (
      <div className="flex items-center justify-center h-64 text-sm text-[#737373]">
        Awaiting telemetry from NetShield daemon...
      </div>
    );
  }

  const {
    latency_ms,
    network_health,
    current_signal,
    best_rssi,
    radar_source,
    blocked_queries,
    bandwidth_saved_kb,
    health_score,
    score_status,
    download_speed_mbps,
    download_speed_str,
    before_metrics,
    after_metrics,
    improvements,
    traffic_wave,
    robo_speech,
    esp_connected,
  } = stats;

  const sparklineData = (traffic_wave || []).map((val, idx) => ({
    i: idx + 1,
    utilization: val,
  }));

  // Latency indicator dot
  const latencyDot =
    latency_ms <= 0
      ? "bg-[#EF4444]"
      : latency_ms < 40
      ? "bg-[#10B981]"
      : latency_ms < 90
      ? "bg-[#F59E0B]"
      : "bg-[#EF4444]";

  return (
    <div className="space-y-6">
      {/* 4 Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Internet Status */}
        <div className="p-4 rounded-xl border border-[#E5E5E5] bg-[#FFFFFF] shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-[#737373]">Internet Status</span>
            <Activity size={15} strokeWidth={1.75} className="text-[#737373]" />
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-2xl font-semibold tracking-tight text-[#111111] font-mono">
              {latency_ms >= 0 ? `${latency_ms.toFixed(1)} ms` : "Timeout"}
            </span>
          </div>
          <div className="mt-2 flex items-center gap-1.5 text-xs text-[#737373]">
            <span className={`w-2 h-2 rounded-full ${latencyDot}`} />
            <span className="truncate">{network_health || "Analyzing connection"}</span>
          </div>
        </div>

        {/* Card 2: Signal Strength */}
        <div className="p-4 rounded-xl border border-[#E5E5E5] bg-[#FFFFFF] shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-[#737373]">Signal Strength</span>
            <Wifi size={15} strokeWidth={1.75} className="text-[#737373]" />
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-2xl font-semibold tracking-tight text-[#111111] font-mono">
              {current_signal}%
            </span>
            <span className="text-xs text-[#737373] font-mono">
              {best_rssi ? `${best_rssi} dBm` : "Optimal"}
            </span>
          </div>
          <div className="mt-2 flex items-center gap-1.5 text-xs text-[#737373]">
            <span
              className={`w-2 h-2 rounded-full ${
                current_signal >= 70
                  ? "bg-[#10B981]"
                  : current_signal >= 40
                  ? "bg-[#F59E0B]"
                  : "bg-[#EF4444]"
              }`}
            />
            <span className="truncate font-mono">Ch {stats.current_channel || 1} · {stats.current_ssid || "Wi-Fi"}</span>
          </div>
        </div>

        {/* Card 3: Active Interface */}
        <div className="p-4 rounded-xl border border-[#E5E5E5] bg-[#FFFFFF] shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-[#737373]">Active Radar Interface</span>
            <Cpu size={15} strokeWidth={1.75} className="text-[#737373]" />
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-base font-semibold tracking-tight text-[#111111] truncate">
              {esp_connected ? "ESP32 Hardware" : "Laptop Wi-Fi"}
            </span>
          </div>
          <div className="mt-2 flex items-center gap-1.5 text-xs text-[#737373]">
            <span
              className={`w-2 h-2 rounded-full ${
                esp_connected ? "bg-[#10B981]" : "bg-[#F59E0B]"
              }`}
            />
            <span className="truncate font-mono text-[11px]">{radar_source}</span>
          </div>
        </div>

        {/* Card 4: DNS Protection */}
        <div className="p-4 rounded-xl border border-[#E5E5E5] bg-[#FFFFFF] shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-[#737373]">DNS Shield Protection</span>
            <Shield size={15} strokeWidth={1.75} className="text-[#737373]" />
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-2xl font-semibold tracking-tight text-[#111111] font-mono">
              {blocked_queries}
            </span>
            <span className="text-xs text-[#737373]">blocked</span>
          </div>
          <div className="mt-2 flex items-center gap-1.5 text-xs text-[#737373]">
            <span className="w-2 h-2 rounded-full bg-[#10B981]" />
            <span className="truncate font-mono text-[11px]">
              {bandwidth_saved_kb.toFixed(1)} KB traffic saved
            </span>
          </div>
        </div>
      </div>

      {/* Hero Section: Master Health Score + Live Air Traffic */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Master Score Card */}
        <div className="p-5 rounded-xl border border-[#E5E5E5] bg-[#FFFFFF] shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-[#737373]">
                Master Network Health
              </span>
              <span
                className={`text-[10px] font-mono px-2 py-0.5 rounded border ${
                  health_score >= 80
                    ? "bg-[#F5F5F5] border-[#E5E5E5] text-[#111111]"
                    : health_score >= 60
                    ? "bg-[#F5F5F5] border-[#E5E5E5] text-[#111111]"
                    : "bg-[#F5F5F5] border-[#EF4444] text-[#EF4444]"
                }`}
              >
                {score_status}
              </span>
            </div>

            <div className="mt-6 flex items-center gap-5">
              <div className="w-20 h-20 rounded-xl border border-[#E5E5E5] bg-[#F5F5F5] flex flex-col items-center justify-center">
                <span className="text-3xl font-bold font-mono text-[#111111] tracking-tight">
                  {health_score}
                </span>
                <span className="text-[10px] font-mono text-[#737373] uppercase">
                  / 100
                </span>
              </div>
              <div className="space-y-1">
                <div className="text-sm font-semibold text-[#111111]">
                  {health_score >= 80
                    ? "Optimal Link Quality"
                    : health_score >= 60
                    ? "Satisfactory Quality"
                    : "Suboptimal Link Condition"}
                </div>
                <div className="text-xs text-[#737373] leading-relaxed">
                  {stats.simple_summary || "Real-time analysis from ESP32 & internal adapter."}
                </div>
              </div>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-[#E5E5E5] flex items-center justify-between text-xs">
            <span className="text-[#737373]">Live Speed:</span>
            <span className="font-mono font-semibold text-[#111111]">
              {download_speed_str || `${download_speed_mbps.toFixed(2)} Mbps`}
            </span>
          </div>
        </div>

        {/* Live Channel / Air Traffic Sparkline Chart */}
        <div className="lg:col-span-2 p-5 rounded-xl border border-[#E5E5E5] bg-[#FFFFFF] shadow-xs flex flex-col justify-between">
          <div className="flex items-center justify-between mb-2">
            <div>
              <div className="text-xs font-semibold uppercase tracking-wider text-[#737373]">
                RF Medium Congestion Index
              </div>
              <div className="text-xs text-[#111111] font-medium mt-0.5">
                Channel Utilization Waveform (0–100%)
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span
                className={`text-[10px] font-mono px-2 py-0.5 rounded border font-medium ${
                  stats.esp_connected
                    ? "bg-[#111111] text-[#FFFFFF] border-[#111111]"
                    : "bg-[#F5F5F5] text-[#737373] border-[#E5E5E5]"
                }`}
              >
                {stats.esp_connected ? "ESP32 Active: High Wave" : "Standby: Low Wave"}
              </span>
              <span className="text-xs font-mono text-[#737373]">
                Zone: {stats.traffic_zone || "Normal"}
              </span>
            </div>
          </div>

          <div className="h-36 w-full mt-2">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={sparklineData} margin={{ top: 5, right: 0, left: -25, bottom: 0 }}>
                <defs>
                  <linearGradient id="areaGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#111111" stopOpacity={0.15} />
                    <stop offset="95%" stopColor="#111111" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="i" hide />
                <YAxis domain={[0, 100]} tick={{ fontSize: 10, fill: "#737373" }} />
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      return (
                        <div className="p-2 rounded bg-white border border-[#E5E5E5] shadow-sm text-xs font-mono">
                          Utilization: {payload[0].value}%
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="utilization"
                  stroke="#111111"
                  strokeWidth={1.5}
                  fillOpacity={1}
                  fill="url(#areaGradient)"
                  isAnimationActive={false}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          <div className="mt-3 pt-3 border-t border-[#E5E5E5] flex items-center justify-between text-xs text-[#737373]">
            <span className="font-mono text-[11px]">
              Ch 1: {stats.ch1} APs · Ch 6: {stats.ch6} APs · Ch 11: {stats.ch11} APs
            </span>
            <button
              onClick={() => onNavigateTab("spectrum")}
              className="text-[#111111] hover:underline flex items-center gap-1 font-medium"
            >
              <span>Full Spectrum</span>
              <ArrowUpRight size={12} strokeWidth={1.75} />
            </button>
          </div>
        </div>
      </div>

      {/* Robo-Sentry Calm Enterprise Advisory */}
      <div className="p-4 rounded-xl border border-[#E5E5E5] bg-[#FFFFFF] shadow-xs flex items-start gap-3.5">
        <div className="w-8 h-8 rounded-lg bg-[#F5F5F5] border border-[#E5E5E5] flex items-center justify-center shrink-0 text-[#111111]">
          <Bot size={16} strokeWidth={1.75} />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-[#111111]">
              NetShield Copilot Observation
            </span>
            <span className="text-[10px] font-mono text-[#737373] uppercase tracking-wider">
              Autonomous Monitor
            </span>
          </div>
          <p className="text-xs text-[#737373] mt-1 leading-relaxed">
            {robo_speech || "Continuously inspecting airwaves for lowest latency paths."}
          </p>
        </div>
      </div>

      {/* Before vs. After Optimization Matrix */}
      <div className="p-5 rounded-xl border border-[#E5E5E5] bg-[#FFFFFF] shadow-xs space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-sm font-semibold text-[#111111]">
              Performance Optimization Matrix
            </h2>
            <p className="text-xs text-[#737373] mt-0.5">
              Truthful comparison between recorded Baseline snapshot and Live telemetry.
            </p>
          </div>

          {/* Quick Metrics Badges */}
          <div className="flex items-center gap-2">
            {improvements.speed_boost_pct > 0 && (
              <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-[#F5F5F5] border border-[#E5E5E5] text-xs font-mono text-[#111111]">
                <TrendingUp size={12} strokeWidth={1.75} className="text-[#10B981]" />
                Speed: +{improvements.speed_boost_pct}%
              </span>
            )}
            {improvements.latency_drop_pct > 0 && (
              <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-[#F5F5F5] border border-[#E5E5E5] text-xs font-mono text-[#111111]">
                <TrendingDown size={12} strokeWidth={1.75} className="text-[#10B981]" />
                Latency: -{improvements.latency_drop_pct}%
              </span>
            )}
            {improvements.signal_gain_pct > 0 && (
              <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-[#F5F5F5] border border-[#E5E5E5] text-xs font-mono text-[#111111]">
                <Zap size={12} strokeWidth={1.75} className="text-[#10B981]" />
                Signal: +{improvements.signal_gain_pct}%
              </span>
            )}
          </div>
        </div>

        {/* Table of Metrics */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-[#E5E5E5] text-[#737373] uppercase tracking-wider text-[10px]">
                <th className="py-2.5 px-3 font-semibold">Parameter</th>
                <th className="py-2.5 px-3 font-semibold">Baseline Reference</th>
                <th className="py-2.5 px-3 font-semibold">Live State</th>
                <th className="py-2.5 px-3 font-semibold text-right">Optimization Delta</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#E5E5E5]">
              <tr>
                <td className="py-3 px-3 font-medium text-[#111111]">Access Point (BSSID)</td>
                <td className="py-3 px-3 font-mono text-[#737373]">
                  {before_metrics?.bssid || "KU-WL"}
                </td>
                <td className="py-3 px-3 font-mono text-[#111111] font-semibold">
                  {after_metrics?.bssid || "Live State"}
                </td>
                <td className="py-3 px-3 text-right">
                  <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-[#F5F5F5] border border-[#E5E5E5] text-[#111111]">
                    {improvements.channel_cleared ? "Steered to cleaner BSSID" : "Active Link"}
                  </span>
                </td>
              </tr>
              <tr>
                <td className="py-3 px-3 font-medium text-[#111111]">Wi-Fi Channel</td>
                <td className="py-3 px-3 font-mono text-[#737373]">
                  Channel {before_metrics?.channel ?? 6}
                </td>
                <td className="py-3 px-3 font-mono text-[#111111] font-semibold">
                  Channel {after_metrics?.channel ?? stats.current_channel}
                </td>
                <td className="py-3 px-3 text-right font-mono text-[#111111]">
                  {improvements.channel_cleared ? "Cleaned" : "Maintained"}
                </td>
              </tr>
              <tr>
                <td className="py-3 px-3 font-medium text-[#111111]">Ping Latency</td>
                <td className="py-3 px-3 font-mono text-[#737373]">
                  {before_metrics?.latency_ms ?? 0} ms
                </td>
                <td className="py-3 px-3 font-mono text-[#111111] font-semibold">
                  {after_metrics?.latency_ms ?? latency_ms.toFixed(1)} ms
                </td>
                <td className="py-3 px-3 text-right font-mono">
                  {improvements.latency_drop_pct > 0 ? (
                    <span className="text-[#10B981] font-medium">-{improvements.latency_drop_pct}%</span>
                  ) : (
                    <span className="text-[#737373]">Steady</span>
                  )}
                </td>
              </tr>
              <tr>
                <td className="py-3 px-3 font-medium text-[#111111]">Signal Quality</td>
                <td className="py-3 px-3 font-mono text-[#737373]">
                  {before_metrics?.signal ?? 55}%
                </td>
                <td className="py-3 px-3 font-mono text-[#111111] font-semibold">
                  {after_metrics?.signal ?? current_signal}%
                </td>
                <td className="py-3 px-3 text-right font-mono">
                  {improvements.signal_gain_pct > 0 ? (
                    <span className="text-[#10B981] font-medium">+{improvements.signal_gain_pct}%</span>
                  ) : (
                    <span className="text-[#737373]">0%</span>
                  )}
                </td>
              </tr>
              <tr>
                <td className="py-3 px-3 font-medium text-[#111111]">Download Speed</td>
                <td className="py-3 px-3 font-mono text-[#737373]">
                  {before_metrics?.download_speed || "Awaiting Test"}
                </td>
                <td className="py-3 px-3 font-mono text-[#111111] font-semibold">
                  {after_metrics?.download_speed || download_speed_str}
                </td>
                <td className="py-3 px-3 text-right font-mono">
                  {improvements.speed_boost_pct > 0 ? (
                    <span className="text-[#10B981] font-medium">+{improvements.speed_boost_pct}% Boost</span>
                  ) : (
                    <span className="text-[#737373]">Awaiting Test</span>
                  )}
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        {advancedMode && (
          <div className="pt-2 flex items-center justify-between text-xs text-[#737373]">
            <span>Baseline timestamp: {before_metrics?.timestamp || "N/A"}</span>
            <span>Live snapshot: {after_metrics?.timestamp || "Continuous"}</span>
          </div>
        )}
      </div>
    </div>
  );
};
