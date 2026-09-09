import test, {after} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync, readFileSync, readdirSync, rmSync, writeFileSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {pathToFileURL} from 'node:url';
import ts from 'typescript';
import katex from 'katex';

// Compile just the content modules in an isolated temporary directory. This
// exercises the same source as the app without adding a test-only dependency,
// changing Next's import conventions, or relying on a generated .next tree.
const scratch = mkdtempSync(join(tmpdir(), 'switch-learn-test-'));
after(() => rmSync(scratch, {recursive: true, force: true}));
const contentDir = new URL('../components/learn/', import.meta.url);
for (const filename of readdirSync(contentDir).filter(f => f.endsWith('.ts'))) {
  const input = readFileSync(new URL(filename, contentDir), 'utf8');
  const output = ts.transpileModule(input, {
    fileName: filename,
    compilerOptions: {target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.ES2022},
  }).outputText.replace(/from '(\.\/[^']+)'/g, "from '$1.mjs'");
  writeFileSync(join(scratch, filename.replace(/\.ts$/, '.mjs')), output);
}
const load = name => import(pathToFileURL(join(scratch, name + '.mjs')).href);
const {lessons, parts, equationIndex, lessonText, readingMinutes, searchLessons, parseReadingState} = await load('course');
const {variables, glossary} = await load('reference');
const {sources} = await load('sources');
const {crf, finance, dispatch, weights, storage, cvar, uncertainty} = await load('calculations');
const close = (a, b, tolerance = 1e-7) => assert.ok(Math.abs(a - b) < tolerance, `${a} != ${b}`);

test('the curriculum has unique, ordered lessons with complete teaching components', () => {
  assert.equal(lessons.length, 44);
  assert.equal(parts.length, 10);
  assert.equal(new Set(lessons.map(l => l.id)).size, lessons.length);
  assert.equal(new Set(parts.map(p => p.id)).size, parts.length);
  let lastPart = -1;
  for (const l of lessons) {
    const partIndex = parts.findIndex(p => p.id === l.part);
    assert.ok(partIndex >= lastPart, `${l.id} is out of learning-path order`);
    lastPart = partIndex;
    assert.match(l.id, /^[a-z][a-z0-9-]+$/);
    assert.ok(l.title.length > 10 && l.summary.length > 30, l.id);
    assert.equal(l.goals.length, 3, l.id);
    assert.ok(l.sections.length >= 3, l.id);
    assert.ok(l.sections.every(s => s.title && s.paragraphs.length && s.paragraphs.every(Boolean)), l.id);
    assert.ok(l.worked.setup && l.worked.result && l.worked.steps.length >= 3, l.id);
    assert.ok(l.pitfalls.length >= 2, l.id);
    assert.equal(l.checks.length, 3, l.id);
    assert.deepEqual(l.checks.map(q => q.level), ['Foundation', 'Apply', 'Think deeper']);
    assert.ok(l.checks.every(q => q.question.length > 10 && q.answer.length > 25), l.id);
    assert.ok(lessonText(l).split(/\s+/).length >= 350, `${l.id} lacks depth`);
    assert.ok(readingMinutes(l) >= 4, l.id);
    assert.ok(l.sources.length >= 1 && l.sources.every(id => sources[id]), l.id);
    for (const s of l.sections) if (s.table) {
      assert.ok(s.table.rows.every(row => row.length === s.table.headers.length), l.id);
    }
  }
  for (const p of parts) assert.ok(lessons.some(l => l.part === p.id), p.id);
});

test('every displayed equation is valid KaTeX and has an interpretation', () => {
  assert.ok(equationIndex.length >= 50);
  for (const e of equationIndex) {
    assert.ok(e.explain.length >= 35, `${e.lesson}: ${e.tex}`);
    assert.doesNotThrow(() => katex.renderToString(e.tex, {
      displayMode: true, throwOnError: true, trust: false, strict: 'error', output: 'htmlAndMathml',
    }), `${e.lesson}: ${e.tex}`);
  }
});

test('the reference has complete, unique objects and no dangling lesson/source links', () => {
  assert.ok(variables.length >= 100);
  assert.equal(new Set(variables.map(v => v.object)).size, variables.length);
  const kinds = new Set(['Set / index', 'Input', 'Derived', 'Decision', 'Constraint', 'Objective', 'Registry']);
  for (const v of variables) {
    assert.ok(Object.values(v).every(value => typeof value === 'string' && value.length > 0), v.object);
    assert.ok(kinds.has(v.kind), v.object);
    assert.ok(sources[v.source], v.object);
    assert.ok(lessons.some(l => l.id === v.lesson), v.object);
  }
  for (const [term, definition, id] of glossary) {
    assert.ok(term && definition.length > 20 && lessons.some(l => l.id === id), term);
  }
  for (const source of Object.values(sources)) assert.equal(new URL(source.url).protocol, 'https:');
});

test('core and Kenya citations are pinned and key module boundaries are explicit', () => {
  for (const source of Object.values(sources)) {
    if (/github.com\/(switch-model\/switch\/|NotEleven\/)/.test(source.url)) {
      assert.match(source.url, /\/(blob|tree)\/[0-9a-f]{40}(\/|$)/);
    }
  }
  assert.match(lessonText(lessons.find(l => l.id === 'kenya-hydrogen')), /do not|does not|not load|absent/i);
  assert.match(lessonText(lessons.find(l => l.id === 'external-demand')), /optional/i);
  assert.match(lessonText(lessons.find(l => l.id === 'two-stage')), /non-anticipativity/i);
  assert.match(lessonText(lessons.find(l => l.id === 'time-weights')), /duration/i);
  assert.ok(variables.some(v => v.object === 'BuildStorageEnergy[g,b]' && v.units === 'MWh'));
});

test('course search includes body text and requires all terms regardless of case', () => {
  assert.equal(searchLessons('   ').length, lessons.length);
  assert.ok(searchLessons('non-anticipativity').some(l => l.id === 'two-stage'));
  assert.ok(searchLessons('KENYA hydrogen').some(l => l.id === 'kenya-hydrogen'));
  for (const l of searchLessons('Kenya hydrogen')) {
    assert.match(lessonText(l), /kenya/i);
    assert.match(lessonText(l), /hydrogen/i);
  }
  assert.deepEqual(searchLessons('this-term-is-not-in-the-course'), []);
});

test('reading state is resilient to missing, invalid, outdated and duplicated data', () => {
  const initial = {lesson: lessons[0].id, completed: []};
  for (const raw of [null, '', '{bad json', 'null', '42', '"text"', '[]']) {
    assert.deepEqual(parseReadingState(raw), initial);
  }
  assert.deepEqual(parseReadingState(JSON.stringify({lesson: 'storage', completed: ['storage', 'storage', 'gone', 1, null]})), {lesson: 'storage', completed: ['storage']});
  assert.deepEqual(parseReadingState(JSON.stringify({lesson: 'missing', completed: 'not an array'})), initial);
  assert.deepEqual(parseReadingState(JSON.stringify({lesson: 'storage', completed: ['annualization']})), {lesson: 'storage', completed: ['annualization']});
});

test('capital recovery handles zero interest and the worked financing example', () => {
  close(crf(0, 20), .05);
  close(crf(.07, 20), .094392925743);
  close(finance(1e6, .07, 20, 20000).total, 114392.925743, .00001);
  close(crf(1e-12, 20), .05, 1e-10);
  assert.throws(() => crf(.07, 0));
  assert.throws(() => finance(-1, .07, 20, 0));
  assert.throws(() => crf(NaN, 20));
});

test('dispatch obeys merit order, power balance and capacity limits', () => {
  assert.deepEqual(dispatch(100, 80, 50), {a: 80, b: 20, shortage: 0, cost: 5200});
  assert.deepEqual(dispatch(140, 80, 50), {a: 80, b: 50, shortage: 10, cost: 18200});
  assert.deepEqual(dispatch(0, 80, 50), {a: 0, b: 0, shortage: 0, cost: 0});
  const reversed = dispatch(100, 80, 50, 100, 40);
  assert.equal(reversed.b, 50);
  assert.equal(reversed.a, 50);
  assert.equal(reversed.cost, 7000);
  for (const demand of [0, 50, 80, 100, 130, 250]) {
    const r = dispatch(demand, 80, 50);
    close(r.a + r.b + r.shortage, demand);
    assert.ok(r.a <= 80 && r.b <= 50 && r.shortage >= 0);
  }
  assert.throws(() => dispatch(100, 80, 50, 40, 100, 10));
});

test('physical time and annual/period weights remain distinct', () => {
  assert.deepEqual(weights(4, 90.25, 1, 50, 50), {duration: 4, period: 361, annual: 361, energy: 18050, cost: 902500});
  const multi = weights(4, 90.25 * 5, 5, 50, 50);
  assert.equal(multi.duration, 4);
  assert.equal(multi.period, 1805);
  assert.equal(multi.annual, 361);
  assert.equal(multi.energy, 18050);
  assert.throws(() => weights(4, 90, 0, 50, 50));
});

test('storage charges with the pinned efficiency convention and exposes invalid schedules', () => {
  const r = storage(20, 80, 10, 2, 8, 3, .9);
  close(r.afterCharge, 38);
  close(r.final, 14);
  close(r.loss, 2);
  assert.equal(r.feasible, true);
  assert.equal(storage(90, 80, 0, 1, 0, 1, 1).feasible, false);
  assert.equal(storage(20, 30, 10, 2, 0, 1, .9).feasible, false);
  const depleted = storage(0, 80, 0, 1, 20, 1, .9);
  assert.equal(depleted.final, -20);
  assert.equal(depleted.feasible, false);
  assert.throws(() => storage(0, 80, 0, 1, 0, 1, 1.01));
});

test('CVaR weights probability mass, including a partial tail scenario', () => {
  close(cvar([100, 200, 500], [.5, .3, .2], .75), 440);
  close(cvar([100, 200, 500], [.5, .3, .2], 0), 210);
  close(cvar([100, 200, 500], [.5, .3, .2], .99), 500);
  close(cvar([-100, 20], [.5, .5], .5), 20);
  close(cvar([100, 1000], [1, 0], .95), 100);
  assert.throws(() => cvar([1, 2], [.5, .5], 1));
  assert.throws(() => cvar([1, 2], [.2, .2], .5));
  assert.throws(() => cvar([1], [.5, .5], .5));
});

test('the two-stage illustration reproduces the hand-calculated information benchmarks', () => {
  const r = uncertainty(.5, 50, 200, .75, 0);
  assert.equal(r.selected.capacity, 100);
  assert.equal(r.evCapacity, 75);
  close(r.rp, 5000);
  close(r.eev, 6250);
  close(r.ws, 3750);
  close(r.vss, 1250);
  close(r.evpi, 1250);
  close(r.selected.cvar, 5000);
  assert.equal(uncertainty(0, 50, 200, .75, 0).selected.capacity, 50);
  assert.equal(uncertainty(1, 50, 200, .75, 0).selected.capacity, 100);
  assert.equal(uncertainty(.5, 300, 200, .75, 0).selected.capacity, 0);
});

test('risk-neutral benchmarks remain separate from risk-aversion controls', () => {
  const neutral = uncertainty(.1, 50, 200, .75, 0);
  const averse = uncertainty(.1, 50, 200, .75, 1);
  assert.equal(neutral.selected.capacity, 50);
  assert.equal(averse.selected.capacity, 100);
  for (const key of ['rp', 'eev', 'ws', 'vss', 'evpi']) close(neutral[key], averse[key]);
});

test('stochastic identities and exact breakpoint optimum hold across a parameter grid', () => {
  for (const probability of [0, .01, .1, .5, .99, 1]) {
    for (const capital of [10, 50, 200, 300]) {
      for (const alpha of [0, .75, .99]) {
        for (const risk of [0, .5, 1]) {
          const r = uncertainty(probability, capital, 200, alpha, risk);
          assert.ok(r.ws <= r.rp + 1e-7 && r.rp <= r.eev + 1e-7);
          assert.ok(r.selected.cvar >= r.selected.expected - 1e-7);
          assert.ok(r.curve.every(p => r.selected.objective <= p.riskObjective + 1e-7));
          close(r.rp + r.vss, r.eev);
          close(r.ws + r.evpi, r.rp);
        }
      }
    }
  }
});
