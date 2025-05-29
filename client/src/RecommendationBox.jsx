import React, { useState } from 'react';
import axios from 'axios';

function RecommendationBox() {
  const [symbol, setSymbol] = useState('');
  const [result, setResult] = useState('');
  const [error, setError] = useState('');

  const handleRecommend = async () => {
    try {
      const response = await axios.post(`${process.env.REACT_APP_API_URL}/recommend`, {
        symbol: symbol.toUpperCase()
      });
      setResult(response.data.recommendation);
      setError('');
    } catch (err) {
      setError('⚠️ خطأ في الاتصال بالخادم');
      setResult('');
    }
  };

  return (
    <div>
      <input value={symbol} onChange={e => setSymbol(e.target.value)} placeholder="ادخل رمز السهم مثل AAPL" />
      <button onClick={handleRecommend}>احصل على التوصية</button>
      <div>{result && <p>{result}</p>}</div>
      <div>{error && <p style={{ color: 'red' }}>{error}</p>}</div>
    </div>
  );
}

export default RecommendationBox;
