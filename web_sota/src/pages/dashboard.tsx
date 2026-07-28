import { Activity, Layers, Music, PlayCircle } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";

const BACKEND_URL = "http://127.0.0.1:10877";

interface HealthData {
  status: string;
  version: string;
  tool_count?: number;
  server?: string;
  uptime_seconds?: number;
}

async function checkBackendHealth(): Promise<{
  ok: boolean;
  data?: HealthData;
  error?: string;
}> {
  try {
    const r = await fetch(`${BACKEND_URL}/api/health`, {
      signal: AbortSignal.timeout(5000),
    });
    if (!r.ok) return { ok: false, error: `HTTP ${r.status}` };
    const data: HealthData = await r.json();
    return { ok: true, data };
  } catch (e) {
    return {
      ok: false,
      error: e instanceof Error ? e.message : "Network error",
    };
  }
}

export function Dashboard() {
  const [backendOk, setBackendOk] = useState<boolean | null>(null);
  const [healthData, setHealthData] = useState<HealthData | null>(null);
  const [restarting, setRestarting] = useState(false);

  const refresh = useCallback(async () => {
    const h = await checkBackendHealth();
    setBackendOk(h.ok);
    if (h.data) setHealthData(h.data);
  }, []);

  // Exponential backoff retry: 1s, 2s, 4s, 8s, 16s then steady 30s
  useEffect(() => {
    let cancelled = false;
    let delay = 1000;
    const poll = async () => {
      if (cancelled) return;
      await refresh();
      if (!cancelled) {
        if (backendOk === false) {
          delay = Math.min(delay * 2, 30000);
        } else {
          delay = 30000;
        }
        setTimeout(poll, delay);
      }
    };
    poll();
    return () => {
      cancelled = true;
    };
  }, [refresh, backendOk]);

  // Listen for Tauri backend-status event
  useEffect(() => {
    let unlisten: (() => void) | undefined;
    (async () => {
      try {
        const { listen } = await import("@tauri-apps/api/event");
        unlisten = await listen<string>("backend-status", (event) => {
          if (event.payload === "ready") refresh();
          else if (
            typeof event.payload === "string" &&
            event.payload.startsWith("error:")
          )
            setBackendOk(false);
        });
      } catch {
        // Not in Tauri — HTTP polling handles it
      }
    })();
    return () => {
      if (unlisten) unlisten();
    };
  }, [refresh]);

  const restartBackend = useCallback(async () => {
    setRestarting(true);
    try {
      const { invoke } = await import("@tauri-apps/api/core");
      await invoke("start_backend");
    } catch {
      setRestarting(false);
    }
  }, []);

  return (
    <div data-testid="dashboard" className="space-y-10 pb-10 relative isolate">
      {/* Background Aesthetics */}
      <div className="absolute inset-0 -z-10 pointer-events-none overflow-hidden">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-blue-500/10 blur-[120px] rounded-full" />
        <div className="absolute bottom-[10%] right-[-5%] w-[30%] h-[30%] bg-indigo-500/10 blur-[100px] rounded-full" />
      </div>

      {/* Backend Status Bar */}
      <div className="flex items-center gap-3 px-4 py-2 rounded-lg bg-slate-900/60 border border-slate-800 text-sm">
        <div
          data-testid="backend-dot"
          className={`w-2.5 h-2.5 rounded-full ${backendOk === null ? "bg-gray-500" : backendOk ? "bg-green-500" : "bg-red-500"} animate-pulse`}
        />
        <span className="text-slate-300">
          {backendOk === null
            ? "Connecting to backend..."
            : backendOk
              ? `Connected — ${healthData?.server || ""} v${healthData?.version || "?"}${healthData?.tool_count ? ` (${healthData.tool_count} tools)` : ""}`
              : "Backend offline"}
        </span>
        {backendOk === false && (
          <button
            onClick={restartBackend}
            disabled={restarting}
            className="ml-auto text-xs px-3 py-1 rounded bg-blue-600 hover:bg-blue-500 text-white disabled:opacity-50"
          >
            {restarting ? "Restarting..." : "Restart Backend"}
          </button>
        )}
      </div>

      {/* Hero Section */}
      <section className="relative overflow-hidden rounded-3xl bg-slate-900/40 border border-slate-800 shadow-2xl backdrop-blur-md">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-600/20 via-transparent to-indigo-600/20" />
        <div className="relative px-8 py-12 md:px-12 md:py-20 max-w-3xl">
          <div className="inline-flex items-center gap-2 rounded-full bg-blue-500/10 px-3 py-1 text-xs font-bold text-blue-400 border border-blue-500/20 mb-6">
            <Activity className="h-3 w-3" />
            V2 BETA
          </div>
          <h1 className="text-4xl md:text-6xl font-black tracking-tight text-white mb-6">
            VirtualDJ{" "}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-400">
              Orchestrator
            </span>
          </h1>
          <p className="text-lg text-slate-400 mb-8 leading-relaxed max-w-2xl">
            Precision automation engine for VirtualDJ performance. Real-time
            deck control, automated library management, and deep stems
            integration via FastMCP bridge.
          </p>

          <div className="flex flex-wrap gap-4">
            <Link
              to="/tools"
              className="flex items-center gap-2 rounded-full bg-blue-600 hover:bg-blue-500 px-6 py-3 font-bold text-white transition-all transform hover:scale-105 no-underline shadow-lg shadow-blue-500/20"
            >
              <PlayCircle className="h-5 w-5" />
              Launch Controls
            </Link>
            <Link
              to="/help"
              className="flex items-center gap-2 rounded-full bg-slate-800 hover:bg-slate-700 px-6 py-3 font-bold text-slate-100 transition-all no-underline"
            >
              View Documentation
            </Link>
          </div>
        </div>
      </section>

      {/* KPI Stats Grid */}
      <div className="grid gap-6 md:grid-cols-3">
        <div
          data-testid="kpi-decks"
          className="rounded-2xl border border-slate-800 bg-slate-900/50 p-6 backdrop-blur-sm"
        >
          <Music className="h-10 w-10 text-blue-400 mb-4" />
          <h3 className="text-xl font-bold text-slate-100">Decks</h3>
          <p className="text-slate-400">4 channels</p>
        </div>
        <div
          data-testid="kpi-tools"
          className="rounded-2xl border border-slate-800 bg-slate-900/50 p-6 backdrop-blur-sm"
        >
          <Layers className="h-10 w-10 text-indigo-400 mb-4" />
          <h3 className="text-xl font-bold text-slate-100">Tools</h3>
          <p className="text-slate-400">
            {healthData?.tool_count ?? "13"} portmanteau tools
          </p>
        </div>
        <div
          data-testid="kpi-server"
          className="rounded-2xl border border-slate-800 bg-slate-900/50 p-6 backdrop-blur-sm"
        >
          <Activity className="h-10 w-10 text-emerald-400 mb-4" />
          <h3 className="text-xl font-bold text-slate-100">Server</h3>
          <p className="text-slate-400">
            {backendOk === null
              ? "Loading..."
              : backendOk
                ? `v${healthData?.version || "?"}`
                : "Offline"}
          </p>
        </div>
      </div>
    </div>
  );
}
