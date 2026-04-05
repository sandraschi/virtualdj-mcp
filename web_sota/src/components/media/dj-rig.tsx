export function DJRig() {
    return (
        <div className="relative w-full aspect-[2/1] bg-slate-950/40 rounded-3xl border border-slate-800 shadow-2xl overflow-hidden p-6 md:p-8 flex gap-4 backdrop-blur-xl group">
            {/* Deck A */}
            <div className="flex-1 flex flex-col items-center justify-center space-y-4">
                <div className="relative">
                    <div className="absolute -inset-1 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full blur opacity-20 group-hover:opacity-40 transition duration-1000"></div>
                    <div className="relative w-32 h-32 md:w-48 md:h-48 rounded-full border-4 border-slate-800 bg-slate-900 flex items-center justify-center animate-spin-slow">
                        <div className="w-1/3 h-1/3 rounded-full bg-slate-950 border-2 border-slate-800 flex items-center justify-center">
                            <div className="w-2 h-2 rounded-full bg-blue-500 shadow-[0_0_10px_#3b82f6]"></div>
                        </div>
                        <div className="absolute top-2 w-1.5 h-6 bg-blue-400 rounded-full shadow-[0_0_10px_#60a5fa]"></div>
                    </div>
                </div>
                <div className="flex space-x-2">
                    <div className="w-12 h-1 bg-slate-800 rounded-full overflow-hidden">
                        <div className="w-2/3 h-full bg-blue-500 transition-all duration-300"></div>
                    </div>
                    <div className="w-12 h-1 bg-slate-800 rounded-full overflow-hidden">
                        <div className="w-1/2 h-full bg-indigo-500 transition-all duration-300"></div>
                    </div>
                </div>
            </div>

            {/* Central Mixer Section */}
            <div className="w-24 md:w-40 border-x border-slate-800/50 flex flex-col items-center py-4 space-y-6 bg-slate-900/20">
                <div className="grid grid-cols-2 gap-4">
                    {[1, 2, 3, 4].map((i) => (
                        <div key={i} className="flex flex-col items-center space-y-1">
                            <div className="w-6 h-6 md:w-8 md:h-8 rounded-full border-2 border-slate-800 bg-slate-900 shadow-inner flex items-center justify-center relative rotate-45">
                                <div className="absolute top-0 w-0.5 h-2 bg-slate-600 rounded"></div>
                            </div>
                        </div>
                    ))}
                </div>

                <div className="flex-1 flex justify-center space-x-6 w-full px-4 pt-4">
                    <div className="w-2 h-full bg-slate-900 rounded-full border border-slate-800 relative">
                        <div className="absolute bottom-1/4 left-0 right-0 h-4 bg-slate-700 rounded shadow-lg border border-slate-600 -mx-1"></div>
                    </div>
                    <div className="w-2 h-full bg-slate-900 rounded-full border border-slate-800 relative">
                        <div className="absolute bottom-1/2 left-0 right-0 h-4 bg-slate-700 rounded shadow-lg border border-slate-600 -mx-1"></div>
                    </div>
                </div>

                <div className="w-full px-4 pt-2">
                    <div className="h-2 w-full bg-slate-900 rounded-full border border-slate-800 relative">
                        <div className="absolute left-1/3 top-0 bottom-0 w-8 bg-slate-800 rounded shadow-lg border border-slate-700 -my-1"></div>
                    </div>
                </div>
            </div>

            {/* Deck B */}
            <div className="flex-1 flex flex-col items-center justify-center space-y-4">
                <div className="relative">
                    <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500 to-blue-500 rounded-full blur opacity-20 group-hover:opacity-40 transition duration-1000"></div>
                    <div className="relative w-32 h-32 md:w-48 md:h-48 rounded-full border-4 border-slate-800 bg-slate-900 flex items-center justify-center animate-spin-reverse">
                        <div className="w-1/3 h-1/3 rounded-full bg-slate-950 border-2 border-slate-800 flex items-center justify-center">
                            <div className="w-2 h-2 rounded-full bg-indigo-500 shadow-[0_0_10px_#6366f1]"></div>
                        </div>
                        <div className="absolute top-2 w-1.5 h-6 bg-indigo-400 rounded-full shadow-[0_0_10px_#818cf8]"></div>
                    </div>
                </div>
                <div className="flex space-x-2">
                    <div className="w-12 h-1 bg-slate-800 rounded-full overflow-hidden">
                        <div className="w-1/3 h-full bg-indigo-500 transition-all duration-300"></div>
                    </div>
                    <div className="w-12 h-1 bg-slate-800 rounded-full overflow-hidden">
                        <div className="w-3/4 h-full bg-blue-500 transition-all duration-300"></div>
                    </div>
                </div>
            </div>

            <style>{`
        @keyframes spin-slow {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        @keyframes spin-reverse {
          from { transform: rotate(360deg); }
          to { transform: rotate(360deg); }
          to { transform: rotate(0deg); }
        }
        .animate-spin-slow {
          animation: spin-slow 10s linear infinite;
        }
        .animate-spin-reverse {
          animation: spin-reverse 15s linear infinite;
        }
      `}</style>
        </div>
    );
}
