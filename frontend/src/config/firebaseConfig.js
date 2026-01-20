import { initializeApp, getApps } from "firebase/app";
import { getFirestore } from "firebase/firestore";
import { Platform } from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";

// Only import initializeAuth and persistence for non-web
import { initializeAuth, getReactNativePersistence } from "firebase/auth/react-native";



// Your web app's Firebase configuration
// These will be filled from the .env file

/*
const firebaseConfig = {
  apiKey: process.env.EXPO_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.EXPO_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.EXPO_PUBLIC_FIREBASE_PROJECT_ID,
  storageBucket: process.env.EXPO_PUBLIC_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.EXPO_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.EXPO_PUBLIC_FIREBASE_APP_ID,
};
*/
const firebaseConfig = {
  apiKey: "AIzaSyCcjiyt8ScmaAelasbzeU_1OYgxAnGQdaQ",
  authDomain: "mahjongbuddy-33425.firebaseapp.com",
  projectId: "mahjongbuddy-33425",
  storageBucket: "mahjongbuddy-33425.firebasestorage.app",
  messagingSenderId: "746493333340",
  appId: "1:746493333340:web:5ca0a3a3e794d42128bb99",
  measurementId: "G-RGBXE252DX"
};
console.log("Firebase Config:", firebaseConfig);
// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Auth with persistence for React Native
let auth;
if (Platform.OS === "web") {
  auth = getAuth(app);
} else {
  auth = initializeAuth(app, {
    persistence: getReactNativePersistence(AsyncStorage),
  });
}

const db = getFirestore(app);

export { auth, db };
