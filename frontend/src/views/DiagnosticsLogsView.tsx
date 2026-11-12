import React, { useState } from "react";
import {
  Activity,
  FileText,
  Filter,
  CheckCircle2,
  AlertCircle,
  Radio,
  Shield,
  Compass,
  Download,
} from "lucide-react";
import type { AssistantEvent, NetShieldStats } from "../types";

interface DiagnosticsLogsViewProps {
  stats: NetShieldStats | null;
  advancedMode: boolean;
}

export const DiagnosticsLogsView: React.FC<DiagnosticsLogsViewProps> = ({
  stats,
  advancedMode,
}) => {
  const [categoryFilter, setCategoryFilter] = useState<string>("ALL");

  if (!stats) {
    return (
      <div className="flex items-center justify-center h-64 text-sm text-[#737373]">
        Awaiting Diagnostics & Event logs...
      </div>
    );
  }

  const { latency_ms, network_health, assistant_events } = stats;

  const filteredEvents = (assistant_events || []).filter((item: AssistantEvent) => {
    if (categoryFilter === "ALL") return true;
    if (categoryFilter === "ROAM") return item.category === "ROAMER";
    if (categoryFilter === "SHIELD") return item.category === "SHIELD";
    if (categoryFilter === "RADAR") return item.category === "RADAR" || item.category === "COPILOT";
    return true;
  });

  const exportLogsAsJson = () => {
    const dataStr =
      "data:text/json;charset=utf-8," +
      encodeURIComponent(JSON.stringify(assistant_events, null, 2));
    const downloadAnchor = document.createElement("a");
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `netshield_audit_logs_${Date.now()}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  return (
    <div className="space-y-6">
      {/* Diagnostics Health Status Bar */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <div className="p-5 rounded-xl border border-[#E5E5E5] bg-[#FFFFFF] shadow-xs space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-[#737373]">Cloud Probe Ping Latency</span>
            <Activity size={15} strokeWidth={1.75} className="text-[#737373]" />
          </div>
          <div className="text-2xl font-bold font-mono text-[#111111]">
            {latency_ms >= 0 ? `${latency_ms.toFixed(1)} ms` : "Timeout"}
          </div>
          <div className="text-xs text-[#737373]">
            Probing <span className="font-mono text-[#111111]">https://www.google.com/generate_204</span>
          </div>
        </div>

        <div className="p-5 rounded-xl border border-[#E5E5E5] bg-[#FFFFFF] shadow-xs space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-[#737373]">Packet Health & Jitter</span>
            <CheckCircle2 size={15} strokeWidth={1.75} className="text-[#737373]" />
          </div>
          <div className="text-2xl font-bold font-mono text-[#111111]">
            {latency_ms >= 0 ? "0.0% Loss" : "Packet Loss"}
          </div>
          <div className="text-xs text-[#737373]">
            State: <span className="font-medium text-[#111111]">{network_health}</span>
          </div>
        </div>

        <div className="p-5 rounded-xl border border-[#E5E5E5] bg-[#FFFFFF] shadow-xs space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-[#737373]">Audit Events Logged</span>
            <FileText size={15} strokeWidth={1.75} className="text-[#737373]" />
          </div>
          <div className="text-2xl font-bold font-mono text-[#111111]">
            {(assistant_events || []).length}
          </div>
          <div className="text-xs text-[#737373]">
            In-memory circular telemetry buffer
          </div>
        </div>
      </div>

      {/* Event Audit Log Table */}
      <div className="p-5 rounded-xl border border-[#E5E5E5] bg-[#FFFFFF] shadow-xs space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h3 className="text-sm font-semibold text-[#111111]">
              Event Audit Log & System Telemetry Trail
            </h3>
            <p className="text-xs text-[#737373] mt-0.5">
              Structured events emitted by ESP32 RF Sniffer, Roaming Director, and DNS Shield.
            </p>
          </div>

          <div className="flex items-center gap-2">
            {/* Filter Buttons */}
            <div className="inline-flex rounded-lg border border-[#E5E5E5] bg-[#F5F5F5] p-0.5">
              {[
                { id: "ALL", label: "All" },
                { id: "ROAM", label: "Roam Events" },
                { id: "SHIELD", label: "Shield" },
                { id: "RADAR", label: "Radar Alerts" },
              ].map((btn) => (
                <button
                  key={btn.id}
                  onClick={() => setCategoryFilter(btn.id)}
                  className={`px-3 py-1 text-xs font-medium rounded-md transition-colors ${
                    categoryFilter === btn.id
                      ? "bg-[#FFFFFF] text-[#111111] shadow-xs"
                      : "text-[#737373] hover:text-[#111111]"
                  }`}
                >
                  {btn.label}
                </button>
              ))}
            </div>

            {/* Export JSON Button */}
            <button
              onClick={exportLogsAsJson}
              className="p-1.5 rounded-lg border border-[#E5E5E5] bg-[#FFFFFF] hover:bg-[#F0F0F0] text-[#737373] hover:text-[#111111] transition-colors"
              title="Export Audit Trail as JSON"
            >
              <Download size={14} strokeWidth={1.75} />
            </button>
          </div>
        </div>

        {/* Audit Log Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-[#E5E5E5] text-[#737373] uppercase tracking-wider text-[10px]">
                <th className="py-2.5 px-3 font-semibold w-20">Time</th>
                <th className="py-2.5 px-3 font-semibold w-28">Category</th>
                <th className="py-2.5 px-3 font-semibold">Event Title & Summary</th>
                <th className="py-2.5 px-3 font-semibold text-right w-28">Impact Tag</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#E5E5E5]">
              {filteredEvents.length === 0 ? (
                <tr>
                  <td colSpan={4} className="py-8 text-center text-[#737373] text-xs">
                    No events match the selected category filter.
                  </td>
                </tr>
              ) : (
                filteredEvents.map((evt) => {
                  let badge = "text-[#111111] bg-[#F5F5F5]";
                  let icon = <Activity size={12} strokeWidth={1.75} />;

                  if (evt.category === "RADAR") {
                    badge = "text-[#111111] bg-[#F5F5F5]";
                    icon = <Radio size={12} strokeWidth={1.75} />;
                  } else if (evt.category === "ROAMER") {
                    badge = "text-[#111111] bg-[#F5F5F5]";
                    icon = <Compass size={12} strokeWidth={1.75} />;
                  } else if (evt.category === "SHIELD") {
                    badge = "text-[#111111] bg-[#F5F5F5]";
                    icon = <Shield size={12} strokeWidth={1.75} />;
                  }

                  return (
                    <tr key={evt.id} className="hover:bg-[#F5F5F5]/50">
                      <td className="py-3 px-3 font-mono text-[#737373] text-[11px]">
                        {evt.time}
                      </td>
                      <td className="py-3 px-3">
                        <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded border border-[#E5E5E5] bg-[#F5F5F5] text-[10px] font-mono font-medium text-[#111111]">
                          {icon}
                          {evt.category}
                        </span>
                      </td>
                      <td className="py-3 px-3">
                        <div className="font-semibold text-[#111111]">{evt.title}</div>
                        <div className="text-xs text-[#737373] mt-0.5 leading-snug">
                          {evt.message}
                        </div>
                      </td>
                      <td className="py-3 px-3 text-right">
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded border border-[#E5E5E5] bg-[#FFFFFF] text-[#111111]">
                          {evt.impact || "Info"}
                        </span>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
