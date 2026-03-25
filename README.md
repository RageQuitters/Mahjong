# 🀄 Mahjong Sensei

> **Play smarter. Discard better.**  
> Our Sensei will tells you exactly which tile to throw.

---

## What is Mahjong Sensei?

Mahjong Sensei is a mobile app for Singapore Mahjong players. You take a photo of your tile hand, and the AI analyses your tiles and highlights the single best tile to discard — maximising your chances of winning.

No manual tile entry. No guessing. Just point, shoot, and play smarter.

---

## How It Works

![photo_6183901760146050496_y](https://github.com/user-attachments/assets/43d814cd-5dcf-465b-95e9-ad095eac4d4f)

### 1. Open the App

On the home screen you'll see the **Analyse Hand** button. Tap it to get started.

### 2. Capture Your Hand

On the Analyse Hand screen, you'll find instructions on how to get the best results:

- 📸 Lay your tiles face-up on a flat surface
- 🔦 Ensure good lighting for best accuracy
- 🤖 AI identifies the optimal discard
- ✨ The suggested tile is highlighted in the result

![photo_6183901760146050497_y](https://github.com/user-attachments/assets/b9b4fbc3-7b58-4d01-9d6f-a0913968d3dc)

Tap **Take Photo** to use your camera, or **Gallery** to pick an existing photo.

![photo_6183901760146050493_y](https://github.com/user-attachments/assets/fd12a7a4-5baf-4e9f-b24d-5e4e3e901e17)

### 3. Analyse

Once your hand is captured, tap **ANALYSE DISCARD**. The app uploads your image to the AI backend, which:

1. Detects all tiles using a YOLO object detection model
2. Classifies each tile through a 3-layer CNN pipeline (suit → type → exact tile)
3. Runs a Singapore Mahjong engine to find the optimal discard
4. Returns an annotated image with the recommended tile highlighted in red

![photo_6183901760146050494_y](https://github.com/user-attachments/assets/e4e002e6-97fb-41da-9844-f8120b71d7eb)

### 4. See Your Result

The result screen shows your hand with the **DISCARD** label drawn over the recommended tile in red. All other tiles are outlined in grey for reference.

If your hand is already a winning hand, all tiles are highlighted in gold instead.

Tap **New Hand** to analyse another hand.


### 5. Convolutional Neural Network and Classification Model
<img width="1280" height="960" alt="image" src="https://github.com/user-attachments/assets/e20136aa-67e7-4665-b671-a99de557a26d" />


## Running the App

The app is built with **Expo** (React Native).

### Prerequisites

- Node.js 18+
- Expo CLI
- Expo Go app on your phone ([iOS](https://apps.apple.com/app/expo-go/id982107779) / [Android](https://play.google.com/store/apps/details?id=host.exp.exponent))

### Install & Run

```bash
# Install dependencies
npm install

# Start the Expo dev server on android
npx expo run:android
```

### Troubleshooting

**Cannot connect to Metro**  
Make sure your phone and computer are on the same WiFi network. If they are and it still fails, run with tunnel mode:

```bash
npx expo start --tunnel
```

**502 Bad Gateway on first request**  
This is Render's free tier cold start. Wait 30–60 seconds and try again. The app will automatically retry.

**422 Unprocessable Entity**  
The image could not be decoded. Make sure all tiles are visible and the photo is taken in good lighting.

---

## Tech Stack

| Layer               | Technology                    |
| ------------------- | ----------------------------- |
| Mobile App          | React Native + Expo           |
| Tile Detection      | YOLOv8 (custom trained)       |
| Tile Classification | 3-layer TileCNN (PyTorch)     |
| Mahjong Engine      | Custom Singapore rules engine |
| Backend API         | FastAPI (Python)              |
| Hosting             | Render.com (free tier)        |

---

---

## API Endpoints

| Method | Endpoint           | Description                              |
| ------ | ------------------ | ---------------------------------------- |
| `POST` | `/image/visualise` | Upload image, returns annotated JPEG     |
| `POST` | `/image`           | Upload image, returns JSON prediction    |
| `POST` | `/predict`         | JSON hand input, returns JSON prediction |
| `GET`  | `/docs`            | Swagger UI (also used to wake up server) |

---

_Built for Singapore Mahjong (14-tile) rules._
