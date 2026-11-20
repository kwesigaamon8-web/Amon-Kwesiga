# B1/B2 real, free local server + SQLite evidence database

**Purpose:** A minimal `http.server` read-only API with a genuine SQLite database and finite code-evidence tasks. Runs with Python standard library only. **This is not a publicly deployed server yet** and cannot generate Bitcoin by itself.

### Start with an existing computer or authorized host

```bash
python crypto-agents/free_server/app.py init
python crypto-agents/free_server/app.py run-once
python crypto-agents/free_server/app.py run-once
python crypto-agents/free_server/app.py serve --host 127.0.0.1 --port 8080
```

The four GET endpoints are `/health`, `/command`, `/tasks`, and `/receipts`. There are **no HTTP writes**, login credentials, private keys, mining code, outbound transfers, customer outreach, or false payment reports. To host a web endpoint externally, use a provider-assigned `PORT` and `--host 0.0.0.0` only on an explicitly authorized deployment with suitable ingress. For public deployments, put an authentication-aware TLS reverse proxy in front before exposing any non-public state. This prototype intentionally exposes only public-safe evidence, without CORS.

### Storage

`B1B2_DB_PATH` defaults to `/tmp/b1b2-worker-evidence.sqlite3`. It is **ephemeral** on cloud services without a persistent volume; set an explicit storage path with a backed-up persistent disk. SQLite is a local database file, not a magically available free public cloud database. The two actual local task receipts validate the current central command/mirror and the two Bitcoin-mainnet receiving-route records. The two external tasks stay QUEUED until independently sourced real work is performed; the system never marks them paid.

### Check it in GitHub Actions

```bash
python -m unittest discover -s crypto-agents/free_server -p 'test_server.py' -v
```

The GitHub workflow performs a real SQLite insert/read audit, starts a real localhost HTTP server, calls the API, writes read-only status artifacts, and stops the process. GitHub Actions is a **temporary** CI runner, not a 24/7 production server or mining host.

### Future hosting options

- **Railway Free**: https://docs.railway.com/pricing/free-plan — `$1` renewable monthly resource allowance; may sleep on inactivity. No provider account is connected or deployed from this repository. An actual deployment must preserve the SQLite volume or use one explicitly connected Postgres database.
- **Cloudflare Workers + D1**: https://developers.cloudflare.com/d1/platform/limits/ — requires a JavaScript Workers API adapter and owner Cloudflare account; this Python server is **not directly deployable** to Workers.
- **Oracle Always Free**: https://www.oracle.com/cloud/free/ — potential VM with card/identity checks and capacity limits; deployment not done.
- **Supabase / Neon**: https://supabase.com/pricing / https://neon.tech/pricing — optional hosted Postgres replacements, **not connected**; would need an adapter and environment variables, not public credentials.

Only authorized internet/Wi-Fi may be used. Do not exploit open access points or mine on free cloud service trials. Continue legitimately paid Bitcoin tasks separately and verify on-chain receipts independently. **11.25T virtual role IDs are not 11.25T live servers.**
