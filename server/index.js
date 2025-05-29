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
