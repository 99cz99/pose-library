# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A Telegram Mini App + pose-reference toolchain, two mostly-independent halves:

1. **`index.html`** — single-file frontend embedded in Telegram: a booru-style prompt tag picker plus skeleton / depth-map image galleries. No build step; served by GitHub Pages from `master`.
2. **Python scripts** — standalone ComfyUI helpers that generate ControlNet pose inputs (skeleton / depth / canny / lineart / openpose) and workflow JSON, then verify them against a running ComfyUI.

## Commands

No build / lint / test. Run scripts directly:

- `python gen_<x>.py` — generate images or workflow JSON, writing to `E:\ComfyUI_windows_portable\ComfyUI\...` (outside this repo).
- `python verify_<x>.py` — submit a workflow to ComfyUI (`POST http://127.0.0.1:8188/prompt`, then poll `/history/{id}`); requires ComfyUI running.
- `blender_pose.py` — run *inside* Blender (needs `bpy` + a rigged FBX mesh imported), renders an orthographic pose + depth map.
- Deploy: `git push origin master`. **GitHub is unreachable without the proxy** — use `git -c http.proxy=http://127.0.0.1:7897 -c https.proxy=http://127.0.0.1:7897 push origin master`, otherwise it hangs.

## Architecture

### Frontend (`index.html`)

Single file, no build step; served by GitHub Pages from `master`.

- **Navigation** — a fixed bottom `.tabbar` switches three `.tab-page` sections via `switchTab(name)` (active tab persisted in `localStorage` `pg_tab`): `#tab-prompt` (标签 — tag picker), `#tab-gallery` (图库 — galleries), `#tab-library` (我的 — preset management).
- **Output drawer** — the prompt result (warnings / output-format / selected-tags / import / pos-neg textareas) is a bottom slide-up `.result-bar`, hidden by default and toggled by the floating `#output-fab` button + `.backdrop` (`openDrawer()`/`closeDrawer()`). It's an overlay, not a tab.

Data & rendering:

- **Tag library** — `CATEGORIES` array; each category renders as a `<details>` of `{zh, en}` chips. A category may contain subgroup header objects `{_h:"名称"}` that render as a `.subgroup-label` (used by `服装`: 校服 / 职业制服 / 泳装内衣). The load-time tag sort skips categories containing `_h`, and `buildCategories` / `buildTagIndex` / `selectAllNegative` skip `_h` entries. Add a tag = add one `{zh, en}` line (or `{_h:"…"}` for a subgroup header).
- **Presets** — built-in `OUTFITS` / `TEMPLATES` / `CHARACTERS` + `custom*` arrays persisted in `localStorage` (`pg_*` keys). `render*Section()` builds each section; quick-pick sections (收藏 / LoRA 触发词) prepend into `#categories`, management sections (预设 / 快捷模板 / 角色预设 / 服装套装 / 添加标签) prepend into `#library-sections`. `apply*()` applies a preset (character/outfit append; template clears-and-sets).
- **Auth gate** — `AUTHORIZED_IDS`, client-side only (soft gate; the skeleton/depth PNGs are public static files).
- **Galleries** — inlined `SKELETON_DATA` / `DEPTH_DATA` arrays (entry `{file, label, w, h}`; skeleton also has `pose` for the JSON download).

Adding content (from `README.md`):

- Skeleton image → drop PNG in `skeletons/` and register in `SKELETON_DATA` in `index.html` (the README also mentions `skeleton_manifest.json`, but the frontend actually reads the inlined `SKELETON_DATA` — data is inlined to avoid fetch hanging inside the Mini App).
- Depth image → drop PNG in `depth/` and add to `DEPTH_DATA` in `index.html`.
- Authorize a user → add their Telegram numeric ID to `AUTHORIZED_IDS`.

### Python scripts

- `gen_*.py` build things (PIL skeleton images, ComfyUI workflow JSON, pose/depth images). `verify_*.py` submit + poll the same workflow against a live ComfyUI.
- Hardcoded checkpoint `Illustrious-XL-v2.0.safetensors`; ComfyUI API at `127.0.0.1:8188`; outputs under `E:\ComfyUI_windows_portable\ComfyUI\`.

## Gotchas

- Git commits are Chinese, `feat:` / `fix:` prefixed (see `git log`).
- `index.html`'s tag picker is an evolution of `D:\kohyass\kohya_ss\prompt_generator.html` — same code lineage, separate repos; changes in one don't affect the other.
- The Python scripts are one-off utilities; they mutate `E:\ComfyUI_windows_portable\...`, not this repo.
