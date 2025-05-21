import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import axios from 'axios';

dotenv.config();
const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());

app.post('/recommend', async (req, res) => {
  const { symbol } = req.body;

  try {
    const yahooRes = await axios.get(`https://yahoo-finance15.p.rapidapi.com/api/yahoo/qu/quote/${symbol}`, {
      headers: {
        'X-RapidAPI-Key': process.env.RAPIDAPI_KEY,
        'X-RapidAPI-Host': 'yahoo-finance15.p.rapidapi.com',
      },
    });

    const data = yahooRes.data[0];
    const prompt = `
سهم: ${data.symbol}
السعر الحالي: ${data.regularMarketPrice}
الأعلى اليوم: ${data.regularMarketDayHigh}
الأدنى اليوم: ${data.regularMarketDayLow}
الحجم: ${data.regularMarketVolume}

اعطني:
- سعر شراء مناسب
- هدف أول
- هدف ثاني
- وقف الخسارة
اعتمد على التحليل الفني فقط.
`;

    const aiRes = await axios.post('https://api.openai.com/v1/chat/completions', {
      model: 'gpt-3.5-turbo',
      messages: [{ role: 'user', content: prompt }],
    }, {
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${process.env.OPENAI_API_KEY}`,
      },
    });

    const result = aiRes.data.choices[0].message.content;
    res.json({ recommendation: result });

  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'فشل في جلب التوصية' });
  }
});

app.listen(PORT, () => {
  console.log(`✅ Server running on http://localhost:${PORT}`);
});
