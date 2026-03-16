import React, { useState } from "react";
import {
  View,
  Text,
  Image,
  TouchableOpacity,
  ActivityIndicator,
  ScrollView,
  StyleSheet,
} from "react-native";
import styles from "./StartScreen.styles";
import CameraComponent from "../../components/CameraComponent/CameraComponent";

// -------------------------
// 🔧 Change to your machine's local IP
// e.g. "http://192.168.1.42:8000"
// -------------------------
const API_BASE_URL = "http://192.168.56.1:8000";

// Screen states
const STATE = {
  CAMERA: "camera",       // showing live camera
  PREVIEW: "preview",     // photo taken, awaiting Suggest tap
  LOADING: "loading",     // waiting for API
  RESULT: "result",       // showing result image
  ERROR: "error",         // something went wrong
};

export default function StartScreen() {
  const [screen, setScreen] = useState(STATE.CAMERA);
  const [photoUri, setPhotoUri] = useState(null);
  const [resultUri, setResultUri] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);
  const [isWinning, setIsWinning] = useState(false);

  // Called by CameraComponent when user taps Snap
  const handlePhoto = (photo) => {
    if (!photo?.uri) return;
    setPhotoUri(photo.uri);
    setResultUri(null);
    setErrorMsg(null);
    setIsWinning(false);
    setScreen(STATE.PREVIEW);
  };

  // Called when user taps Suggest
  const handleSuggest = async () => {
    setScreen(STATE.LOADING);

    try {
      const formData = new FormData();
      formData.append("file", {
        uri: photoUri,
        name: "hand.jpg",
        type: "image/jpeg",
      });

      const response = await fetch(`${API_BASE_URL}/image/visualise`, {
        method: "POST",
        headers: { "Content-Type": "multipart/form-data" },
        body: formData,
      });

      if (!response.ok) {
        // Try to parse error detail from JSON
        let detail = `Server error: ${response.status}`;
        try {
          const err = await response.json();
          detail = err.detail || detail;
        } catch (_) {}
        throw new Error(detail);
      }

      // Response is a JPEG image — convert to a local blob URI
      const blob = await response.blob();
      const localUri = URL.createObjectURL(blob);

      // Check if winning via headers (optional enhancement later)
      // For now just show the image
      setResultUri(localUri);
      setScreen(STATE.RESULT);
    } catch (e) {
      console.error("API error:", e);
      setErrorMsg(e.message || "Something went wrong. Is the server running?");
      setScreen(STATE.ERROR);
    }
  };

  const handleRetake = () => {
    setPhotoUri(null);
    setResultUri(null);
    setErrorMsg(null);
    setScreen(STATE.CAMERA);
  };

  // -------------------------
  // Render
  // -------------------------
  return (
    <ScrollView
      style={{ flex: 1, backgroundColor: "#0B3D2E" }}
      contentContainerStyle={{ flexGrow: 1 }}
    >
      <Text style={styles.title}>Start Game</Text>

      {/* CAMERA — live viewfinder */}
      {screen === STATE.CAMERA && (
        <View style={{ height: 500, width: "100%" }}>
          <CameraComponent onTakePicture={handlePhoto} />
        </View>
      )}

      {/* PREVIEW — photo frozen, Suggest button */}
      {screen === STATE.PREVIEW && (
        <View style={localStyles.centred}>
          <Image
            source={{ uri: photoUri }}
            style={localStyles.photo}
            resizeMode="contain"
          />
          <TouchableOpacity style={localStyles.suggestBtn} onPress={handleSuggest}>
            <Text style={localStyles.suggestText}>✨ Suggest</Text>
          </TouchableOpacity>
          <TouchableOpacity style={localStyles.retakeBtn} onPress={handleRetake}>
            <Text style={localStyles.retakeText}>Retake</Text>
          </TouchableOpacity>
        </View>
      )}

      {/* LOADING — spinner */}
      {screen === STATE.LOADING && (
        <View style={localStyles.centred}>
          <Image
            source={{ uri: photoUri }}
            style={[localStyles.photo, { opacity: 0.4 }]}
            resizeMode="contain"
          />
          <View style={localStyles.loadingOverlay}>
            <ActivityIndicator size="large" color="#FFD700" />
            <Text style={localStyles.loadingText}>Analysing your hand…</Text>
          </View>
        </View>
      )}

      {/* RESULT — highlighted image from backend */}
      {screen === STATE.RESULT && (
        <View style={localStyles.centred}>
          <Image
            source={{ uri: resultUri }}
            style={localStyles.photo}
            resizeMode="contain"
          />
          <Text style={localStyles.resultHint}>
            Red box = suggested discard
          </Text>
          <TouchableOpacity style={localStyles.retakeBtn} onPress={handleRetake}>
            <Text style={localStyles.retakeText}>New Hand</Text>
          </TouchableOpacity>
        </View>
      )}

      {/* ERROR */}
      {screen === STATE.ERROR && (
        <View style={localStyles.centred}>
          <Text style={localStyles.errorText}>⚠️ {errorMsg}</Text>
          <TouchableOpacity style={localStyles.retakeBtn} onPress={handleRetake}>
            <Text style={localStyles.retakeText}>Try Again</Text>
          </TouchableOpacity>
        </View>
      )}
    </ScrollView>
  );
}

const localStyles = StyleSheet.create({
  centred: {
    alignItems: "center",
    paddingVertical: 20,
    paddingHorizontal: 16,
  },
  photo: {
    width: "100%",
    height: 380,
    borderRadius: 12,
  },
  suggestBtn: {
    marginTop: 20,
    backgroundColor: "#FFD700",
    paddingVertical: 14,
    paddingHorizontal: 48,
    borderRadius: 30,
  },
  suggestText: {
    color: "#0B3D0B",
    fontSize: 18,
    fontWeight: "700",
  },
  retakeBtn: {
    marginTop: 12,
    paddingVertical: 10,
    paddingHorizontal: 32,
    borderRadius: 30,
    borderWidth: 1,
    borderColor: "#FFD700",
  },
  retakeText: {
    color: "#FFD700",
    fontSize: 15,
  },
  loadingOverlay: {
    position: "absolute",
    top: "40%",
    alignItems: "center",
  },
  loadingText: {
    color: "#FFD700",
    marginTop: 10,
    fontSize: 16,
  },
  resultHint: {
    color: "#E6D8B5",
    marginTop: 12,
    fontSize: 14,
  },
  errorText: {
    color: "#FF6B6B",
    fontSize: 15,
    textAlign: "center",
    marginBottom: 20,
  },
});