import React from "react";
import { TouchableOpacity, Text } from "react-native";
import styles from "./MenuButton.styles";

export default function MenuButton({ label, onPress }) {
  return (
    <TouchableOpacity style={styles.button} onPress={onPress}>
      <Text style={styles.text}>{label}</Text>
    </TouchableOpacity>
  );
}
