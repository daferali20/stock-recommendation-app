// في RecommendPage.jsx
import { useState } from 'react';
import axios from 'axios';
const express = require('express');
const app = express();
require('dotenv').config();

const recommendRoute = require('./routes/recommend'); // أنشئ هذا الملف

app.use('/recommend', recommendRoute);

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));

export default function RecommendPage() {
  const [symbol, setSymbol] = useState('AAPL');
  const [result, setResult] = useState(null);

  const fetchRecommendation = async () => {
    try {
      const res = await axios.get(`/recommend/${symbol}`);
      setResult(res.data);
    } catch (err) {
      alert('فشل في جلب التوصية!');
    }
  };

  return (
    <div className="p-4 max-w-lg mx-auto">
      <h2 className="text-xl font-bold mb-2">🔍 توصية لحظية</h2>
      <input
        type="text"
        value={symbol}
        onChange={(e) => setSymbol(e.target.value.toUpperCase())}
        className="border p-2 mb-2 w-full"
      />
      <button onClick={fetchRecommendation} className="bg-blue-600 text-white p-2 rounded">
        احصل على التوصية
      </button>

      {result && (
        <div className="mt-4 bg-gray-100 p-4 rounded shadow">
          <h3 className="text-lg font-bold">{result.symbol}</h3>
          <p>📈 السعر الحالي: {result.price.regularMarketPrice.raw}</p>
          <p>⬆️ أعلى: {result.price.regularMarketDayHigh.raw}</p>
          <p>⬇️ أدنى: {result.price.regularMarketDayLow.raw}</p>
          <p>🔊 الحجم: {result.price.regularMarketVolume.raw}</p>
          <hr className="my-2" />
          <p>💡 التوصية:</p>
          <pre className="text-green-700 whitespace-pre-wrap">{result.recommendation}</pre>
        </div>
      )}
    </div>
  );
}

const express = require('express');
const router = express.Router();
const axios = require('axios');
const { Configuration, OpenAIApi } = require('openai');

// إعداد GPT
const configuration = new Configuration({
  apiKey: process.env.OPENAI_API_KEY,
});
const openai = new OpenAIApi(configuration);

// دالة لجلب بيانات السهم من RapidAPI
async function fetchStockData(symbol) {
  const url = `https://yh-finance.p.rapidapi.com/stock/v2/get-summary?symbol=${symbol}&region=US`;

  const headers = {
    'X-RapidAPI-Key': process.env.RAPIDAPI_KEY,
    'X-RapidAPI-Host': 'yh-finance.p.rapidapi.com',
  };

  const response = await axios.get(url, { headers });
  return response.data;
}

// توصية GPT
async function generateRecommendation(stockData, symbol) {
  const price = stockData.price;

  const prompt = `
أعطني توصية فنية لحظية للسهم ${symbol} بناءً على:
السعر الحالي: ${price?.regularMarketPrice?.raw}
أعلى سعر اليوم: ${price?.regularMarketDayHigh?.raw}
أدنى سعر اليوم: ${price?.regularMarketDayLow?.raw}
الحجم الحالي: ${price?.regularMarketVolume?.raw}
  `;

  const response = await openai.createChatCompletion({
    model: 'gpt-4',
    messages: [{ role: 'user', content: prompt }],
  });

  return response.data.choices[0].message.content;
}

// المسار الرئيسي
router.get('/:symbol', async (req, res) => {
  const symbol = req.params.symbol;

  try {
    const stockData = await fetchStockData(symbol);
    const recommendation = await generateRecommendation(stockData, symbol);

    res.json({
      symbol,
      price: stockData.price,
      recommendation,
    });
  } catch (err) {
    console.error('خطأ في التوصية:', err.message);
    res.status(500).json({ error: 'فشل التحليل اللحظي للسهم.' });
  }
});

module.exports = router;
