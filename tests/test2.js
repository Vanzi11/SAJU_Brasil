const { spawn } = require('child_process');
const srv = spawn('node', ['dist/index.js'], { cwd: '/tmp/fortuneteller' });
let buf = ''; const results = [];
srv.stdout.on('data', d => { buf += d.toString(); let i; while ((i = buf.indexOf('\n')) >= 0) { const l = buf.slice(0,i).trim(); buf = buf.slice(i+1); if (l) try { results.push(JSON.parse(l)); } catch(e){} } });
const send = m => srv.stdin.write(JSON.stringify(m) + '\n');
const base = {birthDate:'1990-03-15',birthTime:'10:30',calendar:'solar',isLeapMonth:false,gender:'male'};
send({jsonrpc:'2.0',id:1,method:'initialize',params:{protocolVersion:'2024-11-05',capabilities:{},clientInfo:{name:'t',version:'1'}}});
setTimeout(() => {
  send({jsonrpc:'2.0',method:'notifications/initialized'});
  send({jsonrpc:'2.0',id:2,method:'tools/call',params:{name:'get_dae_un',arguments:base}});
  send({jsonrpc:'2.0',id:3,method:'tools/call',params:{name:'get_daily_fortune',arguments:{...base,targetDate:'2026-07-18'}}});
  send({jsonrpc:'2.0',id:4,method:'tools/call',params:{name:'analyze_saju',arguments:{...base,analysisType:'fortune',fortuneType:'love'}}});
}, 1500);
setTimeout(() => {
  for (const r of results) if (r.id >= 2) {
    const c = r.result?.content?.[0]?.text || JSON.stringify(r.error);
    console.log('=== id ' + r.id + ' ===\n' + (c ? c.slice(0, 1200) : '') + '\n');
  }
  srv.kill(); process.exit(0);
}, 8000);
