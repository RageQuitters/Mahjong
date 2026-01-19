import React from "react";
import { View, Text } from "react-native";
import MenuButton from "../../components/MenuButton/MenuButton";
import styles from "./HomeScreen.styles";

export default function HomeScreen({ navigation }) {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>🀄 Mahjong SG</Text>
      <Text style={styles.subtitle}>Singapore Mahjong</Text>

      <MenuButton label="Start" onPress={() => navigation.navigate("Start")} />
      <MenuButton label="Train" onPress={() => navigation.navigate("Train")} />
      <MenuButton label="Settings" onPress={() => navigation.navigate("Settings")} />

      <Text style={styles.footer}>v1.0.0</Text>
    </View>
  );
}
