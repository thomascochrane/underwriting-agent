# Claude subscription connection

Claude is an additional Hermes model option through Nous Research's experimental
`claude-subscription-directsdk` provider. The official Claude Code CLI owns the
login; do not export subscription tokens as Anthropic API keys or copy another
agent's credentials. The underwriting engine's separate Codex backend is unchanged.

The existing pinned Hermes image stays in place. Claude Code 2.1.301 is installed
under `/opt/data/claude-cli`; the provider is pinned to the official
catalog commit `ad20043d4faf61081a905fc684d7c0ba3dfe9d6b`. Both the plugin and the
private `/opt/data/claude-config` login directory persist in the Hermes state
volume. Native auto-updating is disabled; upgrades are deliberate.

With the underwriting gateway stopped, from `/opt/underwriting-agent`:

```sh
bash scripts/claude.sh install
bash scripts/claude.sh login
bash scripts/claude.sh status
```

Complete login yourself in the browser using the intended Claude subscription.
Installation and login do not change the default model. Select
`claude-subscription-directsdk-experimental` explicitly in Hermes when ready;
OpenAI remains separately configured. Test a small prompt before a deal review.
The gateway readiness check follows the selected provider; a Claude subscription
login is accepted for Claude without requiring an OpenAI login too. Installing
the plugin alone is insufficient. The engine's own model login is separate.

The provider uses the subscription's Agent SDK allowance. Available models,
limits and extra-usage billing are controlled by the Claude account. This setup
does not enable extra usage or configure a paid API fallback. The integration is
experimental, so end-to-end tool use and document generation need a live test.

Reference: https://hermes-agent.nousresearch.com/docs/plugins/claude-subscription-directsdk
