# Country map and profile

The atlas opens on renewable generation share. It has a MapLibre globe and an SVG flat map using D3's Natural Earth projection. The flat map renders without WebGL. If 3D graphics cannot initialize, the app selects the flat map and explains why the 3D control is unavailable.

Both views use the same observations, color stops, selection, and missing-data rules. Clicking a country updates the adjacent profile, which contains the selected value and observation period, a history chart, key energy indicators, generation mix, and comparison controls. The country picker provides access to profiles whose boundaries are too small or absent from the bundled map. At narrower widths the profile appears below the map.

## Reading colors

- The numeric legend includes the unit and displayed observation period. Latest mode explicitly allows different country dates.
- Percentage observations within 0–100 use a stable 0–100 domain. If a source value exceeds that range, the domain expands to retain the reported value and the legend flags the anomaly. The source data is not changed or silently clipped.
- Negative values and year-on-year growth use a symmetric diverging scale centered on zero.
- An optional square-root scale separates smaller nonnegative values in highly skewed datasets. Its numeric tick labels use the inverse transformation; it does not change country values.
- Missing data is slate gray; a reported zero uses the bottom of the numeric palette. Country selection uses a white outline and never replaces its data color.
- The coverage count is the number of statistical profiles with values, not a claim that every profile has a visible boundary polygon.

The profile history inserts explicit gaps for missing calendar years. Its key statistics use the selected observation period in original reported units. The generation mix is separately labeled with the latest year shared by all nine reported categories, independent of the indicator's selected period.

## Controls and accessibility

Use the globe/map toggle, country search, zoom, focus, world reset, and fullscreen controls. Drag the globe to rotate and the flat map to pan. Globe touch gestures support pinch zoom; the SVG flat map has explicit zoom buttons and keyboard plus/minus. Focus the flat map and use arrow keys to pan or Home to reset. Map interaction does not submit scenarios or change model inputs.

## Implementation and licensing

`components/map-state.ts` provides the shared numerical color scale. `components/globe.tsx` controls both renderers. `components/flat-map.tsx` renders the bundled Natural Earth boundaries with `d3-geo` 3.1.1 (ISC licence); `@types/d3-geo` 3.1.0 is a development-only dependency. Boundary data remains public domain. The D3 licence is preserved in `docs/licenses/d3-geo.txt`. No remote tile provider or API key is needed.

The development launcher translates supervised preview flags to Next.js flags. React's optional development debug socket is disabled because it can block hydration behind proxies that do not forward that socket; production rendering is unaffected.

## Verification

The frontend checks include real MapLibre expression evaluation, SVG/WebGL palette agreement, zero versus missing observations, negative domains, square-root labels, small fractional values, and missing-year chart gaps. Browser checks cover the flat map, country selection, recoloring, zoom, and the side panel. The preview browser has WebGL disabled, so its 3D globe could not be visually verified; it exercised the automatic flat-map fallback instead.
