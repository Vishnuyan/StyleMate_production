import React, { useState } from "react";
import { Sparkles } from "lucide-react";
import toast from "react-hot-toast";
import { wardrobeService } from "../services/api";
import ReactMarkdown from "react-markdown";

export default function Stylist() {
  const [prompt, setPrompt] = useState("");
  const [city, setCity] = useState("");
  const [result, setResult] = useState("");

  const userId = localStorage.getItem("userId") || "demo_user";

  const generateRecommendation = async () => {
    if (!prompt) {
      toast.error("Enter event description");
      return;
    }

    try {
      const res = await wardrobeService.getProRecommendation(
        userId,
        prompt,
        city
      );

      console.log(res.data);

      setResult(res.data.recommendation);
    } catch (error) {
      console.error(error);
      toast.error("Failed to generate recommendation");
    }
  };

  return (
    <div className="glass-card p-8 max-w-4xl mx-auto">
      <h2 className="text-3xl font-serif text-amber-300 mb-6">
        AI Stylist
      </h2>

      <input
        type="text"
        placeholder="Enter city"
        value={city}
        onChange={(e) => setCity(e.target.value)}
        className="w-full p-3 rounded-lg bg-white/10 mb-4"
      />

      <textarea
        placeholder="Describe your event"
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        className="w-full p-3 rounded-lg bg-white/10 h-40"
      />

      <button
        onClick={generateRecommendation}
        className="luxury-button mt-6 px-8 py-3 flex items-center gap-2"
      >
        <Sparkles size={18} />
        Generate Recommendation
      </button>

      {result && (
  <div className="mt-8 bg-white/5 p-6 rounded-xl prose prose-invert max-w-none">
    <ReactMarkdown
      components={{
        img: ({ node, ...props }) => (
          <img
            {...props}
            className="w-full max-w-md rounded-xl mt-4 mb-4"
          />
        )
      }}
    >
      {result}
    </ReactMarkdown>
  </div>
)}
    </div>
  );
}