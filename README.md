# Compass

Finding your first open source contribution shouldn't feel like searching through hundreds of issues in a codebase you don't understand.
Compass helps developers find open source issues they can actually solve.

Compass matches contributors to GitHub issues based on their skills, experience, and interests - and explains **why** each recommendation makes sense using measurable signals instead of arbitrary percentages.

## How it works

1. **Tell Compass who you are** — experience level, languages, frameworks, interests.
2. **AI builds a contributor profile** from your inputs.
3. **Compass searches GitHub** for beginner-friendly issues matching your profile.
4. **A deterministic confidence calculator** scores each issue on skill overlap, complexity, repo health, and clarity — then buckets it into High / Medium / Low. No fake percentages, no black box.
5. **An LLM explains the ranking** in plain language — why an issue fits, and honestly, why it might not (yet).

## Roadmap

### v1

- [ ] Contributor profile generation
- [ ] GitHub issue discovery
- [ ] Confidence calculator
- [ ] AI-powered ranking
- [ ] Issue explainer
- [ ] React frontend

## Stack

- **Frontend:** React + Vite + TypeScript
- **Backend:** FastAPI (Python)
- **AI:** Groq API
- **GitHub:** REST API
- **Deployment:** Docker, GitHub Actions CI (planned)

## Philosophy

The LLM has exactly two jobs: turning a form into a readable profile, and explaining a ranking in natural language. Everything else — GitHub search, confidence scoring, sorting — is deterministic, inspectable code. AI handles language and reasoning; explicit logic handles decisions.

## Why Compass?

GitHub already has labels like `good first issue`.

The problem is that those labels don't know anything about *you*.

Compass starts with the contributor, not the repository.

Instead of asking "Which issues are beginner-friendly?"

Compass asks "Which issue is right for *this* developer?"

## License

MIT — see [LICENSE](./LICENSE).