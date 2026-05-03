import React, { useState, useEffect } from "react";
import { Upload, Sparkles } from "lucide-react";
import toast from "react-hot-toast";
import { wardrobeService } from "../services/api";

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const userId = localStorage.getItem("userId") || "demo_user";

  useEffect(() => {
    return () => {
      if (preview) {
        URL.revokeObjectURL(preview);
      }
    };
  }, [preview]);

  const handleUpload = async () => {
    if (!file) {
      toast.error("Upload image first");
      return;
    }

    setLoading(true);

    try {
      const res = await wardrobeService.uploadItem(
        file,
        userId,
        true
      );

      console.log("Upload response:", res.data);

      setResult(res.data.data);
      setFile(null);
      setPreview(null);
      toast.success("Item uploaded successfully");
    } catch (err) {
      console.error(err);
      toast.error("Upload failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-card p-8 max-w-3xl mx-auto">
      <h2 className="text-3xl font-serif text-amber-300 mb-6">
        Upload Wardrobe Item
      </h2>

      <label className="cursor-pointer block">
        <div className="border-2 border-dashed border-white/20 rounded-xl p-10 text-center">
          {preview ? (
            <img
              src={preview}
              alt="Wardrobe Preview"
              className="w-full h-80 object-contain rounded-lg"
            />
          ) : (
            <>
              <Upload size={40} className="mx-auto text-amber-300" />
              <p className="mt-3 text-white/70">
                Upload clothing image
              </p>
            </>
          )}
        </div>

        <input
          type="file"
          hidden
          accept="image/*"
          onChange={(e) => {
            const selected = e.target.files?.[0];
            if (!selected) return;

            setFile(selected);
            setPreview(URL.createObjectURL(selected));
          }}
        />
      </label>

      <button
        onClick={handleUpload}
        className="luxury-button mt-6 px-8 py-3 flex items-center gap-2"
      >
        <Sparkles size={18} />
        {loading ? "Analyzing..." : "Analyze Item"}
      </button>

      {result && (
        <div className="mt-8 bg-white/5 p-6 rounded-xl">
          <h3 className="text-lg font-semibold mb-3 text-amber-300">Upload Details</h3>
          {/* <p><strong>Item:</strong> {result.itemName || "Not detected"}</p> */}
          <p><strong>Category:</strong> {result.category || "Not detected"}</p>
          <p><strong>Color:</strong> {result.color || "Not detected"}</p>
          <p><strong>Fabric:</strong> {result.fabricType || "Not detected"}</p>
        </div>
      )}
    </div>
  );
}