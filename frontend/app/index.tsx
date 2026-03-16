import { useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Animated,
  Dimensions,
} from 'react-native';
import { router } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';

const { width, height } = Dimensions.get('window');

// Decorative mahjong tile characters
const TILES = ['🀇', '🀈', '🀉', '🀙', '🀚', '🀛', '🀄', '🀅', '🀆'];

export default function LoadingScreen() {
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const scaleAnim = useRef(new Animated.Value(0.7)).current;
  const subtitleFade = useRef(new Animated.Value(0)).current;
  const progressAnim = useRef(new Animated.Value(0)).current;
  const tileAnims = useRef(TILES.map(() => new Animated.Value(0))).current;

  useEffect(() => {
    // Logo entrance
    Animated.parallel([
      Animated.spring(scaleAnim, {
        toValue: 1,
        tension: 60,
        friction: 8,
        useNativeDriver: true,
      }),
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 800,
        useNativeDriver: true,
      }),
    ]).start(() => {
      // Subtitle fade in
      Animated.timing(subtitleFade, {
        toValue: 1,
        duration: 600,
        useNativeDriver: true,
      }).start();

      // Tile stagger animation
      const tileAnimations = tileAnims.map((anim, i) =>
        Animated.sequence([
          Animated.delay(i * 80),
          Animated.spring(anim, {
            toValue: 1,
            tension: 80,
            friction: 6,
            useNativeDriver: true,
          }),
        ])
      );
      Animated.stagger(60, tileAnimations).start();

      // Progress bar
      Animated.timing(progressAnim, {
        toValue: 1,
        duration: 2200,
        useNativeDriver: false,
      }).start(() => {
        // Navigate to home
        router.replace('/home');
      });
    });
  }, []);

  const progressWidth = progressAnim.interpolate({
    inputRange: [0, 1],
    outputRange: ['0%', '100%'],
  });

  return (
    <LinearGradient
      colors={['#0D0D0D', '#1A0A00', '#0D0D0D']}
      style={styles.container}
    >
      {/* Decorative tile row */}
      <View style={styles.tilesRow}>
        {TILES.map((tile, i) => (
          <Animated.Text
            key={i}
            style={[
              styles.decorTile,
              {
                opacity: tileAnims[i],
                transform: [
                  {
                    translateY: tileAnims[i].interpolate({
                      inputRange: [0, 1],
                      outputRange: [20, 0],
                    }),
                  },
                ],
              },
            ]}
          >
            {tile}
          </Animated.Text>
        ))}
      </View>

      {/* Main logo */}
      <Animated.View
        style={[
          styles.logoContainer,
          {
            opacity: fadeAnim,
            transform: [{ scale: scaleAnim }],
          },
        ]}
      >
        <View style={styles.tileCard}>
          <Text style={styles.tileEmoji}>🀄</Text>
        </View>
        <Text style={styles.appName}>麻將先生</Text>
        <Text style={styles.appNameEn}>MAHJONG SENSEI</Text>
      </Animated.View>

      {/* Subtitle */}
      <Animated.Text style={[styles.subtitle, { opacity: subtitleFade }]}>
        Singapore Style · AI-Powered Discard Advisor
      </Animated.Text>

      {/* Progress bar */}
      <View style={styles.progressContainer}>
        <View style={styles.progressTrack}>
          <Animated.View
            style={[styles.progressFill, { width: progressWidth }]}
          />
        </View>
        <Animated.Text style={[styles.loadingText, { opacity: subtitleFade }]}>
          Shuffling tiles...
        </Animated.Text>
      </View>

      {/* Bottom decorative line */}
      <View style={styles.bottomDecor}>
        <View style={styles.decorLine} />
        <Text style={styles.decorText}>風 · 花 · 雪 · 月</Text>
        <View style={styles.decorLine} />
      </View>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#0D0D0D',
  },
  tilesRow: {
    flexDirection: 'row',
    position: 'absolute',
    top: height * 0.1,
    gap: 8,
  },
  decorTile: {
    fontSize: 28,
    opacity: 0.3,
  },
  logoContainer: {
    alignItems: 'center',
    marginBottom: 24,
  },
  tileCard: {
    width: 90,
    height: 110,
    backgroundColor: '#F5E6C8',
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 24,
    shadowColor: '#C8860A',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.6,
    shadowRadius: 20,
    elevation: 20,
    borderWidth: 2,
    borderColor: '#C8860A',
  },
  tileEmoji: {
    fontSize: 52,
  },
  appName: {
    fontSize: 36,
    fontWeight: '700',
    color: '#C8860A',
    letterSpacing: 8,
    marginBottom: 4,
  },
  appNameEn: {
    fontSize: 13,
    fontWeight: '300',
    color: '#F5E6C8',
    letterSpacing: 6,
  },
  subtitle: {
    fontSize: 12,
    color: '#8A7A6A',
    letterSpacing: 1.5,
    marginBottom: 60,
    textAlign: 'center',
  },
  progressContainer: {
    width: width * 0.6,
    alignItems: 'center',
    gap: 12,
  },
  progressTrack: {
    width: '100%',
    height: 2,
    backgroundColor: '#2A2A2A',
    borderRadius: 1,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#C8860A',
    borderRadius: 1,
  },
  loadingText: {
    fontSize: 11,
    color: '#5A4A3A',
    letterSpacing: 2,
    textTransform: 'uppercase',
  },
  bottomDecor: {
    flexDirection: 'row',
    alignItems: 'center',
    position: 'absolute',
    bottom: 60,
    gap: 12,
  },
  decorLine: {
    width: 40,
    height: 1,
    backgroundColor: '#3A2A1A',
  },
  decorText: {
    fontSize: 12,
    color: '#3A2A1A',
    letterSpacing: 4,
  },
});
