import React, { useState } from "react";
import { View, Text, Image } from "react-native";
import styles from "./StartScreen.styles";
import CameraComponent from "../../components/CameraComponent/CameraComponent";

export default function StartScreen() {
  const [photoUri, setPhotoUri] = useState(null);

  const handlePhoto = (photo) => {
    if (photo && photo.uri) {
      console.log("Captured photo URI:", photo.uri); // ✅ logs in VSCode terminal
      setPhotoUri(photo.uri);
    } else {
      console.warn("No photo received");
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Start Game</Text>
      <Text style={styles.subtitle}>Choose your options here</Text>

      <View style={{ flex: 1, width: "100%" }}>
        <CameraComponent onTakePicture={handlePhoto} />
      </View>

      {photoUri && (
        <Image
          source={{ uri: photoUri }}
          style={{ width: 200, height: 300, marginTop: 10 }}
        />
      )}
    </View>
  );
}
