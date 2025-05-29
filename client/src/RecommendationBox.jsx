import { useState } from "react";
import axios from "axios";

const RecommendationBox = () => {
  const [symbol, setSymbol] = useState("AAPL");
  const [recommendation, setRecommendation] = useState("");
  const [loading, setLoading] = useState(false);

  const getRecommendation = async () => {
    setLoading(true);
    try {
      const res = await axios.post("http://localhost:3001/recommend", {
        symbol,
      });
      setRecommendation(res.data.recommendation);
    } catch (err) {
      setRecommendation("⚠️ حدث خطأ في جلب التوصية.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4 bg-white rounded shadow">
      <h2 className="text-xl font-bold mb-2">توصية لحظية</h2>
      <input
        type="text"
        value={symbol}
        onChange={(e) => setSymbol(e.target.value.toUpperCase())}
        className="border p-2 mr-2"
      />
      <button onClick={getRecommendation} className="bg-blue-500 text-white px-4 py-2 rounded">
        تحليل
      </button>
      <div className="mt-4">{loading ? "⏳ جاري التحميل..." : recommendation}</div>
    </div>
  );
};

export default RecommendationBox;
