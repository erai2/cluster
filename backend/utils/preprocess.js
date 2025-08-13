const fs = require('fs');
const pdfParse = require('pdf-parse');
const mammoth = require('mammoth');
const { franc } = require('franc-min');

async function parseFile(file) {
  const ext = file.originalname.split('.').pop().toLowerCase();
  let text = '';

  if (ext === 'txt' || ext === 'md') {
    text = fs.readFileSync(file.path, 'utf8');
  } else if (ext === 'pdf') {
    const data = await pdfParse(fs.readFileSync(file.path));
    text = data.text;
  } else if (ext === 'docx') {
    const data = await mammoth.extractRawText({ path: file.path });
    text = data.value;
  } else if (ext === 'csv') {
    text = fs.readFileSync(file.path, 'utf8');
  } else {
    throw new Error('지원하지 않는 파일 형식');
  }

  // 언어 감지
  const lang = franc(text);
  if (lang !== 'kor' && lang !== 'eng') {
    console.warn(`언어 감지 결과: ${lang}`);
  }

  // 불필요한 줄 제거
  const cleaned = text.replace(/\n\s*\n/g, '\n').trim();

  // 단락 단위로 나눔
  return cleaned.split('\n').filter(line => line.length > 5);
}

module.exports = { parseFile };
