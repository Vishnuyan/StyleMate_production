import React, { useState } from "react";
import { motion } from "framer-motion";
import {
  Upload,
  Sparkles,
  RefreshCw,
  Image as ImageIcon,
} from "lucide-react";
import toast from "react-hot-toast";
import { apiFetch } from "../lib/api";

const occasions = [
  "Wedding",
  "Birthday",
  "Office Party",
  "Casual Outing",
  "Formal Event",
  "Beach Event",
  "Dinner Date",
  "Sports Event",
];

export default function Outfit() {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [imagePreviews, setImagePreviews] = useState<string[]>([]);
  const [selectedImageIndex, setSelectedImageIndex] = useState<number | null>(null);
  const [occasion, setOccasion] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleFileChange = (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const files = Array.from(e.target.files || []);

    if (!files.length) return;

    setSelectedFiles(files);

    const previews = files.map((file) =>
      URL.createObjectURL(file)
    );

    setImagePreviews(previews);
    setSelectedImageIndex(null);
    setResult(null);
  };

  const handleImageSelect = (index: number) => {
    setSelectedImageIndex(index);
  };

  const handleSubmit = async (
    e: React.FormEvent
  ) => {
    e.preventDefault();

    if (!selectedFiles.length) {
      toast.error("Please upload image");
      return;
    }

    if (
      selectedFiles.length > 1 &&
      selectedImageIndex === null
    ) {
      toast.error("Please select one image");
      return;
    }

    if (!occasion) {
      toast.error("Please select occasion");
      return;
    }

    setLoading(true);

    try {
      const imageFile =
        selectedFiles[
          selectedImageIndex !== null
            ? selectedImageIndex
            : 0
        ];

      const formData = new FormData();
      formData.append("image", imageFile);
      formData.append("occasion", occasion);

      const response = await apiFetch(
        "/api/outfit/predict",
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (response.ok) {
        setResult({
          ...data,
          selectedImage:
            imagePreviews[
              selectedImageIndex !== null
                ? selectedImageIndex
                : 0
            ],
        });

        toast.success("Outfit recommendation ready!");
      } else {
        toast.error(
          data.error || "Prediction failed"
        );
      }
    } catch (error) {
      console.error(error);
      toast.error("Server connection failed");
    } finally {
      setLoading(false);
    }
  };

  const resetAll = () => {
    setSelectedFiles([]);
    setImagePreviews([]);
    setSelectedImageIndex(null);
    setOccasion("");
    setResult(null);
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-10">

      {/* Header */}
      <div className="text-center mb-10">
        <h1 className="text-5xl md:text-6xl font-serif font-bold bg-gradient-to-r from-amber-300 to-yellow-200 bg-clip-text text-transparent">
          Outfit Recommendation
        </h1>

        <p className="text-white/70 mt-4 text-lg">
          Upload event or outfit images and get AI-powered styling recommendations
        </p>
      </div>

      {/* Upload Section */}
      {!result && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-card p-8"
        >
          <form onSubmit={handleSubmit}>
            
            {/* Upload Box */}
            <label className="cursor-pointer block">
              <div className="border-2 border-dashed border-white/20 rounded-2xl p-10 text-center bg-black/20 hover:border-amber-400 transition">
                <Upload
                  size={40}
                  className="mx-auto text-amber-400 mb-4"
                />

                <p className="text-white/70 text-lg">
                  Upload one or multiple outfit images
                </p>
              </div>

              <input
                type="file"
                multiple
                accept="image/*"
                className="hidden"
                onChange={handleFileChange}
              />
            </label>

            {/* Image Preview */}
            {imagePreviews.length > 0 && (
              <div className="mt-8">
                <h3 className="text-xl font-semibold text-white mb-4">
                  Select Image
                </h3>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {imagePreviews.map(
                    (preview, index) => (
                      <div
                        key={index}
                        onClick={() =>
                          handleImageSelect(index)
                        }
                        className={`cursor-pointer rounded-xl overflow-hidden border-2 ${
                          selectedImageIndex === index
                            ? "border-amber-400"
                            : "border-white/10"
                        }`}
                      >
                        <img
                          src={preview}
                          alt="preview"
                          className="w-full h-40 object-cover"
                        />
                      </div>
                    )
                  )}
                </div>
              </div>
            )}

            {/* Occasion */}
            {selectedFiles.length > 0 && (
              <div className="mt-8">
                <label className="block mb-3 text-white font-medium">
                  Select Occasion
                </label>

                <select
                  value={occasion}
                  onChange={(e) =>
                    setOccasion(e.target.value)
                  }
                  className="w-full bg-black/30 border border-white/20 rounded-xl px-4 py-3 text-black bg-white"
                >
                  <option value="">
                    Choose occasion
                  </option>

                  {occasions.map((item) => (
                    <option
                      key={item}
                      value={item}
                    >
                      {item}
                    </option>
                  ))}
                </select>
              </div>
            )}

            {/* Submit */}
            <div className="text-center mt-8">
              <button
                type="submit"
                disabled={loading}
                className="luxury-button px-8 py-4 flex items-center gap-2 mx-auto"
              >
                {loading ? (
                  "Analyzing..."
                ) : (
                  <>
                    <Sparkles size={20} />
                    Get Recommendation
                  </>
                )}
              </button>
            </div>
          </form>
        </motion.div>
      )}

      {/* Result Section */}
      {result && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="glass-card p-8 mt-8"
        >
          <div className="flex justify-between items-center mb-8">
            <h2 className="text-3xl font-serif font-bold text-white">
              Your Outfit Result
            </h2>

            <button
              onClick={resetAll}
              className="flex items-center gap-2 px-4 py-2 border border-white/20 rounded-lg hover:bg-white/5"
            >
              <RefreshCw size={18} />
              Start Over
            </button>
          </div>

          {/* Selected Image */}
          <div className="mb-8">
            <img
              src={result.selectedImage}
              alt="selected"
              className="w-full max-w-md mx-auto rounded-2xl"
            />
          </div>

          {/* Color */}
          <div className="bg-white/5 rounded-2xl p-6 mb-6">
            <h3 className="text-amber-300 text-xl mb-2">
              Dominant Color
            </h3>
            <p className="text-white text-lg">
              {result.predicted_color}
            </p>
            <p className="text-white/60 mt-2">
              Confidence: {result.confidence}%
            </p>
          </div>

          {/* Description */}
          <div className="bg-white/5 rounded-2xl p-6 mb-6">
            <h3 className="text-amber-300 text-xl mb-2">
              Description
            </h3>
            <p className="text-white/80">
              {result.description}
            </p>
          </div>

          {/* Matching Colors */}
          <div className="bg-white/5 rounded-2xl p-6 mb-6">
            <h3 className="text-amber-300 text-xl mb-2">
              Matching Colors
            </h3>

            <div className="flex flex-wrap gap-3">
              {result.matching_colors?.map(
                (color: any, index: number) => (
                  <span
                    key={index}
                    className="px-4 py-2 rounded-full bg-amber-500 text-black font-medium"
                  >
                    {typeof color === "string"
                      ? color
                      : color.name}
                  </span>
                )
              )}
            </div>
          </div>

          {/* Men */}
          <div className="bg-white/5 rounded-2xl p-6 mb-6">
            <h3 className="text-amber-300 text-xl mb-4">
              👔 Men Recommendations
            </h3>

            <ul className="space-y-2 text-white/80">
              {result.men_recommendations?.map(
                (item: string, index: number) => (
                  <li key={index}>• {item}</li>
                )
              )}
            </ul>
          </div>

          {/* Women */}
          <div className="bg-white/5 rounded-2xl p-6">
            <h3 className="text-amber-300 text-xl mb-4">
              👗 Women Recommendations
            </h3>

            <ul className="space-y-2 text-white/80">
              {result.women_recommendations?.map(
                (item: string, index: number) => (
                  <li key={index}>• {item}</li>
                )
              )}
            </ul>
          </div>
        </motion.div>
      )}
    </div>
  );
}