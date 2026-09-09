// Preserve the Next.js dev command while accepting the supervised preview flags.
import {spawn} from 'node:child_process';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const input=process.argv.slice(2);
const supervised=input.includes('--strictPort');
const args=input.filter(arg=>arg!=='--strictPort').map(arg=>arg==='--host'?'--hostname':arg);
// A preview has no local solver service; use the existing hosted atlas edition.
const child=spawn(process.execPath,[require.resolve('next/dist/bin/next'),'dev',...args],{
  stdio:'inherit',env:{...process.env,...(supervised?{VERCEL:'1'}:{})},
});
for(const signal of ['SIGINT','SIGTERM'])process.on(signal,()=>child.kill(signal));
child.on('error',error=>{console.error(error.message);process.exitCode=1;});
child.on('exit',code=>{process.exitCode=code??1;});
