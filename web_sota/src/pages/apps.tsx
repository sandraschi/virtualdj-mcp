import { APPS_CATALOG } from '@/common/apps-catalog';
import { ExternalLink, Tag } from 'lucide-react';

export function Apps() {
    return (
        <div className="space-y-6">
            <header>
                <h2 className="text-3xl font-bold tracking-tight text-slate-100">Fleet Discovery</h2>
                <p className="text-slate-400">Navigate between active SOTA-compliant MCP servers in your network.</p>
            </header>

            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                {APPS_CATALOG.map((app) => (
                    <a
                        key={app.id}
                        href={app.url}
                        className="group flex flex-col rounded-xl border border-slate-800 bg-slate-900/50 hover:bg-slate-800/80 transition-all hover:scale-[1.02] shadow-lg"
                    >
                        <div className="p-6 flex-1">
                            <div className="flex items-center justify-between mb-4">
                                <div className="rounded-lg bg-slate-800 p-2 text-blue-400 group-hover:text-blue-300 transition-colors">
                                    <app.icon className="h-6 w-6" />
                                </div>
                                <div className="rounded-full bg-slate-800/50 px-2.5 py-0.5 text-[10px] font-bold text-slate-500 uppercase">
                                    Port {app.port}
                                </div>
                            </div>
                            <h3 className="text-lg font-bold text-slate-100 mb-1 group-hover:text-white">{app.label}</h3>
                            <p className="text-sm text-slate-400 line-clamp-2">{app.description}</p>
                        </div>
                        <div className="px-6 py-4 border-t border-slate-800 flex items-center justify-between">
                            <div className="flex gap-1 overflow-hidden">
                                {app.tags.map(tag => (
                                    <span key={tag} className="flex items-center gap-1 text-[10px] text-slate-500 lowercase">
                                        <Tag className="h-2 w-2" />
                                        {tag}
                                    </span>
                                ))}
                            </div>
                            <ExternalLink className="h-4 w-4 text-slate-600 group-hover:text-slate-300" />
                        </div>
                    </a>
                ))}
            </div>
        </div>
    );
}
