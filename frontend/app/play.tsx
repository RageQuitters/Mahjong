import { useState, useRef, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Pressable,
  Animated,
  Dimensions,
  Image,
  ScrollView,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { router } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';
import * as ImagePicker from 'expo-image-picker';
import * as Haptics from 'expo-haptics';
import { Ionicons } from '@expo/vector-icons';

const { width, height } = Dimensions.get('window');

// ─── CONFIG ──────────────────────────────────────────────────
// Replace with your actual backend API URL
const API_URL = 'https://mahjong-9j6h.onrender.com/image/visualise';
// ─────────────────────────────────────────────────────────────

type AnalysisState = 'idle' | 'captured' | 'loading' | 'result' | 'error';

export default function PlayScreen() {
  const [state, setState] = useState<AnalysisState>('idle');
  const [capturedUri, setCapturedUri] = useState<string | null>(null);
  const [resultUri, setResultUri] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string>('');

  const fadeAnim = useRef(new Animated.Value(0)).current;
  const slideAnim = useRef(new Animated.Value(30)).current;
  const pulseAnim = useRef(new Animated.Value(1)).current;

  const animateIn = useCallback(() => {
    Animated.parallel([
      Animated.timing(fadeAnim, { toValue: 1, duration: 400, useNativeDriver: true }),
      Animated.spring(slideAnim, { toValue: 0, tension: 60, friction: 8, useNativeDriver: true }),
    ]).start();
  }, []);

  const startPulse = useCallback(() => {
    Animated.loop(
      Animated.sequence([
        Animated.timing(pulseAnim, { toValue: 1.05, duration: 800, useNativeDriver: true }),
        Animated.timing(pulseAnim, { toValue: 1, duration: 800, useNativeDriver: true }),
      ])
    ).start();
  }, []);

  const stopPulse = useCallback(() => {
    pulseAnim.stopAnimation();
    pulseAnim.setValue(1);
  }, []);

  // Reset all state
  const handleReset = () => {
    fadeAnim.setValue(0);
    slideAnim.setValue(30);
    setCapturedUri(null);
    setResultUri(null);
    setErrorMsg('');
    setState('idle');
    stopPulse();
  };

  // Launch camera
  const handleCamera = async () => {
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permission Required', 'Camera access is needed to capture your hand.');
      return;
    }
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    const result = await ImagePicker.launchCameraAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      quality: 0.9,
      allowsEditing: false,
    });
    if (!result.canceled && result.assets[0]) {
      setCapturedUri(result.assets[0].uri);
      setState('captured');
      animateIn();
    }
  };

  // Launch photo library
  const handleGallery = async () => {
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permission Required', 'Photo library access is needed to pick your hand.');
      return;
    }
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      quality: 0.9,
      allowsEditing: false,
    });
    if (!result.canceled && result.assets[0]) {
      setCapturedUri(result.assets[0].uri);
      setState('captured');
      animateIn();
    }
  };

  // Send to backend API
  const handleAnalyse = async () => {
    if (!capturedUri) return;
    Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
    setState('loading');
    startPulse();

    try {
      const formData = new FormData();
      const filename = capturedUri.split('/').pop() ?? 'hand.jpg';
      const match = /\.(\w+)$/.exec(filename);
      const mimeType = match ? `image/${match[1]}` : 'image/jpeg';

      formData.append('image', {
        uri: capturedUri,
        name: filename,
        type: mimeType,
      } as any);

      const response = await fetch(API_URL, {
        method: 'POST',
        body: formData,
        headers: { Accept: 'image/jpeg, image/png, application/json' },
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      // Backend returns the annotated image
      const blob = await response.blob();
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64 = reader.result as string;
        setResultUri(base64);
        stopPulse();
        setState('result');
        animateIn();
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      };
      reader.readAsDataURL(blob);
    } catch (err: any) {
      stopPulse();
      setErrorMsg(err.message ?? 'Something went wrong. Please try again.');
      setState('error');
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
    }
  };

  return (
    <View style={styles.container}>
      <LinearGradient
        colors={['#0D0D0D', '#150A00', '#0D0D0D']}
        style={StyleSheet.absoluteFill}
      />
      <View style={styles.glowCenter} />

      {/* Nav bar */}
      <View style={styles.navbar}>
        <Pressable
          onPress={() => {
            handleReset();
            router.back();
          }}
          style={styles.backButton}
        >
          <Ionicons name="chevron-back" size={20} color="#C8860A" />
          <Text style={styles.backText}>Home</Text>
        </Pressable>
        <Text style={styles.navTitle}>Analyse Hand</Text>
        <View style={{ width: 70 }} />
      </View>

      <ScrollView
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* ── IDLE STATE ─────────────────────────────── */}
        {state === 'idle' && (
          <View style={styles.idleContainer}>
            {/* Instruction card */}
            <View style={styles.instructCard}>
              <View style={styles.instructHeader}>
                <Text style={styles.instructTitle}>How to use</Text>
              </View>
              {[
                { icon: '📸', text: 'Lay your tiles face-up on a flat surface' },
                { icon: '🔦', text: 'Ensure good lighting for best accuracy' },
                { icon: '🤖', text: 'AI identifies the optimal discard' },
                { icon: '✨', text: 'The suggested tile is highlighted in the result' },
              ].map((item, i) => (
                <View key={i} style={styles.instructRow}>
                  <Text style={styles.instructIcon}>{item.icon}</Text>
                  <Text style={styles.instructText}>{item.text}</Text>
                </View>
              ))}
            </View>

            {/* Camera prompt */}
            <View style={styles.captureArea}>
              <View style={styles.captureFrame}>
                <Ionicons name="camera-outline" size={56} color="#3A2A1A" />
                <Text style={styles.captureHint}>Your hand appears here</Text>
              </View>
            </View>

            {/* Capture buttons */}
            <View style={styles.captureButtons}>
              <Pressable onPress={handleCamera} style={styles.capturePrimary}>
                <LinearGradient
                  colors={['#C8860A', '#E8A020']}
                  start={{ x: 0, y: 0 }}
                  end={{ x: 1, y: 0 }}
                  style={styles.capturePrimaryGrad}
                >
                  <Ionicons name="camera" size={22} color="#0D0800" />
                  <Text style={styles.capturePrimaryText}>Take Photo</Text>
                </LinearGradient>
              </Pressable>
              <Pressable onPress={handleGallery} style={styles.captureSecondary}>
                <Ionicons name="images-outline" size={20} color="#C8860A" />
                <Text style={styles.captureSecondaryText}>Gallery</Text>
              </Pressable>
            </View>
          </View>
        )}

        {/* ── CAPTURED STATE ──────────────────────────── */}
        {state === 'captured' && capturedUri && (
          <Animated.View
            style={[
              styles.capturedContainer,
              { opacity: fadeAnim, transform: [{ translateY: slideAnim }] },
            ]}
          >
            <Text style={styles.sectionLabel}>YOUR HAND</Text>
            <View style={styles.imageWrapper}>
              <Image source={{ uri: capturedUri }} style={styles.handImage} resizeMode="contain" />
              <View style={styles.imageOverlay}>
                <Pressable onPress={handleReset} style={styles.retakeBtn}>
                  <Ionicons name="refresh" size={16} color="#F5E6C8" />
                  <Text style={styles.retakeBtnText}>Retake</Text>
                </Pressable>
              </View>
            </View>
            <Text style={styles.capturedHint}>
              Make sure all tiles are visible and well-lit.
            </Text>
            <Pressable onPress={handleAnalyse} style={styles.analyseBtn}>
              <LinearGradient
                colors={['#C8860A', '#E8A020', '#C8860A']}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 0 }}
                style={styles.analyseBtnGrad}
              >
                <Text style={styles.analyseBtnText}>ANALYSE DISCARD</Text>
                <Ionicons name="sparkles" size={18} color="#0D0800" />
              </LinearGradient>
            </Pressable>
          </Animated.View>
        )}

        {/* ── LOADING STATE ───────────────────────────── */}
        {state === 'loading' && (
          <View style={styles.loadingContainer}>
            <Animated.View style={[styles.loadingTileWrap, { transform: [{ scale: pulseAnim }] }]}>
              <View style={styles.loadingTile}>
                <Text style={styles.loadingTileEmoji}>🀄</Text>
              </View>
              <View style={styles.loadingGlow} />
            </Animated.View>
            <ActivityIndicator size="small" color="#C8860A" style={{ marginTop: 32 }} />
            <Text style={styles.loadingTitle}>Analysing your hand...</Text>
            <Text style={styles.loadingSubtitle}>
              Our AI is studying your tiles{'\n'}and calculating the best discard
            </Text>
            <View style={styles.loadingSteps}>
              {['Detecting tiles', 'Evaluating combinations', 'Identifying best discard'].map(
                (step, i) => (
                  <View key={i} style={styles.loadingStep}>
                    <View style={styles.loadingStepDot} />
                    <Text style={styles.loadingStepText}>{step}</Text>
                  </View>
                )
              )}
            </View>
          </View>
        )}

        {/* ── RESULT STATE ────────────────────────────── */}
        {state === 'result' && resultUri && (
          <Animated.View
            style={[
              styles.resultContainer,
              { opacity: fadeAnim, transform: [{ translateY: slideAnim }] },
            ]}
          >
            <View style={styles.resultBadge}>
              <Ionicons name="checkmark-circle" size={18} color="#0D0800" />
              <Text style={styles.resultBadgeText}>Analysis Complete</Text>
            </View>
            <Text style={styles.sectionLabel}>BEST DISCARD</Text>
            <View style={styles.resultImageWrapper}>
              <Image source={{ uri: resultUri }} style={styles.resultImage} resizeMode="contain" />
            </View>
            <View style={styles.resultHintCard}>
              <Text style={styles.resultHintIcon}>💡</Text>
              <Text style={styles.resultHintText}>
                The highlighted tile is your recommended discard. It maximises your winning
                probability based on Singapore Mahjong rules.
              </Text>
            </View>
            <View style={styles.resultActions}>
              <Pressable onPress={handleReset} style={styles.resultActionPrimary}>
                <LinearGradient
                  colors={['#C8860A', '#E8A020']}
                  start={{ x: 0, y: 0 }}
                  end={{ x: 1, y: 0 }}
                  style={styles.resultActionGrad}
                >
                  <Ionicons name="camera" size={18} color="#0D0800" />
                  <Text style={styles.resultActionPrimaryText}>New Hand</Text>
                </LinearGradient>
              </Pressable>
            </View>
          </Animated.View>
        )}

        {/* ── ERROR STATE ─────────────────────────────── */}
        {state === 'error' && (
          <View style={styles.errorContainer}>
            <View style={styles.errorIcon}>
              <Ionicons name="warning-outline" size={40} color="#C8860A" />
            </View>
            <Text style={styles.errorTitle}>Analysis Failed</Text>
            <Text style={styles.errorMessage}>{errorMsg}</Text>
            <Pressable onPress={handleReset} style={styles.errorRetry}>
              <Text style={styles.errorRetryText}>Try Again</Text>
            </Pressable>
          </View>
        )}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0D0D0D' },
  glowCenter: {
    position: 'absolute',
    top: height * 0.3,
    left: width / 2 - 120,
    width: 240,
    height: 240,
    borderRadius: 120,
    backgroundColor: 'rgba(200, 134, 10, 0.05)',
  },
  navbar: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingTop: 60,
    paddingBottom: 16,
  },
  backButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    width: 70,
  },
  backText: { fontSize: 14, color: '#C8860A', fontWeight: '500' },
  navTitle: { fontSize: 14, color: '#F5E6C8', fontWeight: '600', letterSpacing: 2 },
  scrollContent: { paddingHorizontal: 20, paddingBottom: 48 },

  // Idle
  idleContainer: { gap: 20 },
  instructCard: {
    backgroundColor: '#110D08',
    borderRadius: 16,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: '#2A1E10',
  },
  instructHeader: {
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#2A1E10',
  },
  instructTitle: { fontSize: 11, color: '#C8860A', fontWeight: '700', letterSpacing: 2 },
  instructRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#1A1208',
  },
  instructIcon: { fontSize: 18 },
  instructText: { fontSize: 13, color: '#8A7A6A', flex: 1, lineHeight: 18 },
  captureArea: {
    aspectRatio: 1.4,
    backgroundColor: '#0D0A06',
    borderRadius: 16,
    borderWidth: 2,
    borderColor: '#2A1E10',
    borderStyle: 'dashed',
    alignItems: 'center',
    justifyContent: 'center',
  },
  captureFrame: { alignItems: 'center', gap: 12 },
  captureHint: { fontSize: 12, color: '#3A2A1A', letterSpacing: 1 },
  captureButtons: { flexDirection: 'row', gap: 12 },
  capturePrimary: { flex: 1, borderRadius: 12, overflow: 'hidden' },
  capturePrimaryGrad: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    gap: 8,
  },
  capturePrimaryText: { fontSize: 15, fontWeight: '700', color: '#0D0800', letterSpacing: 1 },
  captureSecondary: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    paddingHorizontal: 20,
    borderWidth: 1,
    borderColor: '#2A1E10',
    borderRadius: 12,
  },
  captureSecondaryText: { fontSize: 14, color: '#C8860A', fontWeight: '500' },

  // Captured
  capturedContainer: { gap: 16 },
  sectionLabel: { fontSize: 10, color: '#6A5A4A', letterSpacing: 3, fontWeight: '700' },
  imageWrapper: {
    borderRadius: 16,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: '#2A1E10',
    aspectRatio: 1.4,
    backgroundColor: '#0D0A06',
  },
  handImage: { width: '100%', height: '100%' },
  imageOverlay: {
    position: 'absolute',
    bottom: 12,
    right: 12,
  },
  retakeBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    backgroundColor: 'rgba(0,0,0,0.7)',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#3A2A1A',
  },
  retakeBtnText: { fontSize: 12, color: '#F5E6C8' },
  capturedHint: { fontSize: 12, color: '#5A4A3A', textAlign: 'center', lineHeight: 18 },
  analyseBtn: { borderRadius: 14, overflow: 'hidden' },
  analyseBtnGrad: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 18,
    gap: 10,
  },
  analyseBtnText: { fontSize: 15, fontWeight: '800', color: '#0D0800', letterSpacing: 2 },

  // Loading
  loadingContainer: { flex: 1, alignItems: 'center', justifyContent: 'center', paddingTop: 60, gap: 8 },
  loadingTileWrap: { position: 'relative', alignItems: 'center', justifyContent: 'center' },
  loadingTile: {
    width: 80,
    height: 96,
    backgroundColor: '#F5E6C8',
    borderRadius: 10,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 2,
    borderColor: '#C8860A',
  },
  loadingTileEmoji: { fontSize: 44 },
  loadingGlow: {
    position: 'absolute',
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: 'rgba(200,134,10,0.15)',
    zIndex: -1,
  },
  loadingTitle: { fontSize: 18, fontWeight: '700', color: '#F5E6C8', marginTop: 8, letterSpacing: 0.5 },
  loadingSubtitle: { fontSize: 13, color: '#6A5A4A', textAlign: 'center', lineHeight: 20 },
  loadingSteps: { marginTop: 24, gap: 10, width: '100%', paddingHorizontal: 40 },
  loadingStep: { flexDirection: 'row', alignItems: 'center', gap: 10 },
  loadingStepDot: { width: 6, height: 6, borderRadius: 3, backgroundColor: '#C8860A', opacity: 0.6 },
  loadingStepText: { fontSize: 12, color: '#5A4A3A', letterSpacing: 0.5 },

  // Result
  resultContainer: { gap: 16 },
  resultBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    alignSelf: 'flex-start',
    backgroundColor: '#C8860A',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
    marginBottom: 4,
  },
  resultBadgeText: { fontSize: 12, fontWeight: '700', color: '#0D0800', letterSpacing: 0.5 },
  resultImageWrapper: {
    borderRadius: 16,
    overflow: 'hidden',
    borderWidth: 2,
    borderColor: '#C8860A',
    aspectRatio: 1.4,
    backgroundColor: '#0D0A06',
    shadowColor: '#C8860A',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.3,
    shadowRadius: 16,
    elevation: 10,
  },
  resultImage: { width: '100%', height: '100%' },
  resultHintCard: {
    flexDirection: 'row',
    gap: 12,
    backgroundColor: '#110D08',
    borderRadius: 12,
    padding: 14,
    borderWidth: 1,
    borderColor: '#2A1E10',
    alignItems: 'flex-start',
  },
  resultHintIcon: { fontSize: 18, marginTop: 1 },
  resultHintText: { flex: 1, fontSize: 13, color: '#8A7A6A', lineHeight: 20 },
  resultActions: {},
  resultActionPrimary: { borderRadius: 14, overflow: 'hidden' },
  resultActionGrad: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    gap: 8,
  },
  resultActionPrimaryText: { fontSize: 15, fontWeight: '700', color: '#0D0800', letterSpacing: 1 },

  // Error
  errorContainer: { flex: 1, alignItems: 'center', justifyContent: 'center', paddingTop: 80, gap: 16 },
  errorIcon: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#1A0E00',
    borderWidth: 1,
    borderColor: '#C8860A',
    alignItems: 'center',
    justifyContent: 'center',
  },
  errorTitle: { fontSize: 20, fontWeight: '700', color: '#F5E6C8' },
  errorMessage: { fontSize: 13, color: '#8A7A6A', textAlign: 'center', lineHeight: 20, paddingHorizontal: 32 },
  errorRetry: {
    marginTop: 8,
    paddingHorizontal: 32,
    paddingVertical: 14,
    borderWidth: 1,
    borderColor: '#C8860A',
    borderRadius: 12,
  },
  errorRetryText: { fontSize: 14, color: '#C8860A', fontWeight: '600', letterSpacing: 1 },
});
