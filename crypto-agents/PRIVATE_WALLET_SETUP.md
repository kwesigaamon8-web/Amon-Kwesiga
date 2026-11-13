# Set up private owner payment routes for the AI research companies

The research repo is PUBLIC. Do not commit `owner_wallet_directory_private.json` or its full contents to a public issue or file.

## What is already in place
- `wallet_routes.py` knows how to parse a JSON wallet directory from environment variable `OWNER_WALLET_DIRECTORY_JSON`. It yields only route IDs/status in research outputs, never the private address list.
- `company_workers.py`, `company_ai_review.py` and `agents.py` can use the read-only route directory while working.
- Until the directory is securely configured, these agents explicitly report `private_directory_not_configured` and keep using only previously public approved receiving routes.

## Owner setup (manual GitHub Actions edit required)
1. In the connected repository choose **Settings → Secrets and variables → Actions → New repository secret**.
2. Name: `OWNER_WALLET_DIRECTORY_JSON`. Value: the full contents of the private wallet-directory JSON supplied in the owner's chat. Do not paste wallet login credentials, private keys, seeds, passwords, verification codes or exchange passwords.
3. In `.github/workflows/crypto-directors.yml`, pass the repository secret as an environment variable **only to the three trusted Python run steps** for `company_workers.py`, `company_ai_review.py` and `agents.py`: `OWNER_WALLET_DIRECTORY_JSON: ${{ secrets.OWNER_WALLET_DIRECTORY_JSON }}`. Keep it out of third-party actions, public posts, logs and artifact uploads.
4. Re-run the workflow and check per-role `wallet_directory_access` status. It must say `private_directory_available` before claiming all addresses are available during a job.
5. Rotate or delete the secret if unwanted; all cryptographic signing and funds handling must stay outside the research system.

## Privacy and payment requirements
- This secret contains **public receiving addresses and potential exchange deposit destinations only**, not access to funds or bank/exchange accounts.
- The Binance addresses were provided from **USDC** deposit screens. Exact Binance-supported network/asset is still unconfirmed for several entries; memo IDs must match on shared destinations. Never use an ambiguous route for a payment request.
- Direct payer agreement, account ownership and exact network must be checked before suggesting a route, and a public blockchain deposit is not the same as a credited exchange account.
- Research roles may independently recommend work and prepare requests, but cannot sign, send, withdraw, or claim fees with these addresses.

The source-code connection currently does **not** have permission to write Actions repository secrets. Configuring the encrypted value and ensuring the workflow receives it requires the owner's direct action. Do not falsely mark the directory as deployed before that is complete.
