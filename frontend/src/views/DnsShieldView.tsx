import React, { useState } from "react";
import {
  ShieldCheck,
  ShieldAlert,
  Server,
  Zap,
  CheckCircle2,
  Search,
  Filter,
} from "lucide-react";
import type { NetShieldStats } from "../types";

interface DnsShieldViewProps {
  stats: NetShieldStats | null;
  advancedMode: boolean;
}

export const DnsShieldView: React.FC<DnsShieldViewProps> = ({ stats, advancedMode }) => {
  const [searchFilter, setSearchFilter] = useState("");

  const blockedList = [
    { domain: "doubleclick.net", category: "Advertising / Behavioral Tracking", status: "Active Sinkhole", hitRate: "High" },
    { domain: "googleadservices.com", category: "Ad Network Conversion", status: "Active Sinkhole", hitRate: "High" },
    { domain: "adservice.google.com", category: "Ad Delivery Gateway", status: "Active Sinkhole", hitRate: "Medium" },
    { domain: "telemetry.microsoft.com", category: "OS Background Diagnostics", status: "Active Sinkhole", hitRate: "Medium" },
    { domain: "analytics.google.com", category: "Web Analytics / Tracking", status: "Active Sinkhole", hitRate: "Medium" },
    { domain: "facebook.com/tr", category: "Social Graph Pixel Tracking", status: "Active Sinkhole", hitRate: "High" },
    { domain: "scorecardresearch.com", category: "Audience Fingerprinting", status: "Active Sinkhole", hitRate: "Low" },
    { domain: "adnxs.com", category: "AppNexus Real-Time Ad Exchange", status: "Active Sinkhole", hitRate: "Medium" },
    { domain: "taboola.com", category: "Sponsored Content Injection", status: "Active Sinkhole", hitRate: "Medium" },
    { domain: "outbrain.com", category: "Sponsored Content Injection", status: "Active Sinkhole", hitRate: "Medium" },
    { domain: "adroll.com", category: "Retargeting Tracker", status: "Active Sinkhole", hitRate: "Low" },
    { domain: "criteo.com", category: "Commercial Retargeting", status: "Active Sinkhole", hitRate: "Low" },
    { domain: "popads.net", category: "Popunder / Invasive Network", status: "Active Sinkhole", hitRate: "Low" },
  ];

  if (!stats) {
    return (
      <div className="flex items-center justify-center h-64 text-sm text-[#737373]">
        Awaiting DNS Shield telemetry...
      </div>
    );
  }

  const { total_queries, blocked_queries, bandwidth_saved_kb } = stats;
  const blockRatio =
    total_queries > 0 ? ((blocked_queries / total_queries) * 100).toFixed(1) : "0.0";

  const filteredDomains = blockedList.filter((item) =>
    item.domain.toLowerCase().includes(searchFilter.toLowerCase()) ||
    item.category.toLowerCase().includes(searchFilter.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Sinkhole Architecture Status Header */}
      <div className="p-5 rounded-xl border border-[#E5E5E5] bg-[#FFFFFF] shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-start gap-3.5">
          <div className="p-2 rounded-lg bg-[#F5F5F5] border border-[#E5E5E5] text-[#111111]">
            <Server size={18} strokeWidth={1.75} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-base font-semibold text-[#111111]">
                Local DNS Sinkhole & Privacy Firewall
              </h2>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#F5F5F5] border border-[#E5E5E5] text-[#111111]">
                Port 5353
              </span>
            </div>
            <p className="text-xs text-[#737373] mt-1 max-w-2xl leading-relaxed">
              Daemon intercepts UDP requests on <span className="font-mono text-[#111111]">127.0.0.1:5353</span>. Malicious and telemetry domains are poisoned with an immediate <span className="font-mono text-[#111111]">0.0.0.0</span> reply. Clean queries are securely forwarded upstream to Cloudflare DNS (<span className="font-mono text-[#111111]">1.1.1.1:53</span>).
            </p>
          </div>
        </div>

        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg border border-[#E5E5E5] bg-[#F5F5F5] shrink-0">
          <span className="w-2 h-2 rounded-full bg-[#10B981]" />
          <span className="text-xs font-mono font-medium text-[#111111]">UPSTREAM: 1.1.1.1:53</span>
        </div>
      </div>

      {/* 3 DNS Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <div className="p-5 rounded-xl border border-[#E5E5E5] bg-[#FFFFFF] shadow-xs space-y-2">
          <span className="text-xs font-medium text-[#737373]">Total Inspected Queries</span>
          <div className="text-2xl font-bold font-mono text-[#111111]">
            {total_queries.toLocaleString()}
          </div>
          <div className="text-xs text-[#737373]">
            Processed DNS resolver requests
          </div>
        </div>

        <div className="p-5 rounded-xl border border-[#E5E5E5] bg-[#FFFFFF] shadow-xs space-y-2">
          <span className="text-xs font-medium text-[#737373]">Blocked Tracker Queries</span>
          <div className="text-2xl font-bold font-mono text-[#111111] flex items-baseline gap-2">
            <span>{blocked_queries.toLocaleString()}</span>
            <span className="text-xs font-mono text-[#737373] font-normal">
              ({blockRatio}% sinkholed)
            </span>
          </div>
          <div className="text-xs text-[#737373]">
            Zero-delay local sinkhole intercepts
          </div>
        </div>

        <div className="p-5 rounded-xl border border-[#E5E5E5] bg-[#FFFFFF] shadow-xs space-y-2">
          <span className="text-xs font-medium text-[#737373]">Bandwidth Saved</span>
          <div className="text-2xl font-bold font-mono text-[#111111]">
            {bandwidth_saved_kb >= 1024
              ? `${(bandwidth_saved_kb / 1024).toFixed(2)} MB`
              : `${bandwidth_saved_kb.toFixed(1)} KB`}
          </div>
          <div className="text-xs text-[#737373]">
            Eliminated unrendered tracking payload traffic
          </div>
        </div>
      </div>

      {/* Blocked Domains Directory Table */}
      <div className="p-5 rounded-xl border border-[#E5E5E5] bg-[#FFFFFF] shadow-xs space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h3 className="text-sm font-semibold text-[#111111]">
              Active Sinkhole Filter Policy ({filteredDomains.length} rules)
            </h3>
            <p className="text-xs text-[#737373] mt-0.5">
              Strict rule matching against known advertising networks, surveillance beacons, and vendor telemetry.
            </p>
          </div>

          {/* Search Box */}
          <div className="relative w-full sm:w-64">
            <Search
              size={13}
              strokeWidth={1.75}
              className="absolute left-3 top-1/2 -translate-y-1/2 text-[#737373]"
            />
            <input
              type="text"
              placeholder="Filter domain or category..."
              value={searchFilter}
              onChange={(e) => setSearchFilter(e.target.value)}
              className="w-full pl-8 pr-3 py-1.5 text-xs rounded-lg border border-[#E5E5E5] bg-[#F5F5F5] focus:bg-[#FFFFFF] focus:outline-none focus:border-[#111111] transition-colors"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-[#E5E5E5] text-[#737373] uppercase tracking-wider text-[10px]">
                <th className="py-2.5 px-3 font-semibold">Blocked Domain / Substring</th>
                <th className="py-2.5 px-3 font-semibold">Category Classification</th>
                <th className="py-2.5 px-3 font-semibold">Sinkhole Response</th>
                <th className="py-2.5 px-3 font-semibold text-right">Policy Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#E5E5E5]">
              {filteredDomains.map((rule, idx) => (
                <tr key={idx} className="hover:bg-[#F5F5F5]/50">
                  <td className="py-3 px-3 font-mono text-[#111111] font-medium">
                    {rule.domain}
                  </td>
                  <td className="py-3 px-3 text-[#737373]">{rule.category}</td>
                  <td className="py-3 px-3 font-mono text-[11px] text-[#737373]">
                    A 0.0.0.0 (TTL 60)
                  </td>
                  <td className="py-3 px-3 text-right">
                    <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-[#F5F5F5] border border-[#E5E5E5] text-[10px] font-mono text-[#111111] font-medium">
                      <span className="w-1.5 h-1.5 rounded-full bg-[#10B981]" />
                      DROP / SINKHOLE
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
