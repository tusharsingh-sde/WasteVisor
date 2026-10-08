// server.js
require('dotenv').config();
const express = require('express');
const multer = require('multer');
// Bedrock SDK imported in visionProvider module
const fs = require('fs');
const path = require('path');

const app = express();
const upload = multer({ storage: multer.memoryStorage() });

// Bedrock client initialization moved to visionProvider



// Load rule engine – separates business logic
const { getRecommendations } = require('./src/ruleEngine');
const { invokeVisionModel, validateVisionResult } = require('./src/visionProvider');

app.post('/api/analyze', upload.single('image'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No image uploaded' });
    }
    const visionResult = await invokeVisionModel(req.file.buffer);
    // Basic validation of expected fields
    // Validate vision result structure and confidence
    const validationError = validateVisionResult(visionResult);
    if (validationError) {
      return res.status(502).json({ error: validationError });
    }
    const recommendations = getRecommendations(visionResult);
    res.json({ classification: visionResult, recommendations });
  } catch (err) {
    console.error('Error in /api/analyze:', err);
    res.status(500).json({ error: err.message || 'Internal Server Error' });
  }
});

const PORT = process.env.PORT || 4000;
app.listen(PORT, () => console.log(`API server listening on http://localhost:${PORT}`));
