'use client';

import {memo, useEffect, useMemo, useRef, useState} from 'react';
import katex from 'katex';
import {motion, useReducedMotion} from 'motion/react';
import {ArrowLeft, ArrowRight, ArrowUpRight, BookOpen, Check, CheckCircle2, ChevronDown, ChevronRight, Clock3, FlaskConical, List, Search, ShieldCheck, Sigma, X} from 'lucide-react';
import {equationIndex, LEARN_STORAGE_KEY, lessons, parseReadingState, parts, readingMinutes, searchLessons} from './learn/course';
import type {ReadingState} from './learn/course';
import {glossary, variables} from './learn/reference';
import {sources} from './learn/sources';
import {labList, LessonLab} from './learn/labs';
import type {Equation, Lesson, Section} from './learn/types';

type View = 'course' | 'labs' | 'reference' | 'sources';
const views = [
  {id: 'course', label: 'The course', icon: BookOpen},
  {id: 'labs', label: 'Interactive labs', icon: FlaskConical},
  {id: 'reference', label: 'Model reference', icon: Sigma},
  {id: 'sources', label: 'Sources & scope', icon: ShieldCheck},
] as const;
const matches = (text: string, query: string) => query.trim().toLowerCase().split(/\s+/).every(term => text.toLowerCase().includes(term));

const MathBlock = memo(function MathBlock({tex, explain}: Equation) {
  const html = useMemo(() => katex.renderToString(tex, {
    displayMode: true, throwOnError: false, trust: false, output: 'htmlAndMathml',
  }), [tex]);
  return <figure className="learn-equation"><div className="equation" dangerouslySetInnerHTML={{__html: html}}/><figcaption>{explain}</figcaption></figure>;
});

function SourceLink({id}: {id: string}) {
  const source = sources[id];
  return <a href={source.url} target="_blank" rel="noreferrer">{source.title}<ArrowUpRight size={14} aria-hidden="true"/></a>;
}

function SectionContent({section, index}: {section: Section; index: number}) {
  return <section className="learn-section" id={`learn-section-${index}`}>
    <h3>{section.title}</h3>
    {section.paragraphs.map((p, i) => <p key={i}>{p}</p>)}
    {section.equations?.map((eq, i) => <MathBlock key={i} {...eq}/>)}
    {section.points && <ul>{section.points.map((p, i) => <li key={i}>{p}</li>)}</ul>}
    {section.code && <pre tabIndex={0} aria-label={`Code example: ${section.title}`}><code>{section.code}</code></pre>}
    {section.table && <div className="learn-table-wrap" tabIndex={0} role="region" aria-label={section.title}><table>
      <thead><tr>{section.table.headers.map(h => <th scope="col" key={h}>{h}</th>)}</tr></thead>
      <tbody>{section.table.rows.map((r, i) => <tr key={i}>{r.map((v, j) => <td key={j}>{v}</td>)}</tr>)}</tbody>
    </table></div>}
  </section>;
}

function Practice({lesson}: {lesson: Lesson}) {
  return <section className="learn-practice" aria-labelledby="practice-heading">
    <span className="learn-kicker">RETRIEVE · APPLY · QUESTION</span><h3 id="practice-heading">Check your understanding</h3>
    <p>Try an answer in your own words before revealing the explanation. These are practice prompts, not a scored assessment.</p>
    {lesson.checks.map((q, i) => <div className="learn-question" key={i}>
      <span className="learn-tag">{String(i + 1).padStart(2, '0')} / {q.level}</span><h4>{q.question}</h4>
      <details><summary>Show explained answer<ChevronDown size={16} aria-hidden="true"/></summary><p>{q.answer}</p></details>
    </div>)}
  </section>;
}

export default function Learning() {
  const [view, setView] = useState<View>('course');
  const [reading, setReading] = useState<ReadingState>(() => parseReadingState(null));
  const [ready, setReady] = useState(false);
  const [storageError, setStorageError] = useState(false);
  const [query, setQuery] = useState('');
  const [openPart, setOpenPart] = useState(parts[0].id);
  const [mobileContents, setMobileContents] = useState(false);
  const [referenceKind, setReferenceKind] = useState<'variables' | 'equations' | 'glossary'>('variables');
  const [referenceQuery, setReferenceQuery] = useState('');
  const [kind, setKind] = useState('All types');
  const [lab, setLab] = useState<string>('dispatch');
  const reduced = useReducedMotion();
  const reader = useRef<HTMLElement>(null);
  const readerTitle = useRef<HTMLHeadingElement>(null);
  const shouldFocus = useRef(false);

  useEffect(() => {
    let saved = parseReadingState(null);
    try { saved = parseReadingState(window.localStorage.getItem(LEARN_STORAGE_KEY)); }
    catch { setStorageError(true); }
    const linked = new URLSearchParams(window.location.search).get('learn');
    if (linked && lessons.some(l => l.id === linked)) saved.lesson = linked;
    setReading(saved);
    setOpenPart(lessons.find(l => l.id === saved.lesson)!.part);
    setReady(true);
  }, []);

  useEffect(() => {
    if (!ready) return;
    try { window.localStorage.setItem(LEARN_STORAGE_KEY, JSON.stringify(reading)); }
    catch { setStorageError(true); }
  }, [reading, ready]);

  useEffect(() => {
    if (!shouldFocus.current || view !== 'course') return;
    shouldFocus.current = false;
    readerTitle.current?.focus({preventScroll: true});
    reader.current?.scrollIntoView({behavior: reduced ? 'instant' : 'smooth', block: 'start'});
  }, [reading.lesson, view, reduced]);

  const lesson = lessons.find(l => l.id === reading.lesson)!;
  const position = lessons.indexOf(lesson);
  const part = parts.find(p => p.id === lesson.part)!;
  const resultIds = useMemo(() => new Set(searchLessons(query).map(l => l.id)), [query]);
  const selectedLab = labList.find(l => l.id === lab)!;
  const filteredVariables = useMemo(() => variables.filter(v => (kind === 'All types' || v.kind === kind) && matches(Object.values(v).join(' '), referenceQuery)), [kind, referenceQuery]);
  const filteredEquations = useMemo(() => equationIndex.filter(e => matches([e.title, e.section, e.tex, e.explain].join(' '), referenceQuery)), [referenceQuery]);
  const filteredGlossary = useMemo(() => glossary.filter(g => matches(g.join(' '), referenceQuery)), [referenceQuery]);
  const complete = reading.completed.includes(lesson.id);

  function openLesson(id: string) {
    const next = lessons.find(l => l.id === id);
    if (!next) return;
    shouldFocus.current = true;
    setReading(r => ({...r, lesson: id}));
    setOpenPart(next.part);
    setView('course');
    setMobileContents(false);
    const url = new URL(window.location.href);
    url.searchParams.set('learn', id);
    url.hash = '';
    window.history.replaceState(null, '', url);
  }

  function markUnderstood() {
    setReading(r => ({...r, completed: r.completed.includes(lesson.id) ? r.completed.filter(id => id !== lesson.id) : [...r.completed, lesson.id]}));
  }

  return <div className="learn-course">
    <header className="learn-heading">
      <div><div className="eyebrow">LEARN SWITCH / FROM ZERO TO RESEARCH</div>
        <h1>Understand the model.<br/><span>Then make it your own.</span></h1>
        <p>A guided course from the first megawatt to country applications and uncertainty. Read the equations, work the numbers, inspect the code, and learn what the model can—and cannot—tell you.</p>
        <div className="learn-facts"><span><strong>{lessons.length}</strong> lessons</span><span><strong>{parts.length}</strong> parts</span><span><strong>{variables.length}</strong> reference entries</span><span><strong>{lessons.reduce((n, l) => n + l.checks.length, 0)}</strong> practice questions</span></div>
      </div>
      <aside className="learn-progress-card" aria-label="Personal reading progress">
        <BookOpen size={22} aria-hidden="true"/><span>Your learning trail</span>
        <strong>{ready ? reading.completed.length : '—'}<small> / {lessons.length}</small></strong>
        <progress value={ready ? reading.completed.length : 0} max={lessons.length} aria-label="Lessons marked understood"/>
        <p>{storageError ? 'Browser storage is unavailable. Progress will not persist after you close this page.' : 'Marked understood by you. Saved in this browser only—not synced to GitHub or your model backups.'}</p>
      </aside>
    </header>

    <nav className="learn-view-nav" aria-label="Learning sections">{views.map(v => <button key={v.id} onClick={() => setView(v.id)} aria-current={view === v.id ? 'page' : undefined} className={view === v.id ? 'active' : ''}><v.icon size={18} aria-hidden="true"/>{v.label}</button>)}</nav>

    {view === 'course' && <div className="learn-layout">
      <aside className="learn-contents">
        <button className="learn-mobile-contents" onClick={() => setMobileContents(x => !x)} aria-expanded={mobileContents} aria-controls="learn-contents-body"><List size={18}/><span>Course contents · {position + 1} of {lessons.length}</span><ChevronDown size={17}/></button>
        <div id="learn-contents-body" className={mobileContents ? 'is-open' : ''}>
          <div className="learn-contents-heading"><span className="learn-kicker">YOUR LEARNING PATH</span><span>Start at 01, or find a topic.</span></div>
          <label className="learn-search"><Search size={16} aria-hidden="true"/><input value={query} onChange={e => setQuery(e.target.value)} placeholder="Search the whole course" aria-label="Search all lesson text"/>{query && <button onClick={() => setQuery('')} aria-label="Clear course search"><X size={15}/></button>}</label>
          {query && <p className="learn-search-count" role="status">{resultIds.size} matching {resultIds.size === 1 ? 'lesson' : 'lessons'} · all search words</p>}
          <nav aria-label="Course lessons">{parts.map((p, i) => {
            const all = lessons.filter(l => l.part === p.id);
            const shown = all.filter(l => resultIds.has(l.id));
            if (!shown.length) return null;
            const expanded = Boolean(query.trim()) || openPart === p.id;
            return <div className={'learn-part ' + (p.id === lesson.part ? 'is-current' : '')} key={p.id}>
              <button className="learn-part-toggle" aria-expanded={expanded} aria-controls={`learn-part-${p.id}`} onClick={() => setOpenPart(openPart === p.id ? '' : p.id)}><span className="learn-part-number">{String(i + 1).padStart(2, '0')}</span><span>{p.title}<small>{p.level} · {all.length} lessons</small></span><ChevronDown className={expanded ? 'rotated' : ''} size={15}/></button>
              {expanded && <ol id={`learn-part-${p.id}`}>{shown.map(l => <li key={l.id}><a href={`?learn=${l.id}`} onClick={e => {if (!e.metaKey && !e.ctrlKey && !e.shiftKey && !e.altKey) {e.preventDefault(); openLesson(l.id);}}} aria-current={l.id === lesson.id ? 'page' : undefined}><span>{l.title}</span>{reading.completed.includes(l.id) ? <CheckCircle2 size={15} aria-label="Marked understood"/> : <small>{readingMinutes(l)}m</small>}</a></li>)}</ol>}
            </div>;
          })}</nav>
          {!resultIds.size && <div className="learn-empty"><p>No matching lesson. Try “storage”, “discount”, “Kenya” or “non-anticipativity”.</p><button onClick={() => setQuery('')}>Show the full course</button></div>}
          <p className="learn-contents-note"><ShieldCheck size={15} aria-hidden="true"/>Equations checked against pinned source. Teaching illustrations are labelled separately.</p>
        </div>
      </aside>

      <motion.article ref={reader} key={lesson.id} className="learn-reader" initial={{opacity: 0, y: reduced ? 0 : 6}} animate={{opacity: 1, y: 0}} transition={{duration: reduced ? 0 : 0.2}}>
        <div className="learn-lesson-meta"><span>{part.level} / {part.title}</span><span><Clock3 size={14} aria-hidden="true"/>{readingMinutes(lesson)} min read + practice</span></div>
        <div className="learn-title-row"><span className="learn-lesson-number">{String(position + 1).padStart(2, '0')}</span><h2 ref={readerTitle} tabIndex={-1}>{lesson.title}</h2></div>
        <p className="learn-deck">{lesson.summary}</p>
        <section className="learn-goals"><span className="learn-kicker">AFTER THIS LESSON, YOU CAN</span><ul>{lesson.goals.map(g => <li key={g}><Check size={15} aria-hidden="true"/>{g}</li>)}</ul></section>
        <details className="learn-outline"><summary>In this lesson<ChevronDown size={16} aria-hidden="true"/></summary><ol>{lesson.sections.map((s, i) => <li key={i}><a href={`#learn-section-${i}`}>{s.title}</a></li>)}<li><a href="#learn-worked">Worked example</a></li><li><a href="#practice-heading">Practice questions</a></li></ol></details>
        {lesson.sections.map((s, i) => <SectionContent section={s} index={i} key={i}/>)}
        <section className="learn-worked" id="learn-worked"><span className="learn-kicker">WORK IT THROUGH</span><h3>{lesson.worked.title}</h3><p>{lesson.worked.setup}</p><ol>{lesson.worked.steps.map((s, i) => <li key={i}>{s}</li>)}</ol><div className="learn-result"><CheckCircle2 size={19} aria-hidden="true"/><p>{lesson.worked.result}</p></div></section>
        {lesson.lab && <section className="learn-inline-lab" aria-label="Interactive illustration"><LessonLab id={lesson.lab}/></section>}
        <section className="learn-pitfalls"><h3>Common mistakes to catch</h3><ul>{lesson.pitfalls.map(p => <li key={p}>{p}</li>)}</ul></section>
        <Practice lesson={lesson}/>
        <section className="learn-lesson-sources"><h3>Follow it into the source</h3><p>The equations are explained in context above. These links let you check the implementation and its limits.</p><ul>{lesson.sources.map(id => <li key={id}><SourceLink id={id}/></li>)}</ul></section>
        <div className="learn-complete"><button disabled={!ready} className={'button ' + (complete ? 'learn-understood' : 'primary')} onClick={markUnderstood} aria-pressed={complete}><CheckCircle2 size={18}/>{complete ? 'Marked understood' : 'Mark as understood'}</button><p>A personal checkpoint, not a test score. You can unmark it at any time.</p></div>
        <nav className="learn-pagination" aria-label="Previous and next lessons"><button disabled={position === 0} onClick={() => openLesson(lessons[position - 1].id)}><ArrowLeft size={18}/><span><small>PREVIOUS LESSON</small>{lessons[position - 1]?.title || 'You are at the beginning'}</span></button><button disabled={position === lessons.length - 1} onClick={() => openLesson(lessons[position + 1].id)}><span><small>NEXT LESSON</small>{lessons[position + 1]?.title || 'Course complete—revisit any topic'}</span><ArrowRight size={18}/></button></nav>
      </motion.article>
    </div>}

    {view === 'labs' && <section className="learn-workspace">
      <div className="learn-workspace-heading"><span className="learn-kicker">CHANGE AN ASSUMPTION. WATCH THE CONSEQUENCE.</span><h2>Build intuition with small experiments</h2><p>Five transparent browser calculations. These do not run SWITCH, submit solver jobs, or change your saved scenarios. Use the source-linked lessons to understand where the simplified illustration stops.</p></div>
      <div className="learn-lab-tabs" aria-label="Choose an illustration">{labList.map(l => <button className={lab === l.id ? 'active' : ''} aria-pressed={lab === l.id} key={l.id} onClick={() => setLab(l.id)}>{l.title}</button>)}</div>
      <div key={lab}><selectedLab.component/></div><button className="learn-text-link" onClick={() => openLesson(selectedLab.lesson)}>Read the full lesson<ArrowRight size={16}/></button>
    </section>}

    {view === 'reference' && <section className="learn-workspace">
      <div className="learn-workspace-heading"><span className="learn-kicker">KEEP THE NOTATION WITHIN REACH</span><h2>A reference you can actually read</h2><p>Symbols are shorthand; code object names identify the implementation. Inputs, decisions and derived quantities are deliberately distinguished. Expand an entry for domains, examples, effects and a source link.</p></div>
      <div className="learn-reference-tabs">{([{id: 'variables', label: `Variables & objects · ${variables.length}`}, {id: 'equations', label: `Equations · ${equationIndex.length}`}, {id: 'glossary', label: `Glossary · ${glossary.length}`}] as const).map(t => <button key={t.id} aria-pressed={referenceKind === t.id} className={referenceKind === t.id ? 'active' : ''} onClick={() => setReferenceKind(t.id)}>{t.label}</button>)}</div>
      <div className="learn-reference-toolbar"><label className="learn-search"><Search size={17} aria-hidden="true"/><input placeholder="Search symbols, names, meanings or units" value={referenceQuery} onChange={e => setReferenceQuery(e.target.value)} aria-label="Search the model reference"/>{referenceQuery && <button aria-label="Clear reference search" onClick={() => setReferenceQuery('')}><X size={15}/></button>}</label>{referenceKind === 'variables' && <label className="learn-type-filter">Object type<select value={kind} onChange={e => setKind(e.target.value)}>{['All types', 'Set / index', 'Input', 'Derived', 'Decision', 'Constraint', 'Objective', 'Registry'].map(k => <option key={k}>{k}</option>)}</select></label>}</div>
      <p className="learn-search-count" role="status">{referenceKind === 'variables' ? filteredVariables.length : referenceKind === 'equations' ? filteredEquations.length : filteredGlossary.length} matching entries</p>
      {referenceKind === 'variables' && <div className="learn-variable-list">
        <div className="learn-variable-head" aria-hidden="true"><span>Symbol</span><span>Code object & meaning</span><span>Type</span><span>Units</span></div>
        {filteredVariables.map(v => <details className="learn-variable" key={v.object}><summary><code className="learn-symbol">{v.symbol}</code><span className="learn-variable-name"><code>{v.object}</code><span>{v.meaning}</span></span><span className="learn-variable-type">{v.kind}</span><span className="learn-variable-units">{v.units}</span><ChevronDown size={16} aria-hidden="true"/></summary><div className="learn-variable-detail"><dl><dt>Object type</dt><dd>{v.kind}</dd><dt>Units</dt><dd>{v.units}</dd><dt>Domain / indexing</dt><dd>{v.domain}</dd><dt>Example</dt><dd>{v.example}</dd><dt>What changes?</dt><dd>{v.effect}</dd></dl><div className="learn-variable-links"><button onClick={() => openLesson(v.lesson)}>Learn this in context<ArrowRight size={15}/></button><SourceLink id={v.source}/></div></div></details>)}
        {!filteredVariables.length && <p className="learn-empty">No matching objects. Clear the search or change the type filter.</p>}
      </div>}
      {referenceKind === 'equations' && <div className="learn-equation-grid">{filteredEquations.map(e => <article className="learn-reference-card" key={`${e.lesson}-${e.sectionIndex}-${e.index}`}><span className="learn-kicker">{e.title}</span><h3>{e.section}</h3><MathBlock {...e}/><button className="learn-text-link" onClick={() => openLesson(e.lesson)}>Read the derivation & example<ArrowRight size={15}/></button></article>)}{!filteredEquations.length && <p className="learn-empty">No matching equations. Try a concept such as “energy” or “cost”.</p>}</div>}
      {referenceKind === 'glossary' && <div className="learn-glossary-grid">{filteredGlossary.map(([term, definition, lessonId]) => <article className="learn-reference-card" key={term}><h3>{term}</h3><p>{definition}</p><button className="learn-text-link" onClick={() => openLesson(lessonId)}>Explore this idea<ArrowRight size={15}/></button></article>)}{!filteredGlossary.length && <p className="learn-empty">No matching glossary entries.</p>}</div>}
    </section>}

    {view === 'sources' && <section className="learn-workspace">
      <div className="learn-workspace-heading"><span className="learn-kicker">TRACEABLE, NOT ORACULAR</span><h2>Know which model you are learning</h2><p>This course was checked against the source snapshots below on 9 September 2026. It teaches the important architecture and research workflow; it is not a claim to cover every optional module, prove every extension correct, or replicate a published optimum.</p></div>
      <div className="learn-boundary-grid"><article><span className="learn-tag">Framework</span><h3>Core SWITCH</h3><p>Core snapshot <code>239d62c</code>. The actual active modules determine the equations. A simple teaching formula is labelled when it omits implementation detail.</p></article><article><span className="learn-tag">Country application</span><h3>Xi Xi’s Kenya model</h3><p>Kenya snapshot <code>089834b</code>. Data and custom code are inspected separately. Model construction is not the same as a completed, validated national optimization.</p></article><article><span className="learn-tag">Illustration</span><h3>Two different teaching tools</h3><p>The browser labs are small calculations. The workbench’s annual stochastic Pyomo lab is a separate solver model. Neither automatically makes the Kenya formulation stochastic.</p></article></div>
      <div className="learn-source-grid">{Object.entries(sources).map(([id, s]) => <article className="learn-source-card" key={id}><SourceLink id={id}/><p>{s.note}</p><small>Referenced in {lessons.filter(l => l.sources.includes(id)).length} lessons</small></article>)}</div>
      <div className="learn-audit-note"><ShieldCheck size={23} aria-hidden="true"/><div><h3>Learn to audit, not just copy</h3><p>The Kenya lessons identify a conditional build-limit bug, hydrogen activation requirements, and output-weighting conventions worth checking. They also distinguish previously verified tutorial runs from the national case that has not been solved to optimality here.</p><button className="learn-text-link" onClick={() => openLesson('kenya-replication')}>Read the replication checklist<ChevronRight size={16}/></button></div></div>
    </section>}
  </div>;
}
