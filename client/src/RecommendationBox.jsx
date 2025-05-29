import React, { useState } from 'react';
import axios from 'axios';

const RecommendationBox = () => {
  const [symbol, setSymbol] = useState('');
  const [recommendation, setRecommendation] = useState('');
  const [loading, setLoading] = useState(false);

  const fetchRecommendation = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${process.env.REACT_APP_API_URL}/recommend`, {
        symbol: symbol.toUpperCase(),
      });

      setRecommendation(JSON.stringify(response.data, null, 2));
    } catch (error) {
      console.error(error);
      setRecommendation('⚠️ حدث خطأ أثناء الاتصال بالخادم');
    }
    setLoading(false);
  };

  return (
    <div className="p-4">
      <input
        type="text"
        value={symbol}
        onChange={(e) => setSymbol(e.target.value)}
        placeholder="أدخل رمز السهم مثل AAPL"
        className="border p-2"
      />
      <button onClick={fetchRecommendation} className="ml-2 bg-blue-500 text-white px-4 py-2 rounded">
        🔍 تحليل
      </button>
      <div className="mt-4 whitespace-pre-wrap bg-gray-100 p-4 rounded">
        {loading ? '⏳ جاري التحميل...' : recommendation}
      </div>
    </div>
  );
};

export default RecommendationBox;
