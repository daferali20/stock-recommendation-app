import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';

dotenv.config();

const app = express();

// ✅ هذا السطر هو الأهم، تأكد أنه موجود ومُعد بشكل صحيح:
app.use(cors({
  origin: 'https://stock-recommendation-app.vercel.app',
  methods: ['GET', 'POST', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));

app.use(express.json());

// بقية الكود...


// نقطة نهاية للتوصيات الذكية
app.post('/recommend', async (req, res) => {
  const { symbol } = req.body;

  try {
    // 1. جلب بيانات السوق من Yahoo Finance API
    const marketRes = await axios.get(
      `https://yahoo-finance15.p.rapidapi.com/api/yahoo/qu/quote/${symbol}`,
      {
        headers: {
          'X-RapidAPI-Key': process.env.RAPIDAPI_KEY,
          'X-RapidAPI-Host': 'yahoo-finance15.p.rapidapi.com'
        }
      }
    );

    const stock = marketRes.data[0];

    const { regularMarketPrice, regularMarketDayHigh, regularMarketDayLow, regularMarketVolume } = stock;

    // 2. إرسال البيانات إلى OpenAI لتوليد التوصية
    const prompt = `السهم: ${symbol}\nالسعر الحالي: ${regularMarketPrice}\nأعلى سعر اليوم: ${regularMarketDayHigh}\nأدنى سعر اليوم: ${regularMarketDayLow}\nالحجم: ${regularMarketVolume}\n\nقدّم توصية فنية: سعر الشراء، هدف البيع، ووقف الخسارة.`;

    const aiRes = await axios.post(
      'https://api.openai.com/v1/chat/completions',
      {
        model: 'gpt-3.5-turbo',
        messages: [
          { role: 'system', content: 'أنت محلل فني للأسهم.' },
          { role: 'user', content: prompt }
        ]
      },
      {
        headers: {
          'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`,
          'Content-Type': 'application/json'
        }
      }
    );

    const recommendation = aiRes.data.choices[0].message.content;

    // 3. إرسال البيانات إلى الواجهة
    res.json({
      symbol,
      currentPrice: regularMarketPrice,
      high: regularMarketDayHigh,
      low: regularMarketDayLow,
      volume: regularMarketVolume,
      recommendation
    });

  } catch (err) {
    console.error('❌ خطأ:', err.response?.data || err.message);
    res.status(500).json({ error: 'فشل في جلب البيانات أو التوصية' });
  }
});

// بدء الخادم
const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  console.log(`✅ الخادم يعمل على المنفذ ${PORT}`);
});
