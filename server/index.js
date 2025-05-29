import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import { Configuration, OpenAIApi } from "openai";

dotenv.config();

const app = express();
app.use(cors({
  origin: "https://stock-recommendation-app.vercel.app"
}));
app.use(express.json());

const configuration = new Configuration({
  apiKey: process.env.OPENAI_API_KEY,
});
const openai = new OpenAIApi(configuration);

app.get("/", (req, res) => {
  res.send("Server is running");
});

app.post('/recommend', async (req, res) => {
  try {
    const { stockSymbol } = req.body;

    if (!stockSymbol) {
      return res.status(400).json({ error: "Please provide stockSymbol in request body" });
    }

    // مثال على prompt ترسل للنموذج لتوليد توصية
    const prompt = `Please provide a short recommendation about the stock: ${stockSymbol}. Include buy/sell/hold advice and a brief explanation.`;

    const completion = await openai.createChatCompletion({
      model: "gpt-4o-mini", // أو "gpt-4" حسب ما هو متاح لديك
      messages: [{ role: "user", content: prompt }],
      max_tokens: 150,
      temperature: 0.7,
    });

    const recommendation = completion.data.choices[0].message.content;

    res.json({ recommendation });

  } catch (error) {
    console.error(error);
    res.status(500).json({ error: "Internal server error" });
  }
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
