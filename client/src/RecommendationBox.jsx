import React, { useState } from 'react';
import axios from 'axios';

function RecommendationBox() {
  const [symbol, setSymbol] = useState('AAPL');
  const [recommendation, setRecommendation] = useState('');
  const [loading, setLoading] = useState(false);

  const fetchRecommendation = async () => {
    setLoading(true);
    try {
      const res = await axios.post('http://localhost:5000/recommend', { symbol });
      setRecommendation(res.data.recommendation);
    } catch (err) {
      setRecommendation('حدث خطأ في جلب التوصية.');
    }
    setLoading(false);
  };

  return (
    <div>
      <h2>📊 توصية لحظية لسهم</h2>
      <input value={symbol} onChange={(e) => setSymbol(e.target.value)} placeholder="AAPL" />
      <button onClick={fetchRecommendation} disabled={loading}>
        {loading ? 'جاري التحليل...' : '🔍 تحليل'}
      </button>
      <pre>{recommendation}</pre>
    </div>
  );
}

export default RecommendationBox;
