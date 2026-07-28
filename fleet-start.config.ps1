# Per-repo fleet start config for virtualdj-mcp
# Edit ports/backend target here - start.ps1 is fleet-standard.
@{
    Name         = 'virtualdj-mcp'
    BackendPort  = 10877
    FrontendPort = 10876
    HealthPath   = '/health'
    WebRoot      = 'D:\Dev\repos\virtualdj-mcp\web_sota'
    Backend = @{
        Kind          = 'uvicorn'
        UvicornTarget = 'virtualdj_mcp.server:app'
        SyncExtras    = @('dev')
        Env           = @{ WEB_PORT = '10877' }
    }
    Frontend = @{
        Kind           = 'vite-npm'
        PackageManager = 'npm'
        PortEnvVar     = 'VITE_PORT'
        ApiTargetEnv   = 'VITE_API_TARGET'
    }
}
