# Engineering Decisions

This document records the major design decisions made while building Compass, including approaches that were tried, why some of them failed, and why the final implementation looks the way it does.

The goal isn't to document every change, but to explain the reasoning behind decisions that significantly affected the architecture.

---

## 1. Started as "search GitHub better," ended up as something else

First idea was basically: user pastes a repo, AI explains the issues in it. That's just a smarter search bar. 
while exploring I Realized pretty quickly that's not actually solving the real problem - a beginner doesn't have a repo in mind, that's the whole issue. 
Flipped it: user describes themselves, tool finds them something. That's when it actually became a product instead of a feature.

## 2. Wanted a confidence percentage. Talked myself out of it.

Original idea: show something like "73% chance you can solve this." Sounds good on a slide. Problem is there's no actual data behind that number - nobody validated that 73% is right instead of 68 or 80. It's just a made-up number that *looks* rigorous. Instead I went with High/Medium/Low instead, since at least that's honest about being a rough bucket, not fake precision.

Funny enough, a similar idea came back later in a different shape - someone suggested doing the confidence math as a weighted formula, like skill match = 40%, complexity = 25%, etc. Same problem, just wearing a decimal point. Nobody validated those weights either. Rejected it for the same reason.

## 3. Confidence logic: kept it dumb on purpose

Ended up with a simple decision tree for confidence - a handful of if/else checks, nothing fancy. Could've made it a "real" weighted scoring system. Didn't, because a decision tree I can actually read and explain beats a formula that just pretends to be smarter than it is. Might revisit with actual weights once there's real data (like: did people's PRs actually get merged) to tune against. Not before.

## 4. Cut a bunch of stuff that sounded cool

Original brainstorm had mentor mode (AI walks you through the whole PR live), a leveling/progress system, a resume builder, community features. All of it got cut from v1. Mentor mode alone is basically a second project - live command execution, tracking state - that's not "a feature," that's a whole separate problem space. Progress tracking needs real usage data before it's worth building. Community stuff is a full social app on its own. Kept telling myself: finish one small thing instead of half-building five big ones.

## 5. Almost over-built the stack for no reason

Initially I planed to go with Postgres + Redis + Docker + CI from day one, partly just because it looks good on a resume. Cut Postgres and Redis from v1. **Why**, because v1 has no accounts, no history, nothing that actually needs a real database yet. Kept Docker and CI because those don't carry the same risk (no data model to mess up) and they're basically free once set up. Rule I used: if the infra isn't solving a problem I have *right now*, it waits.

## 6. Confidence calculation: eliminating false negatives

Confidence calculator required BOTH the **language** to match AND the **framework** name to literally show up in the issue text before it'd give "High." Turns out that basically never happens - a FastAPI repo's issues almost never say "FastAPI" in the body, even though the whole repo is FastAPI. Ran a test, got 10 results, every single one Medium or Low. That was the tell something was broken. Dropped the framework-text requirement, kept language match as the main signal. Fixed instantly.

## 7. Word count is not the same as "unclear"

Had a rule: if an issue's description was under ~40 words, mark it "vague." Then a real test case came up - an issue that just said "add screenshots to the README" - genuinely one of the clearest, easiest issues you could ask for, and the calculator flagged it vague purely because it was short. That's backwards. Short issues are often the clearest ones.

Pulled the word-count check out completely. Now the LLM actually reads the issue and judges if it's clear, with one rule bolted on: it's only allowed to make the confidence score *worse* than the baseline, never better. So if it decides something's genuinely confusing, it can knock High down to Medium - but it can never invent a High that the deterministic signals didn't already support. Keeps the LLM useful without letting it just hand out confidence for free.

## 8. Interest matching and GitHub search limitations

This was the annoying one. Picked **"Frontend"** as an interest, expected frontend issues back. Tried filtering GitHub search by topic tags **(topic:frontend, topic:react, etc.)** combined with the chosen language. Ran it - zero results. Turns out a Python repo tagged `topic:frontend` barely exists on GitHub. Added a fallback to plain search when the topic filter came back empty... and then realized the fallback was firing basically every time, meaning "Frontend" as a filter was doing nothing at all. Tested it directly: picked Frontend, got back CI issues, doc updates, backend stuff. Maybe 2 out of 10 were actually frontend-relevant.

Had two options: try to fake it with keyword search instead of topics, or just stop pretending GitHub search can filter by "vibe" and let the LLM judge topical fit from the actual issue text instead. Went with the second one. It's more honest - the LLM will actually say "this doesn't really match your frontend interest, but it's solvable" instead of silently returning junk. 
Downside: interest doesn't narrow the list anymore, it just explains it. Wrote that limitation straight into the README instead of hiding it.

## 9. Preventing file-path hallucinations

The issue explainer used to just ask the LLM to guess which files were relevant based on the issue text and typical project conventions. It sounded like you can solve every time - which was the problem, because sometimes those files didn't actually exist in the repo. For a beginner who has no way to know that, hitting a file that isn't there kills trust in the whole tool immediately.

Fixed it by actually fetching the real folder structure (top level plus one level into a few subfolders - not the whole repo, that'd be too many API calls) and telling the LLM: only name a file if it's literally in this list, otherwise describe where to look in plain words instead of guessing a filename. Checked it against a couple of real repos afterward and the paths held up.

(There was a much bigger version of this fix floated at one point - full recursive repo scanning, reason-objects on every field, a whole "reading order" feature. Didn't do any of that. Just fixed the actual bug. Wrote the bigger ideas down for later, didn't build them yet.)

---

## The pattern underneath most of this

Most of the actual bugs - the fake confidence percentage, the file hallucination, the word-count-as-clarity thing came from the same mistake in different spots: letting the AI make a call it had no real basis for, or making something deterministic that actually needed real judgment. The fix, every time, was the same: let the AI reason about stuff that genuinely needs reasoning (is this clear, does this fit their interest), and make everything checkable a hard fact computed in code (does this file exist, does the language match). Whenever those two got blurred together, that's where the bugs were.
