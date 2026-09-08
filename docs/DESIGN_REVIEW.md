# Research studio redesign · 8 September 2026

## Direction

Liquid Glass-inspired navigation, not glass behind every number. Warm ivory surfaces, ocean blue actions and globe, amber assumptions, green status, and violet teaching/comparison accents. Solid reading surfaces preserve legibility in tables, equations and source notes. No imagery or decorative chart implies a model result.

The shared visual layer is `app/studio.css`, loaded after the existing styles. Overview composition and model illustrations live in `app/page.tsx`; atlas/globe palettes and learning selection semantics remain in their components. Model inputs, calculations, datasets and API contracts are unchanged.

## Verification

- Production `npm run build`: passed, including TypeScript and static export.
- `node --test tests/*.test.mjs`: all 12 passed. Python suite: all 21 passed during this redesign.
- Chrome reviewed at 1440 × 1000 and 390 × 844; overview width checks also passed at 768 and 1024. No document-level horizontal overflow in checked screens. Wide scientific tables and long equations scroll within their own containers.
- Reviewed overview, model library (including expanded Kenya modules), scenario creation/editor, completed results, compatible-run comparison, all four atlas views, learning and workspace/backups.
- Created and solved two tutorial scenarios and one separate stochastic scenario in `artifacts/design-qa/workspace`, served on a separate QA port. Tutorial objectives were 126750492.10678375 and 152435913.2644603; the stochastic run was optimal at 33464000 USD/year. No Kenya solve was started.
- Checked result charts, logs, input snapshot and file links. Comparison excludes the incompatible stochastic model. No backup/restore was performed against the user's workspace.
- Verified mobile navigation focus wrapping, Escape dismissal, focus restoration and inert background; verified modal initial focus and Escape focus restoration. Learning tabs wrap into a two-by-two grid on phones. Reduced-motion and reduced-transparency CSS fallbacks are provided.
- Caught and fixed a production CSS prefix-order issue: standard `backdrop-filter` now survives optimization. Computed Chrome styles confirm 20px header blur and 26px sidebar blur.
- Production health remained OK with a live worker, one existing scenario and zero runs. User data, source years, units and missing-data labels were preserved.

## Globe follow-up and hosted edition

- Reworked the globe with a larger responsive camera fit, atmospheric rim, hover country identification, dedicated zoom/focus/reset controls and actual browser fullscreen. Page scrolling no longer zooms the map accidentally; pinch and explicit controls remain available. Resize observation keeps the canvas fitted to its container.
- Verified country focus, fullscreen entry/exit and 390px phone rendering in Chrome. Preserved numeric map colors and their missing-data category. Corrected case-sensitive infrastructure technology colors and removed unrelated GEM attribution from maps without infrastructure data.
- Vercel builds use an explicit atlas/learning edition, starting in the atlas with no local-API polling. Local builds retain the full workbench. The deploy ignore list excludes the worker, backend, sources, workspace, backups and QA artifacts.
- Atmosphere properties follow the [MapLibre sky specification](https://maplibre.org/maplibre-style-spec/sky/); no satellite imagery, terrain or live-weather accuracy is implied.

## Remaining verification limits

This is targeted Chrome visual/interaction QA, not an exhaustive accessibility certification or a cross-browser/device lab. Safari, Firefox, real touch hardware and every atlas indicator combination were not tested. A non-failing WebGL driver performance warning appeared during map inspection. Existing Node module-type and Python dependency deprecation warnings remain. The full Kenya optimal solve remains unverified.
