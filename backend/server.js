require('dotenv').config();
const express = require('express');
const cors = require('cors');

const aiRoutes = require('./aiRoutes');

const app = express();
app.use(cors({ origin: '*' }));
app.use(express.json());

// API
app.use('/api', aiRoutes);

const PORT = process.env.PORT || 8000;
app.listen(PORT, () => {
  console.log(`✅ Backend on http://localhost:${PORT}`);
});
