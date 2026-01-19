import React from "react";
import { View, Text } from "react-native";
import styles from "./SettingsScreen.styles";

export default function SettingsScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Settings</Text>
      <Text style={styles.subtitle}>Choose your options here</Text>
    </View>
  );
}
