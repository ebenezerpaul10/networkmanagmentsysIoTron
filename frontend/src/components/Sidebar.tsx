import React from "react";
import {
  LayoutDashboard,
  Wifi,
  Activity,
  Layers,
  ShieldCheck,
  FileText,
  Settings,
  SlidersHorizontal,
} from "lucide-react";
import type { ViewTab } from "../types";

interface SidebarProps {
  activeTab: ViewTab;
  onSelectTab: (tab: ViewTab) => void;
  advancedMode: boolean;
  onToggleAdvancedMode: () => void;
  espConnected: boolean;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  onSelectTab,
  advancedMode,
  onToggleAdvancedMode,
}) => {
  const navItems = [
    { id: "overview" as ViewTab, label: "Overview", icon: LayoutDashboard },
    { id: "wifi" as ViewTab, label: "Wi-Fi Manager", icon: Wifi },
    { id: "spectrum" as ViewTab, label: "Spectrum Analyzer", icon: Activity },
    { id: "duallink" as ViewTab, label: "Dual-Link Controller", icon: Layers },
    { id: "dns" as ViewTab, label: "DNS Shield", icon: ShieldCheck },
    { id: "diagnostics" as ViewTab, label: "Diagnostics & Logs", icon: FileText },
    { id: "settings" as ViewTab, label: "Settings", icon: Settings },
  ];

  return (
    <aside className="w-64 shrink-0 bg-[#FFFFFF] border-r border-[#E5E5E5] flex flex-col justify-between h-screen sticky top-0 select-none z-20">
      <div>
        {/* Brand / Logo Header */}
        <div className="h-16 px-5 border-b border-[#E5E5E5] flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 bg-[#111111] rounded flex items-center justify-center text-white font-bold text-xs tracking-tight">
              NS
            </div>
            <div>
              <div className="text-sm font-semibold text-[#111111] leading-none tracking-tight">
                NetShield
              </div>
              <div className="text-[10px] text-[#737373] mt-0.5 font-medium">
                Enterprise NOC
              </div>
            </div>
          </div>
          <span className="text-[10px] uppercase font-mono px-2 py-0.5 bg-[#F5F5F5] text-[#111111] border border-[#E5E5E5] rounded font-semibold tracking-wider">
            v5.0 Enterprise
          </span>
        </div>

        {/* Navigation List */}
        <nav className="p-3 space-y-1">
          <div className="px-3 py-1.5 text-[11px] font-semibold tracking-wider text-[#A3A3A3] uppercase">
            Navigation
          </div>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onSelectTab(item.id)}
                className={`w-full flex items-center gap-3 px-3 py-2 text-xs font-medium rounded-lg transition-colors text-left ${
                  isActive
                    ? "bg-[#111111] text-[#FFFFFF]"
                    : "text-[#737373] hover:text-[#111111] hover:bg-[#F0F0F0]"
                }`}
              >
                <Icon
                  size={16}
                  strokeWidth={1.75}
                  className={isActive ? "text-[#FFFFFF]" : "text-[#737373]"}
                />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Bottom Mode Switcher */}
      <div className="p-3 border-t border-[#E5E5E5] bg-[#FFFFFF]">
        <div className="p-2.5 rounded-lg border border-[#E5E5E5] bg-[#F5F5F5] flex items-center justify-between">
          <div className="flex items-center gap-2">
            <SlidersHorizontal size={14} strokeWidth={1.75} className="text-[#737373]" />
            <div>
              <div className="text-xs font-medium text-[#111111]">
                {advancedMode ? "Advanced Mode" : "Standard Mode"}
              </div>
              <div className="text-[10px] text-[#737373]">
                {advancedMode ? "Full technical telemetry" : "Essential indicators"}
              </div>
            </div>
          </div>
          <button
            onClick={onToggleAdvancedMode}
            type="button"
            role="switch"
            aria-checked={advancedMode}
            className={`relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
              advancedMode ? "bg-[#111111]" : "bg-[#D4D4D4]"
            }`}
          >
            <span
              className={`pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                advancedMode ? "translate-x-4" : "translate-x-0"
              }`}
            />
          </button>
        </div>
      </div>
    </aside>
  );
};
