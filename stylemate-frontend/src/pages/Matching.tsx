import React, { useState } from "react";
import { Users } from "lucide-react";
import { wardrobeService } from "../services/api";
import toast from "react-hot-toast";

export default function Matching() {
  const [users, setUsers] = useState("");
  const [result, setResult] = useState<any>(null);

  const handleMatch = async () => {
    try {
      const ids = users.split(",").map(id => id.trim());

      const res = await wardrobeService.matchMultiUser(
        ids,
        {
          type: "group",
          style: "casual"
        }
      );

      setResult(res.data);
    } catch {
      toast.error("Matching failed");
    }
  };

  return (
    <div className="glass-card p-8 max-w-4xl mx-auto">
      <h2 className="text-3xl font-serif text-amber-300 mb-6">
        Group Matching
      </h2>

      <input
        value={users}
        onChange={(e) => setUsers(e.target.value)}
        placeholder="user1,user2,user3"
        className="w-full p-3 rounded-lg bg-white/10"
      />

      <button
        onClick={handleMatch}
        className="luxury-button mt-6 px-8 py-3 flex items-center gap-2"
      >
        <Users size={18}/>
        Match Outfits
      </button>

      {result && (
        <div className="mt-8 bg-white/5 p-6 rounded-xl">
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}