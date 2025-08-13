import fetch from 'node-fetch';
import pkg from 'pg';
const { Pool } = pkg;

const pool = new Pool({
  connectionString: process.env.DATABASE_URL
});

/**
 * OpenAI API를 이용해 텍스트 임베딩 생성
 * @param {string} text
 * @returns {Promise<number[]>} 벡터 배열
 */
export async function getEmbedding(text) {
  try {
    const res = await fetch('https://api.openai.com/v1/embeddings', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`
      },
      body: JSON.stringify({
        input: text,
        model: 'text-embedding-3-small' // 1536차원
      })
    });

    if (!res.ok) {
      const errText = await res.text();
      throw new Error(`OpenAI API Error: ${errText}`);
    }

    const data = await res.json();
    return data.data[0].embedding;
  } catch (err) {
    console.error("❌ getEmbedding 오류:", err.message);
    throw err;
  }
}

/**
 * 용어 저장
 * @param {Object} param0
 */
export async function saveTerm({ keyword, definition, example, rules }) {
  try {
    const embedding = await getEmbedding(`${keyword} ${definition}`);
    await pool.query(
      `INSERT INTO terms (keyword, definition, example, rules, embedding)
       VALUES ($1, $2, $3, $4, $5)`,
      [keyword, definition, example, rules, embedding]
    );
    console.log(`✅ 저장 완료: ${keyword}`);
  } catch (err) {
    console.error("❌ saveTerm 오류:", err.message);
  }
}

/**
 * 의미 기반 검색
 * @param {string} query 검색어
 * @param {number} limit 검색 결과 수
 */
export async function searchTerms(query, limit = 5) {
  try {
    const emb = await getEmbedding(query);
    const { rows } = await pool.query(
      `SELECT *, embedding <#> $1 AS distance
       FROM terms
       ORDER BY distance ASC
       LIMIT $2`,
      [emb, limit]
    );
    return rows;
  } catch (err) {
    console.error("❌ searchTerms 오류:", err.message);
    return [];
  }
}
