const fetch = require('node-fetch');
const { getEmbedding } = require('./embedding');

async function runAIPipeline(text) {
  const prompt = `
다음 내용을 분석하여 JSON으로 작성해줘:
1. 주요 키워드
2. 각 키워드의 정의와 해설
3. 관련 사례
4. 사례에서 도출되는 원리/규칙

형식:
{
  "keywords": ["..."],
  "definitions": [{"term": "...", "definition": "..."}],
  "examples": ["..."],
  "rules": ["..."]
}

내용: """${text}"""
`;

  const res = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`
    },
    body: JSON.stringify({
      model: 'gpt-4o-mini',
      messages: [{ role: 'user', content: prompt }],
      temperature: 0.3
    })
  });

  const data = await res.json();
  const result = JSON.parse(data.choices[0].message.content);

  // Embedding 생성
  result.embedding = await getEmbedding(text);
  return result;
}

module.exports = { runAIPipeline };
