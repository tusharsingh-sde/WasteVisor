// tests/visionProvider.test.js
const { invokeVisionModel, validateVisionResult } = require('../src/visionProvider');
const { BedrockRuntimeClient, InvokeModelCommand } = require('@aws-sdk/client-bedrock-runtime');

jest.mock('@aws-sdk/client-bedrock-runtime', () => {
  const mSend = jest.fn();
  const MockClient = jest.fn(() => ({ send: mSend }));
  return {
    BedrockRuntimeClient: MockClient,
    ConverseCommand: jest.fn(),
    __esModule: true,
    _mockSend: mSend,
  };
});

describe('visionProvider fallback', () => {
  beforeAll(() => {
    delete process.env.BEDROCK_MODEL_ID; // ensure fallback path
  });

  test('returns deterministic stub when client missing', async () => {
    const result = await invokeVisionModel(Buffer.from('dummy'));
    expect(result).toEqual({
      item: 'unknown',
      category: 'unknown',
      materials: [],
      condition: 'unknown',
      hazards: [],
      confidence: 0.0,
    });
  });
});

describe('visionProvider error handling', () => {
  beforeAll(() => {
    process.env.BEDROCK_MODEL_ID = 'test-model';
  });

  afterAll(() => {
    delete process.env.BEDROCK_MODEL_ID;
  });

  test('throws normalized error when Bedrock invocation fails', async () => {
    const { _mockSend } = require('@aws-sdk/client-bedrock-runtime');
    _mockSend.mockRejectedValueOnce(new Error('Network error'));
    await expect(invokeVisionModel(Buffer.from('data'))).rejects.toThrow('Vision model invocation error');
  });
});

describe('validateVisionResult', () => {
  test('returns null for valid result', () => {
    const valid = {
      item: 'plastic bottle',
      category: 'plastic',
      materials: ['PET'],
      condition: 'intact',
      hazards: [],
      confidence: 0.92,
    };
    expect(validateVisionResult(valid)).toBeNull();
  });

  test('detects missing field', () => {
    const invalid = { category: 'metal' };
    expect(validateVisionResult(invalid)).toMatch(/missing required field/);
  });

  test('detects low confidence', () => {
    const lowConf = {
      item: 'paper',
      category: 'paper',
      materials: [],
      condition: 'crumpled',
      hazards: [],
      confidence: 0.3,
    };
    expect(validateVisionResult(lowConf)).toMatch(/Low confidence/);
  });
});
