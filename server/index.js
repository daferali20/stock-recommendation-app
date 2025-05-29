import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import axios from "axios";

dotenv.config();
const app = express();
const PORT = process.env.PORT || 3001;

app.use(cors());
app.use(express.json());

app.post("/recommend", async (req, res) => {
  const { symbol } = req.body;
  if (!symbol) return res.status(400).json({ error: "Missing symbol" });

  try {
    // جلب البيانات من RapidAPI (مثل بيانات السعر والتحليل الفني)
    const rapidResponse = await axios.get(
      `https://twelve-data1.p.rapidapi.com/quote?symbol=${symbol}&interval=1min&format=json`,
      {
        headers: {
          "X-RapidAPI-Key": process.env.RAPIDAPI_KEY,
          "X-RapidAPI-Host": "twelve-data1.p.rapidapi.com",
        },
      }
    );

    const stockData = rapidResponse.data;

    // تحليل باستخدام OpenAI
    const openaiResponse = await axios.post(
      "https://api.openai.com/v1/chat/completions",
      {
        model: "gpt-4",
        messages: [
          {
            role: "system",
            content:
              "أنت خبير في تحليل الأسهم. اعتمد على البيانات المقدمة لتقديم توصية لحظية للسهم.",
          },
          {
            role: "user",
            content: `هذه بيانات السهم:\nالرمز: ${symbol}\nالسعر: ${stockData.price}\nالتغيير: ${stockData.change_percent}%\nهل السهم مناسب للشراء الآن؟`,
          },
        ],
        temperature: 0.7,
      },
      {
        headers: {
          Authorization: `Bearer ${process.env.OPENAI_API_KEY}`,
        },
      }
    );

    const recommendation =
      openaiResponse.data.choices?.[0]?.message?.content || "لا توجد توصية.";

    res.json({ recommendation });
  } catch (error) {
    console.error("Error in /recommend:", error.message);
    res.status(500).json({ error: "فشل في جلب التوصية" });
  }
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
