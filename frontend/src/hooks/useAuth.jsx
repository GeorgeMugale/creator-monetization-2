import { createContext, useContext, useState, useEffect } from "react";
import { creatorService } from "@/services/creatorService";
import { walletService } from "../services/walletService";
import { auth, db, googleProvider, handleFirestoreError, OperationType } from "../firebase";
import { 
  onAuthStateChanged, 
  signInWithEmailAndPassword, 
  createUserWithEmailAndPassword, 
  signOut, 
  signInWithPopup,
  updateProfile
} from "firebase/auth";
import { doc, getDoc, setDoc, serverTimestamp } from "firebase/firestore";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const enhanceUserInBackground = async (userData) => {
    try {
      // This part depends on the existing creatorService which might still point to the old backend
      // If the user wants full Firebase, we might need to migrate these services too.
      // For now, I'll keep it but wrap in try-catch.
      if (userData.slug) {
        const [{ data: creatorData }, walletData] = await Promise.all([
          creatorService.getCreatorBySlug(userData.slug),
          walletService.getWalletData(),
        ]);

        const enhanced = {
          ...userData,
          bio: creatorData.bio,
          profileImage: creatorData.profileImage,
          coverImage: creatorData.coverImage,
          hasEarnings: walletData?.totalEarnings > 0 || walletData?.transactionCount,
        };
        setUser(prev => ({ ...prev, ...enhanced }));
      }
    } catch (err) {
      console.warn("User enhancement failed:", err);
    }
  };

  const formatUser = (firebaseUser, userData) => {
    if (!firebaseUser) return null;
    return {
      uid: firebaseUser.uid,
      email: firebaseUser.email,
      displayName: firebaseUser.displayName,
      photoURL: firebaseUser.photoURL,
      emailVerified: firebaseUser.emailVerified,
      ...userData,
    };
  };

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      if (firebaseUser) {
        try {
          // Get user profile from Firestore
          const userDoc = await getDoc(doc(db, "users", firebaseUser.uid));
          if (userDoc.exists()) {
            const userData = userDoc.data();
            setUser(formatUser(firebaseUser, userData));
            enhanceUserInBackground(userData);
          } else {
            // If doc doesn't exist, we might need to create it (e.g. after Google login)
            const newUser = {
              uid: firebaseUser.uid,
              email: firebaseUser.email,
              name: firebaseUser.displayName || firebaseUser.email.split("@")[0],
              role: "user",
              bio: "",
              createdAt: serverTimestamp(),
            };
            await setDoc(doc(db, "users", firebaseUser.uid), newUser);
            setUser(formatUser(firebaseUser, newUser));
          }
        } catch (error) {
          handleFirestoreError(error, OperationType.GET, `users/${firebaseUser.uid}`);
        }
      } else {
        setUser(null);
      }
      setLoading(false);
    });

    return () => unsubscribe();
  }, []);

  const login = async (email, password) => {
    try {
      const userCredential = await signInWithEmailAndPassword(auth, email, password);
      const firebaseUser = userCredential.user;
      
      // Fetch user profile from Firestore to get role and bio
      const userDoc = await getDoc(doc(db, "users", firebaseUser.uid));
      let userData = {};
      
      if (userDoc.exists()) {
        userData = userDoc.data();
      }
      
      const combinedUser = formatUser(firebaseUser, userData);
      return { success: true, user: combinedUser };
    } catch (error) {
      return { success: false, error: error.message };
    }
  };

  const register = async (data) => {
    const { email, password, name } = data;

    try {
      const userCredential = await createUserWithEmailAndPassword(auth, email, password);
      await updateProfile(userCredential.user, { displayName: name });
      
      const newUser = {
        uid: userCredential.user.uid,
        email: email,
        name: name || "",
        slug: (name || "").toLowerCase().replace(/[^a-z0-9]/g, ""),
        role: "creator", // Defaulting to creator for this app's context
        bio: "",
        createdAt: serverTimestamp(),
      };

      await setDoc(doc(db, "users", userCredential.user.uid), newUser);
      
      return { success: true, user: newUser };
    } catch (error) {
      return { success: false, error: error.message };
    }
  };

  const googleAuth = async () => {
    try {
      const result = await signInWithPopup(auth, googleProvider);
      const firebaseUser = result.user;
      
      // Fetch or create profile
      const userDoc = await getDoc(doc(db, "users", firebaseUser.uid));
      let userData;
      
      if (userDoc.exists()) {
        userData = userDoc.data();
      } else {
        const name = firebaseUser.displayName || firebaseUser.email.split("@")[0];
        userData = {
          uid: firebaseUser.uid,
          email: firebaseUser.email,
          name: name,
          role: "creator", // Defaulting to creator for social login too
          bio: "",
          createdAt: serverTimestamp(),
          slug: name.toLowerCase().replace(/[^a-z0-9]/g, ""),
        };
        await setDoc(doc(db, "users", firebaseUser.uid), userData);
      }
      
      const combinedUser = formatUser(firebaseUser, userData);
      return { success: true, user: combinedUser };
    } catch (error) {
      return { success: false, error: error.message };
    }
  };

  const logout = async () => {
    try {
      await signOut(auth);
    } catch (error) {
      console.error("Logout failed", error);
    }
  };

  const update = async (formData) => {
    if (!user) return { success: false, error: "Not authenticated" };
    
    try {
      // Call backend
      const result = await creatorService.updateCreator(formData);
      
      if (result.success) {
        const updatedData = result.data;
        
        // Prepare Firestore updates to keep in sync
        const firestoreUpdates = {
          name: updatedData.name,
          bio: updatedData.bio,
          slug: updatedData.slug,
          profileImage: updatedData.profileImage,
          coverImage: updatedData.coverImage,
          // Social links
          tiktok: updatedData.tiktok || "",
          facebook: updatedData.facebook || "",
          website: updatedData.website || "",
          instagram: updatedData.instagram || "",
          twitter: updatedData.twitter || "",
        };

        // Remove undefined fields
        Object.keys(firestoreUpdates).forEach(key => 
          firestoreUpdates[key] === undefined && delete firestoreUpdates[key]
        );

        await setDoc(doc(db, "users", user.uid), firestoreUpdates, { merge: true });
        
        // Update Firebase Auth display name if name changed
        if (updatedData.name) {
          await updateProfile(auth.currentUser, { displayName: updatedData.name });
        }

        setUser(prev => ({ ...prev, ...updatedData }));
        return { success: true, data: updatedData };
      } else {
        return result;
      }
    } catch (error) {
      console.error("Update failed:", error);
      return { success: false, error: error.message || "Update failed" };
    }
  };

  return (
    <AuthContext.Provider
      value={{ user, login, register, logout, update, googleAuth, loading }}
    >
      {!loading && children}
    </AuthContext.Provider>
  );
};

// eslint-disable-next-line react-refresh/only-export-components
export const useAuth = () => useContext(AuthContext);

