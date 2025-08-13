require('dotenv').config();
const express = require('express');
const fetch = require('node-fetch'); // v2 (CommonJS)
const multer = require('multer');
const Papa = require('papaparse');
const XLSX = require('xlsx');
const fs = require('fs');
const path = require('path');

const router = express.Router();
const upload = multer({ dest: path.join(__dirname, 'uploads') });

const OPENAI_KEY = process.env.OPENAI_API_KEY;
const MODEL = process.env.OPENAI_MODEL || 'gpt-4o-mini';

const DATA_FILE = path.join(__dirname, 'data', 'terms.json');
fs.mkdirSync(path.dirname(DATA_FILE), { recursive: true });
if (!fs.existsSync(DATA_FILE)) fs.writeFileSync(DATA_FILE, '[]', 'utf8');

function loadTerms() {
  try { return JSON.parse(fs.readFileSync(DATA_FILE, 'utf8')); }
  catch { return []; }
}
function saveTerms(arr) {
  fs.writeFileSync(DATA_FILE, JSON.stringify(arr, null, 2), 'utf8');
}

let terms = loadTerms(); // 메모리 + 파일동기화

async function getOpenAIJSON(prompt) {
  const r = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type':'application/json',
      'Authorization': `Bearer ${OPENAI_KEY}`
    },
    body: JSON.stringify({
      model: MODEL,
      messages: [{ role: 'user', content: prompt }],
      temperature: 0.3
    })
  });
  const data = await r.json();
  return JSON.parse(data.choices[0].message.content);
}

async function getEmbedding(text) {
  const r = await fetch('https://api.openai.com/v1/embeddings', {
    method: 'POST',
    headers: {
      'Content-Type':'application/json',
      'Authorization': `Bearer ${OPENAI_KEY}`
    },
    body: JSON.stringify({
      input: text,
      model: 'text-embedding-ada-002'
    })
  });
  const data = await r.json();
  return data.data[0].embedding;
}

function cosineSim(a, b) {
  let s=0, sa=0, sb=0;
  for (let i=0;i<a.length;i++){ s+=a[i]*b[i]; sa+=a[i]**2; sb+=b[i]**2; }
  return s/(Math.sqrt(sa)*Math.sqrt(sb));
}

// (1) 단일 텍스트 → 구조화
router.post('/parse-text', async (req, res) => {
  try {
    const prompt = `아래 텍스트를 {"category":"", "term":"", "definition":"", "example":""} JSON으로.
텍스트: """${req.body.text}"""`;
    const obj = await getOpenAIJSON(prompt);
    obj.id = Date.now();
    obj.embedding = await getEmbedding(`${obj.term} ${obj.definition}`);
    terms.push(obj);
    saveTerms(terms);
    res.json(obj);
  } catch (e) {
    res.status(500).json({ error: '구조화 실패', details: String(e) });
  }
});

// (2) 파일 업로드 → 구조화 (csv/xlsx/json/txt/md)
router.post('/upload-file', upload.single('file'), async (req, res) => {
  try {
    const fp = req.file.path;
    const ext = path.extname(req.file.originalname).toLowerCase();
    let rows = [];

    if (ext === '.csv') {
      const csvData = fs.readFileSync(fp, 'utf8');
      rows = Papa.parse(csvData, { header: true }).data;
    } else if (ext === '.xlsx') {
      const wb = XLSX.readFile(fp);
      rows = XLSX.utils.sheet_to_json(wb.Sheets[wb.SheetNames[0]]);
    } else if (ext === '.json') {
      rows = JSON.parse(fs.readFileSync(fp, 'utf8'));
    } else if (ext === '.txt' || ext === '.md') {
      const lines = fs.readFileSync(fp, 'utf8').split('\n');
      rows = lines.map(t => ({ text: t.trim() }));
    } else {
      fs.unlinkSync(fp); return res.status(400).json({ error: '지원하지 않는 파일 형식' });
    }
    fs.unlinkSync(fp);

    let added = 0;
    for (const row of rows) {
      const text = Object.values(row).join(' ').trim();
      if (!text) continue;
      try {
        const prompt = `아래 텍스트를 {"category":"", "term":"", "definition":"", "example":""} JSON으로.
텍스트: """${text}"""`;
        const obj = await getOpenAIJSON(prompt);
        obj.id = Date.now() + Math.random();
        obj.embedding = await getEmbedding(`${obj.term} ${obj.definition}`);
        terms.push(obj);
        added++;
      } catch {}
    }
    saveTerms(terms);
    res.json({ message: '파일 처리 완료', added });
  } catch (e) {
    res.status(500).json({ error: '파일 처리 실패', details: String(e) });
  }
});

// (3) 전체 목록
router.get('/terms', (req, res) => res.json(terms));

// (4) 검색
router.post('/search', async (req, res) => {
  try {
    const emb = await getEmbedding(req.body.query);
    const sims = terms.map(t => ({ ...t, sim: cosineSim(emb, t.embedding) }))
                      .sort((a,b)=>b.sim-a.sim)
                      .slice(0,5);
    res.json(sims);
  } catch (e) {
    res.status(500).json({ error: '검색 실패', details: String(e) });
  }
});

module.exports = router;
