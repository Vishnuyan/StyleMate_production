import React from "react";
import CanvasTryOn from "../components/CanvasTryOn";

const API_BASE = "http://localhost:8000/api/necklace";

export default function Accessories() {
  const [image, setImage] = React.useState<File | null>(null);
  const [imagePreview, setImagePreview] = React.useState<string | null>(null);

  const [features, setFeatures] = React.useState<any>(null);
  const [recommendation, setRecommendation] = React.useState<any>(null);
  const [prompt, setPrompt] = React.useState("");
  const [generatedImage, setGeneratedImage] = React.useState("");

  const [openAiTryOnImage, setOpenAiTryOnImage] = React.useState("");
  const [showCanvasTryOn, setShowCanvasTryOn] = React.useState(false);

  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState("");

  const [wardrobeItems, setWardrobeItems] = React.useState<any[]>([]);
  const [selectedNecklace, setSelectedNecklace] = React.useState<any>(null);

  const [showAccessoryUpload, setShowAccessoryUpload] =
    React.useState(false);

  const [accessoryImage, setAccessoryImage] =
    React.useState<File | null>(null);

  const resetAll = () => {
    setImage(null);
    setImagePreview(null);
    setFeatures(null);
    setRecommendation(null);
    setPrompt("");
    setGeneratedImage("");
    setOpenAiTryOnImage("");
    setShowCanvasTryOn(false);
    setWardrobeItems([]);
    setSelectedNecklace(null);
    setError("");
    setShowAccessoryUpload(false);
    setAccessoryImage(null);
  };

  // Upload outfit image
  const handleImageChange = (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setImage(file);
    setImagePreview(URL.createObjectURL(file));

    setFeatures(null);
    setGeneratedImage("");
    setOpenAiTryOnImage("");
    setWardrobeItems([]);
    setSelectedNecklace(null);
    setError("");
  };

  // Upload necklace to wardrobe
  const handleAccessoryUpload = async () => {
    if (!accessoryImage) {
      setError("Please upload necklace image");
      return;
    }

    setLoading(true);

    try {
      const formData = new FormData();
      formData.append("file", accessoryImage);

      const res = await fetch(
        "http://localhost:8000/api/accessories/upload-accessory",
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await res.json();

      if (data.error) {
        setError(data.error);
        return;
      }

      alert("Necklace saved successfully!");
      setShowAccessoryUpload(false);
      setAccessoryImage(null);

    } catch {
      setError("Failed to upload necklace");
    } finally {
      setLoading(false);
    }
  };

  // Extract features
  const handleExtract = async () => {
    if (!image) return;

    setLoading(true);

    try {
      const formData = new FormData();
      formData.append("file", image);

      const res = await fetch(`${API_BASE}/extract`, {
        method: "POST",
        body: formData,
      });

      const data = await res.json();

      setFeatures(data);

    } catch {
      setError("Feature extraction failed");
    } finally {
      setLoading(false);
    }
  };

  // Generate necklace flow
  const handleGenerateNecklace = async () => {
    if (!features) {
      setError("Extract features first");
      return;
    }

    setLoading(true);

    try {
      // Step 1: Get recommendation from ML model
      const recommendRes = await fetch(
        `${API_BASE}/recommend`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify(features)
        }
      );

      if (!recommendRes.ok) {
        throw new Error("Failed to get recommendation");
      }

      const recommendData = await recommendRes.json();
      console.log("Recommendation:", recommendData);
      setRecommendation(recommendData);

      // Step 2: Build correct format for prompt generation
      const modelRecommendation = recommendData.model_recommendation;
      const promptRequest = {
        necklace_style: modelRecommendation.necklace_style || "",
        metal: modelRecommendation.metal || "",
        input: {
          skin_tone: features.skin_tone || "",
          neckline: features.neckline || "",
          dress_color: features.dress_color || ""
        }
      };

      console.log("Prompt request:", promptRequest);

      const promptRes = await fetch(
        `${API_BASE}/generate/prompt`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify(promptRequest)
        }
      );

      if (!promptRes.ok) {
        const errorData = await promptRes.json().catch(() => ({}));
        console.error("Prompt error:", errorData);
        throw new Error("Failed to generate prompt");
      }

      const promptData = await promptRes.json();
      console.log("Generated prompt:", promptData);
      setPrompt(promptData.prompt);

      // Step 3: Generate image
      const imageRes = await fetch(
        `${API_BASE}/generate/image`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            prompt: promptData.prompt
          })
        }
      );

      if (!imageRes.ok) {
        const errorData = await imageRes.json().catch(() => ({}));
        console.error("Image error:", errorData);
        throw new Error("Failed to generate image");
      }

      const imageData = await imageRes.json();
      console.log("Generated image:", imageData);

      const imageUrl =
        imageData.image_url.startsWith("/")
          ? `http://localhost:8000${imageData.image_url}`
          : imageData.image_url;

      setGeneratedImage(imageUrl);

    } catch (err: any) {
      console.error("Full error:", err);
      setError(err.message || "Necklace generation failed");
    } finally {
      setLoading(false);
    }
  };

  // try-on
  const handleOpenAiTryOn = async () => {
    if (!image || !generatedImage) return;

    setLoading(true);

    try {
      const formData = new FormData();
      formData.append("person_image", image);

      const necklaceRes = await fetch(generatedImage);
      const necklaceBlob = await necklaceRes.blob();

      formData.append(
        "necklace_image",
        necklaceBlob,
        "necklace.png"
      );

      const res = await fetch(
        `${API_BASE}/virtual-tryon`,
        {
          method: "POST",
          body: formData
        }
      );

      const data = await res.json();

      const finalUrl =
        data.image_url.startsWith("/")
          ? `http://localhost:8000${data.image_url}`
          : data.image_url;

      setOpenAiTryOnImage(finalUrl);

    } catch {
      setError("Virtual try-on failed");
    } finally {
      setLoading(false);
    }
  };

  // Fetch all wardrobe necklaces
  const handleFetchWardrobe = async () => {
    if (!features) {
      setError("Please extract features first");
      return;
    }

    setLoading(true);

    try {
      const res = await fetch(
        "http://localhost:8000/api/accessories/get-accessories"
      );

      const data = await res.json();

      setWardrobeItems(data.accessories || []);

    } catch {
      setError("Failed to fetch wardrobe");
    } finally {
      setLoading(false);
    }
  };

  // Suggest best wardrobe necklace
  const handleSuggestWardrobe = async () => {
    if (!features || wardrobeItems.length === 0) return;

    setLoading(true);

    try {
      const res = await fetch(
        "http://localhost:8000/api/accessories/recommend-accessory",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            features,
            accessories: wardrobeItems
          })
        }
      );

      const data = await res.json();
      setSelectedNecklace(data.best_match);

    } catch {
      setError("Failed to recommend wardrobe necklace");
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteAccessory = async (
  id: string
) => {
  try {
    const response = await fetch(
      `http://localhost:8000/api/accessories/delete-accessory/${id}`,
      {
        method: "DELETE"
      }
    );

    const data = await response.json();

    if (data.error) {
      alert(data.error);
      return;
    }

    alert("Accessory deleted successfully");

    // remove deleted item from UI
    setWardrobeItems((prev: any[]) =>
      prev.filter(
        (item) => item.id !== id
      )
    );

  } catch (error) {
    console.log(error);
    alert("Delete failed");
  }
};
  return (
    <div className="max-w-6xl mx-auto px-4 py-10 text-white">

      {/* Title */}
      <div className="text-center mb-10">
        <h1 className="text-6xl font-serif text-gold">
          AI Accessories Guide
        </h1>

        <p className="mt-4 text-white/70">
          Upload photos • Get personalized necklace recommendations
        </p>
      </div>

      {/* Upload Outfit */}
      {!imagePreview && (
        <div className="glass-card p-10 text-center">
          <h2 className="text-4xl font-serif mb-8">
            Upload Outfit Photo
          </h2>

          <label className="cursor-pointer block border-2 border-dashed border-white/20 rounded-3xl h-[350px] flex items-center justify-center">
            <span className="text-white/60 text-xl">
              Upload your outfit image
            </span>

            <input
              type="file"
              accept="image/*"
              className="hidden"
              onChange={handleImageChange}
            />
          </label>

          {/* Upload accessory button */}
          <div className="mt-8">
            <button
              onClick={() => setShowAccessoryUpload(true)}
              className="px-6 py-3 border border-gold text-gold rounded-full"
            >
              Upload Accessories For Wardrobe
            </button>
          </div>
        </div>
      )}

      {/* Outfit preview */}
      {imagePreview && !features && (
        <div className="glass-card p-10 text-center">
          <img
            src={imagePreview}
            className="max-h-[500px] object-contain mx-auto rounded-2xl mb-8"
          />
          <button
            onClick={resetAll}
            className="px-8 py-3 border border-white/30 rounded-lg"
          >
            Back
          </button>
          <button
            onClick={handleExtract}
            className="luxury-button"
          >
            Extract Features
          </button>
        </div>
      )}

      {/* Features */}
      {features && !generatedImage && wardrobeItems.length === 0 && (
        <div className="glass-card p-10 text-center">
          <h2 className="text-3xl mb-6">
            Extracted Features
          </h2>

          <div className="grid md:grid-cols-3 gap-6">
            <div className="glass-card p-4">
              Skin Tone: {features.skin_tone}
            </div>

            <div className="glass-card p-4">
              Neckline: {features.neckline}
            </div>

            <div className="glass-card p-4">
              Dress Color: {features.dress_color}
            </div>
          </div>

          <div className="flex justify-center gap-6 mt-8">
            <button
              onClick={() => {
              setFeatures(null);
              setImage(null);
              setImagePreview(null);
            }}
            className="px-8 py-3 border border-white/30 rounded-lg"
            >
              Back
            </button>

            <button
              onClick={handleGenerateNecklace}
              className="luxury-button"
            >
              Generate Necklace
            </button>

            <button
              onClick={handleFetchWardrobe}
              className="px-6 py-3 bg-gold text-black rounded-full"
            >
              Find From Wardrobe
            </button>
          </div>
        </div>
      )}

      {/* Generated necklace */}
      {generatedImage && (
        <div className="glass-card p-10 text-center mt-8">
          <h2 className="text-3xl mb-6">
            AI Generated Necklace
          </h2>

          <img
            src={generatedImage}
            className="w-80 mx-auto rounded-2xl mb-8"
          />

          <div className="flex justify-center gap-6">
            <button
              onClick={() => {
              setGeneratedImage("");
              setRecommendation(null);
              setPrompt("");
            }}
            className="px-8 py-3 border border-white/30 rounded-lg"
            >
              Back
            </button>
            <button
              onClick={() => setShowCanvasTryOn(true)}
              className="luxury-button"
            >
              Canvas Try-On
            </button>

            <button
              onClick={handleOpenAiTryOn}
              className="px-6 py-3 bg-gold text-black rounded-full"
            >
              Try-On
            </button>
          </div>
        </div>
      )}

      {/* Canvas Try On */}
      {showCanvasTryOn && (
        <CanvasTryOn
          userImage={imagePreview}
          necklaceImage={generatedImage}
        />
      )}

      {/* Try-on Result */}
      {openAiTryOnImage && (
        <div className="glass-card p-10 text-center mt-8">
          <h2 className="text-3xl mb-6">
            Virtual Try-On Result
          </h2>

          <img
            src={openAiTryOnImage}
            className="w-96 mx-auto rounded-2xl"
          />
        </div>
      )}

      {/* Wardrobe items */}
      {wardrobeItems.length > 0 && (
        <div className="glass-card p-10 mt-8">
          <h2 className="text-3xl text-center mb-8">
            Your Wardrobe
          </h2>

          {/* <div className="grid md:grid-cols-3 gap-6">
            {wardrobeItems.map((item, index) => (
              <div
                key={index}
                className="glass-card p-4 text-center"
              >
                <img
                  src={item.image_url}
                  className="h-48 w-full object-contain rounded-xl mb-4 bg-white p-2"
                />

                <p>{item.style}</p>
              </div>
            ))}
            
          </div> */}

          <div className="grid md:grid-cols-3 gap-6">
          {wardrobeItems.map((item, index) => (
            <div
              key={index}
              className="glass-card p-4 text-center"
            >
              <img
                src={item.image_url}
                className="h-48 w-full object-contain rounded-xl mb-4 bg-white p-2"
              />

              <p>{item.style}</p>

            <button
              onClick={() =>
              handleDeleteAccessory(item.id)
            }
              className="mt-3 px-4 py-2 bg-red-500 text-white rounded-lg"
            >
        Delete
      </button>
    </div>
  ))}
</div>

          <div className="text-center mt-8">
            <button
              onClick={handleSuggestWardrobe}
              className="luxury-button"
            >
              Suggest Best Necklace
            </button>
          </div>
        </div>
      )}

      {/* Best wardrobe match */}
      {selectedNecklace && (
        <div className="glass-card p-10 text-center mt-8">
          <h2 className="text-3xl text-gold mb-6">
            Best Match From Wardrobe
          </h2>

          <img
            src={selectedNecklace.image_url}
            className="w-80 mx-auto rounded-2xl mb-6"
          />

          <div className="flex justify-center gap-6">
  <button
    onClick={() => {
      setSelectedNecklace(null);
      setWardrobeItems([]);
    }}
    className="px-8 py-3 border border-white/30 rounded-lg"
  >
    Back
  </button>

  <button
    onClick={resetAll}
    className="px-8 py-3 border border-white/30 rounded-lg"
  >
    Start Over
  </button>
</div>
        </div>
      )}

      {/* Upload accessory modal */}
      {showAccessoryUpload && (
        <div className="fixed inset-0 bg-black/70 flex justify-center items-center z-50">
          <div className="bg-gray-900 p-6 rounded-xl w-[450px] text-center">
            <h2 className="text-2xl text-gold mb-6">
              Upload Necklace
            </h2>

            <input
              type="file"
              accept="image/*"
              onChange={(e) =>
                setAccessoryImage(
                  e.target.files?.[0] || null
                )
              }
              className="w-full mb-6"
            />

            <div className="flex justify-center gap-4">
              <button
                onClick={handleAccessoryUpload}
                className="luxury-button"
              >
                Save Necklace
              </button>

              <button
                onClick={() =>
                  setShowAccessoryUpload(false)
                }
                className="px-6 py-3 border border-white/20 rounded-lg"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {loading && (
        <p className="text-center mt-6">
          Loading...
        </p>
      )}

      {error && (
        <p className="text-red-500 text-center mt-6">
          {error}
        </p>
      )}
    </div>
  );
}