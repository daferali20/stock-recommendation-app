import React, { useState } from 'react';
import axios from 'axios';

function RecommendationBox() {
  const [symbol, setSymbol] = useState('AAPL');
  const [recommendation, setRecommendation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchRecommendation = async () => {
    if (!symbol.trim()) {
      setError('الرجاء إدخال رمز سهم صحيح');
      return;
    }

    setLoading(true);
    setError(null);
    setRecommendation(null);

    try {
      const res = await fetch('https://stock-recommendation-server.onrender.com/recommend', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ symbol: symbol.trim().toUpperCase() }),
});
const data = await res.json();
      
      if (res.data && res.data.recommendation) {
        setRecommendation(res.data.recommendation);
      } else {
        setError('لا توجد توصية متاحة لهذا السهم');
      }
    } catch (err) {
      const errorMessage = err.response?.data?.message || 
                          err.message || 
                          'حدث خطأ في جلب التوصية';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      maxWidth: '600px',
      margin: '0 auto',
      padding: '20px',
      textAlign: 'right',
      direction: 'rtl'
    }}>
      <h2 style={{ color: '#2c3e50' }}>📊 توصية لحظية لسهم</h2>
      
      <div style={{ margin: '20px 0' }}>
        <input
          value={symbol}
          onChange={(e) => setSymbol(e.target.value)}
          placeholder="أدخل رمز السهم (مثال: AAPL)"
          style={{
            padding: '10px',
            width: '200px',
            marginLeft: '10px'
          }}
        />
        
        <button 
          onClick={fetchRecommendation} 
          disabled={loading}
          style={{
            padding: '10px 20px',
            backgroundColor: loading ? '#95a5a6' : '#3498db',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          {loading ? 'جاري التحليل...' : '🔍 تحليل'}
        </button>
      </div>

      {error && (
        <div style={{
          color: '#e74c3c',
          padding: '10px',
          backgroundColor: '#fadbd8',
          borderRadius: '4px',
          margin: '10px 0'
        }}>
          {error}
        </div>
      )}

      {recommendation && (
        <div style={{
          padding: '15px',
          backgroundColor: '#e8f4f8',
          borderRadius: '4px',
          borderRight: '4px solid #3498db',
          whiteSpace: 'pre-wrap'
        }}>
          <h3 style={{ marginTop: 0 }}>توصية لسهم {symbol.toUpperCase()}:</h3>
          <p>{recommendation}</p>
        </div>
      )}
    </div>
  );
}

export default RecommendationBox;
