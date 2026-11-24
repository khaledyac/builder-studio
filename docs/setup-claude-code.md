# Working on builder-studio with Claude Code

Claude Code gets everything it needs from the repo. Don't give it the deck, the whiteboard or the overview file. The repo already holds that content in `docs/architecture.md` and `docs/plan/`.

## Set up once

1. **Repo.** `builder-studio` is on GitHub with the plan package at its root.
2. **Start Claude Code at the root.** Clone the repo and run `claude` from the root folder. Claude Code then loads:
   - `CLAUDE.md`, which imports `AGENTS.md`. The rules, the stack and the way to work a step come from there. See the [memory docs](https://docs.claude.com/en/docs/claude-code/memory).
   - The 9 project skills in `.claude/skills/<skill-name>/SKILL.md`. They apply to this project only. See the [skills docs](https://code.claude.com/docs/en/skills.md).
   - The tracker settings in `docs/agents/`, which `AGENTS.md` points to.
3. **Tools.**
   - Install the GitHub CLI (`gh`) and log in. The skills use it to create issues.
   - Step 01 also needs uv, Task, Node and Docker.

## For each step

- **Start a fresh session in plan mode.** Press `Shift+Tab` (or `Alt+M` in some configurations) to cycle permission modes, or launch with `claude --permission-mode plan`. Approve the plan, then let it build. See the [interactive mode docs](https://code.claude.com/docs/en/interactive-mode.md).
- **First prompt:**

  ```text
  Read docs/plan/steps/01-platform-monorepo.md and the
  architecture sections it links. Write a short plan first.
  Then implement the step test-first, staying in scope. Stop
  when every acceptance criterion is met, and show how each
  one is met in the pull request.
  ```

- **One step = one branch = one pull request.** Review each one against its acceptance criteria.
- **Size L steps:** type `/to-tickets`, then `/implement-spec`, which builds the tickets with subagents working in parallel. Claude can't start these two skills on its own, because they set `disable-model-invocation: true`.

## Steps that touch builder-kit

Steps 10, 11, 12 and 21 work in `builder-kit`. Start Claude Code in `builder-studio` with:

```bash
claude --add-dir ../builder-kit
```

This grants file access to `builder-kit`. It doesn't load `.claude/` configuration from there, so the rules and skills still come from `builder-studio`. See the [CLI docs](https://code.claude.com/docs/en/cli).

## Code review

The project's `.claude/skills/code-review` replaces Claude Code's bundled `/code-review`. The replacement checks code against both `AGENTS.md` and the step's spec.
