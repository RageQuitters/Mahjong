import React, { useState, useEffect, useRef } from "react";
import { View, Button, Text } from "react-native";
import { Camera } from "expo-camera";
import styles from "./CameraComponent.styles";

export default function CameraComponent({ onTakePicture }) {
  const [hasPermission, setHasPermission] = useState(null);
  const [type, setType] = useState(Camera.Constants.Type.back);
  const cameraRef = useRef(null);

  useEffect(() => {
    (async () => {
      const { status } = await Camera.requestCameraPermissionsAsync();
      setHasPermission(status === "granted");
    })();
  }, []);

  if (hasPermission === null) return <View />;
  if (hasPermission === false) return <Text>No access to camera</Text>;

  const takePicture = async () => {
    if (!cameraRef.current) return;
    const photo = await cameraRef.current.takePictureAsync();
    console.log("Photo object:", photo); 
    if (onTakePicture) onTakePicture(photo);
  };

  return (
    <View style={styles.container}>
      <Camera ref={cameraRef} style={styles.camera} type={type} />

      {/* Buttons outside Camera view */}
      <View style={styles.buttonContainer}>
        <Button
          title="Flip"
          onPress={() =>
            setType(
              type === Camera.Constants.Type.back
                ? Camera.Constants.Type.front
                : Camera.Constants.Type.back
            )
          }
        />
        <Button title="Snap" onPress={takePicture} />
      </View>
    </View>
  );
}
