import express from "express";
import multer from "multer";
import fetch from "node-fetch";
import Papa from "papaparse";
import XLSX from "xlsx";
import fs from "fs";
import path from "path";

const router = express.Router();
const upload = multer({ dest: "uploads/" });

const OPENAI_KEY = process.env.OPENAI_API_KEY;
let terms = []; // { id, category, term, definition, example, embedding: [...] }

// 🔹 OpenAI Chat API로 JSON 구조화
async function getOpenAIJSON(prompt) {
  const res = await fetch("https://api.openai.com/v1/chat/completions", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${OPENAI_KEY}`,
    },
    body: JSON.stringify({
      model: "gpt-3.5-turbo",
      messages: [{ role: "user", content: prompt }],
      temperature: 0.3,
    }),
  });
  const data = await res.json();
  return JSON.parse(data.choices[0].message.content);
}

// 🔹 OpenAI 임베딩 생성
async function getEmbedding(text) {
  const res = await fetch("https://api.openai.com/v1/embeddings", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${OPENAI_KEY}`,
    },
    body: JSON.stringify({
      input: text,
      model: "text-embedding-ada-002",
    }),
  });
  const data = await res.json();
  return data.data[0].embedding;
}

// 🔹 코사인 유사도
function cosineSim(a, b) {
  let s = 0,
    sa = 0,
    sb = 0;
  for (let i = 0; i < a.length; ++i) {
    s += a[i] * b[i];
    sa += a[i] ** 2;
    sb += b[i] ** 2;
  }
  return s / (Math.sqrt(sa) * Math.sqrt(sb));
}

// 📌 (1) 단일 텍스트 → 구조화
router.post("/parse-text", async (req, res) => {
  try {
    const prompt = `
아래 내용을 category, term, definition, example JSON 구조로 정리해줘.
내용: """${req.body.text}"""
형식: {"category": "...", "term": "...", "definition": "...", "example": "..."}
    `;
    const obj = await getOpenAIJSON(prompt);
    obj.id = Date.now();
    obj.embedding = await getEmbedding(obj.term + " " + obj.definition);
    terms.push(obj);
    res.json(obj);
  } catch (err) {
    res.status(500).json({ error: "구조화 실패", details: err.message });
  }
});

// 📌 (2) 파일 업로드 → 구조화
router.post("/upload-file", upload.single("file"), async (req, res) => {
  try {
    const filePath = req.file.path;
    let rows = [];
    const ext = path.extname(req.file.originalname).toLowerCase();

    if (ext === ".csv") {
      const csvData = fs.readFileSync(filePath, "utf8");
      const parsed = Papa.parse(csvData, { header: true });
      rows = parsed.data;
    } else if (ext === ".xlsx") {
      const workbook = XLSX.readFile(filePath);
      const sheetName = workbook.SheetNames[0];
      rows = XLSX.utils.sheet_to_json(workbook.Sheets[sheetName]);
    } else if (ext === ".json") {
      rows = JSON.parse(fs.readFileSync(filePath, "utf8"));
    } else if ([".txt", ".md"].includes(ext)) {
      const textData = fs.readFileSync(filePath, "utf8");
      rows = textData.split("\n").map((line) => ({ text: line.trim() }));
    } else {
      return res.status(400).json({ error: "지원하지 않는 파일 형식" });
    }

    fs.unlinkSync(filePath);

    let addedCount = 0;
    for (const row of rows) {
      const text = Object.values(row).join(" ").trim();
      if (!text) continue;

      try {
        const prompt = `
아래 내용을 category, term, definition, example JSON 구조로 정리해줘.
내용: """${text}"""
형식: {"category": "...", "term": "...", "definition": "...", "example": "..."}
        `;
        const obj = await getOpenAIJSON(prompt);
        obj.id = Date.now() + Math.random();
        obj.embedding = await getEmbedding(obj.term + " " + obj.definition);
        terms.push(obj);
        addedCount++;
      } catch (err) {
        console.warn("행 처리 실패:", err.message);
      }
    }

    res.json({ message: "파일 처리 완료", added: addedCount });
  } catch (err) {
    res.status(500).json({ error: "파일 처리 실패", details: err.message });
  }
});

// 📌 (3) 전체 목록
router.get("/terms", (req, res) => res.json(terms));

// 📌 (4) 검색
router.post("/search", async (req, res) => {
  try {
    const { query } = req.body;
    const emb = await getEmbedding(query);
    const sims = terms.map((t) => ({
      ...t,
      sim: cosineSim(emb, t.embedding),
    }));
    sims.sort((a, b) => b.sim - a.sim);
    res.json(sims.slice(0, 5));
  } catch (err) {
    res.status(500).json({ error: "검색 실패", details: err.message });
  }
});

export default router;
