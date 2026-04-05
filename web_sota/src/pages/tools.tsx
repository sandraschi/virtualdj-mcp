import { Settings2, Play, Info } from 'lucide-react';

const TOOLS = [
    { name: 'vdj_deck', description: 'Control playback, speed, and positioning for any deck.' },
    { name: 'vdj_mixer', description: 'Modify volume, gain, EQ, and effects for any channel.' },
    { name: 'vdj_library', description: 'Search, load, and manage tracks in the VirtualDJ database.' },
    { name: 'vdj_automation', description: 'Execute complex macro sequences and automated transitions.' },
    { name: 'vdj_performance', description: 'Trigger hotcues, loops, and sampler pads.' },
];

export function Tools() {
    return (
        <div className="space-y-6">
            <header>
                <h2 className="text-3xl font-bold tracking-tight text-slate-100">MCP Tool Explorer</h2>
                <p className="text-slate-400">Directly execute and test FastMCP tools for VirtualDJ orchestration.</p>
            </header>

            <div className="grid gap-6">
                {TOOLS.map((tool) => (
                    <div key={tool.name} className="flex flex-col rounded-xl border border-slate-800 bg-slate-900/50 overflow-hidden backdrop-blur-sm">
                        <div className="flex items-center justify-between bg-slate-800/50 px-6 py-4">
                            <div className="flex items-center gap-3">
                                <Settings2 className="h-5 w-5 text-blue-400" />
                                <span className="font-mono text-sm font-bold text-slate-100">{tool.name}</span>
                            </div>
                            <button className="flex items-center gap-2 rounded-md bg-blue-600 px-4 py-2 text-xs font-bold text-white hover:bg-blue-500 transition-colors">
                                <Play className="h-3 w-3" />
                                EXECUTE
                            </button>
                        </div>
                        <div className="p-6">
                            <p className="text-sm text-slate-400 mb-4">{tool.description}</p>
                            <div className="rounded bg-slate-950 p-4">
                                <div className="flex items-start gap-2 text-xs text-slate-500 font-mono">
                                    <Info className="h-3 w-3 mt-0.5" />
                                    <span>Schema: {'{ deck: number, action: string, value?: number }'}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
