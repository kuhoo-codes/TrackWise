# Contributing to TrackWise

Thank you for your interest in contributing to **TrackWise**! This document outlines our guidelines and best practices to help you make high-quality contributions.

---

## 🚀 About TrackWise

TrackWise is a dynamic, timeline-based portfolio and achievement tracker. It helps users chronologically organize projects, experiences, milestones, and reflections, providing a richer, more accurate representation of their professional journey.

---

## 🛠️ Tech Stack

- **Backend:** FastAPI, Ruff (linter)
- **Database:** PostgreSQL
- **Caching/Background Tasks:** Redis
- **Frontend:** React.js
- **Media Storage:** Supabase
- **AI Wrapper (Planned):** OpenAI (GPT-4) via FastAPI

---

## 📝 Commit Discipline

- **Each commit must be a minimal, coherent idea.**
- **Tests must pass** in every commit.
- **No partial or broken user flows.**
- **Each commit should be safe to deploy** (or clearly marked otherwise).
- **Error handling and TODOs** should be included with relevant logic.

---

### Commit Message Format

**Prefix:** Lowercase, 1–2 words indicating the app area (e.g., `timeline`, `editor`, `api`, `auth`, `docs`, etc.).

**Summary:** Imperative, concise description.

**Examples:**
- `timeline: Add support for zooming to a date range.`
- `editor: Improve UX of skill tagging.`
- `api: Validate uploaded certificate file types.`

**Optional Description:** Motivation, summary, implementation notes, trade-offs, related issues.

---

## 🌿 Branch Naming Convention

Format: `<type>/<issue-number>-<short-description>`

**Types:** `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `style`, `ci`

**Examples:**
- `feat/312-add-scraper-for-github`
- `fix/128-resume-formatting-issue`
- `docs/215-update-readme-with-setup-guide`

---

## ✅ Pull Request Checklist

- [ ] Follow branch naming convention.
- [ ] Clear, descriptive PR title.
- [ ] Reference the issue (`Fixes #<issue_number>`).
- [ ] Concise, informative description.
- [ ] Code follows structure and style guide.
- [ ] Includes tests or a testing plan.
- [ ] Passes linters, formatting, and build checks.
- [ ] Tested locally.
- [ ] Commits are organized and meaningful.

---

## ✍️ PR Description Template

```markdown
### 🔧 What’s Changed

<!-- A brief summary of what this PR does -->

### 📌 Related Issue

Fixes #<issue-number>

### ✅ Checklist

- [ ] Follow the correct **branch naming convention**.
- [ ] Include a **clear and descriptive title**.
- [ ] Reference the issue using `Fixes #<issue_number>`.
- [ ] Provide a concise but informative **description** of what was changed and why.
- [ ] Ensure your code:
    - [ ] Follows the project’s **folder structure and style guide**.
    - [ ] Includes **tests** or has a clear plan for testing (if applicable).
    - [ ] Passes **linters**, **formatting**, and **build checks**.
- [ ] Test your changes **locally** before submitting.
- [ ] Squash or organize commits meaningfully using `git rebase -i`.
```

---

## 📓 Best Practices

- Keep PRs focused and relevant.
- Group logically related changes together.
- Avoid unrelated refactors in the same PR.
- Write clear, actionable commit messages.
- Review your own code before requesting review.

---

Thank you for helping make TrackWise better!
