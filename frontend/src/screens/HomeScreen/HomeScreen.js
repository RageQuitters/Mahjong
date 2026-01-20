import React, { useState, useRef, useEffect } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  Dimensions,
  Animated,
  Easing,
  ImageBackground,
} from "react-native";
import Carousel from "react-native-snap-carousel";
import styles from "./HomeScreen.styles";

const { width: screenWidth, height: screenHeight } = Dimensions.get("window");

// Bottom carousel slides
const slides = [
  {
    key: "start",
    title: "Start your Mahjong journey",
    buttonLabel: "Start",
    navigateTo: "Start",
  },
  {
    key: "train",
    title: "Train your Mahjong skills",
    buttonLabel: "Train",
    navigateTo: "Train",
  },
];

export default function HomeScreen({ navigation }) {
  const [activeSlide, setActiveSlide] = useState(0);
  const carouselRef = useRef(null);

  // Animated values for each letter
  const logoText = "MahjongBuddy";
  const animatedValues = useRef(
    logoText.split("").map(() => new Animated.Value(0))
  ).current;

  // Gentle bob every 5 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      animatedValues.forEach((anim, index) => {
        Animated.sequence([
          Animated.timing(anim, {
            toValue: -8, // move up
            duration: 400,
            easing: Easing.inOut(Easing.sin),
            useNativeDriver: true,
          }),
          Animated.timing(anim, {
            toValue: 0, // back down
            duration: 400,
            easing: Easing.inOut(Easing.sin),
            useNativeDriver: true,
          }),
        ]).start();
      });
    }, 5000); // once every 5 seconds

    return () => clearInterval(interval);
  }, [animatedValues]);

  const renderItem = ({ item }) => (
    <View style={styles.slide}>
      <Text style={styles.slideText}>{item.title}</Text>
      <TouchableOpacity
        style={styles.slideButton}
        onPress={() => navigation.navigate(item.navigateTo)}
      >
        <Text style={styles.slideButtonText}>{item.buttonLabel}</Text>
      </TouchableOpacity>
    </View>
  );

  return (
    <ImageBackground
      source={require("../../../assets/mahjong_bg.png")}
      style={styles.backgroundImage}
      imageStyle={{ opacity: 0.2 }}
    >
      <View style={styles.container}>
        {/* Settings Button */}
        <TouchableOpacity
          style={styles.settingsButton}
          onPress={() => navigation.navigate("Settings")}
        >
          <Text style={styles.settingsText}>⚙️</Text>
        </TouchableOpacity>

        {/* Centered Logo */}
        <View style={styles.logoContainer}>
          {logoText.split("").map((char, i) => (
            <Animated.Text
              key={i}
              style={[
                styles.logoLetter,
                { transform: [{ translateY: animatedValues[i] }] },
              ]}
            >
              {char}
            </Animated.Text>
          ))}
        </View>

        {/* Bottom Carousel */}
        <View style={styles.bottomSection}>
          <Carousel
            ref={carouselRef}
            data={slides}
            renderItem={renderItem}
            sliderWidth={screenWidth}
            itemWidth={screenWidth * 0.8}
            onSnapToItem={(index) => setActiveSlide(index)}
            loop={true}
          />
        </View>
      </View>
    </ImageBackground>
  );
}
