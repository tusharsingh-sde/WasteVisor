import React, { useState } from 'react';

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
    setResult(null);
    setError(null);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    setLoading(true);
    setError(null);
    const form = new FormData();
    form.append('image', selectedFile);
    try {
      const resp = await fetch('/api/analyze', {
        method: 'POST',
        body: form,
      });
      if (!resp.ok) {
        const err = await resp.json();
        throw new Error(err.error || 'Upload failed');
      }
      const data = await resp.json();
      setResult(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const renderResult = () => {
    if (!result) return null;
    const { classification, recommendations } = result;
    const primary = recommendations[0];
    const others = recommendations.slice(1);
    const isHazard = classification.hazards && classification.hazards.length > 0;
    return (
      <div style={{ marginTop: '2rem', padding: '1rem', borderRadius: '8px', background: '#fff', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}>
        <h2 style={{ marginBottom: '0.5rem' }}>Identified Item</h2>
        <p><strong>Item:</strong> {classification.item}</p>
        <p><strong>Category:</strong> {classification.category}</p>
        <p><strong>Materials:</strong> {classification.materials?.join(', ')}</p>
        <p><strong>Condition:</strong> {classification.condition}</p>
        {isHazard && (
          <div style={{ color: '#b91c1c', marginTop: '0.5rem' }}>
            <strong>⚠ Hazard Detected:</strong> {classification.hazards.join(', ')} – Follow safe disposal guidelines.
          </div>
        )}
        <h3 style={{ marginTop: '1rem' }}>Recommended Action</h3>
        <div style={{ padding: '0.75rem', background: '#e0f2fe', borderRadius: '6px', fontWeight: '600' }}>{primary.replace('_', ' ')}</div>
        {others.length > 0 && (
          <div style={{ marginTop: '0.5rem' }}>
            <p>Other options:</p>
            <ul>
              {others.map((a) => (
                <li key={a}>{a.replace('_', ' ')}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    );
  };

  return (
    <div style={{ padding: '2rem', fontFamily: 'Inter, sans-serif' }}>
      <h1>WasteVisor – Know Before You Throw</h1>
      <p>Upload a photo of a waste item to get a responsible next‑action recommendation.</p>
      <input type="file" accept="image/*" onChange={handleFileChange} disabled={loading} />
      <button onClick={handleUpload} disabled={!selectedFile || loading} style={{ marginLeft: '1rem', padding: '0.5rem 1rem' }}>
        {loading ? 'Analyzing…' : 'Analyze'}
      </button>
      {error && <p style={{ color: '#b91c1c' }}>Error: {error}</p>}
      {renderResult()}
    </div>
  );
}

export default App;
