# Frontend Development Guidelines

> Follow native Sub2API Vue 3 conventions for admin patches and modular ES scripts for embedded evaluation pages.

---

## Overview

This repository touches two distinct frontend surfaces across its plugin submodules.
First, plugin patches extend the upstream Sub2API Vue 3, TypeScript, and Tailwind CSS administrator application.
Second, the evaluation plugin serves an embedded standalone web interface under `/codex-eval` inside an administrator iframe.
Use [API Key Account Usage](../backend/api-key-quota.md) for the quota extension cross-layer contract.
Use [Administrator Evaluation](../backend/runtime-installation.md) and [Native Candy Inspection](../backend/native-inspection.md) for evaluation and inspection page contracts.
Use [Quality and Commits](../backend/quality-guidelines.md) for the default build and focused verification rules.

---

## Guidelines Index

| Guide | Description | Status |
| --- | --- | --- |
| [API Key Account Usage](../backend/api-key-quota.md) | Script editor, draft tests, native quota fields, cells, and refresh | Current |
| [Directory Structure](./directory-structure.md) | Patched Vue paths, embedded evaluation assets, and flat test placement | Current |
| [Component Guidelines](./component-guidelines.md) | Vue 3 script-setup patterns, shared editors, cells, and DOM renderers | Current |
| [Hook Guidelines](./hook-guidelines.md) | Composition utilities, request queues, and stale-response guards | Current |
| [State Management](./state-management.md) | Component refs, usage caches, embedded page state, and session secrets | Current |
| [Quality Guidelines](./quality-guidelines.md) | Build verification, i18n parity, error visibility, and review checks | Current |
| [Type Safety](./type-safety.md) | TypeScript interfaces, extra-field guards, and JSON payload contracts | Current |

---

## Pre-Development Checklist

1. Read the active task requirements and affected backend and frontend specs before editing.
2. Inspect the target patch hunks in `plugins/<name>/patches/*.patch` and tests in `plugins/<name>/tests/`.
3. Reuse existing native components, formatters, and refresh utilities before adding new helpers.
4. Keep English and Chinese locale files synchronized whenever you add or change user-facing text.
5. Verify that `python3 scripts/build.py` passes `pnpm run check:i18n`, `vue-tsc --noEmit`, `vite build`, and staged tests.

---

**Language**: Write all specification files in **English** following the [documentation rules](../backend/index.md#documentation-rules).
