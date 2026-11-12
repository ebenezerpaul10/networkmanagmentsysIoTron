import type { BenchmarkResult, NetShieldStats } from "./types";

export let API_BASE_URL = "";

export function setApiBaseUrl(url: string) {
  API_BASE_URL = url.trim().replace(/\/+$/, "");
}

function getUrl(path: string): string {
  if (!API_BASE_URL) return path;
  return `${API_BASE_URL}${path}`;
}

export async function fetchStats(): Promise<NetShieldStats> {
  const res = await fetch(getUrl("/api/stats"), {
    headers: { Accept: "application/json" },
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}: Failed to fetch stats`);
  }
  return res.json();
}

export async function switchAp(): Promise<{ success: boolean; message: string }> {
  const res = await fetch(getUrl("/api/switch_ap"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}: Failed to switch AP`);
  }
  return res.json();
}

export async function toggleAutoRoam(): Promise<{ auto_roam_enabled: boolean }> {
  const res = await fetch(getUrl("/api/toggle_auto_roam"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}: Failed to toggle auto roam`);
  }
  return res.json();
}

export async function captureBaseline(): Promise<{ success: boolean; baseline: any }> {
  const res = await fetch(getUrl("/api/capture_baseline"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}: Failed to capture baseline`);
  }
  return res.json();
}

export async function runBenchmark(): Promise<BenchmarkResult> {
  const res = await fetch(getUrl("/api/run_benchmark"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}: Failed to execute speed benchmark`);
  }
  return res.json();
}
