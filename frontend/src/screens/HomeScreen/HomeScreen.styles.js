import { StyleSheet, Dimensions } from "react-native";

const { width: screenWidth, height: screenHeight } = Dimensions.get("window");

export default StyleSheet.create({
  backgroundImage: {
    flex: 1,
    backgroundColor: "#0B3D0B",
  },
  container: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center", // Center everything vertically
  },
  settingsButton: {
    position: "absolute",
    top: 50,
    right: 20,
    zIndex: 10,
  },
  settingsText: {
    fontSize: 24,
    color: "#fff",
  },
  logoContainer: {
    flexDirection: "row",
    justifyContent: "center",
    alignItems: "center",
    flex: 1, // take up remaining space
  },
  logoLetter: {
    fontSize: 40,
    fontWeight: "bold",
    color: "#FFD700",
    marginHorizontal: 2,
  },
  bottomSection: {
    position: "absolute",
    bottom: 50, // pinned near bottom
    width: "100%",
    height: 150,
  },
  slide: {
    backgroundColor: "#145214",
    borderRadius: 15,
    padding: 25,
    alignItems: "center",
    shadowColor: "#000",
    shadowOpacity: 0.3,
    shadowOffset: { width: 0, height: 3 },
    shadowRadius: 5,
    elevation: 5,
  },
  slideText: {
    fontSize: 18,
    fontWeight: "600",
    marginBottom: 15,
    textAlign: "center",
    color: "#fff",
  },
  slideButton: {
    backgroundColor: "#FFD700",
    paddingVertical: 12,
    paddingHorizontal: 30,
    borderRadius: 25,
  },
  slideButtonText: {
    color: "#0B3D0B",
    fontSize: 16,
    fontWeight: "600",
  },
});
