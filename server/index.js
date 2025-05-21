
import cors from 'cors';
import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import axios from 'axios';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

// ✅ تفعيل CORS للسماح فقط لموقع Vercel
app.use(cors({
  origin: 'https://stock-recommendation-app.vercel.app',
  methods: ['GET', 'POST', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));

app.use(express.json());

app.get('/', (req, res) => {
  res.send('🟢 الخادم يعمل بنجاح');
});

app.post('/recommend', async (req, res) => {
  try {
    const { symbol } = req.body;

    const prompt = `حلل سهم ${symbol} بناءً على التحليل الفني. قدم التوصية مع سعر الشراء، الهدف، وقف الخسارة.`;

    const aiRes = await axios.post('https://api.openai.com/v1/chat/completions', {
      model: 'gpt-3.5-turbo',
      messages: [
        { role: 'system', content: 'أنت خبير في سوق الأسهم' },
        { role: 'user', content: prompt }
      ]
    }, {
      headers: {
        'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`,
        'Content-Type': 'application/json'
      }
    });

    const recommendation = aiRes.data.choices[0]?.message?.content || '❌ لم يتم توليد توصية.';

    res.json({ recommendation });

  } catch (err) {
    console.error('❌ خطأ في جلب التوصية:', err.response?.data || err.message);
    res.status(500).json({ error: 'حدث خطأ في جلب التوصية.' });
  }
});

app.listen(PORT, () => {
  console.log(`🚀 Server is running on port ${PORT}`);
});

// تأكد من كتابة اسم الدومين الصحيح لموقع Vercel
app.use(cors({
  origin: 'https://stock-recommendation-app.vercel.app', 
  methods: ['GET', 'POST', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));
