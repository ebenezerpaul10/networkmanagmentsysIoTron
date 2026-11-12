export interface LaneInfo {
  channel: number;
  count: number;
  status: string;
  desc: string;
}

export interface HighwayData {
  lane1: LaneInfo;
  lane6: LaneInfo;
  lane11: LaneInfo;
  best_lane: number;
}

export interface MetricsSnapshot {
  bssid: string;
  channel: number;
  signal: number;
  latency_ms: number;
  download_speed: string;
  hardware: string;
  status: string;
  timestamp: string;
}

export interface Improvements {
  speed_boost_pct: number;
  latency_drop_pct: number;
  signal_gain_pct: number;
  channel_cleared: boolean;
  mode: string;
}

export interface SpectrumPoint {
  ch1: number;
  ch6: number;
  ch11: number;
}

export interface AssistantEvent {
  id: number;
  time: string;
  category: "RADAR" | "ROAMER" | "SHIELD" | "COPILOT" | string;
  title: string;
  message: string;
  impact: string;
}

export interface NetShieldStats {
  esp_connected: boolean;
  esp_port: string;
  radar_source: string;
  auto_roam_enabled: boolean;
  health_score: number;
  score_status: string;
  simple_summary: string;
  robo_speech: string;
  robo_mood: string;
  current_ssid: string;
  current_bssid: string;
  current_channel: number;
  current_signal: number;
  signal_bars: number;
  current_band?: string;
  current_radio?: string;
  current_rx_rate?: number;
  current_tx_rate?: number;
  current_rssi?: number;
  download_speed_mbps: number;
  download_speed_str: string;
  speed_verdict: string;
  best_ssid: string;
  best_bssid: string;
  best_rssi: number;
  recommended_channel: number;
  congestion_score: number;
  total_aps: number;
  ch1: number;
  ch6: number;
  ch11: number;
  spectrum_history: SpectrumPoint[];
  traffic_wave: number[];
  traffic_zone: string;
  highway: HighwayData;
  latency_ms: number;
  network_health: string;
  total_queries: number;
  blocked_queries: number;
  bandwidth_saved_kb: number;
  before_metrics: MetricsSnapshot;
  after_metrics: MetricsSnapshot;
  improvements: Improvements;
  wlan0_speed_mbps: number;
  wlan1_speed_mbps: number;
  dual_combined_mbps: number;
  wlan1_detected: boolean;
  assistant_events: AssistantEvent[];
}

export interface BenchmarkResult {
  success: boolean;
  wlan1_connected: boolean;
  solo_speed_mbps: number;
  wlan1_speed_mbps?: number;
  dual_speed_mbps: number;
  boost_pct: number;
  message?: string;
}

export interface ToastNotification {
  id: string;
  title: string;
  message: string;
  type: "success" | "info" | "warning" | "error";
  timestamp: string;
}

export type ViewTab =
  | "overview"
  | "wifi"
  | "spectrum"
  | "duallink"
  | "dns"
  | "diagnostics"
  | "settings";

