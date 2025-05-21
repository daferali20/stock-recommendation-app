import cors from 'cors';

// تأكد من كتابة اسم الدومين الصحيح لموقع Vercel
app.use(cors({
  origin: 'https://stock-recommendation-app.vercel.app', 
  methods: ['GET', 'POST', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));
