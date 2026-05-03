import React, { useState } from "react";
import {
  Upload,
  Shirt,
  Sparkles,
  Users
} from "lucide-react";

import UploadPage from "./Upload";
import Closet from "./Closet";
import Stylist from "./Stylist";
import Matching from "./Matching";

export default function Wardrobe() {
  const [tab, setTab] = useState("upload");

  const menu = [
    { id: "upload", label: "Upload", icon: <Upload size={18}/> },
    { id: "closet", label: "Closet", icon: <Shirt size={18}/> },
    { id: "stylist", label: "Stylist", icon: <Sparkles size={18}/> },
    { id: "matching", label: "Matching", icon: <Users size={18}/> },
  ];

  const renderPage = () => {
    switch (tab) {
      case "upload":
        return <UploadPage />;
      case "closet":
        return <Closet />;
      case "stylist":
        return <Stylist />;
      case "matching":
        return <Matching />;
      default:
        return <UploadPage />;
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-10">
      <h1 className="text-5xl font-serif text-center bg-gradient-to-r from-amber-300 to-yellow-200 bg-clip-text text-transparent mb-10">
        Smart Wardrobe
      </h1>

      <div className="flex flex-wrap justify-center gap-4 mb-10">
        {menu.map((item) => (
          <button
            key={item.id}
            onClick={() => setTab(item.id)}
            className={`px-6 py-3 rounded-full flex items-center gap-2 ${
              tab === item.id
                ? "bg-amber-400 text-black"
                : "bg-white/10 text-white"
            }`}
          >
            {item.icon}
            {item.label}
          </button>
        ))}
      </div>

      {renderPage()}
    </div>
  );
}