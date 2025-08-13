const express = require('express');
const multer = require('multer');
const { parseFile } = require('../utils/preprocess');
const { runAIPipeline } = require('../utils/aiPipeline');
const { saveTermToDB } = require('../db');

const upload = multer({ dest: 'uploads/' });
const router = express.Router();

router.post('/upload', upload.single('file'), async (req, res) => {
  try {
    const textBlocks = await parseFile(req.file);
    for (const block of textBlocks) {
      const result = await runAIPipeline(block);
      await saveTermToDB(result);
    }
    res.json({ success: true, message: '파일 처리 완료' });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: err.message });
  }
});

module.exports = router;
