# Missing inference provider — recovery plan (16 Nov 2026)

## Verified blocker
GitHub Models inference API was fully retired July 30, 2026. Official docs: https://docs.github.com/en/github-models and https://github.blog/changelog/2026-07-01-github-models-is-being-fully-retired-on-july-30-2026/. Do NOT attempt old models.github.ai endpoints or assert GITHUB_TOKEN enables free inference.

## Existing state
The manual workflow .github/workflows/b-superworker-pilot.yml runs crypto-agents/superworker_runtime.py, which requires a working HTTPS OpenAI-compatible inference endpoint, model name and provider key configured as GitHub repository variables/secrets. No credentials or endpoint were verified by this plan. A GitHub workflow without a model backend is NOT an AI assistant.

## Zero-upfront-cost candidate
Owner-controlled computer with Ollama: https://ollama.com/ . Install a small compatible open-weight model, evaluate speed and memory, and expose inference only through a secure owner-approved mechanism. Do not publicly expose a local inference port or put private credentials in the repository. GitHub-hosted runners cannot assume access to a home computer.

## Other candidates requiring eligibility checks
Hugging Face Inference Providers: https://huggingface.co/docs/inference-providers . Account, token, quota, and pricing must be confirmed; never assume unlimited free usage. Other free trial providers may impose geographic, billing or rate restrictions. No account creation or authentication without owner approval.

## Director action checklist
D1 verify owner-approved runtime and logs; D2 validate actual endpoint, available quota and zero-spend ceiling; D3 create queue; D6 review output; D9 verify acceptable-use compliance and no-cost deployment; D10 count only actual model calls and overlapping runs.

## Next milestone
Get a permitted model provider connected, execute the pilot with two independent inference calls and a reviewer, retain invocation evidence, then expand to 10/20 as measured capacity permits. No mass account registration, mining on hosted runners, or quota circumvention.
