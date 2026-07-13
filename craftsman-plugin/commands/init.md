---
description: Detect this project's tech stack (or ask, if none is detected) and propose a CLAUDE.md/KNOWN_ISSUES.md scaffold — shows the exact content and asks for confirmation before writing anything.
argument-hint: (no arguments — runs against the current project)
---

Scaffold project-level conventions for the current project. This command **never writes a file
without first showing its exact proposed content and getting explicit confirmation** — that rule
applies on every run, not just the first.

## Step 1 — Detect the stack

Use Glob to check for marker files at the project root, and one level deep for monorepo
subfolders. Match against this table:

| Marker file(s) | Stack | Default build/verify command |
|---|---|---|
| `build.gradle.kts`/`build.gradle` + `AndroidManifest.xml` | Android (Kotlin/Java) | `.\gradlew.bat assembleDebug`, `.\gradlew.bat testDebugUnitTest` |
| `pom.xml` with a `spring-boot` dependency | Spring Boot (Maven) | `mvn compile -q`, `mvn test -q` |
| `build.gradle(.kts)` with `org.springframework.boot` | Spring Boot (Gradle) | `.\gradlew.bat compileJava`, `.\gradlew.bat test` |
| `pom.xml` (no Spring) | Java (Maven) | `mvn compile -q` |
| `build.gradle(.kts)` (no Android/Spring) | Java/Kotlin (Gradle) | `.\gradlew.bat build` |
| `package.json` + `package-lock.json` | Node (npm) | `npm run build`, `npm test` |
| `package.json` + `yarn.lock` | Node (Yarn) | `yarn build`, `yarn test` |
| `package.json` + `pnpm-lock.yaml` | Node (pnpm) | `pnpm build`, `pnpm test` |
| `tsconfig.json` alongside any of the above | + TypeScript | `tsc --noEmit` as an added check |
| `next.config.*` | Next.js (within Node) | `npm run build` (Next-aware) |
| `angular.json` | Angular | `ng build`, `ng test` |
| `pyproject.toml` with `[tool.poetry]` | Python (Poetry) | `poetry run pytest` |
| `pyproject.toml` (no Poetry) / `requirements.txt` | Python (pip/venv) | `pytest` |
| `manage.py` | Django | `python manage.py test` |
| `Cargo.toml` | Rust | `cargo build`, `cargo test` |
| `go.mod` | Go | `go build ./...`, `go test ./...` |
| `pubspec.yaml` | Flutter/Dart | `flutter analyze`, `flutter test` |
| `*.csproj` / `*.sln` | .NET/C# | `dotnet build`, `dotnet test` |
| `Gemfile` | Ruby | `bundle exec rspec` |
| `composer.json` | PHP | `composer install`, `vendor/bin/phpunit` |
| `Package.swift` | Swift | `swift build`, `swift test` |
| `CMakeLists.txt` | C/C++ (CMake) | `cmake --build build` |
| `Makefile` (no CMake) | C/C++ / generic | `make`, `make test` |
| `deno.json`/`deno.jsonc` | Deno | `deno check`, `deno test` |
| `mix.exs` | Elixir | `mix test` |
| `Dockerfile` only, no other markers | Containerized/unknown | `docker build .` |
| Two or more unrelated markers at the root | Monorepo/mixed | don't guess — ask which subproject/root command applies |

## Step 2 — Resolve the real command (existing projects only)

If markers were found, don't stop at the table's default. Look for the command actually used in
practice, in priority order:
1. CI config (`.github/workflows/*.yml`, `azure-pipelines.yml`, `.gitlab-ci.yml`, etc.)
2. Documented command in `README.md` or `CONTRIBUTING.md`
3. `package.json` `scripts` block (or the equivalent: Makefile targets, `pyproject.toml` tool
   config)
4. The table's default command, only as a last resort

This avoids proposing `npm test` when the project actually runs a custom script name.

Also check for an existing issue-tracking file under a different name (`TODO.md`, `ISSUES.md`,
`BACKLOG.md`) before proposing a new `KNOWN_ISSUES.md` — if one exists, ask whether to adopt it
for the `logging-tradeoffs` convention instead of creating a duplicate.

## Step 3 — New/empty project (no markers found)

Don't guess and don't scaffold project files — don't invent a `package.json`/`pyproject.toml`,
that's out of scope unless explicitly requested. Instead, ask the user directly which stack they
intend to use, offering the table's stack list as options (use AskUserQuestion or equivalent).
Proceed with whatever they choose to build the `CLAUDE.md` content.

## Step 4 — Propose, then ask

Show the user exactly what would be created:
- A project `CLAUDE.md` — **only if none already exists** — pre-filled with the resolved
  build/verify command(s). If a `CLAUDE.md` already exists, do not overwrite it; instead offer to
  append the detected command as a note, and still ask first.
- A blank `KNOWN_ISSUES.md` using this template (skip if an equivalent file was adopted in Step 2):
  ```
  ## <date> — <short title>
  - What changed / what shortcut was taken:
  - Ceiling (when this breaks):
  - Upgrade trigger (what to do when it's hit):
  - Status: open | resolved (<date>, <how>)
  ```
- **Graphify status** — detect what's available, then branch. Detection is read-only:
  ```powershell
  $graphifyCli   = Get-Command graphify -ErrorAction SilentlyContinue   # CLI on PATH (OS-agnostic)
  $graphifySkill = @(Get-ChildItem "$HOME\.claude\skills" -Directory -Filter 'graphify*' -ErrorAction SilentlyContinue).Count -gt 0
  $graphExists   = Test-Path 'graphify-out\graph.json'
  ```
  Probe the CLI/skill rather than a hardcoded folder name — graphify ships OS-specific skill
  variants (`graphify-windows`, etc.), so match any `graphify*` skill folder, not just `graphify`.
  Then branch:
  - **Graph already built** (`$graphExists`): note in the proposed `CLAUDE.md` that graphify is
    active — graph-aware bug investigation and query-first codebase navigation are on. No install,
    no build prompt.
  - **graphify available, no graph** (`$graphifyCli -or $graphifySkill`): add a note to the
    proposed `CLAUDE.md` that running `graphify .` (CLI) or `/graphify .` (skill) would build the
    graph and enable graph-aware debugging. **Do not run the build automatically** — building a
    graph is a real side effect the user triggers themselves.
  - **graphify missing** (neither CLI nor skill): recommend it — it powers recurring-bug dedup
    *and* query-first codebase navigation. Show the install command (`uv tool install graphifyy`
    if `uv` is on PATH, else `pip install graphifyy`) and **offer to run it, executing only on
    explicit yes** — the same propose-then-ask rule this command uses for file writes. If the
    graphify *skill* is also absent, point the user at it for `/graphify` full builds rather than
    offering to run something. Never auto-install.

**Do not write anything until the user confirms.** Nothing in this command writes a file before
this explicit confirmation step, on any run.

## Step 5 — Write only on explicit yes

Write exactly what was shown and confirmed. Report what was created (or appended) and where.
