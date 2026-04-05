import { Link } from 'react-router-dom';
import { Music, Activity, Layers, PlayCircle } from 'lucide-react';
import { DJRig } from '@/components/media/dj-rig';

export function Dashboard() {
    return (
        <div className="space-y-10 pb-10 relative isolate">
            {/* SOTA Background Aesthetics */}
            <div className="absolute inset-0 -z-10 pointer-events-none overflow-hidden">
                <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-blue-500/10 blur-[120px] rounded-full" />
                <div className="absolute bottom-[10%] right-[-5%] w-[30%] h-[30%] bg-indigo-500/10 blur-[100px] rounded-full" />
            </div>

            {/* Hero Section */}
            <section className="relative overflow-hidden rounded-3xl bg-slate-900/40 border border-slate-800 shadow-2xl backdrop-blur-md">
                <div className="absolute inset-0 bg-gradient-to-br from-blue-600/20 via-transparent to-indigo-600/20" />
                <div className="relative px-8 py-12 md:px-12 md:py-20 max-w-3xl">
                    <div className="inline-flex items-center gap-2 rounded-full bg-blue-500/10 px-3 py-1 text-xs font-bold text-blue-400 border border-blue-500/20 mb-6">
                        <Activity className="h-3 w-3" />
                        V2026 SOTA EDITION
                    </div>
                    <h1 className="text-4xl md:text-6xl font-black tracking-tight text-white mb-6">
                        VirtualDJ <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-400">Orchestrator</span>
                    </h1>
                    <p className="text-lg text-slate-400 mb-8 leading-relaxed max-w-2xl">
                        Precision automation engine for VirtualDJ performance. Real-time deck control,
                        automated library management, and deep stems integration via FastMCP bridge.
                    </p>

                    {/* DJ Rig Visualization */}
                    <div className="mb-10 max-w-4xl">
                        <DJRig />
                    </div>

                    <div className="flex flex-wrap gap-4">
                        <Link to="/tools" className="flex items-center gap-2 rounded-full bg-blue-600 hover:bg-blue-500 px-6 py-3 font-bold text-white transition-all transform hover:scale-105 no-underline shadow-lg shadow-blue-500/20">
                            <PlayCircle className="h-5 w-5" />
                            Launch Controls
                        </Link>
                        <Link to="/help" className="flex items-center gap-2 rounded-full bg-slate-800 hover:bg-slate-700 px-6 py-3 font-bold text-slate-100 transition-all no-underline">
                            View Documentation
                        </Link>
                    </div>
                </div>
            </section>

            {/* Quick Stats Grid */}
            <div className="grid gap-6 md:grid-cols-3">
                <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-6 backdrop-blur-sm">
                    <Music className="h-10 w-10 text-blue-400 mb-4" />
                    <h3 className="text-xl font-bold text-slate-100">Live Decks</h3>
                    <p className="text-slate-400">4 channels active</p>
                </div>
                <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-6 backdrop-blur-sm">
                    <Layers className="h-10 w-10 text-indigo-400 mb-4" />
                    <h3 className="text-xl font-bold text-slate-100">Stems Mode</h3>
                    <p className="text-slate-400">Real-time isolation active</p>
                </div>
                <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-6 backdrop-blur-sm">
                    <Activity className="h-10 w-10 text-emerald-400 mb-4" />
                    <h3 className="text-xl font-bold text-slate-100">Latency</h3>
                    <p className="text-slate-400">0.8ms average Jitter</p>
                </div>
            </div>
        </div>
    );
}
