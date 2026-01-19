import React from "react";
import { View, Text } from "react-native";
import styles from "./TrainScreen.styles";

export default function TrainScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Train</Text>
      <Text style={styles.subtitle}>Choose your options here</Text>
    </View>
  );
}
