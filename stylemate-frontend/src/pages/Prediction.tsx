import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Camera, Sparkles, CheckCircle2, ChevronRight, Upload, RefreshCw } from 'lucide-react';
import toast from 'react-hot-toast';
import { apiFetch } from '../lib/api';

const categories = ["casual", "formal", "party"];

export default function Prediction() {
  const [step, setStep] = React.useState(1);
  const [bodyImagePreview, setBodyImagePreview] = React.useState<string | null>(null);
  const [skinImagePreview, setSkinImagePreview] = React.useState<string | null>(null);
  const [bodyFile, setBodyFile] = React.useState<File | null>(null);
  const [skinFile, setSkinFile] = React.useState<File | null>(null);
  const [category, setCategory] = React.useState('casual');
  const [loading, setLoading] = React.useState(false);
  const [result, setResult] = React.useState<any>(null);

  React.useEffect(() => {
    return () => {
      if (bodyImagePreview) URL.revokeObjectURL(bodyImagePreview);
      if (skinImagePreview) URL.revokeObjectURL(skinImagePreview);
    };
  }, [bodyImagePreview, skinImagePreview]);

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>, type: 'body' | 'skin') => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (!file.type.startsWith('image/')) {
      toast.error('Please upload an image');
      return;
    }
    const previewUrl = URL.createObjectURL(file);
    if (type === 'body') {
      setBodyFile(file);
      setBodyImagePreview(previewUrl);
    } else {
      setSkinFile(file);
      setSkinImagePreview(previewUrl);
    }
  };

  const getRecommendation = async () => {
    if (!bodyFile || !skinFile) {
      toast.error('Please upload both images');
      return;
    }

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('body_image', bodyFile);
      formData.append('skin_image', skinFile);
      formData.append('category', category);

      const response = await apiFetch('/api/recommend', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        setResult(data);
        setStep(4);
        toast.success('Your style guide is ready!');
      } else {
        toast.error(data?.detail || 'Recommendation failed');
      }
    } catch (error) {
      console.error(error);
      toast.error('Server connection failed');
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setStep(1);
    setBodyImagePreview(null);
    setSkinImagePreview(null);
    setBodyFile(null);
    setSkinFile(null);
    setResult(null);
  };

  const TierBadge = ({ tier }: { tier: string }) => {
    const colors: Record<string, string> = {
      excellent: 'bg-emerald-600/30 text-emerald-300 border-emerald-500/40',
      good: 'bg-blue-600/30 text-blue-300 border-blue-500/40',
      neutral: 'bg-gray-600/30 text-gray-300 border-gray-500/40',
      average: 'bg-amber-600/30 text-amber-300 border-amber-500/40',
      poor: 'bg-rose-600/30 text-rose-300 border-rose-500/40',
    };

    return (
      <span
        className={`inline-block px-2.5 py-1 text-xs font-medium rounded-full border capitalize ${colors[tier.toLowerCase()] || 'bg-gray-700/40 text-gray-300'}`}
      >
        {tier}
      </span>
    );
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-12">
      <div className="text-center mb-12">
        <h1 className="text-5xl md:text-6xl font-serif font-bold bg-gradient-to-r from-amber-300 to-yellow-200 bg-clip-text text-transparent">
          AI Style Guide
        </h1>
        <p className="text-white/70 mt-4 text-lg">
          Upload photos • Get personalized outfit recommendations
        </p>
      </div>

      {/* Progress bar */}
      <div className="flex justify-center mb-10 md:mb-14">
        {[1, 2, 3, 4].map((s) => (
          <div key={s} className="flex items-center">
            <div
              className={`w-9 h-9 md:w-11 md:h-11 rounded-full flex items-center justify-center border text-sm md:text-base font-medium
                ${step >= s
                  ? 'bg-amber-500 border-amber-500 text-black'
                  : 'border-white/30 text-white/50'}`}
            >
              {step > s ? <CheckCircle2 size={18} /> : s}
            </div>
            {s < 4 && <div className="w-12 md:w-20 h-px bg-white/20" />}
          </div>
        ))}
      </div>

      <AnimatePresence mode="wait">
        {/* STEP 1 – Body photo */}
        {step === 1 && (
          <motion.div
            key="1"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="glass-card p-8 md:p-10 text-center max-w-2xl mx-auto"
          >
            <h2 className="text-2xl md:text-3xl font-serif mb-6">Full Body Photo</h2>
            <label className="cursor-pointer block">
              <div className="border-2 border-dashed border-white/25 rounded-2xl aspect-[3/4] max-w-xs md:max-w-sm mx-auto overflow-hidden bg-black/20">
                {bodyImagePreview ? (
                  <img src={bodyImagePreview} alt="body preview" className="w-full h-full object-cover" />
                ) : (
                  <div className="h-full flex flex-col items-center justify-center text-white/50 gap-3">
                    <Upload size={44} />
                    <p className="text-lg">Upload full-body photo</p>
                  </div>
                )}
              </div>
              <input
                type="file"
                className="hidden"
                accept="image/*"
                onChange={(e) => handleImageUpload(e, 'body')}
              />
            </label>
            <button
              onClick={() => (bodyFile ? setStep(2) : toast.error("Please upload a body photo"))}
              className="luxury-button mt-8 px-10 py-3.5 text-lg"
              disabled={loading}
            >
              Next
            </button>
          </motion.div>
        )}

        {/* STEP 2 – Skin photo */}
        {step === 2 && (
          <motion.div
            key="2"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="glass-card p-8 md:p-10 text-center max-w-2xl mx-auto"
          >
            <h2 className="text-2xl md:text-3xl font-serif mb-6">Skin Tone Photo</h2>
            <label className="cursor-pointer block">
              <div className="border-2 border-dashed border-white/25 rounded-2xl aspect-square max-w-xs md:max-w-sm mx-auto overflow-hidden bg-black/20">
                {skinImagePreview ? (
                  <img src={skinImagePreview} alt="skin preview" className="w-full h-full object-cover" />
                ) : (
                  <div className="h-full flex flex-col items-center justify-center text-white/50 gap-3">
                    <Camera size={44} />
                    <p className="text-lg">Upload close-up of skin</p>
                  </div>
                )}
              </div>
              <input
                type="file"
                className="hidden"
                accept="image/*"
                onChange={(e) => handleImageUpload(e, 'skin')}
              />
            </label>

            <div className="flex justify-center gap-6 mt-8">
              <button onClick={() => setStep(1)} className="px-8 py-3 border border-white/30 rounded-lg">
                Back
              </button>
              <button
                onClick={() => (skinFile ? setStep(3) : toast.error("Please upload a skin photo"))}
                className="luxury-button px-10 py-3.5 text-lg"
              >
                Next
              </button>
            </div>
          </motion.div>
        )}

        {/* STEP 3 – Category */}
        {step === 3 && (
          <motion.div
            key="3"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="glass-card p-8 md:p-10 max-w-2xl mx-auto"
          >
            <h2 className="text-2xl md:text-3xl font-serif text-center mb-10">Choose Occasion</h2>
            <div className="grid grid-cols-3 gap-4 md:gap-6 max-w-xl mx-auto">
              {categories.map((c) => (
                <button
                  key={c}
                  onClick={() => setCategory(c)}
                  className={`py-6 md:py-8 rounded-xl capitalize text-base md:text-lg font-medium border transition-all
                    ${category === c
                      ? 'bg-amber-500 text-black border-amber-500 shadow-lg shadow-amber-500/20'
                      : 'border-white/20 text-white/80 hover:border-white/50'}`}
                >
                  {c}
                </button>
              ))}
            </div>

            <div className="flex justify-center mt-12 gap-6">
              <button onClick={() => setStep(2)} className="px-8 py-3 border border-white/30 rounded-lg">
                Back
              </button>
              <button
                onClick={getRecommendation}
                disabled={loading}
                className="luxury-button px-10 py-4 text-lg flex items-center gap-2.5"
              >
                {loading ? (
                  <>Analyzing...</>
                ) : (
                  <>
                    <Sparkles size={20} />
                    Generate Style Guide
                  </>
                )}
              </button>
            </div>
          </motion.div>
        )}

        {/* RESULT – STEP 4 */}
        {step === 4 && result && (
          <motion.div
            key="4"
            initial={{ opacity: 0, scale: 0.96 }}
            animate={{ opacity: 1, scale: 1 }}
            className="space-y-8 md:space-y-10"
          >
            <div className="glass-card p-8 md:p-10">
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-6 mb-8">
                <div>
                  <h2 className="text-3xl md:text-4xl font-serif font-bold flex items-center gap-3">
                    <Sparkles className="text-amber-400" size={32} />
                    Your Style Guide
                  </h2>
                  <p className="text-white/70 mt-2 capitalize">
                    {result.body_shape} body shape • {result.skin_tone} skin tone • {result.category}
                  </p>
                </div>
                <button
                  onClick={reset}
                  className="flex items-center gap-2 px-6 py-2.5 border border-white/25 rounded-lg hover:bg-white/5 transition-colors"
                >
                  <RefreshCw size={18} />
                  Start Over
                </button>
              </div>

              {/* Main recommendation */}
              <div className="bg-gradient-to-br from-white/5 to-white/3 border border-white/10 rounded-2xl p-6 md:p-8 mb-8">
                <h3 className="text-amber-300 font-semibold text-xl mb-3">Today's Recommendation</h3>
                <p className="text-white/90 text-lg leading-relaxed">{result.outfit_recommendation}</p>
              </div>

              {/* Colors */}
              <div className="mb-10">
                <h3 className="text-amber-300 font-semibold text-xl mb-4">Best Colors for You</h3>
                <div className="flex flex-wrap gap-3">
                  {result.recommended_colours.map((color: string) => (
                    <span
                      key={color}
                      className="px-5 py-2 rounded-full bg-white/8 border border-white/15 capitalize text-white/90"
                    >
                      {color}
                    </span>
                  ))}
                </div>
                <p className="text-white/60 mt-3 text-sm">
                  Color family: <span className="font-medium">{result.colour_family}</span>
                </p>
              </div>

              {/* Pattern & type info */}
              <div className="grid md:grid-cols-2 gap-6 mb-10">
                <div className="bg-white/5 p-6 rounded-xl border border-white/10">
                  <h4 className="text-amber-300 mb-2 font-medium">Pattern</h4>
                  <p className="capitalize text-lg">{result.pattern}</p>
                </div>

                <div className="bg-white/5 p-6 rounded-xl border border-white/10">
                  <h4 className="text-amber-300 mb-2 font-medium">Outfit Type</h4>
                  <p className="text-lg">
                    {result.is_single_piece
                      ? result.outfit_type
                      : `${result.upper_wear || '?'} + ${result.lower_wear || '?'}`}
                  </p>
                </div>
              </div>

              {/* Why this recommendation */}
              <div className="mb-10">
                <h3 className="text-amber-300 font-semibold text-xl mb-4">Why This Works for You</h3>
                <div className="bg-white/5 border border-white/10 rounded-xl p-6 md:p-8 text-white/90 leading-relaxed whitespace-pre-wrap">
                  {result.why_this_recommendation}
                </div>
              </div>

            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}