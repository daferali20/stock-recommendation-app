import React, { useState } from 'react';
import axios from 'axios';

function RecommendationBox() {
  const [symbol, setSymbol] = useState('AAPL');
  const [recommendation, setRecommendation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchRecommendation = async () => {
    if (!symbol.trim()) {
      setError('الرجاء إدخال رمز سهم');
      return;
    }

    setLoading(true);
    setError(null);
    setRecommendation(null);

    try {
      const res = await axios.post(
        'https://stock-recommendation-server.onrender.com/recommend',
        { symbol: symbol.trim().toUpperCase() },
        {
          headers: { 'Content-Type': 'application/json' },
          timeout: 10000,
        }
      );

      if (res.data?.recommendation) {
        setRecommendation(res.data.recommendation);
      } else {
        setError('لا توجد توصية متاحة');
      }
    } catch (err) {
      console.error("Error:", err);
      setError(
        err.response?.data?.message || 
        err.message || 
        'فشل الاتصال بالخادم. تحقق من الإنترنت.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ textAlign: 'right', direction: 'rtl', padding: '20px' }}>
      <h2>📊 توصية سهم</h2>
      <input
        value={symbol}
        onChange={(e) => setSymbol(e.target.value)}
        placeholder="أدخل رمز السهم (مثال: AAPL)"
      />
      <button onClick={fetchRecommendation} disabled={loading}>
        {loading ? 'جاري التحليل...' : '🔍 تحليل'}
      </button>
      
      {error && <div style={{ color: 'red' }}>{error}</div>}
      
      {recommendation && (
        <div style={{ marginTop: '20px' }}>
          <h3>توصية لـ {symbol.toUpperCase()}:</h3>
          <p>{recommendation}</p>
        </div>
      )}
    </div>
  );
}

export default RecommendationBox;
