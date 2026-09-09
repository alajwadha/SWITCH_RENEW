import type {Country, Observation} from './types.ts';

export type MapView = 'globe' | 'flat';
export type ScaleMode = 'linear' | 'sqrt';
export type ColorScale = {
  stops: {value: number; color: string}[];
  mode: ScaleMode;
  diverging: boolean;
  count: number;
};
export const NO_DATA_COLOR = '#344557';
const sequential = ['#46327e', '#365c9e', '#238a8d', '#64bd73', '#f5df53'];
const diverging = ['#4059ad', '#8fb7da', '#f3f0e8', '#efa36f', '#bb452c'];

/** Missing observations never enter the domain; a reported zero always does. */
export function makeColorScale(values: unknown[], options: {mode?: ScaleMode; percentage?: boolean; diverging?: boolean} = {}): ColorScale {
  const valid = values.filter((v): v is number => typeof v === 'number' && Number.isFinite(v));
  const signed = options.diverging || valid.some(v => v < 0);
  const mode = signed ? 'linear' : options.mode || 'linear';
  const maximum = valid.length ? Math.max(...valid) : 0;
  const minimum = valid.length ? Math.min(...valid) : 0;
  const upper = signed ? Math.max(Math.abs(minimum), Math.abs(maximum)) || 1
    : options.percentage && maximum <= 100 ? 100 : maximum > 0 ? maximum : 1;
  const lower = signed ? -upper : 0;
  return {
    count: valid.length, mode, diverging: Boolean(signed),
    stops: (signed ? diverging : sequential).map((color, i) => ({
      color, value: lower + (upper - lower) * (mode === 'sqrt' ? (i / 4) ** 2 : i / 4),
    })),
  };
}

/** The legend and the renderer use exactly these stops, including square-root spacing. */
export function colorExpression(countries: Country[], key: string, scale: ColorScale): unknown[] {
  const values = Object.fromEntries(countries.flatMap(c => {
    const value = c.indicators[key]?.value;
    return typeof value === 'number' && Number.isFinite(value) ? [[c.iso3, value]] : [];
  }));
  const value: unknown[] = ['to-number', ['get', ['get', 'iso3'], ['literal', values]], 0];
  return ['case', ['has', ['get', 'iso3'], ['literal', values]],
    ['interpolate', ['linear'], scale.mode === 'sqrt' ? ['sqrt', ['max', 0, value]] : value,
      ...scale.stops.flatMap(s => [scale.mode === 'sqrt' ? Math.sqrt(s.value) : s.value, s.color])], NO_DATA_COLOR];
}

export function numericObservation(o?: Observation): number | null {
  return typeof o?.value === 'number' && Number.isFinite(o.value) ? o.value : null;
}

/** SVG and WebGL share the same RGB interpolation and scale stops. */
export function colorAt(value: unknown, scale: ColorScale): string {
  if (typeof value !== 'number' || !Number.isFinite(value)) return NO_DATA_COLOR;
  const transform = (v: number) => scale.mode === 'sqrt' ? Math.sqrt(Math.max(0, v)) : v;
  const v = transform(value), stops = scale.stops;
  if (v <= transform(stops[0].value)) return stops[0].color;
  if (v >= transform(stops.at(-1)!.value)) return stops.at(-1)!.color;
  const i = stops.findIndex(s => transform(s.value) >= v);
  const lo = stops[i - 1], hi = stops[i], t = (v - transform(lo.value)) / (transform(hi.value) - transform(lo.value));
  const rgb = (hex: string) => [1, 3, 5].map(start => parseInt(hex.slice(start, start + 2), 16));
  const a = rgb(lo.color), b = rgb(hi.color);
  return '#' + a.map((channel, j) => Math.round(channel + (b[j] - channel) * t).toString(16).padStart(2, '0')).join('');
}

/** Include missing calendar years so a line chart cannot bridge unpublished years. */
export function chartObservations(observations: Observation[], frequency?: string): Observation[] {
  const sorted = [...observations].sort((a, b) => String(a.period || a.year || '').localeCompare(String(b.period || b.year || '')));
  if (frequency !== 'annual' || !sorted.length) return sorted;
  const years = sorted.map(o => o.year).filter((y): y is number => y != null && Number.isInteger(y));
  if (!years.length || Math.max(...years) - Math.min(...years) > 500) return sorted;
  const byYear = new Map(sorted.map(o => [o.year, o]));
  return Array.from({length: Math.max(...years) - Math.min(...years) + 1}, (_, i) => {
    const year = Math.min(...years) + i;
    return byYear.get(year) || {year, period: String(year), value: null};
  });
}
