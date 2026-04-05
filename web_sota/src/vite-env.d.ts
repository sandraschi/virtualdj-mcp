/// <reference types="vite/client" />

interface ImportMetaEnv {
    /** Optional override; default matches web_sota/start.ps1 $BackendPort (10877). */
    readonly VITE_MCP_BRIDGE_URL?: string;
}

interface ImportMeta {
    readonly env: ImportMetaEnv;
}
