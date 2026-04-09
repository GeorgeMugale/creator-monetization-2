import { useState } from "react";
import { Star, X, Send, Loader2, CheckCircle2 } from "lucide-react";
import { motion as Motion, AnimatePresence } from "motion/react";
import { db, auth } from "../../firebase";
import { collection, addDoc, serverTimestamp } from "firebase/firestore";

const FeedbackModal = ({ isOpen, onClose, userRole = "supporter" }) => {
  const [rating, setRating] = useState(0);
  const [hover, setHover] = useState(0);
  const [suggestion, setSuggestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (rating === 0) {
      setError("Please select a rating");
      return;
    }
    if (!suggestion.trim()) {
      setError("Please share your thoughts");
      return;
    }

    setLoading(true);
    setError("");

    try {
      await addDoc(collection(db, "feedback"), {
        userId: auth.currentUser?.uid || null,
        userRole,
        rating,
        suggestion: suggestion.trim(),
        createdAt: serverTimestamp(),
      });
      setSubmitted(true);
      setTimeout(() => {
        onClose();
        // Reset after modal closes
        setTimeout(() => {
          setSubmitted(false);
          setRating(0);
          setSuggestion("");
        }, 300);
      }, 2000);
    } catch (err) {
      console.error("Error submitting feedback:", err);
      setError("Failed to submit feedback. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
        <Motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          className="bg-white rounded-3xl shadow-2xl w-full max-w-md overflow-hidden relative"
        >
          <button
            onClick={onClose}
            className="absolute top-4 right-4 p-2 hover:bg-gray-100 rounded-full transition-colors z-10"
          >
            <X size={20} className="text-gray-400" />
          </button>

          {submitted ? (
            <div className="p-12 text-center">
              <div className="w-20 h-20 bg-green-50 text-green-500 rounded-full flex items-center justify-center mx-auto mb-6">
                <CheckCircle2 size={40} />
              </div>
              <h2 className="text-2xl font-black text-gray-900 mb-2">Thank You!</h2>
              <p className="text-gray-500">Your feedback helps us make TipZed better for everyone.</p>
            </div>
          ) : (
            <div className="p-8">
              <div className="text-center mb-8">
                <h2 className="text-2xl font-black text-gray-900 mb-2">Talk to us</h2>
                <p className="text-gray-500">How was your experience with TipZed?</p>
              </div>

              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Rating */}
                <div className="flex justify-center gap-2">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <button
                      key={star}
                      type="button"
                      onClick={() => setRating(star)}
                      onMouseEnter={() => setHover(star)}
                      onMouseLeave={() => setHover(0)}
                      className="p-1 transition-transform hover:scale-110"
                    >
                      <Star
                        size={32}
                        className={`transition-colors ${
                          star <= (hover || rating)
                            ? "fill-amber-400 text-amber-400"
                            : "text-gray-200"
                        }`}
                      />
                    </button>
                  ))}
                </div>

                {/* Suggestion */}
                <div>
                  <label className="block text-sm font-bold text-gray-700 mb-2">
                    Suggestions / Comments
                  </label>
                  <textarea
                    value={suggestion}
                    onChange={(e) => setSuggestion(e.target.value)}
                    rows={4}
                    className="w-full px-4 py-3 rounded-2xl bg-gray-50 border border-gray-200 focus:ring-2 focus:ring-zed-green focus:border-transparent transition-all resize-none text-black"
                    placeholder="Tell us what you like or what we can improve..."
                  />
                </div>

                {error && (
                  <p className="text-red-500 text-sm font-medium text-center">{error}</p>
                )}

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full py-4 bg-zed-black text-white rounded-2xl font-black flex items-center justify-center gap-2 hover:bg-gray-800 transition-all disabled:opacity-50"
                >
                  {loading ? (
                    <Loader2 className="animate-spin" size={20} />
                  ) : (
                    <>
                      <Send size={20} />
                      Submit Feedback
                    </>
                  )}
                </button>
              </form>
            </div>
          )}
        </Motion.div>
      </div>
    </AnimatePresence>
  );
};

export default FeedbackModal;

