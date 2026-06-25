# 1. Install the LLM (Claude Code)

The agent you talk to. This repo's dictation and transcription tools feed it
context; install it first. These commands are from the
[official setup docs](https://code.claude.com/docs/en/setup) - check there for
the authoritative, up-to-date version.

## Requirements

- **OS**: macOS 13+, Windows 10 1809+ , or Linux (Ubuntu 20.04+ / Debian 10+ /
  Alpine 3.19+).
- **Hardware**: 4 GB+ RAM, x64 or ARM64.
- **Network**: an internet connection (Claude Code runs in the cloud; only the
  voice tools in this repo are local).
- **Account**: a Claude **Pro, Max, Team, or Enterprise** plan, or API access
  via the Anthropic Console / Bedrock / Vertex / Foundry. The free Claude.ai
  plan does **not** include Claude Code.

## Install

**Native installer (recommended):**

```bash
# macOS, Linux, WSL
curl -fsSL https://claude.ai/install.sh | bash
```

```powershell
# Windows PowerShell
irm https://claude.ai/install.ps1 | iex
```

Native installs auto-update in the background.

**Or via a package manager:**

```bash
brew install --cask claude-code        # macOS (Homebrew)
```

```powershell
winget install Anthropic.ClaudeCode    # Windows (WinGet)
```

```bash
npm install -g @anthropic-ai/claude-code   # any platform; needs Node.js 18+
```

> Prefer a GUI? There is also a [Claude Code desktop app](https://code.claude.com/docs/en/desktop-quickstart).

## Verify

```bash
claude --version
claude doctor      # detailed health check of your install
```

## Start and sign in

Open a terminal in the project you want to work in:

```bash
claude
```

The first run opens a browser to log in. After that, you talk to Claude Code in
the terminal - and with the [dictation tool](dictation/) in this repo, you can
talk to it literally, in your own language.
