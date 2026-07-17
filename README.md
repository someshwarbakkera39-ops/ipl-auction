# 🏏 IPL Auction — Multiplayer Web App

Play IPL auction with your friends on their phones over the internet!

## How to Deploy (FREE on Render.com)

### Step 1: Put the code on GitHub
1. Go to [github.com](https://github.com) → Sign up (free)
2. Click **New Repository** → name it `ipl-auction` → Create
3. Upload all these files to the repo

### Step 2: Deploy on Render
1. Go to [render.com](https://render.com) → Sign up with GitHub (free)
2. Click **New → Web Service**
3. Connect your `ipl-auction` GitHub repo
4. Render auto-detects `render.yaml` — just click **Deploy**
5. Wait ~2 minutes — you get a URL like `https://ipl-auction.onrender.com`

### Step 3: Play!
1. Open the URL on your phone
2. Enter your name → **Create New Auction**
3. Share the **4-digit room code** with friends on WhatsApp
4. Each friend opens the same URL, enters the code, joins
5. Everyone picks a team, host clicks **Start Auction**
6. Bid from your own phones! 🎉

## How to Play Locally (Test on Your PC)

```bash
pip install flask flask-socketio eventlet
python app.py
```
Open `http://localhost:5000` — share your local IP (like `192.168.1.5:5000`) on the same WiFi.

## Game Rules
- Each team gets **₹100 Crore** budget
- 45 real IPL players in the pool
- Auctioneer picks players one by one
- Teams bid — timer resets with each new bid
- Highest bidder wins the player when timer hits 0
- Unsold players get a second chance at half price
- Team with highest average player rating wins!

## Files
```
ipl-auction/
├── app.py           ← Flask server + game logic
├── requirements.txt ← Python packages
├── render.yaml      ← Render deployment config
└── templates/
    └── index.html   ← Full mobile web UI
```
