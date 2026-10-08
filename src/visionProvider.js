// src/visionProvider.js

/**
 * Vision Provider – handles AWS Bedrock multimodal calls.
 * Provides:
 *   - invokeVisionModel(imageBuffer): returns structured classification.
 *   - validateVisionResult(result): validates schema & confidence.
 */

const { BedrockRuntimeClient, ConverseCommand } = require('@aws-sdk/client-bedrock-runtime');
const logger = console; // simple logger; could be replaced with a proper logger later.

// Lazy initialisation function for Bedrock client
function getBedrockClient() {
  if (!process.env.BEDROCK_MODEL_ID) {
    return null;
  }
  if (!global.__bedrockClient) {
    global.__bedrockClient = new BedrockRuntimeClient({ region: process.env.AWS_REGION || 'us-east-1' });
    logger.info('Bedrock client (Nova 2 Lite) lazily initialized for model', process.env.BEDROCK_MODEL_ID);
  }
  return global.__bedrockClient;
}

/**
 * Development fallback – deterministic stub used when Bedrock is not configured.
 */
function fallbackResult() {
  logger.info('VisionProvider: using development fallback stub');
  return {
    item: 'unknown',
    category: 'unknown',
    materials: [],
    condition: 'unknown',
    hazards: [],
    confidence: 0.0,
  };
}

/**
 * Invoke the Bedrock multimodal model (Amazon Nova 2 Lite) with a base64‑encoded image.
 * @param {Buffer} imageBuffer - Uploaded image data.
 * @returns {Promise<Object>} Structured classification JSON.
 */
async function invokeVisionModel(imageBuffer) {
  // Obtain a client; if not configured, fall back to deterministic stub.
  const client = getBedrockClient();
  if (!client) {
    return fallbackResult();
  }

  // Build the Converse payload. Image is sent as raw bytes; Bedrock expects the format field.
  const payload = {
    messages: [
      {
        role: 'user',
        content: [
          {
            type: 'text',
            text: 'Identify the waste item, its category, materials, condition, and any hazards. Return ONLY the JSON matching the schema. Do not include any explanations or markdown.',
          },
          {
            type: 'image',
            format: 'jpeg',
            source: { bytes: imageBuffer },
          },
        ],
      },
    ],
  };

  const command = new ConverseCommand({
    modelId: process.env.BEDROCK_MODEL_ID,
    messages: payload.messages,
  });

  try {
    const response = await client.send(command);
    // The Converse API returns the assistant message in response.output.message.content.
    let responseText = '';
    if (response && response.output && response.output.message && Array.isArray(response.output.message.content)) {
      const textPart = response.output.message.content.find((c) => c.type === 'text' && c.text);
      if (textPart) {
        responseText = textPart.text;
      }
    }
    // Fallback to raw body if the structured location is missing (defensive).
    if (!responseText && response.body) {
      responseText = Buffer.from(response.body).toString('utf8');
    }
    // Strip optional markdown fences.
    responseText = responseText.replace(/^\s*```\s*json?\s*/i, '').replace(/\s*```\s*$/g, '').trim();
    const parsed = JSON.parse(responseText);
    return parsed;
  } catch (err) {
    // Log safe diagnostic metadata without exposing secrets or image data
    const safeInfo = {
      name: err.name,
      message: err.message,
      code: err.code,
      httpStatusCode: err.$metadata?.httpStatusCode,
      requestId: err.$metadata?.requestId,
    };
    logger.error('VisionProvider: Bedrock invocation failed', safeInfo);
    throw new Error('Vision model invocation error');
  }
}

/**
 * Validate the structure of a vision result.
 */
function validateVisionResult(result) {
  const required = ['item', 'category', 'materials', 'condition', 'hazards', 'confidence'];
  for (const key of required) {
    if (!(key in result)) {
      return `Vision result missing required field: ${key}`;
    }
  }
  if (!Array.isArray(result.materials) || !Array.isArray(result.hazards)) {
    return 'Materials and hazards must be arrays';
  }
  if (typeof result.confidence !== 'number') {
    return 'Confidence must be a number';
  }
  if (result.confidence < 0.5) {
    return `Low confidence (${result.confidence}); classification may be unreliable`;
  }
  return null;
}

module.exports = { invokeVisionModel, validateVisionResult, diagnosticTextOnly };

/**
 * Diagnostic helper – sends a text‑only Converse request to verify Bedrock connectivity.
 * Returns the raw assistant message text.
 */
async function diagnosticTextOnly() {
  const client = getBedrockClient();
  if (!client) {
    throw new Error('Bedrock client not configured');
  }
  const payload = {
    messages: [
      {
        role: 'user',
        content: [{ type: 'text', text: 'Reply with exactly: BEDROCK_OK' }],
      },
    ],
  };
  const command = new ConverseCommand({
    modelId: process.env.BEDROCK_MODEL_ID,
    messages: payload.messages,
  });
  const response = await client.send(command);
  let responseText = '';
  if (response && response.output && response.output.message && Array.isArray(response.output.message.content)) {
    const textPart = response.output.message.content.find((c) => c.type === 'text' && c.text);
    if (textPart) responseText = textPart.text;
  }
  if (!responseText && response.body) {
    responseText = Buffer.from(response.body).toString('utf8');
  }
  return responseText.trim();
}

