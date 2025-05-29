import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

// إعداد CORS للسماح للواجهة بالاتصال بالخادم
app.use(cors({
  origin: 'https://stock-recommendation-app.vercel.app', // بدون "/"
  methods: ['GET', 'POST'],
  allowedHeaders: ['Content-Type'],
}));

app.use(express.json());

// ✅ مسار ترحيبي ل GET /
app.get('/', (req, res) => {
  res.send('✅ Stock Recommendation Server is running.');
});

// نقطة النهاية لتوليد التوصيات
app.post('/recommend', async (req, res) => {
  // كود الاتصال بـ OpenAI API هنا...
});

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
