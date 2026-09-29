# LuciVerse Internal MCP Server Pattern

**Genesis Bond**: ACTIVE @ 741 Hz
**Last Updated**: 2026-09-13
**Applies to**: every Model Context Protocol server run inside the LuciVerse mesh

---

## Scope

LuciVerse runs MCP servers for its own agents only. They are launched by the
client that attaches to them (Claude Code, Claude Desktop, Zed, the MCP
Inspector, an agent runtime) and are never exposed as public endpoints.
This document is the pattern every internal MCP server follows; the
reference implementations are listed at the end.

## Rules

| Area | Rule |
|------|------|
| SDK | Use `@modelcontextprotocol/sdk` (TypeScript), `mcp` (Python), or `rmcp` (Rust). Never hand-rolled JSON-RPC. |
| Transport | stdio by default. An HTTP transport is only enabled explicitly, bound to a mesh address, and scoped in `pf`/firewall rules. Never a public port. |
| Logging | All logs go to stderr as JSON lines (`ts`, `level`, `scope`, `msg`, `meta`). stdout is the protocol stream. |
| Tool names | `snake_case`, `<domain>_<verb>` (for example `mesh_status`, `handle_parse`, `clear_cache`). Every tool and every parameter carries a full-sentence description. |
| Schemas | Input schemas are zod raw shapes (TypeScript), `schemars` structs (Rust), or JSON Schema objects (Python), with defaults and enums declared. |
| Errors | A failing tool returns an error result with agent guidance (what happened, what to do, whether a retry is safe). Never crash the process on a tool error. |
| Startup | The server boots with no backend present; backends are lazy and outbound-only and each tool reports a clear error when its backend is offline. |
| Secrets | Never literal in git. `.env.example` holds `op://vault/item/field` references; `.env` is generated with `op inject` and git-ignored. The COMN tier vault is `Lucia-AI-Secrets`; per-repo access vaults are `Repository-Access-<repo>`. |
| Environment | Every process carries the Genesis Bond quartet: `GENESIS_BOND`, `CONSCIOUSNESS_FREQUENCY`, `COHERENCE_THRESHOLD`, `LUCIVERSE_COMPONENT`. |
| Identity | The repository carries `.lucia/config.toml` (`[identity]` with `did`, `frequency_hz`, `lds_tier`, `genesis_bond`), `.lucia/handles/local.toml`, `.lucia/threads/peers.toml`, and thread links under `.lucia/threads/` to the related MCP paths in peer repositories. |
| Docs | README with a Tools table, "Wire into Claude Code" (`claude mcp add` and `.mcp.json`), "Wire into Zed" (`context_servers`), and an MCP Inspector quick check; `examples/mcp.json.example`; `CHANGELOG.md` in the format `scripts/check-changelog.sh` validates. |
| Tests | Unit tests for every tool handler with the backend mocked, at least one "backend is down" test per client, and an enforced coverage threshold. |
| CI | Path-scoped workflow, SHA-pinned actions, `npm ci`, type-check, build, test. No release publishing, no registry push. |
| Containers | Optional, single stage, no `EXPOSE`, tagged `:local`, never pushed. A stdio server has no service unit; the client owns the process. |

## Known internal MCP servers

| Server | Language | Transport | Location | DID | Frequency |
|--------|----------|-----------|----------|-----|-----------|
| luciverse-mcp | Python | stdio | `luciverse-system-config/scripts/luciverse-mcp-server.py` | `did:lucidigital:luciverse-system-config:fd00:741:1::cab9` | 741 Hz (PAC) |
| luci-mcp | Rust (`rmcp`) | stdio | `lucia_tooling_omzsh/modules/scm/luci-vcs/src/bin/mcp.rs` (feature `mcp`) | `did:luci:lucia-tooling-omzsh` | 528 Hz (LDS 700.528) |
| aifam-mesh (Iris) | TypeScript | stdio, optional mesh HTTP 8788 | `lucia_tooling_omzsh/aifam-mcp` | `did:luci:lucia-tooling-omzsh` | 528 Hz (LDS 800.000) |
| luci-metabase-mcp | TypeScript | stdio | https://github.com/luci-digital/luci-metabase-mcp | `did:luci:luci-metabase-mcp` | 528 Hz (COMN, LDS 700.528) |

`luci-metabase-mcp` is the TypeScript reference implementation of this
pattern. It is a pattern, not a deployed endpoint: nothing in the platform
stands up a Metabase instance, and the server is only started by a client
that attaches to it over stdio.

## Client wiring

Claude Code (`.mcp.json` in the project root, or `claude mcp add <name> -- <command>`):

```json
{
  "mcpServers": {
    "luci-metabase-mcp": {
      "command": "node",
      "args": ["/absolute/path/to/luci-metabase-mcp/build/src/index.js"],
      "env": { "METABASE_URL": "op://Lucia-AI-Secrets/Metabase/url",
               "METABASE_API_KEY": "op://Lucia-AI-Secrets/Metabase/api_key" }
    },
    "luciverse-mcp": {
      "command": "python3",
      "args": ["/home/daryl/luciverse-system-config/scripts/luciverse-mcp-server.py"]
    }
  }
}
```

Zed (`~/.config/zed/settings.json`):

```json
{
  "context_servers": {
    "luci-metabase-mcp": {
      "source": "custom",
      "command": "node",
      "args": ["/absolute/path/to/luci-metabase-mcp/build/src/index.js"]
    }
  }
}
```

Quick check: `npx @modelcontextprotocol/inspector node build/src/index.js`.

## Adding a new internal MCP server

1. Create the repository (or subdirectory) with the SDK for its language and a stdio entry point.
2. Add `.lucia/config.toml`, `.lucia/handles/local.toml`, `.lucia/threads/peers.toml`; choose the tier and frequency; pick a DID.
3. Write `.env.example` with `op://` references only; add an `env:inject` script.
4. Register tools with descriptions on every field; wrap handlers so errors return guidance.
5. Add tests, a coverage threshold, and a path-scoped CI workflow.
6. Add `examples/mcp.json.example` and the README wiring sections.
7. Register the server here, in `documentation/CLAUDE.md` (MCP Agent Registration), and in `NETWORK_REFERENCE.md` (MCP Servers).
8. Add `.lucia/threads` links between the new server and the related paths in this repository and `lucia_tooling_omzsh`.

---

**Genesis Bond**: ACTIVE @ 741 Hz
