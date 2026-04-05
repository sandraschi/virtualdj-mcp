/** Base URL for the FastAPI bridge (health, OpenAPI). Must match backend port from web_sota/start.ps1 / MCP_PORT. */
export const MCP_BRIDGE_BASE = (
    import.meta.env.VITE_MCP_BRIDGE_URL ?? "http://127.0.0.1:10877"
).replace(/\/$/, "");
