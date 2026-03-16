import { useRef, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Animated,
  ScrollView,
  Pressable,
  Dimensions,
  Linking,
} from 'react-native';
import { router } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';

const { width } = Dimensions.get('window');

const TEAM = [
  { initials: '张', role: 'AI Engineer', desc: 'Built the tile detection model' },
  { initials: '李', role: 'Backend Dev', desc: 'Designed the inference API' },
  { initials: '陈', role: 'Mobile Dev', desc: 'Crafted this beautiful app' },
];

const FEATURES = [
  { icon: '🀄', title: 'Singapore Rules', desc: 'Trained on authentic SG Mahjong gameplay data' },
  { icon: '🤖', title: 'AI-Powered', desc: 'Deep learning model identifies all 144 tile types' },
  { icon: '⚡', title: 'Real-time', desc: 'Analysis returned in under 3 seconds' },
  { icon: '🎯', title: 'High Accuracy', desc: 'Highlights the statistically optimal discard' },
];

function FadeInView({ children, delay = 0 }: { children: React.ReactNode; delay?: number }) {
  const anim = useRef(new Animated.Value(0)).current;
  const slideAnim = useRef(new Animated.Value(20)).current;

  useEffect(() => {
    Animated.parallel([
      Animated.timing(anim, { toValue: 1, duration: 500, delay, useNativeDriver: true }),
      Animated.timing(slideAnim, { toValue: 0, duration: 500, delay, useNativeDriver: true }),
    ]).start();
  }, []);

  return (
    <Animated.View style={{ opacity: anim, transform: [{ translateY: slideAnim }] }}>
      {children}
    </Animated.View>
  );
}

export default function AboutScreen() {
  return (
    <View style={styles.container}>
      <LinearGradient
        colors={['#0D0D0D', '#150A00', '#0D0D0D']}
        style={StyleSheet.absoluteFill}
      />

      {/* Navbar */}
      <View style={styles.navbar}>
        <Pressable onPress={() => router.back()} style={styles.backButton}>
          <Ionicons name="chevron-back" size={20} color="#C8860A" />
          <Text style={styles.backText}>Home</Text>
        </Pressable>
        <Text style={styles.navTitle}>About Us</Text>
        <View style={{ width: 70 }} />
      </View>

      <ScrollView
        contentContainerStyle={styles.scroll}
        showsVerticalScrollIndicator={false}
      >
        {/* Hero */}
        <FadeInView delay={0}>
          <View style={styles.heroSection}>
            <View style={styles.heroTile}>
              <Text style={styles.heroTileEmoji}>🀄</Text>
            </View>
            <Text style={styles.heroTitle}>麻將先生</Text>
            <Text style={styles.heroSubtitle}>MAHJONG SENSEI</Text>
            <Text style={styles.heroBio}>
              We built Mahjong Sensei because we love Singapore Mahjong — and we were tired of losing.
              Our AI model has studied thousands of hands to give you the edge at every table.
            </Text>
          </View>
        </FadeInView>

        {/* Divider */}
        <View style={styles.divider}>
          <View style={styles.dividerLine} />
          <Text style={styles.dividerText}>FEATURES</Text>
          <View style={styles.dividerLine} />
        </View>

        {/* Features */}
        <FadeInView delay={100}>
          <View style={styles.featuresGrid}>
            {FEATURES.map((f, i) => (
              <View key={i} style={styles.featureCard}>
                <Text style={styles.featureIcon}>{f.icon}</Text>
                <Text style={styles.featureTitle}>{f.title}</Text>
                <Text style={styles.featureDesc}>{f.desc}</Text>
              </View>
            ))}
          </View>
        </FadeInView>

        {/* Divider */}
        <View style={styles.divider}>
          <View style={styles.dividerLine} />
          <Text style={styles.dividerText}>THE TEAM</Text>
          <View style={styles.dividerLine} />
        </View>

        {/* Team */}
        <FadeInView delay={200}>
          <View style={styles.teamSection}>
            {TEAM.map((member, i) => (
              <View key={i} style={styles.memberCard}>
                <View style={styles.memberAvatar}>
                  <Text style={styles.memberInitials}>{member.initials}</Text>
                </View>
                <View style={styles.memberInfo}>
                  <Text style={styles.memberRole}>{member.role}</Text>
                  <Text style={styles.memberDesc}>{member.desc}</Text>
                </View>
                <View style={styles.memberBadge}>
                  <Text style={styles.memberBadgeText}>SG</Text>
                </View>
              </View>
            ))}
          </View>
        </FadeInView>

        {/* Version info */}
        <FadeInView delay={300}>
          <View style={styles.versionCard}>
            <View style={styles.versionRow}>
              <Text style={styles.versionLabel}>Version</Text>
              <Text style={styles.versionValue}>1.0.0</Text>
            </View>
            <View style={styles.versionRow}>
              <Text style={styles.versionLabel}>Built for</Text>
              <Text style={styles.versionValue}>Singapore Mahjong</Text>
            </View>
            <View style={[styles.versionRow, { borderBottomWidth: 0 }]}>
              <Text style={styles.versionLabel}>Model</Text>
              <Text style={styles.versionValue}>Custom CNN v2</Text>
            </View>
          </View>
        </FadeInView>

        {/* Disclaimer */}
        <FadeInView delay={350}>
          <Text style={styles.disclaimer}>
            Mahjong Sensei is a decision-support tool. Final game decisions remain yours. Play
            responsibly and within your means.
          </Text>
        </FadeInView>

        {/* Bottom ornament */}
        <View style={styles.bottomOrnament}>
          <View style={styles.dividerLine} />
          <Text style={styles.ornamentText}>風 · 花 · 雪 · 月</Text>
          <View style={styles.dividerLine} />
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0D0D0D' },
  navbar: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingTop: 60,
    paddingBottom: 16,
  },
  backButton: { flexDirection: 'row', alignItems: 'center', gap: 4, width: 70 },
  backText: { fontSize: 14, color: '#C8860A', fontWeight: '500' },
  navTitle: { fontSize: 14, color: '#F5E6C8', fontWeight: '600', letterSpacing: 2 },
  scroll: { paddingHorizontal: 20, paddingBottom: 60 },

  // Hero
  heroSection: { alignItems: 'center', paddingVertical: 32, gap: 10 },
  heroTile: {
    width: 80,
    height: 96,
    backgroundColor: '#F5E6C8',
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 2,
    borderColor: '#C8860A',
    shadowColor: '#C8860A',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.4,
    shadowRadius: 16,
    elevation: 12,
    marginBottom: 8,
  },
  heroTileEmoji: { fontSize: 44 },
  heroTitle: { fontSize: 28, fontWeight: '800', color: '#C8860A', letterSpacing: 6 },
  heroSubtitle: { fontSize: 11, color: '#6A5A4A', letterSpacing: 4, fontWeight: '300' },
  heroBio: {
    fontSize: 14,
    color: '#8A7A6A',
    textAlign: 'center',
    lineHeight: 22,
    paddingHorizontal: 16,
    marginTop: 8,
  },

  // Divider
  divider: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    marginVertical: 20,
  },
  dividerLine: { flex: 1, height: 1, backgroundColor: '#2A1E10' },
  dividerText: { fontSize: 10, color: '#C8860A', fontWeight: '700', letterSpacing: 3 },

  // Features
  featuresGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
  },
  featureCard: {
    width: (width - 50) / 2,
    backgroundColor: '#110D08',
    borderRadius: 14,
    padding: 16,
    gap: 6,
    borderWidth: 1,
    borderColor: '#2A1E10',
  },
  featureIcon: { fontSize: 26 },
  featureTitle: { fontSize: 13, fontWeight: '700', color: '#F5E6C8', letterSpacing: 0.5 },
  featureDesc: { fontSize: 11, color: '#6A5A4A', lineHeight: 16 },

  // Team
  teamSection: { gap: 10 },
  memberCard: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 14,
    backgroundColor: '#110D08',
    borderRadius: 14,
    padding: 16,
    borderWidth: 1,
    borderColor: '#2A1E10',
  },
  memberAvatar: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#2A1400',
    borderWidth: 1.5,
    borderColor: '#C8860A',
    alignItems: 'center',
    justifyContent: 'center',
  },
  memberInitials: { fontSize: 20, color: '#C8860A', fontWeight: '700' },
  memberInfo: { flex: 1 },
  memberRole: { fontSize: 13, fontWeight: '600', color: '#F5E6C8', letterSpacing: 0.5 },
  memberDesc: { fontSize: 11, color: '#5A4A3A', marginTop: 2 },
  memberBadge: {
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderWidth: 1,
    borderColor: '#2A1E10',
    borderRadius: 4,
  },
  memberBadgeText: { fontSize: 9, color: '#5A4A3A', letterSpacing: 1 },

  // Version
  versionCard: {
    backgroundColor: '#110D08',
    borderRadius: 14,
    borderWidth: 1,
    borderColor: '#2A1E10',
    overflow: 'hidden',
    marginTop: 4,
  },
  versionRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#1A1208',
  },
  versionLabel: { fontSize: 12, color: '#6A5A4A' },
  versionValue: { fontSize: 12, color: '#F5E6C8', fontWeight: '500' },

  // Disclaimer
  disclaimer: {
    fontSize: 11,
    color: '#3A2A1A',
    textAlign: 'center',
    lineHeight: 18,
    marginTop: 20,
    paddingHorizontal: 16,
  },

  // Bottom
  bottomOrnament: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    marginTop: 32,
  },
  ornamentText: { fontSize: 11, color: '#2A1E10', letterSpacing: 4 },
});
