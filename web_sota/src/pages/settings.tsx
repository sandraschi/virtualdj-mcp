import { useEffect, useState } from "react";
import { CheckCircle2, CircleSlash, Loader2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { MCP_BRIDGE_BASE } from "@/common/bridge";

const OSC_PORT_STORAGE_KEY = "virtualdj-mcp-osc-port";
const DEFAULT_OSC_PORT = 40100;

function clampPort(n: number): number {
    if (!Number.isFinite(n)) return DEFAULT_OSC_PORT;
    return Math.min(65535, Math.max(1, Math.floor(n)));
}

function readStoredOscPort(): number {
    try {
        const stored = localStorage.getItem(OSC_PORT_STORAGE_KEY);
        if (!stored) return DEFAULT_OSC_PORT;
        const parsed = Number.parseInt(stored, 10);
        return Number.isNaN(parsed) ? DEFAULT_OSC_PORT : clampPort(parsed);
    } catch {
        return DEFAULT_OSC_PORT;
    }
}

type ConnectionTestPayload = {
    success: boolean;
    http_plugin: { ok: boolean; message: string; base_url: string };
    osc: { ok: boolean; message: string; port: number; target: string };
};

export function Settings() {
    const [oscPort, setOscPort] = useState<number>(readStoredOscPort);
    const [connTesting, setConnTesting] = useState(false);
    const [connResult, setConnResult] = useState<ConnectionTestPayload | null>(null);
    const [connError, setConnError] = useState<string | null>(null);

    useEffect(() => {
        void (async () => {
            try {
                const res = await fetch(`${MCP_BRIDGE_BASE}/api/v1/settings`);
                if (res.ok) {
                    const data = (await res.json()) as { osc_port?: number };
                    if (typeof data.osc_port === "number") {
                        const v = clampPort(data.osc_port);
                        setOscPort(v);
                        localStorage.setItem(OSC_PORT_STORAGE_KEY, String(v));
                    }
                }
            } catch {
                // keep default / localStorage
            }
        })();
    }, []);

    const persistOscPort = (next: number) => {
        const v = clampPort(next);
        setOscPort(v);
        localStorage.setItem(OSC_PORT_STORAGE_KEY, String(v));
    };

    const testConnection = async () => {
        setTesting(true);
        setTestLine(null);
        try {
            const res = await fetch(`${MCP_BRIDGE_BASE}/health`);
            if (res.ok) {
                const data = (await res.json().catch(() => null)) as { status?: string } | null;
                setTestLine(data?.status ? `Connected (${data.status})` : "Connected");
            } else {
                setTestLine(`HTTP ${res.status}`);
            }
        } catch {
            setTestLine("Unreachable — start the backend (web_sota/start.ps1) or set VITE_MCP_BRIDGE_URL to match MCP_PORT.");
        } finally {
            setTesting(false);
        }
    };

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-2xl font-bold tracking-tight text-white">Configuration</h2>
                <p className="text-slate-400">Connections, VirtualDJ reachability, and OSC port alignment</p>
            </div>

            <div className="grid gap-6">
                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <CardTitle className="text-white">API bridge</CardTitle>
                        <CardDescription className="text-slate-400">
                            The FastAPI bridge URL is not edited in this UI. It comes from{" "}
                            <code className="text-slate-300">VITE_MCP_BRIDGE_URL</code> at build time (optional), otherwise
                            defaults to the same host/port as <code className="text-slate-300">web_sota/start.ps1</code> (
                            <code className="text-slate-300">$BackendPort</code> / <code className="text-slate-300">MCP_PORT</code>
                            ).
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="grid gap-2">
                            <Label className="text-slate-300">Bridge base URL (read-only)</Label>
                            <Input
                                readOnly
                                className="bg-slate-900 border-slate-800 text-slate-100 font-mono text-sm"
                                value={MCP_BRIDGE_BASE}
                            />
                        </div>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <CardTitle className="text-white">Connection tests</CardTitle>
                        <CardDescription className="text-slate-400">
                            Runs checks against <span className="text-slate-300">VDJ_HTTP_HOST</span> /{" "}
                            <span className="text-slate-300">VDJ_HTTP_PORT</span> (Network Control Plugin) and a UDP send to{" "}
                            <span className="text-slate-300">VDJ_OSC_PORT</span>. Fix failures in VirtualDJ or env before
                            expecting MCP tools to work.
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <Button
                            type="button"
                            variant="outline"
                            disabled={connTesting}
                            onClick={() => void runConnectionTests()}
                            className="border-slate-800 text-slate-300 hover:bg-slate-800"
                        >
                            {connTesting ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin inline" />
                                    Running tests…
                                </>
                            ) : (
                                "Run connection tests"
                            )}
                        </Button>

                        {connError ? (
                            <p className="text-sm text-red-400" role="alert">
                                {connError}
                            </p>
                        ) : null}

                        {connResult ? (
                            <div className="space-y-3 rounded-lg border border-slate-800 bg-slate-900/40 p-4 text-sm">
                                <div className="flex items-start gap-2">
                                    {connResult.success ? (
                                        <CheckCircle2 className="h-5 w-5 shrink-0 text-emerald-400" aria-hidden />
                                    ) : (
                                        <CircleSlash className="h-5 w-5 shrink-0 text-amber-400" aria-hidden />
                                    )}
                                    <div>
                                        <p className="font-medium text-slate-200">
                                            {connResult.success ? "All checks passed" : "Some checks failed"}
                                        </p>
                                        <p className="text-xs text-slate-500 mt-1">
                                            HTTP uses <code className="text-slate-400">{connResult.http_plugin.base_url}</code>
                                            ; OSC target <code className="text-slate-400">{connResult.osc.target}</code>.
                                        </p>
                                    </div>
                                </div>
                                <ul className="space-y-2 border-t border-slate-800 pt-3">
                                    <li className="flex gap-2">
                                        {connResult.http_plugin.ok ? (
                                            <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-400 mt-0.5" />
                                        ) : (
                                            <CircleSlash className="h-4 w-4 shrink-0 text-red-400 mt-0.5" />
                                        )}
                                        <div>
                                            <span className="text-slate-300">Network Control (HTTP)</span>
                                            <p className="text-slate-500 text-xs mt-0.5">{connResult.http_plugin.message}</p>
                                        </div>
                                    </li>
                                    <li className="flex gap-2">
                                        {connResult.osc.ok ? (
                                            <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-400 mt-0.5" />
                                        ) : (
                                            <CircleSlash className="h-4 w-4 shrink-0 text-red-400 mt-0.5" />
                                        )}
                                        <div>
                                            <span className="text-slate-300">OSC port (UDP send)</span>
                                            <p className="text-slate-500 text-xs mt-0.5">{connResult.osc.message}</p>
                                        </div>
                                    </li>
                                </ul>
                            </div>
                        ) : null}
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <CardTitle className="text-white">OSC (OS2V)</CardTitle>
                        <CardDescription className="text-slate-400">
                            <span className="text-amber-200/90">Required for control.</span> This UDP port must match
                            VirtualDJ <span className="text-slate-300">Settings → OSC</span> exactly (factory default is
                            often <code className="text-slate-300">40100</code>). If it is wrong, OSC cannot reach
                            VirtualDJ and control fails. Set <code className="text-slate-300">VDJ_OSC_PORT</code> on the
                            server to that value; <code className="text-slate-300">web_sota/start.ps1</code> exports{" "}
                            <code className="text-slate-300">40100</code> when unset.
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="grid gap-2 max-w-xs">
                            <Label htmlFor="osc-port" className="text-slate-300">
                                OSC port (required)
                            </Label>
                            <Input
                                id="osc-port"
                                type="number"
                                required
                                min={1}
                                max={65535}
                                value={oscPort}
                                onChange={(e) => {
                                    const raw = e.target.value;
                                    if (raw === "") return;
                                    const n = Number.parseInt(raw, 10);
                                    if (!Number.isNaN(n)) persistOscPort(n);
                                }}
                                className="bg-slate-900 border-slate-800 text-slate-100 font-mono text-sm"
                                aria-required
                            />
                            <p className="text-xs text-slate-500">
                                Value shown here is synced from the bridge when online. Keep it in sync with{" "}
                                <code className="text-slate-400">VDJ_OSC_PORT</code> and VirtualDJ.
                            </p>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
