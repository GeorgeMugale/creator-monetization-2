import { useState } from "react";
import { Camera, Save, Loader2, User, Image as ImageIcon } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";

const EditProfile = () => {
  const navigate = useNavigate();
  const { user, update } = useAuth();

  const [loading, setLoading] = useState(false);
  const [successMsg, setSuccessMsg] = useState("");

  const [formData, setFormData] = useState({
    fullName: user?.firstName + user?.lastName || "",
    bio: user?.bio || "",
    profileImage: user?.profileImage || null,
    coverImage: user?.coverImage || null,
  });

  //preview State (showing new images before upload)
  const [previews, setPreviews] = useState({
    profile: user?.profileImage || null,
    cover: user?.coverImage || null,
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleImageChange = (e, type) => {
    const file = e.target.files[0];
    if (file) {
      //update Form Data (Real file for backend)
      setFormData((prev) => ({ ...prev, [`${type}Image`]: file }));

      //generate Local Preview URL
      const previewUrl = URL.createObjectURL(file);
      setPreviews((prev) => ({ ...prev, [type]: previewUrl }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setSuccessMsg("");

    try {
      const cleanData = {};

      // VALIDATION
      if (!formData.fullName?.trim()) {
        throw new Error("Display name is required");
      }

      // Split full name
      const nameParts = formData.fullName.trim().split(/\s+/);
      cleanData.firstName = nameParts[0];
      cleanData.lastName = nameParts.slice(1).join(" ") || "";

      if (formData.bio?.trim()) cleanData.bio = formData.bio.trim();

      if (formData.profileImage) cleanData.profileImage = formData.profileImage;

      if (formData.coverImage) cleanData.coverImage = formData.coverImage;

      await update(user.id, cleanData);

      setSuccessMsg("Profile updated successfully!");

      setTimeout(() => navigate("/creator-dashboard"), 2000);
    } catch (error) {
      console.error(error);
      // optionally show error to user later
    } finally {
      setLoading(false);
    }
  };

  const isEmpty = {
    fullName: !formData.fullName?.trim(),
    bio: !formData.bio?.trim(),
    profileImage: !formData.profileImage,
    coverImage: !formData.coverImage,
  };

  const hasMissingFields = Object.values(isEmpty).some(Boolean);

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      <form onSubmit={handleSubmit} className="max-w-3xl mx-auto mt-6 px-4">
        {/* Success Message */}
        {successMsg && (
          <div className="mb-6 bg-green-50 text-green-700 px-4 py-3 rounded-xl border border-green-200 flex items-center gap-2 animate-in slide-in-from-top-2">
            <User size={18} /> {successMsg}
          </div>
        )}

        {/*IMAGES SECTION */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden mb-6">
          {/* Cover Image Input */}
          <div
            className={`h-48 w-full bg-gray-100 relative group
              ${isEmpty.coverImage ? "ring-2 ring-zed-green animate-pulse" : ""}
            `}
          >
            {isEmpty.coverImage && (
              <span className="absolute top-3 right-3 w-3 h-3 bg-zed-green rounded-full animate-ping" />
            )}
            {previews.cover ? (
              <img
                src={previews.cover}
                alt="Cover"
                className="w-full h-full object-cover opacity-90 group-hover:opacity-75 transition-opacity"
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-gray-400 bg-gray-100">
                <ImageIcon size={48} opacity={0.2} />
              </div>
            )}

            {/* Edit Button Overlay */}
            <label className="absolute inset-0 flex items-center justify-center cursor-pointer bg-black/0 group-hover:bg-black/20 transition-all">
              <div className="bg-white/90 backdrop-blur-sm text-gray-700 px-4 py-2 rounded-full font-medium shadow-lg flex items-center gap-2 hover:bg-white hover:text-zed-green transition-colors">
                <Camera size={18} />
                <span>Change Cover</span>
              </div>
              <input
                type="file"
                accept="image/*"
                className="hidden"
                onChange={(e) => handleImageChange(e, "cover")}
              />
            </label>
          </div>

          <div className="px-8 pb-8">
            {/* Profile Image Input (Overlapping) */}

            <div className="relative -mt-16 mb-6 inline-block">
              <div className="relative group">
                {previews.profile ? (
                  <img
                    src={previews.profile}
                    alt="Profile"
                    className="w-32 h-32 rounded-2xl border-4 border-white shadow-md object-cover bg-white"
                  />
                ) : (
                  <div
                    className={`relative group rounded-2xl
                    ${isEmpty.profileImage ? "ring-2 ring-zed-green animate-pulse" : ""}
                  `}
                  >
                    <div className="w-32 h-32 rounded-2xl border-4 border-white shadow-md bg-zed-green flex items-center justify-center text-white text-4xl font-bold">
                      {formData.fullName?.charAt(0) || "U"}
                    </div>
                    {isEmpty.profileImage && (
                      <span className="absolute -top-1 -right-1 w-3 h-3 bg-zed-green rounded-full" />
                    )}
                  </div>
                )}

                {/* Edit Button for Avatar */}
                <label className="absolute bottom-[-10px] right-[-10px] bg-white p-2.5 rounded-full shadow-md border border-gray-100 cursor-pointer hover:bg-gray-50 text-gray-600 hover:text-zed-green transition-colors">
                  <Camera size={20} />
                  <input
                    type="file"
                    accept="image/*"
                    className="hidden"
                    onChange={(e) => handleImageChange(e, "profile")}
                  />
                </label>
              </div>
            </div>

            {/* TEXT FIELDS */}
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">
                  Display Name
                </label>
                <input
                  type="text"
                  name="fullName"
                  value={formData.fullName}
                  onChange={handleChange}
                  className={`w-full px-4 py-3 rounded-xl font-medium transition-all text-black
                  ${
                    isEmpty.fullName
                      ? "bg-green-50 border-zed-green ring-2 ring-zed-green animate-pulse"
                      : "bg-gray-50 border-gray-200 focus:ring-zed-green"
                  }
                `}
                  placeholder="e.g. Chanda Mwamba"
                />
              </div>

              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">
                  Bio / About
                </label>
                <textarea
                  name="bio"
                  rows={4}
                  value={formData.bio}
                  onChange={handleChange}
                  className={`w-full px-4 py-3 rounded-xl resize-none transition-all text-black
                  ${
                    isEmpty.bio
                      ? "bg-green-50 border-zed-green ring-2 ring-zed-green animate-pulse"
                      : "bg-gray-50 border-gray-200 focus:ring-zed-green"
                  }
                `}
                  placeholder="Tell your supporters about what you create..."
                />
                <p className="text-right text-xs text-gray-400 mt-2">
                  {formData.bio.length}/500
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* ACTIONS */}
        <div className="flex items-center justify-end gap-4 mb-10">
          <button
            type="button"
            onClick={() => navigate("/creator-dashboard")}
            className="px-6 py-3 rounded-xl font-bold text-gray-500 hover:bg-gray-100 transition-colors"
          >
            Cancel
          </button>

          <button
            type="submit"
            disabled={loading}
            className={`px-8 py-3 rounded-xl font-bold flex items-center gap-2
            ${
              hasMissingFields
                ? "bg-zed-black/80 animate-pulse"
                : "bg-zed-black hover:bg-gray-800"
            }
          `}
          >
            {loading ? (
              <>
                <Loader2 size={20} className="animate-spin" /> Saving...
              </>
            ) : (
              <>
                <Save size={20} /> Save Changes
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default EditProfile;
