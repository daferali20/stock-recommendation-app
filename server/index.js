import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import axios from 'axios';

dotenv.config();

const app = express();
const port = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());

app.get('/', (req, res) => {
  res.send('Backend is running!');
});

// نقطة الربط للتوصيات
app.post('/recommend', async (req, res) => {
  const { symbol } = req.body;

  try {
    // مثال لاستخدام RapidAPI
    const response = await axios.get('https://apidojo-yahoo-finance-v1.p.rapidapi.com/stock/v2/get-summary', {
      params: { symbol, region: 'US' },
      headers: {
        'X-RapidAPI-Key': process.env.RAPIDAPI_KEY,
        'X-RapidAPI-Host': 'apidojo-yahoo-finance-v1.p.rapidapi.com'
      }
    });

    const data = response.data;
    res.json({ recommendation: `تفاصيل السهم ${symbol}`, data });

  } catch (error) {
    console.error('Error fetching stock data:', error.message);
    res.status(500).json({ error: 'Failed to fetch stock data' });
  }
});

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});
