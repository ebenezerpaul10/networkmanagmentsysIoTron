import React from "react";
import {
  Layers,
  Gauge,
  RefreshCw,
  Info,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  TrendingUp,
} from "lucide-react";
import type { BenchmarkResult, NetShieldStats } from "../types";

interface DualLinkViewProps {
  stats: NetShieldStats | null;
  advancedMode: boolean;
  onRunBenchmark: () => void;
  isBenchmarking: boolean;
  lastBenchmarkResult: BenchmarkResult | null;
}

export const DualLinkView: React.FC<DualLinkViewProps> = ({
  stats,
  advancedMode,
  onRunBenchmark,
  isBenchmarking,
  lastBenchmarkResult,
}) => {
  if (!stats) {
    return (
      <div className="flex items-center justify-center h-64 text-sm text-[#737373]">
        Awaiting Dual-Link telemetry...
      </div>
    );
  }

  const {
    wlan0_speed_mbps,
    wlan1_speed_mbps,
    dual_combined_mbps,
    wlan1_detected,
    improvements,
  } = stats;

  return (
    <div className="space-y-6">
      {/* Honest Routing Disclosure Card */}
      <div className="p-4 rounded-xl border border-[#E5E5E5] bg-[#FFFFFF] shadow-xs flex items-start gap-3.5">
        <div className="p-1.5 rounded-lg bg-[#F5F5F5] border border-[#E5E5E5] text-[#111111] shrink-0">
          <Info size={16} strokeWidth={1.75} />
        </div>
        <div>
          <div className="text-xs font-semibold text-[#111111]">
            Multi-Link Transport Architecture Disclosure
          </div>
          <p className="text-xs text-[#737373] mt-0.5 leading-relaxed">
            Multi-interface bandwidth aggregation in this environment is performed via application-layer proxy distribution (e.g. <span className="font-mono text-[#111111]">dispatch-proxy</span>) or parallel interface curl benchmarking. It does not construct low-level L2 link aggregation or L3 Multipath TCP (MPTCP) kernel trunks.
          </p>
        </div>
      </div>

      {/* Interface Split Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {/* Primary Interface */}
        <div className="p-5 rounded-xl border border-[#E5E5E5] bg-[#FFFFFF] shadow-xs space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-[#737373]">
              Primary Link (wlan0)
            </span>
            <span className="text-xs font-mono px-2 py-0.5 rounded bg-[#F5F5F5] border border-[#E5E5E5] text-[#111111]">
              Built-in Wi-Fi
            </span>
          </div>

          <div>
            <div className="text-2xl font-bold font-mono text-[#111111]">
              {wlan0_speed_mbps > 0 ? `${wlan0_speed_mbps.toFixed(1)} Mbps` : "Idle / Standby"}
            </div>
            <div className="text-xs text-[#737373] mt-1">
              Internal network card endpoint
            </div>
          </div>

          <div className="pt-2 border-t border-[#E5E5E5] flex items-center justify-between text-xs">
            <span className="text-[#737373]">Status:</span>
            <span className="font-medium text-[#111111] flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-[#10B981]" />
              Active Route
            </span>
          </div>
        </div>

        {/* Secondary Interface */}
        <div className="p-5 rounded-xl border border-[#E5E5E5] bg-[#FFFFFF] shadow-xs space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-[#737373]">
              Secondary Link (wlan1)
            </span>
            <span
              className={`text-xs font-mono px-2 py-0.5 rounded border ${
                wlan1_detected
                  ? "bg-[#F5F5F5] border-[#E5E5E5] text-[#111111]"
                  : "bg-[#F5F5F5] border-[#E5E5E5] text-[#737373]"
              }`}
            >
              {wlan1_detected ? "USB Adapter Detected" : "Not Detected"}
            </span>
          </div>

          <div>
            <div className="text-2xl font-bold font-mono text-[#111111]">
              {wlan1_detected
                ? wlan1_speed_mbps > 0
                  ? `${wlan1_speed_mbps.toFixed(1)} Mbps`
                  : "Standby"
                : "Disconnected"}
            </div>
            <div className="text-xs text-[#737373] mt-1">
              {wlan1_detected
                ? "Secondary USB Wi-Fi dongle ready"
                : "Plug in USB Wi-Fi dongle to unlock Dual Link"}
            </div>
          </div>

          <div className="pt-2 border-t border-[#E5E5E5] flex items-center justify-between text-xs">
            <span className="text-[#737373]">Status:</span>
            <span className="font-medium text-[#111111] flex items-center gap-1.5">
              <span
                className={`w-2 h-2 rounded-full ${
                  wlan1_detected ? "bg-[#10B981]" : "bg-[#A3A3A3]"
                }`}
              />
              {wlan1_detected ? "Secondary Online" : "Awaiting Hardware"}
            </span>
          </div>
        </div>

        {/* Combined Aggregated Speed */}
        <div className="p-5 rounded-xl border border-[#111111] bg-[#FFFFFF] shadow-xs space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-[#111111]">
              Combined Aggregation
            </span>
            <span className="text-xs font-mono px-2 py-0.5 rounded bg-[#111111] text-[#FFFFFF]">
              Multi-Link
            </span>
          </div>

          <div>
            <div className="text-2xl font-bold font-mono text-[#111111]">
              {dual_combined_mbps > 0 ? `${dual_combined_mbps.toFixed(1)} Mbps` : "Run Benchmark"}
            </div>
            <div className="text-xs text-[#737373] mt-1">
              {improvements.speed_boost_pct > 0
                ? `+${improvements.speed_boost_pct}% boost over solo link`
                : "Parallel socket dispatch speed"}
            </div>
          </div>

          <div className="pt-2 border-t border-[#E5E5E5] flex items-center justify-between text-xs">
            <span className="text-[#737373]">Bonding State:</span>
            <span className="font-medium text-[#111111]">
              {wlan1_detected ? "Dual-Interface Ready" : "Solo Mode (Internal Only)"}
            </span>
          </div>
        </div>
      </div>

      {/* Benchmark Action & Results Section */}
      <div className="p-5 rounded-xl border border-[#E5E5E5] bg-[#FFFFFF] shadow-xs space-y-4">
        <div className="flex items-center justify-between flex-wrap gap-3">
          <div>
            <h3 className="text-sm font-semibold text-[#111111]">
              Dual-Interface Performance Benchmark
            </h3>
            <p className="text-xs text-[#737373] mt-0.5">
              Measures real-world HTTP download bandwidth against Cloudflare CDN across both interfaces concurrently.
            </p>
          </div>

          <button
            onClick={onRunBenchmark}
            disabled={isBenchmarking}
            className="inline-flex items-center gap-2 px-4 py-2 text-xs font-medium rounded-lg bg-[#111111] text-[#FFFFFF] hover:bg-[#262626] transition-colors disabled:opacity-50"
          >
            {isBenchmarking ? (
              <RefreshCw size={14} strokeWidth={1.75} className="animate-spin text-white" />
            ) : (
              <Gauge size={14} strokeWidth={1.75} className="text-white" />
            )}
            <span>{isBenchmarking ? "Measuring Interfaces..." : "Run Throughput Benchmark"}</span>
          </button>
        </div>

        {/* Benchmark Progress or Last Result */}
        {isBenchmarking ? (
          <div className="p-4 rounded-lg border border-[#E5E5E5] bg-[#F5F5F5] flex items-center gap-3">
            <RefreshCw size={16} strokeWidth={1.75} className="animate-spin text-[#111111]" />
            <div className="text-xs text-[#111111] font-medium">
              Transmitting 25 MB test payload via primary and secondary Wi-Fi sockets... Please hold on.
            </div>
          </div>
        ) : lastBenchmarkResult ? (
          <div className="p-4 rounded-lg border border-[#E5E5E5] bg-[#F5F5F5] space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-[#111111] flex items-center gap-1.5">
                <CheckCircle2 size={14} strokeWidth={1.75} className="text-[#10B981]" />
                Benchmark Completed Successfully
              </span>
              <span className="text-xs font-mono text-[#737373]">
                {lastBenchmarkResult.wlan1_connected ? "Dual-Link Mode" : "Solo Mode"}
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-1">
              <div className="p-3 rounded border border-[#E5E5E5] bg-[#FFFFFF]">
                <div className="text-[10px] text-[#737373] uppercase">Primary Speed</div>
                <div className="text-base font-bold font-mono text-[#111111] mt-0.5">
                  {lastBenchmarkResult.solo_speed_mbps.toFixed(1)} Mbps
                </div>
              </div>
              <div className="p-3 rounded border border-[#E5E5E5] bg-[#FFFFFF]">
                <div className="text-[10px] text-[#737373] uppercase">Secondary Speed</div>
                <div className="text-base font-bold font-mono text-[#111111] mt-0.5">
                  {lastBenchmarkResult.wlan1_speed_mbps
                    ? `${lastBenchmarkResult.wlan1_speed_mbps.toFixed(1)} Mbps`
                    : "0.0 Mbps"}
                </div>
              </div>
              <div className="p-3 rounded border border-[#111111] bg-[#FFFFFF]">
                <div className="text-[10px] text-[#111111] uppercase font-semibold">
                  Aggregated Total
                </div>
                <div className="text-base font-bold font-mono text-[#111111] mt-0.5 flex items-center gap-1">
                  <span>{lastBenchmarkResult.dual_speed_mbps.toFixed(1)} Mbps</span>
                  {lastBenchmarkResult.boost_pct > 0 && (
                    <span className="text-xs font-normal text-[#10B981]">
                      (+{lastBenchmarkResult.boost_pct}%)
                    </span>
                  )}
                </div>
              </div>
            </div>

            {lastBenchmarkResult.message && (
              <p className="text-xs text-[#737373] leading-relaxed">
                {lastBenchmarkResult.message}
              </p>
            )}
          </div>
        ) : null}
      </div>
    </div>
  );
};
