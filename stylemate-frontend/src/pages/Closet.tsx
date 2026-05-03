import React, { useEffect, useState } from "react";
import toast from "react-hot-toast";
import { Trash2 } from "lucide-react";
import { wardrobeService } from "../services/api";

export default function Closet() {
  const [items, setItems] = useState<any[]>([]);

  const userId = localStorage.getItem("userId") || "demo_user";

  useEffect(() => {
    loadItems();
  }, []);

  const loadItems = async () => {
    try {
      const res = await wardrobeService.getWardrobe(userId);

      console.log("Wardrobe items:", res.data);

      setItems(res.data.items || []);
    } catch (error) {
      console.error(error);
      toast.error("Failed to load wardrobe");
    }
  };

  const handleDelete = async (itemId: string) => {
    try {
      await wardrobeService.deleteWardrobeItem(itemId);

      // remove deleted item from UI immediately
      setItems((prevItems) =>
        prevItems.filter((item) => item._id !== itemId)
      );

      toast.success("Item deleted successfully");
    } catch (error) {
      console.error(error);
      toast.error("Delete failed");
    }
  };

  return (
    <div className="glass-card p-8">
      <h2 className="text-3xl font-serif text-amber-300 mb-6">
        My Closet
      </h2>

      {items.length === 0 ? (
        <p className="text-white/70">
          No wardrobe items found.
        </p>
      ) : (
        <div className="grid md:grid-cols-3 gap-6">
          {items.map((item) => (
            <div
              key={item._id}
              className="bg-white/5 rounded-xl p-4 relative"
            >
              {/* Delete Button */}
              <button
                onClick={() => handleDelete(item._id)}
                className="absolute top-3 right-3 bg-red-500 hover:bg-red-600 text-white p-2 rounded-full z-10"
              >
                <Trash2 size={18} />
              </button>

              {/* Image */}
              <img
                src={`http://localhost:8000/${item.imageUrl}`}
                alt={item.itemName}
                className="w-full h-60 object-cover rounded-lg"
                onError={(e) => {
                  console.log("Image failed:", item.imageUrl);
                }}
              />

              {/* Item details */}
              <h3 className="mt-3 font-semibold">
                {item.itemName}
              </h3>

              <p className="text-white/70">
                {item.category}
              </p>

              <p className="text-white/60">
                {item.color} • {item.fabricType}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}