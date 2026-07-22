<div align="center">

# 🧭 Compass

**Find the open source issue you can actually solve.**

[![CI](https://github.com/akhwasim/compass/actions/workflows/ci.yml/badge.svg)](https://github.com/akhwasim/compass/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Built with FastAPI](https://img.shields.io/badge/backend-FastAPI-009688)](https://fastapi.tiangolo.com/)
[![Built with React](https://img.shields.io/badge/frontend-React%20%2B%20Vite-61DAFB)](https://react.dev/)
[![Follow on X](https://img.shields.io/badge/Built%20in%20public-%40akhwasim-000000?logo=x)](https://x.com/akhwasim)

Compass helps developers find GitHub issues they can realistically contribute to. It combines deterministic ranking with bounded LLM reasoning to recommend beginner-friendly issues and explain why they're a good match.

**🔗 Live app:** [compass-oss.netlify.app](https://compass-oss.netlify.app)
**🔗 Backend API:** https://compass-quwc.onrender.com
**🐦 Built in public on X:** [@akhwasim](https://x.com/akhwasim)

</div>

> The backend runs on Render's free tier, which spins down after inactivity. The first request after idle time may take 30–60 seconds to wake up.

---

## The problem

Every beginner wants to contribute to open source. Then they open a repository and see 500 issues, 50 labels, and an unfamiliar codebase - and close the tab.

Compass replaces that with a short, ranked, explained list of issues suited to who you actually are.

## How it works

1. **Tell Compass who you are** - experience level, languages, frameworks, and interests.
2. **An LLM builds a contributor profile** from your inputs.
3. **Compass searches GitHub** for beginner-friendly issues in your languages.
4. **A deterministic confidence calculator** scores each issue on skill overlap, complexity, and repository health - bucketed into High / Medium / Low, not a fabricated percentage.
5. **An LLM reasons over the real issue text** to judge clarity and topical fit, and can only *downgrade* the confidence score if the issue is genuinely unclear - never upgrade it. The score stays grounded in verifiable signals, never LLM optimism.
6. **Click any issue** for a plain-language explainer: what it's asking for, which files are likely relevant (verified against the real repo structure - never invented), what concepts you'll need, and a suggested first step.

## Design philosophy

The LLM has exactly two jobs: turning a form into a readable profile, and reasoning over real text to explain a ranking. Everything else - GitHub search, the confidence baseline, sorting, file-path verification - is deterministic, inspectable code.

This split matters in practice, not just in theory. An early version let the LLM guess likely file paths from naming convention, and it occasionally invented plausible-but-nonexistent paths - exactly the kind of error that would break a beginner's trust the first time they hit it. The fix wasn't a better prompt. It was giving the LLM only *verified* repository data and instructing it to describe uncertainty in words instead of naming files it couldn't confirm. 

Compass follows one simple principle:
> **If the system can verify a fact itself, the LLM should never be allowed to invent it.**

## Screenshots

*(add a screenshot or short GIF of the form and results screen here)*

---

## Engineering Decisions

Compass intentionally avoids several approaches that seemed reasonable but failed in practice.

- Framework names are not required for skill matching because real issues rarely mention the framework explicitly.
- Confidence starts from deterministic signals. The LLM may lower confidence if an issue is unclear, but never increase it.
- File paths are verified against the repository structure before being shown. If a path cannot be verified, Compass describes the location instead of inventing one.

Interested in the reasoning behind these decisions?
See [DECISIONS.md](./DECISIONS.md) for a detailed record of the trade-offs, failed approaches, and implementation notes that shaped Compass.

## Stack

**Frontend**
- React + Vite + TypeScript
- Deployed on Netlify

**Backend**
- FastAPI (Python)
- Deployed on Render (Docker)

**AI**
- Groq API (Llama 3.3 70B)

**Other**
- GitHub REST API for issue discovery and repository verification
- Docker + Docker Compose for local development
- GitHub Actions CI (backend tests + frontend build/typecheck on every push)
- Pytest for confidence-calculator unit tests

## Architecture

```
React frontend (Netlify)
        │
        ▼
FastAPI backend (Render)
        │
   ┌────┼────────────────┐
   ▼    ▼              ▼
GitHub  Confidence   Groq API
API     Calculator   (contributor profile,
(search, (deterministic:  ranking + reasoning,
 verify)  skill match,    issue explanation)
          complexity,
          repo health)
```

## API

| Endpoint | Method | Purpose |
|---|---|---|
| `/profile` | POST | Turns form data into a natural-language contributor profile |
| `/recommendations` | POST | Returns ranked, confidence-scored issue matches with reasoning |
| `/issue/{owner}/{repo}/{issue_number}` | GET | Returns a plain-language breakdown of a specific issue |

## Running locally

**Requirements:** Python 3.12+, Node 20+, a GitHub personal access token (`public_repo` scope), a Groq API key.

```bash
git clone https://github.com/akhwasim/compass.git
cd compass
```

**Backend**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# create a .env file with GITHUB_TOKEN and GROQ_API_KEY
python -m uvicorn app.main:app --reload
```

**Frontend**
```bash
cd frontend
npm install
# create a .env file with VITE_API_URL=http://127.0.0.1:8000
npm run dev
```

**Or with Docker:**
```bash
docker compose up --build
```

## Testing

```bash
cd backend
python -m pytest tests/ -v
```

## Status

**v1 complete and deployed.**

- [x] Contributor profile generation
- [x] GitHub issue discovery
- [x] Deterministic confidence calculator (skill overlap, complexity, repo health)
- [x] LLM-powered ranking with grounded reasoning
- [x] Issue explainer with verified file paths
- [x] Full frontend (form, results, issue detail)
- [x] Docker + CI
- [x] Live deployment (Render + Netlify)

## Known limitations (v1)

- **Interest matching is soft, not a hard filter.** GitHub topic tags proved too sparse to reliably filter issues by interest area (e.g. "frontend") when combined with a language filter. Interest is instead judged by the LLM against real issue text and reflected in the explanation - it shapes *why* an issue is or isn't a good topical fit, but doesn't narrow the candidate pool.
- **Folder structure verification is two levels deep**, not fully recursive, to keep GitHub API usage bounded. Deeply nested files may not be verifiable and are described in words instead of named directly.
- **No accounts or history.** Every session is stateless by design for v1.
---

## Roadmap (v2)

- Repository-aware solution guidance grounded in verified file contents
- Visual distinction between verified facts and inferred suggestions
- Explain every confidence signal individually instead of only the overall score
- User feedback to improve recommendation quality over time
- Contribution history and progress tracking

## Follow the build

I'm documenting this project's development in public on X: **[@akhwasim](https://x.com/akhwasim)**.

## License

MIT — see [LICENSE](./LICENSE).
