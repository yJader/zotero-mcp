# Windows Docker Deployment for Zotero Web API

This guide covers the official Docker deployment path for running zotero-mcp on Windows with the Zotero Web API.

This setup is intended for:

- Windows 10/11
- Docker Desktop
- Zotero Web API access using `ZOTERO_API_KEY` and `ZOTERO_LIBRARY_ID`
- MCP clients that can connect to an HTTP MCP endpoint

This setup does **not** cover:

- Local Zotero desktop integration
- `ZOTERO_LOCAL=true`
- `zotero.sqlite` access or local attachment storage
- Better BibTeX or local `127.0.0.1` Zotero endpoints

## Prerequisites

Before you start, make sure you have:

- Docker Desktop installed and running
- A Zotero API key from [zotero.org/settings/keys](https://www.zotero.org/settings/keys)
- Your Zotero library ID
- This repository checked out locally

## 1. Open the Docker deployment directory

From PowerShell:

```powershell
cd path\to\zotero-mcp\docker
```

## 2. Create your environment file

Copy the example file:

```powershell
Copy-Item .env.example .env
```

Then edit `.env` and set:

```dotenv
ZOTERO_LOCAL=false
ZOTERO_API_KEY=your_zotero_api_key
ZOTERO_LIBRARY_ID=your_zotero_library_id
ZOTERO_LIBRARY_TYPE=user
```

Use `group` instead of `user` if you are connecting to a Zotero group library.

## 3. Start the container

Build and start the service:

```powershell
docker compose up -d --build
```

This starts zotero-mcp as a long-running HTTP MCP service on port `8152`.

## 4. Verify the container is running

Check the service status:

```powershell
docker compose ps
```

Inspect logs:

```powershell
docker compose logs -f
```

The service should be listening on:

```text
http://localhost:8152/mcp/
```

If you want a quick endpoint check from PowerShell:

```powershell
Invoke-WebRequest http://localhost:8152/mcp/
```

Depending on the client negotiation flow, you may see a non-200 response for a plain browser-style request. That is still useful as long as the request reaches the MCP server and the container logs show traffic.

## 5. Connect your MCP client

Point your HTTP-capable MCP client at:

```text
http://localhost:8152/mcp/
```

Use this Docker deployment only for HTTP MCP clients. Do not use it as the default path for local `stdio` desktop integrations.

## Scope and limitations

This Docker path is intentionally limited to Zotero Web API access.

- Supported: metadata search, collections, recent items, and Web API write operations
- Not supported: local Zotero desktop API access, local full-text extraction, local attachment lookup, Better BibTeX local endpoints

If you need local Zotero integration on the same machine, use the standard `zotero-mcp` installation flow from the main README instead of Docker.

## Security note

This container exposes an unauthenticated HTTP MCP endpoint on your machine. For local-only use, `localhost` may be sufficient. If you expose it beyond your machine or LAN, add authentication and a reverse proxy before doing so.
