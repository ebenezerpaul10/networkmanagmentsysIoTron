import React, { useState, useEffect, useCallback, useRef } from "react";
import { Sidebar } from "./components/Sidebar";
import { TopHeader } from "./components/TopHeader";
import { ConfirmationModal } from "./components/ConfirmationModal";
import { ToastContainer } from "./components/ToastContainer";
import { OverviewView } from "./views/OverviewView";
import { WifiManagerView } from "./views/WifiManagerView";
import { SpectrumAnalyzerView } from "./views/SpectrumAnalyzerView";
import { DualLinkView } from "./views/DualLinkView";
import { DnsShieldView } from "./views/DnsShieldView";
import { DiagnosticsLogsView } from "./views/DiagnosticsLogsView";
import { SettingsView } from "./views/SettingsView";
import type {
  BenchmarkResult,
  NetShieldStats,
  ToastNotification,
  ViewTab,
} from "./types";
import {
  fetchStats,
  switchAp,
  toggleAutoRoam,
  captureBaseline,
  runBenchmark,
} from "./api";

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<ViewTab>("overview");
  const [advancedMode, setAdvancedMode] = useState<boolean>(false);
  const [stats, setStats] = useState<NetShieldStats | null>(null);
  const [pollIntervalMs, setPollIntervalMs] = useState<number>(2000);
  const [toasts, setToasts] = useState<ToastNotification[]>([]);

  // Action loading states
  const [isBenchmarking, setIsBenchmarking] = useState<boolean>(false);
  const [isCapturingBaseline, setIsCapturingBaseline] = useState<boolean>(false);
  const [isTogglingRoam, setIsTogglingRoam] = useState<boolean>(false);
  const [isSwitchingAp, setIsSwitchingAp] = useState<boolean>(false);
  const [isSwitchModalOpen, setIsSwitchModalOpen] = useState<boolean>(false);
  const [lastBenchmarkResult, setLastBenchmarkResult] = useState<BenchmarkResult | null>(null);

  const isPollingRef = useRef<boolean>(false);

  const addToast = useCallback(
    (title: string, message: string, type: ToastNotification["type"] = "info") => {
      const id = `${Date.now()}-${Math.random().toString(36).substring(2, 7)}`;
      const newToast: ToastNotification = {
        id,
        title,
        message,
        type,
        timestamp: new Date().toLocaleTimeString(),
      };
      setToasts((prev) => [newToast, ...prev].slice(0, 5));

      setTimeout(() => {
        setToasts((prev) => prev.filter((t) => t.id !== id));
      }, 5000);
    },
    []
  );

  const dismissToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  // Polling loop
  const loadStats = useCallback(async () => {
    if (isPollingRef.current) return;
    isPollingRef.current = true;
    try {
      const data = await fetchStats();
      setStats(data);
    } catch (err: any) {
      // Backend may be restarting or starting up
      console.warn("NetShield poller:", err?.message || err);
    } finally {
      isPollingRef.current = false;
    }
  }, []);

  useEffect(() => {
    loadStats();
    const timer = setInterval(loadStats, pollIntervalMs);
    return () => clearInterval(timer);
  }, [loadStats, pollIntervalMs]);

  // Handlers for Quick Action Buttons
  const handleToggleAutoRoam = async () => {
    setIsTogglingRoam(true);
    try {
      const res = await toggleAutoRoam();
      addToast(
        res.auto_roam_enabled ? "Auto-Pilot Armed" : "Auto-Pilot Standby",
        res.auto_roam_enabled
          ? "Autonomous continuous BSSID optimization is now active."
          : "Switched to manual connection roaming mode.",
        res.auto_roam_enabled ? "success" : "info"
      );
      loadStats();
    } catch (err: any) {
      addToast("Auto-Roam Error", err.message || "Failed to toggle Auto-Pilot", "error");
    } finally {
      setIsTogglingRoam(false);
    }
  };

  const handleCaptureBaseline = async () => {
    setIsCapturingBaseline(true);
    try {
      await captureBaseline();
      addToast(
        "Baseline Captured",
        `Recorded baseline snapshot at ping ${stats?.latency_ms ?? 0} ms, channel ${stats?.current_channel ?? 6}.`,
        "success"
      );
      loadStats();
    } catch (err: any) {
      addToast("Baseline Error", err.message || "Failed to capture baseline", "error");
    } finally {
      setIsCapturingBaseline(false);
    }
  };

  const handleRunBenchmark = async () => {
    setIsBenchmarking(true);
    addToast(
      "Benchmarking Interfaces",
      "Streaming multi-megabyte throughput payloads against Cloudflare CDN...",
      "info"
    );
    try {
      const result = await runBenchmark();
      setLastBenchmarkResult(result);
      if (result.wlan1_connected) {
        addToast(
          "Dual Turbo Benchmark",
          `Solo Link: ${result.solo_speed_mbps} Mbps | Aggregated Multi-Link: ${result.dual_speed_mbps} Mbps (+${result.boost_pct}% boost)`,
          "success"
        );
      } else {
        addToast(
          "Solo Benchmark Complete",
          `Solo Laptop Speed: ${result.solo_speed_mbps} Mbps. Connect secondary USB Wi-Fi dongle for dual speed aggregation.`,
          "info"
        );
      }
      loadStats();
    } catch (err: any) {
      addToast("Benchmark Failed", err.message || "Error running speed benchmark", "error");
    } finally {
      setIsBenchmarking(false);
    }
  };

  const handleConfirmSwitchAp = async () => {
    setIsSwitchingAp(true);
    try {
      const res = await switchAp();
      if (res.success) {
        addToast("BSSID Steered", res.message || "Successfully steered to cleanest access point.", "success");
      } else {
        addToast("Safety Guard Intervened", res.message || "Could not switch AP safely.", "warning");
      }
      setIsSwitchModalOpen(false);
      loadStats();
    } catch (err: any) {
      addToast("Steering Error", err.message || "Handover failed", "error");
    } finally {
      setIsSwitchingAp(false);
    }
  };

  const tabTitles: Record<ViewTab, string> = {
    overview: "Overview & Master Health",
    wifi: "Wi-Fi Manager & Access Points",
    spectrum: "Hardware RF Spectrum Analyzer (2.4 GHz)",
    duallink: "Dual-Link Controller & Speed Aggregation",
    dns: "DNS Shield & Ad Tracker Sinkhole",
    diagnostics: "Diagnostics & System Telemetry Logs",
    settings: "Controller Settings",
  };

  return (
    <div className="min-h-screen bg-[#F5F5F5] flex">
      {/* Sidebar */}
      <Sidebar
        activeTab={activeTab}
        onSelectTab={setActiveTab}
        advancedMode={advancedMode}
        onToggleAdvancedMode={() => setAdvancedMode((prev) => !prev)}
        espConnected={Boolean(stats?.esp_connected)}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <TopHeader
          stats={stats}
          activeTabTitle={tabTitles[activeTab]}
          onToggleAutoRoam={handleToggleAutoRoam}
          onCaptureBaseline={handleCaptureBaseline}
          onRunBenchmark={handleRunBenchmark}
          isBenchmarking={isBenchmarking}
          isCapturingBaseline={isCapturingBaseline}
          isTogglingRoam={isTogglingRoam}
        />

        <main className="flex-1 p-6 md:p-8 max-w-7xl w-full mx-auto">
          {activeTab === "overview" && (
            <OverviewView
              stats={stats}
              advancedMode={advancedMode}
              onNavigateTab={setActiveTab}
              onRunBenchmark={handleRunBenchmark}
              onTriggerSwitch={() => setIsSwitchModalOpen(true)}
            />
          )}

          {activeTab === "wifi" && (
            <WifiManagerView
              stats={stats}
              advancedMode={advancedMode}
              onRequestSwitch={() => setIsSwitchModalOpen(true)}
              isSwitching={isSwitchingAp}
            />
          )}

          {activeTab === "spectrum" && (
            <SpectrumAnalyzerView
              stats={stats}
              advancedMode={advancedMode}
            />
          )}

          {activeTab === "duallink" && (
            <DualLinkView
              stats={stats}
              advancedMode={advancedMode}
              onRunBenchmark={handleRunBenchmark}
              isBenchmarking={isBenchmarking}
              lastBenchmarkResult={lastBenchmarkResult}
            />
          )}

          {activeTab === "dns" && (
            <DnsShieldView
              stats={stats}
              advancedMode={advancedMode}
            />
          )}

          {activeTab === "diagnostics" && (
            <DiagnosticsLogsView
              stats={stats}
              advancedMode={advancedMode}
            />
          )}

          {activeTab === "settings" && (
            <SettingsView
              stats={stats}
              advancedMode={advancedMode}
              onToggleAdvancedMode={() => setAdvancedMode((prev) => !prev)}
              pollIntervalMs={pollIntervalMs}
              onChangePollInterval={setPollIntervalMs}
              onRefreshNow={loadStats}
            />
          )}
        </main>
      </div>

      {/* Confirmation Modal */}
      <ConfirmationModal
        isOpen={isSwitchModalOpen}
        onClose={() => setIsSwitchModalOpen(false)}
        onConfirm={handleConfirmSwitchAp}
        title="Steer Connection to Recommended AP"
        description="Trigger seamless BSSID handover to candidate radio channel."
        currentSsid={stats?.current_ssid || ""}
        currentBssid={stats?.current_bssid || ""}
        targetSsid={stats?.best_ssid || stats?.current_ssid || ""}
        targetBssid={stats?.best_bssid || ""}
        targetChannel={stats?.recommended_channel || 1}
        isLoading={isSwitchingAp}
      />

      {/* Floating Notifications */}
      <ToastContainer toasts={toasts} onDismiss={dismissToast} />
    </div>
  );
};

export default App;
