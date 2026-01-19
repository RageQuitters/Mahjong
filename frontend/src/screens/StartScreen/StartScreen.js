import React from "react";
import { View, Text } from "react-native";
import styles from "./StartScreen.styles";

export default function StartScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Start Game</Text>
      <Text style={styles.subtitle}>Choose your options here</Text>
    </View>
  );
}
