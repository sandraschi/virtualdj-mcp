import { Book, Code, HelpCircle, Terminal } from 'lucide-react';
import { MCP_BRIDGE_BASE } from "@/common/bridge";

export function Help() {
    return (
        <div className="max-w-4xl space-y-8">
            <header>
                <h2 className="text-3xl font-bold tracking-tight text-slate-100">Documentation & Support</h2>
                <p className="text-slate-400">Master the VirtualDJ MCP bridge and its automation capabilities.</p>
            </header>

            <div className="grid gap-6 md:grid-cols-2">
                <section className="space-y-4 rounded-xl border border-slate-800 bg-slate-900/50 p-6">
                    <div className="flex items-center gap-3 text-blue-400">
                        <Book className="h-6 w-6" />
                        <h3 className="font-bold text-slate-100">Getting Started</h3>
                    </div>
                    <ul className="space-y-2 text-sm text-slate-400 list-disc list-inside">
                        <li>Ensure VirtualDJ is running with OS2V (OSC) support.</li>
                        <li>Configure the VDJ host IP in your .env file.</li>
                        <li>Try your first command: "Load track to deck 1".</li>
                    </ul>
                </section>

                <section className="space-y-4 rounded-xl border border-slate-800 bg-slate-900/50 p-6">
                    <div className="flex items-center gap-3 text-emerald-400">
                        <Terminal className="h-6 w-6" />
                        <h3 className="font-bold text-slate-100">CLI Access</h3>
                    </div>
                    <div className="rounded bg-slate-950 p-3 font-mono text-xs text-slate-300">
                        uv run virtualdj-mcp --host 127.0.0.1
                    </div>
                    <p className="text-xs text-slate-500 italic">Direct stdio interface for headless environments.</p>
                </section>
            </div>

            <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6">
                <div className="flex items-center gap-3 text-amber-400 mb-4">
                    <Code className="h-6 w-6" />
                    <h3 className="font-bold text-slate-100">API Reference</h3>
                </div>
                <p className="text-sm text-slate-400 leading-relaxed">
                    The VirtualDJ MCP bridge exposes a FastAPI endpoint at <code className="text-blue-400">{MCP_BRIDGE_BASE}</code>.
                    Standard documentation is available at{" "}
                    <a href={`${MCP_BRIDGE_BASE}/api/docs`} className="underline hover:text-white">/api/docs</a>.
                </p>
            </div>

            <div className="flex items-center gap-2 text-slate-500 text-xs justify-center pt-8">
                <HelpCircle className="h-4 w-4" />
                <span>Need more help? Visit the <a href="https://github.com/sandraschi/virtualdj-mcp" className="underline">GitHub Repository</a>.</span>
            </div>
        </div>
    );
}
