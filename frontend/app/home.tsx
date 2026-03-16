import { useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Animated,
  Dimensions,
  Pressable,
} from 'react-native';
import { router } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';
import { BlurView } from 'expo-blur';
import * as Haptics from 'expo-haptics';

const { width, height } = Dimensions.get('window');

function GlowButton({
  label,
  sublabel,
  onPress,
  primary = false,
  delay = 0,
}: {
  label: string;
  sublabel: string;
  onPress: () => void;
  primary?: boolean;
  delay?: number;
}) {
  const slideAnim = useRef(new Animated.Value(40)).current;
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const scaleAnim = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    Animated.parallel([
      Animated.timing(slideAnim, {
        toValue: 0,
        duration: 600,
        delay,
        useNativeDriver: true,
      }),
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 600,
        delay,
        useNativeDriver: true,
      }),
    ]).start();
  }, []);

  const handlePressIn = () => {
    Animated.spring(scaleAnim, {
      toValue: 0.97,
      useNativeDriver: true,
    }).start();
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
  };

  const handlePressOut = () => {
    Animated.spring(scaleAnim, {
      toValue: 1,
      tension: 100,
      friction: 5,
      useNativeDriver: true,
    }).start();
  };

  return (
    <Animated.View
      style={{
        opacity: fadeAnim,
        transform: [{ translateY: slideAnim }, { scale: scaleAnim }],
        width: '100%',
      }}
    >
      <Pressable
        onPress={onPress}
        onPressIn={handlePressIn}
        onPressOut={handlePressOut}
      >
        {primary ? (
          <LinearGradient
            colors={['#C8860A', '#E8A020', '#C8860A']}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 0 }}
            style={styles.buttonPrimary}
          >
            <Text style={styles.buttonLabelPrimary}>{label}</Text>
            <Text style={styles.buttonSublabelPrimary}>{sublabel}</Text>
          </LinearGradient>
        ) : (
          <BlurView intensity={20} style={styles.buttonSecondary}>
            <View style={styles.buttonSecondaryInner}>
              <Text style={styles.buttonLabelSecondary}>{label}</Text>
              <Text style={styles.buttonSublabelSecondary}>{sublabel}</Text>
            </View>
          </BlurView>
        )}
      </Pressable>
    </Animated.View>
  );
}

// Animated floating tile component
function FloatingTile({
  emoji,
  style,
  duration,
}: {
  emoji: string;
  style: object;
  duration: number;
}) {
  const floatAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.loop(
      Animated.sequence([
        Animated.timing(floatAnim, {
          toValue: 1,
          duration,
          useNativeDriver: true,
        }),
        Animated.timing(floatAnim, {
          toValue: 0,
          duration,
          useNativeDriver: true,
        }),
      ])
    ).start();
  }, []);

  const translateY = floatAnim.interpolate({
    inputRange: [0, 1],
    outputRange: [0, -14],
  });

  return (
    <Animated.Text style={[style, { transform: [{ translateY }] }]}>
      {emoji}
    </Animated.Text>
  );
}

export default function HomeScreen() {
  const headerFade = useRef(new Animated.Value(0)).current;
  const headerSlide = useRef(new Animated.Value(-20)).current;

  useEffect(() => {
    Animated.parallel([
      Animated.timing(headerFade, {
        toValue: 1,
        duration: 700,
        useNativeDriver: true,
      }),
      Animated.timing(headerSlide, {
        toValue: 0,
        duration: 700,
        useNativeDriver: true,
      }),
    ]).start();
  }, []);

  return (
    <View style={styles.container}>
      {/* Background gradient */}
      <LinearGradient
        colors={['#0D0D0D', '#150A00', '#1A0D00', '#0D0D0D']}
        locations={[0, 0.3, 0.7, 1]}
        style={StyleSheet.absoluteFill}
      />

      {/* Ambient glow */}
      <View style={styles.glowTop} />
      <View style={styles.glowBottom} />

      {/* Floating tiles - decorative */}
      <FloatingTile
        emoji="🀇"
        style={styles.floatTile1}
        duration={3000}
      />
      <FloatingTile
        emoji="🀙"
        style={styles.floatTile2}
        duration={3800}
      />
      <FloatingTile
        emoji="🀄"
        style={styles.floatTile3}
        duration={2700}
      />
      <FloatingTile
        emoji="🀅"
        style={styles.floatTile4}
        duration={4200}
      />

      {/* Header */}
      <Animated.View
        style={[
          styles.header,
          {
            opacity: headerFade,
            transform: [{ translateY: headerSlide }],
          },
        ]}
      >
        <View style={styles.logoRow}>
          <View style={styles.miniTile}>
            <Text style={styles.miniTileEmoji}>🀄</Text>
          </View>
          <View>
            <Text style={styles.titleChinese}>麻將先生</Text>
            <Text style={styles.titleEn}>MAHJONG SENSEI</Text>
          </View>
        </View>
        <View style={styles.badge}>
          <Text style={styles.badgeText}>SG</Text>
        </View>
      </Animated.View>

      {/* Hero section */}
      <View style={styles.hero}>
        <Animated.Text
          style={[
            styles.heroHeadline,
            { opacity: headerFade, transform: [{ translateY: headerSlide }] },
          ]}
        >
          Play smarter.{'\n'}Discard better.
        </Animated.Text>
        <Animated.Text style={[styles.heroSub, { opacity: headerFade }]}>
          Snap your hand. Our AI tells you{'\n'}exactly which tile to throw.
        </Animated.Text>
      </View>

      {/* Tile visual showcase */}
      <Animated.View style={[styles.tileShowcase, { opacity: headerFade }]}>
        {['🀇', '🀈', '🀉', '🀊', '🀙', '🀚', '🀛', '🀄', '🀅'].map(
          (tile, i) => (
            <View
              key={i}
              style={[
                styles.showcaseTile,
                i === 7 && styles.showcaseTileHighlight,
              ]}
            >
              <Text
                style={[
                  styles.showcaseTileEmoji,
                  i === 7 && styles.showcaseTileEmojiHighlight,
                ]}
              >
                {tile}
              </Text>
            </View>
          )
        )}
      </Animated.View>

      {/* Buttons */}
      <View style={styles.buttons}>
        <GlowButton
          label="ANALYSE HAND"
          sublabel="Tap to capture your tiles"
          onPress={() => router.push('/play')}
          primary
          delay={300}
        />
        <GlowButton
          label="ABOUT US"
          sublabel="Learn about Mahjong Sensei"
          onPress={() => router.push('/about')}
          delay={420}
        />
      </View>

      {/* Footer */}
      <Animated.View style={[styles.footer, { opacity: headerFade }]}>
        <View style={styles.footerLine} />
        <Text style={styles.footerText}>Singapore Style Mahjong · v1.0</Text>
        <View style={styles.footerLine} />
      </Animated.View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0D0D0D',
  },
  glowTop: {
    position: 'absolute',
    top: -100,
    left: width / 2 - 150,
    width: 300,
    height: 300,
    borderRadius: 150,
    backgroundColor: 'rgba(200, 134, 10, 0.08)',
  },
  glowBottom: {
    position: 'absolute',
    bottom: -50,
    right: -50,
    width: 250,
    height: 250,
    borderRadius: 125,
    backgroundColor: 'rgba(200, 134, 10, 0.05)',
  },
  // Floating tiles
  floatTile1: {
    position: 'absolute',
    top: height * 0.15,
    left: 20,
    fontSize: 22,
    opacity: 0.12,
  },
  floatTile2: {
    position: 'absolute',
    top: height * 0.25,
    right: 24,
    fontSize: 26,
    opacity: 0.1,
  },
  floatTile3: {
    position: 'absolute',
    top: height * 0.55,
    left: 16,
    fontSize: 20,
    opacity: 0.08,
  },
  floatTile4: {
    position: 'absolute',
    top: height * 0.45,
    right: 18,
    fontSize: 18,
    opacity: 0.1,
  },
  // Header
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 24,
    paddingTop: 64,
    paddingBottom: 8,
  },
  logoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  miniTile: {
    width: 38,
    height: 46,
    backgroundColor: '#F5E6C8',
    borderRadius: 6,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: '#C8860A',
  },
  miniTileEmoji: {
    fontSize: 22,
  },
  titleChinese: {
    fontSize: 16,
    fontWeight: '700',
    color: '#C8860A',
    letterSpacing: 2,
  },
  titleEn: {
    fontSize: 9,
    color: '#6A5A4A',
    letterSpacing: 3,
    fontWeight: '300',
  },
  badge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderWidth: 1,
    borderColor: '#C8860A',
    borderRadius: 4,
  },
  badgeText: {
    fontSize: 10,
    color: '#C8860A',
    fontWeight: '700',
    letterSpacing: 1,
  },
  // Hero
  hero: {
    paddingHorizontal: 24,
    paddingTop: 32,
    paddingBottom: 28,
  },
  heroHeadline: {
    fontSize: 38,
    fontWeight: '800',
    color: '#F5E6C8',
    lineHeight: 46,
    letterSpacing: -0.5,
    marginBottom: 14,
  },
  heroSub: {
    fontSize: 14,
    color: '#8A7A6A',
    lineHeight: 22,
    letterSpacing: 0.3,
  },
  // Tile showcase
  tileShowcase: {
    flexDirection: 'row',
    paddingHorizontal: 24,
    gap: 6,
    marginBottom: 36,
  },
  showcaseTile: {
    flex: 1,
    aspectRatio: 0.7,
    backgroundColor: '#1A1410',
    borderRadius: 6,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: '#2A1E10',
  },
  showcaseTileHighlight: {
    backgroundColor: '#2A1A00',
    borderColor: '#C8860A',
    shadowColor: '#C8860A',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.6,
    shadowRadius: 8,
    elevation: 8,
  },
  showcaseTileEmoji: {
    fontSize: 16,
    opacity: 0.5,
  },
  showcaseTileEmojiHighlight: {
    opacity: 1,
  },
  // Buttons
  buttons: {
    paddingHorizontal: 24,
    gap: 12,
  },
  buttonPrimary: {
    borderRadius: 14,
    paddingVertical: 18,
    paddingHorizontal: 24,
    alignItems: 'center',
  },
  buttonLabelPrimary: {
    fontSize: 15,
    fontWeight: '800',
    color: '#0D0800',
    letterSpacing: 2,
  },
  buttonSublabelPrimary: {
    fontSize: 11,
    color: 'rgba(13,8,0,0.6)',
    marginTop: 2,
    letterSpacing: 0.5,
  },
  buttonSecondary: {
    borderRadius: 14,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: '#2A2018',
  },
  buttonSecondaryInner: {
    paddingVertical: 18,
    paddingHorizontal: 24,
    alignItems: 'center',
    backgroundColor: 'rgba(255,255,255,0.03)',
  },
  buttonLabelSecondary: {
    fontSize: 15,
    fontWeight: '600',
    color: '#F5E6C8',
    letterSpacing: 2,
  },
  buttonSublabelSecondary: {
    fontSize: 11,
    color: '#6A5A4A',
    marginTop: 2,
    letterSpacing: 0.5,
  },
  // Footer
  footer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 12,
    paddingVertical: 24,
    marginTop: 'auto',
  },
  footerLine: {
    flex: 1,
    height: 1,
    backgroundColor: '#1E1810',
    marginHorizontal: 12,
  },
  footerText: {
    fontSize: 10,
    color: '#3A2E22',
    letterSpacing: 1.5,
  },
});
