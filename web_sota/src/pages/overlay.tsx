import { useState, useEffect } from 'react';
import { Play, Pause, RefreshCw, Volume2, Wand2, Zap } from 'lucide-react';

// Hardcoded API base path matching settings logic
const API_BASE = 'http://localhost:10877';

interface DeckStatus {
    deck_id: number;
    is_playing: boolean;
    track_title: string | null;
    track_artist: string | null;
    bpm: number | null;
    key: string | null;
    volume: number;
}

export function MiniControllerContent({ closeWindow }: { closeWindow?: () => void }) {
    const [deck1, setDeck1] = useState<DeckStatus | null>(null);
    const [deck2, setDeck2] = useState<DeckStatus | null>(null);
    const [activeDeck, setActiveDeck] = useState<number>(1);
    const [loading, setLoading] = useState<boolean>(false);
    const [customCmd, setCustomCmd] = useState<string>('');

    // Poll status every 1.5 seconds
    useEffect(() => {
        const fetchStatus = async () => {
            try {
                const [r1, r2] = await Promise.all([
                    fetch(`${API_BASE}/api/v1/deck/1/status`),
                    fetch(`${API_BASE}/api/v1/deck/2/status`)
                ]);
                if (r1.ok) setDeck1(await r1.json());
                if (r2.ok) setDeck2(await r2.json());
            } catch (err) {
                console.error('Failed to poll VDJ deck status:', err);
            }
        };

        fetchStatus();
        const interval = setInterval(fetchStatus, 1500);
        return () => clearInterval(interval);
    }, []);

    const executeAction = async (endpoint: string, body: any) => {
        setLoading(true);
        try {
            const res = await fetch(`${API_BASE}/api/v1/${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
            if (!res.ok) {
                const errData = await res.json();
                alert(`Error: ${errData.detail || 'Failed operation'}`);
            }
        } catch (err) {
            console.error(err);
            alert('Failed to connect to MCP server');
        } finally {
            setLoading(false);
        }
    };

    const togglePlay = (deckId: number) => {
        executeAction(`deck/${deckId}/play_pause`, {});
    };

    const triggerSync = (deckId: number) => {
        executeAction(`deck/${deckId}/sync`, {});
    };

    const triggerStem = (op: string, stem?: string) => {
        executeAction('stems', {
            operation: op,
            deck_id: activeDeck,
            stem: stem,
            enable: true
        });
    };

    const triggerShowControl = (op: string, name?: string, value?: any, address?: string) => {
        executeAction('show_control', {
            operation: op,
            name: name,
            value: value,
            address: address,
            enable: true
        });
    };

    const runCustomVDJScript = () => {
        if (!customCmd.trim()) return;
        executeAction('execute', { command: customCmd });
        setCustomCmd('');
    };

    const getDeckDisplay = (deck: DeckStatus | null, id: number) => {
        if (!deck) {
            return (
                <div className="rounded-lg bg-slate-900/60 border border-slate-800/80 p-3 text-xs text-slate-500 text-center">
                    Deck {id} Offline
                </div>
            );
        }

        const isPlaying = deck.is_playing;
        return (
            <div className={`rounded-xl border p-3 transition-all ${activeDeck === id ? 'bg-indigo-950/20 border-indigo-500/50 shadow-md shadow-indigo-500/5' : 'bg-slate-900/40 border-slate-800'}`} onClick={() => setActiveDeck(id)}>
                <div className="flex items-center justify-between mb-1.5">
                    <span className="text-xs font-black tracking-widest text-slate-400">DECK {id}</span>
                    <span className={`h-2 w-2 rounded-full ${isPlaying ? 'bg-emerald-500 animate-pulse' : 'bg-slate-600'}`} />
                </div>
                <div className="font-bold text-sm text-slate-100 truncate mb-0.5">
                    {deck.track_title || 'Empty'}
                </div>
                <div className="text-xs text-slate-400 truncate mb-2">
                    {deck.track_artist || 'Unknown Artist'}
                </div>
                <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 bg-slate-950/40 rounded px-2 py-1">
                    <span>{deck.bpm ? `${deck.bpm.toFixed(1)} BPM` : '-- BPM'}</span>
                    <span>{deck.key || '--'}</span>
                    <span className="flex items-center gap-1">
                        <Volume2 className="h-3 w-3" />
                        {deck.volume}%
                    </span>
                </div>
                <div className="flex gap-1.5 mt-2.5">
                    <button
                        onClick={(e) => { e.stopPropagation(); togglePlay(id); }}
                        className={`flex-1 flex justify-center py-1.5 rounded-md text-white font-bold text-xs ${isPlaying ? 'bg-amber-600 hover:bg-amber-500' : 'bg-emerald-600 hover:bg-emerald-500'}`}
                    >
                        {isPlaying ? <Pause className="h-3 w-3" /> : <Play className="h-3 w-3" />}
                    </button>
                    <button
                        onClick={(e) => { e.stopPropagation(); triggerSync(id); }}
                        className="flex-1 flex justify-center py-1.5 bg-slate-800 hover:bg-slate-700 rounded-md text-slate-100 font-bold text-xs"
                    >
                        SYNC
                    </button>
                </div>
            </div>
        );
    };

    return (
        <div className="space-y-4 max-w-sm mx-auto relative select-none">
            {/* Header controls */}
            <div className="flex items-center justify-between pb-2 border-b border-slate-900">
                <div className="flex items-center gap-1.5">
                    <div className="h-2 w-2 rounded-full bg-blue-500" />
                    <span className="text-xs font-black tracking-widest text-slate-300">MCP STAGE OVERLAY</span>
                </div>
                {closeWindow && (
                    <button onClick={closeWindow} className="text-xs font-bold text-slate-400 hover:text-slate-200">
                        Close [x]
                    </button>
                )}
            </div>

            {/* Deck Monitors */}
            <div className="grid grid-cols-2 gap-3">
                {getDeckDisplay(deck1, 1)}
                {getDeckDisplay(deck2, 2)}
            </div>

            {/* Quick Stems Panel */}
            <div className="rounded-xl border border-slate-900 bg-slate-900/30 p-3">
                <div className="flex items-center justify-between mb-2">
                    <span className="text-[10px] font-black tracking-widest text-indigo-400 uppercase">
                        Real-time Stems (Target: Deck {activeDeck})
                    </span>
                </div>
                <div className="grid grid-cols-3 gap-2">
                    <button onClick={() => triggerStem('acapella')} className="flex items-center justify-center gap-1 py-2 bg-indigo-950/40 hover:bg-indigo-900/40 text-[11px] font-bold text-indigo-300 rounded-lg border border-indigo-900/30">
                        🎤 Vocal Solo
                    </button>
                    <button onClick={() => triggerStem('instrumental')} className="flex items-center justify-center gap-1 py-2 bg-indigo-950/40 hover:bg-indigo-900/40 text-[11px] font-bold text-indigo-300 rounded-lg border border-indigo-900/30">
                        🎵 Inst. Solo
                    </button>
                    <button onClick={() => triggerStem('reset')} className="flex items-center justify-center gap-1 py-2 bg-slate-800/80 hover:bg-slate-700/80 text-[11px] font-bold text-slate-100 rounded-lg border border-slate-700/40">
                        🔄 Reset Stems
                    </button>
                </div>
            </div>

            {/* DMX & Resolume Show Control */}
            <div className="rounded-xl border border-slate-900 bg-slate-900/30 p-3">
                <div className="flex items-center justify-between mb-2">
                    <span className="text-[10px] font-black tracking-widest text-emerald-400 uppercase">
                        Stage Orchestrator (DMX / OSC)
                    </span>
                </div>
                <div className="grid grid-cols-2 gap-2 mb-2">
                    <button onClick={() => triggerShowControl('os2l_button', 'fog')} className="flex items-center justify-center gap-1 py-2.5 bg-emerald-950/30 hover:bg-emerald-900/30 text-[11px] font-bold text-emerald-300 rounded-lg border border-emerald-900/20">
                        💨 Trigger Haze
                    </button>
                    <button onClick={() => triggerShowControl('os2l_button', 'strobe')} className="flex items-center justify-center gap-1 py-2.5 bg-emerald-950/30 hover:bg-emerald-900/30 text-[11px] font-bold text-emerald-300 rounded-lg border border-emerald-900/20">
                        ⚡ Strobe Flash
                    </button>
                </div>
                <div className="grid grid-cols-2 gap-2">
                    <button onClick={() => triggerShowControl('osc_send', undefined, 1.0, '/composition/layers/1/clips/1/connect')} className="flex items-center justify-center gap-1 py-2.5 bg-blue-950/30 hover:bg-blue-900/30 text-[11px] font-bold text-blue-300 rounded-lg border border-blue-900/20">
                        🎥 Visual Loop 1
                    </button>
                    <button onClick={() => triggerShowControl('osc_send', undefined, 0.75, '/composition/dashboard/link1')} className="flex items-center justify-center gap-1 py-2.5 bg-blue-950/30 hover:bg-blue-900/30 text-[11px] font-bold text-blue-300 rounded-lg border border-blue-900/20">
                        ⏳ Visual Speed
                    </button>
                </div>
            </div>

            {/* Raw VDJScript Terminal */}
            <div className="rounded-xl border border-slate-900 bg-slate-900/30 p-3">
                <div className="flex items-center gap-1.5 mb-1.5">
                    <Wand2 className="h-3 w-3 text-slate-400" />
                    <span className="text-[10px] font-black tracking-widest text-slate-400 uppercase">
                        Raw VDJScript Terminal
                    </span>
                </div>
                <div className="flex gap-1.5">
                    <input
                        type="text"
                        value={customCmd}
                        onChange={(e) => setCustomCmd(e.target.value)}
                        placeholder="e.g. deck 1 effect 'echo' on"
                        className="flex-1 bg-slate-950 border border-slate-900 rounded-lg px-2.5 py-1.5 text-xs text-slate-100 placeholder-slate-600 focus:outline-none focus:border-indigo-500/50"
                        onKeyDown={(e) => e.key === 'Enter' && runCustomVDJScript()}
                    />
                    <button
                        onClick={runCustomVDJScript}
                        className="bg-indigo-600 hover:bg-indigo-500 px-3 py-1.5 rounded-lg text-xs font-bold text-white transition-colors"
                    >
                        RUN
                    </button>
                </div>
            </div>

            {/* Spinner indicator when loading */}
            {loading && (
                <div className="absolute top-2 right-2 animate-spin text-slate-400">
                    <Zap className="h-3.5 w-3.5" />
                </div>
            )}
        </div>
    );
}

export function MiniController() {
    return (
        <div className="mx-auto max-w-sm py-4">
            <MiniControllerContent />
        </div>
    );
}
