const { spawn } = require('child_process');
const srv = spawn('node', ['dist/index.js'], { cwd: '/tmp/fortuneteller' });
let buf = '';
const results = [];
srv.stdout.on('data', d => {
  buf += d.toString();
  let idx;
  while ((idx = buf.indexOf('\n')) >= 0) {
    const line = buf.slice(0, idx).trim(); buf = buf.slice(idx + 1);
    if (line) { try { results.push(JSON.parse(line)); } catch(e){} }
  }
});
const send = m => srv.stdin.write(JSON.stringify(m) + '\n');
send({jsonrpc:'2.0',id:1,method:'initialize',params:{protocolVersion:'2024-11-05',capabilities:{},clientInfo:{name:'test',version:'1.0'}}});
setTimeout(() => {
  send({jsonrpc:'2.0',method:'notifications/initialized'});
  send({jsonrpc:'2.0',id:2,method:'tools/call',params:{name:'analyze_saju',arguments:{birthDate:'1990-03-15',birthTime:'10:30',calendar:'solar',isLeapMonth:false,gender:'male',analysisType:'basic'}}});
  send({jsonrpc:'2.0',id:3,method:'tools/call',params:{name:'check_compatibility',arguments:{person1:{birthDate:'1990-03-15',birthTime:'10:30',calendar:'solar',isLeapMonth:false,gender:'male'},person2:{birthDate:'1992-07-20',birthTime:'14:30',calendar:'solar',isLeapMonth:false,gender:'female'}}}});
}, 1500);
setTimeout(() => {
  for (const r of results) {
    if (r.id >= 2) {
      console.log('=== RESPOSTA id ' + r.id + ' ===');
      const c = r.result?.content?.[0]?.text || JSON.stringify(r.error);
      console.log(c ? c.slice(0, 2500) : JSON.stringify(r).slice(0,500));
    }
  }
  srv.kill(); process.exit(0);
}, 8000);
