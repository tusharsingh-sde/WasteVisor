// src/ruleEngine.js
const path = require('path');
const fs = require('fs');

// Load rule definitions once at startup
const rulesPath = path.resolve(__dirname, 'waste_rules.json');
let wasteRules = {};
try {
  const raw = fs.readFileSync(rulesPath, 'utf8');
  wasteRules = JSON.parse(raw);
} catch (e) {
  console.error('Failed to load waste_rules.json:', e);
  wasteRules = {};
}

/**
 * Determine a ranked list of actions for a given classification.
 * @param {Object} classification - The vision model output.
 *   Expected shape:
 *     { item, category, materials, condition, hazards, confidence }
 * @returns {Array<string>} - Ordered actions (e.g., ['repair','resale','authorized_disposal'])
 */
function getRecommendations(classification) {
  const { category = 'default', hazards = [] } = classification;
  // Start with category-specific actions if present, otherwise default.
  const categoryRules = wasteRules[category] || wasteRules['default'] || {};
  let actions = categoryRules.actions ? [...categoryRules.actions] : [];

  // Hazard overrides – if any hazard matches a rule, replace actions.
  if (hazards.length > 0) {
    // Check for explicit overrides for each hazard.
    for (const hazard of hazards) {
      const hazardMap = (categoryRules.hazards && categoryRules.hazards[hazard]) || null;
      if (hazardMap && hazardMap.length > 0) {
        // Override with hazard-specific actions (unique, preserving order).
        actions = [...hazardMap];
        break; // Stop after first matching hazard.
      }
    }
    // If still no specific override, fall back to default hazardOverride if defined.
    if (actions.length === 0 && wasteRules['default'] && wasteRules['default'].hazardOverride) {
      actions = [...wasteRules['default'].hazardOverride];
    }
  }

  // Ensure we always have at least a safe fallback.
  if (actions.length === 0) {
    actions = ['authorized_disposal'];
  }

  // Remove duplicates while preserving order.
  const seen = new Set();
  const uniq = [];
  for (const a of actions) {
    if (!seen.has(a)) {
      seen.add(a);
      uniq.push(a);
    }
  }
  return uniq;
}

module.exports = { getRecommendations };
