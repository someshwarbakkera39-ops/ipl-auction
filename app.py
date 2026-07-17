from flask import Flask, render_template, request, session
from flask_socketio import SocketIO, emit, join_room, leave_room
import random, time, threading, os, uuid

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "ipl-auction-secret-2024")
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# ─── PLAYER DATABASE ───────────────────────────────────────────────────────────
PLAYERS = [
    {"name": "Virat Kohli",      "role": "Batter",      "country": "India",       "base": 200, "rating": 98},
    {"name": "Rohit Sharma",     "role": "Batter",      "country": "India",       "base": 200, "rating": 95},
    {"name": "MS Dhoni",         "role": "WK-Batter",   "country": "India",       "base": 200, "rating": 90},
    {"name": "Rishabh Pant",     "role": "WK-Batter",   "country": "India",       "base": 200, "rating": 91},
    {"name": "Jasprit Bumrah",   "role": "Bowler",      "country": "India",       "base": 200, "rating": 97},
    {"name": "Rashid Khan",      "role": "Bowler",      "country": "Afghanistan", "base": 200, "rating": 95},
    {"name": "KL Rahul",         "role": "Batter",      "country": "India",       "base": 150, "rating": 90},
    {"name": "Shubman Gill",     "role": "Batter",      "country": "India",       "base": 150, "rating": 88},
    {"name": "David Warner",     "role": "Batter",      "country": "Australia",   "base": 150, "rating": 92},
    {"name": "Jos Buttler",      "role": "Batter",      "country": "England",     "base": 150, "rating": 93},
    {"name": "Hardik Pandya",    "role": "All-Rounder", "country": "India",       "base": 150, "rating": 91},
    {"name": "Ravindra Jadeja",  "role": "All-Rounder", "country": "India",       "base": 150, "rating": 90},
    {"name": "Ben Stokes",       "role": "All-Rounder", "country": "England",     "base": 150, "rating": 92},
    {"name": "Glenn Maxwell",    "role": "All-Rounder", "country": "Australia",   "base": 150, "rating": 90},
    {"name": "Suryakumar Yadav", "role": "All-Rounder", "country": "India",       "base": 150, "rating": 94},
    {"name": "Kagiso Rabada",    "role": "Bowler",      "country": "S.Africa",    "base": 150, "rating": 91},
    {"name": "Pat Cummins",      "role": "Bowler",      "country": "Australia",   "base": 150, "rating": 91},
    {"name": "Wanindu Hasaranga","role": "Bowler",      "country": "Sri Lanka",   "base": 150, "rating": 88},
    {"name": "Sunil Narine",     "role": "All-Rounder", "country": "W.Indies",    "base": 150, "rating": 89},
    {"name": "Sam Curran",       "role": "All-Rounder", "country": "England",     "base": 150, "rating": 86},
    {"name": "Yashasvi Jaiswal", "role": "Batter",      "country": "India",       "base": 100, "rating": 85},
    {"name": "Travis Head",      "role": "Batter",      "country": "Australia",   "base": 100, "rating": 88},
    {"name": "Faf du Plessis",   "role": "Batter",      "country": "S.Africa",    "base": 100, "rating": 87},
    {"name": "Ishan Kishan",     "role": "Batter",      "country": "India",       "base": 100, "rating": 82},
    {"name": "Sanju Samson",     "role": "WK-Batter",   "country": "India",       "base": 100, "rating": 83},
    {"name": "Quinton de Kock",  "role": "WK-Batter",   "country": "S.Africa",    "base": 100, "rating": 87},
    {"name": "Heinrich Klaasen", "role": "WK-Batter",   "country": "S.Africa",    "base": 100, "rating": 86},
    {"name": "Mitchell Marsh",   "role": "All-Rounder", "country": "Australia",   "base": 100, "rating": 85},
    {"name": "Liam Livingstone", "role": "All-Rounder", "country": "England",     "base": 100, "rating": 84},
    {"name": "Marcus Stoinis",   "role": "All-Rounder", "country": "Australia",   "base": 100, "rating": 83},
    {"name": "Yuzvendra Chahal", "role": "Bowler",      "country": "India",       "base": 100, "rating": 87},
    {"name": "Kuldeep Yadav",    "role": "Bowler",      "country": "India",       "base": 100, "rating": 86},
    {"name": "Mohammed Siraj",   "role": "Bowler",      "country": "India",       "base": 100, "rating": 85},
    {"name": "Trent Boult",      "role": "Bowler",      "country": "New Zealand", "base": 100, "rating": 86},
    {"name": "Mark Wood",        "role": "Bowler",      "country": "England",     "base": 100, "rating": 85},
    {"name": "R. Ashwin",        "role": "Bowler",      "country": "India",       "base": 100, "rating": 87},
    {"name": "Arshdeep Singh",   "role": "Bowler",      "country": "India",       "base":  75, "rating": 80},
    {"name": "Shardul Thakur",   "role": "All-Rounder", "country": "India",       "base":  75, "rating": 78},
    {"name": "Washington Sundar","role": "All-Rounder", "country": "India",       "base":  75, "rating": 76},
    {"name": "Deepak Chahar",    "role": "Bowler",      "country": "India",       "base":  75, "rating": 79},
    {"name": "Harshal Patel",    "role": "Bowler",      "country": "India",       "base":  75, "rating": 78},
    {"name": "Lockie Ferguson",  "role": "Bowler",      "country": "New Zealand", "base":  75, "rating": 82},
    {"name": "Prasidh Krishna",  "role": "Bowler",      "country": "India",       "base":  75, "rating": 79},
    {"name": "Umesh Yadav",      "role": "Bowler",      "country": "India",       "base":  50, "rating": 76},
    {"name": "Imran Tahir",      "role": "Bowler",      "country": "S.Africa",    "base":  50, "rating": 77},
]

IPL_TEAMS = [
    "Mumbai Indians", "Chennai Super Kings", "Royal Challengers Bengaluru",
    "Kolkata Knight Riders", "Delhi Capitals", "Sunrisers Hyderabad",
    "Rajasthan Royals", "Punjab Kings", "Gujarat Titans", "Lucknow Super Giants"
]

BUDGET = 10000  # in Lakhs = ₹100 Cr

# ─── GAME STATE ────────────────────────────────────────────────────────────────
games = {}   # room_code -> game state

def new_game_state():
    pool = PLAYERS.copy()
    random.shuffle(pool)
    return {
        "phase": "lobby",       # lobby | auction | results
        "teams": {},            # team_name -> {owner, owner_sid, budget_left, players}
        "pool": pool,
        "current_idx": 0,
        "current_bid": 0,
        "current_winner": None,
        "bid_timer": None,
        "timer_seconds": 0,
        "unsold": [],
        "doing_resale": False,
        "auction_log": [],
        "connected_sids": {},   # sid -> {name, team}
    }

# ─── HELPERS ───────────────────────────────────────────────────────────────────
def fmt(lakhs):
    if lakhs >= 100:
        return f"₹{lakhs/100:.2f} Cr"
    return f"₹{lakhs} L"

def current_player(game):
    pool = game["unsold"] if game["doing_resale"] else game["pool"]
    idx = game["current_idx"]
    if idx < len(pool):
        return pool[idx]
    return None

def broadcast(room, event, data):
    socketio.emit(event, data, room=room)

def game_state_payload(game):
    """Build the full state payload sent to clients."""
    cp = current_player(game)
    return {
        "phase": game["phase"],
        "teams": {
            k: {
                "owner": v["owner"],
                "budget_left": v["budget_left"],
                "players": v["players"],
            }
            for k, v in game["teams"].items()
        },
        "current_player": cp,
        "current_bid": game["current_bid"],
        "current_winner": game["current_winner"],
        "timer_seconds": game["timer_seconds"],
        "auction_log": game["auction_log"][-20:],
        "pool_remaining": len(game["pool"]) - game["current_idx"],
        "doing_resale": game["doing_resale"],
    }

def start_bid_timer(room, duration=15):
    game = games[room]
    if game["bid_timer"]:
        game["bid_timer"].cancel()

    def tick(remaining):
        if room not in games:
            return
        g = games[room]
        if g["phase"] != "auction":
            return
        g["timer_seconds"] = remaining
        broadcast(room, "timer_tick", {"seconds": remaining})
        if remaining > 0:
            t = threading.Timer(1.0, tick, args=[remaining - 1])
            g["bid_timer"] = t
            t.start()
        else:
            finalize_bid(room)

    t = threading.Timer(1.0, tick, args=[duration - 1])
    game["bid_timer"] = t
    game["timer_seconds"] = duration
    t.start()

def finalize_bid(room):
    if room not in games:
        return
    game = games[room]
    cp = current_player(game)
    if not cp:
        end_auction(room)
        return

    winner = game["current_winner"]
    bid = game["current_bid"]

    if winner and winner in game["teams"]:
        game["teams"][winner]["players"].append({**cp, "sold_price": bid})
        game["teams"][winner]["budget_left"] -= bid
        msg = f"🔨 {cp['name']} SOLD to {winner} for {fmt(bid)}!"
        game["auction_log"].append(msg)
    else:
        game["unsold"].append(cp)
        msg = f"❌ {cp['name']} UNSOLD"
        game["auction_log"].append(msg)

    game["current_idx"] += 1
    game["current_winner"] = None
    game["current_bid"] = 0

    pool = game["unsold"] if game["doing_resale"] else game["pool"]
    if game["current_idx"] >= len(pool):
        if not game["doing_resale"] and game["unsold"]:
            # start resale round
            game["doing_resale"] = True
            game["current_idx"] = 0
            # halve base prices
            for p in game["unsold"]:
                p["base"] = max(20, p["base"] // 2)
            msg = "🔁 RESALE ROUND — unsold players at half base price!"
            game["auction_log"].append(msg)
            broadcast(room, "game_state", game_state_payload(game))
            next_player(room)
        else:
            end_auction(room)
    else:
        broadcast(room, "game_state", game_state_payload(game))
        next_player(room)

def next_player(room):
    if room not in games:
        return
    game = games[room]
    cp = current_player(game)
    if not cp:
        end_auction(room)
        return
    game["current_bid"] = cp["base"]
    game["current_winner"] = None
    broadcast(room, "game_state", game_state_payload(game))
    start_bid_timer(room, 20)

def end_auction(room):
    if room not in games:
        return
    game = games[room]
    if game["bid_timer"]:
        game["bid_timer"].cancel()
    game["phase"] = "results"
    broadcast(room, "game_state", game_state_payload(game))

# ─── ROUTES ────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/<room_code>")
def room(room_code):
    return render_template("index.html", room_code=room_code.upper())

# ─── SOCKET EVENTS ─────────────────────────────────────────────────────────────
@socketio.on("create_room")
def on_create_room(data):
    room_code = str(random.randint(1000, 9999))
    while room_code in games:
        room_code = str(random.randint(1000, 9999))
    games[room_code] = new_game_state()
    join_room(room_code)
    emit("room_created", {"room_code": room_code})

@socketio.on("join_room_req")
def on_join_room(data):
    room_code = str(data.get("room_code", "")).strip().upper()
    # also allow numeric
    if room_code not in games:
        # try numeric
        room_code = str(data.get("room_code", "")).strip()
    if room_code not in games:
        emit("error", {"msg": "Room not found! Check the code."})
        return
    game = games[room_code]
    if game["phase"] != "lobby":
        emit("error", {"msg": "Game already started!"})
        return
    join_room(room_code)
    game["connected_sids"][request.sid] = {"name": data.get("name", "Player"), "team": None}
    emit("joined_lobby", {"room_code": room_code, "game": game_state_payload(game)})
    broadcast(room_code, "lobby_update", {
        "players": [v["name"] for v in game["connected_sids"].values()],
        "teams": list(game["teams"].keys())
    })

@socketio.on("pick_team")
def on_pick_team(data):
    room_code = data.get("room_code")
    team_name = data.get("team")
    owner_name = data.get("owner_name", "Player")
    if room_code not in games:
        return
    game = games[room_code]
    if team_name not in IPL_TEAMS:
        emit("error", {"msg": "Invalid team."})
        return
    if team_name in game["teams"]:
        emit("error", {"msg": "Team already taken!"})
        return
    game["teams"][team_name] = {
        "owner": owner_name,
        "owner_sid": request.sid,
        "budget_left": BUDGET,
        "players": []
    }
    game["connected_sids"][request.sid] = {"name": owner_name, "team": team_name}
    emit("team_picked", {"team": team_name})
    broadcast(room_code, "lobby_update", {
        "players": [v["name"] for v in game["connected_sids"].values()],
        "teams": list(game["teams"].keys()),
        "team_owners": {k: v["owner"] for k, v in game["teams"].items()}
    })

@socketio.on("start_auction")
def on_start_auction(data):
    room_code = data.get("room_code")
    if room_code not in games:
        return
    game = games[room_code]
    if len(game["teams"]) < 2:
        emit("error", {"msg": "Need at least 2 teams to start!"})
        return
    game["phase"] = "auction"
    broadcast(room_code, "auction_started", {})
    next_player(room_code)

@socketio.on("place_bid")
def on_place_bid(data):
    room_code = data.get("room_code")
    bid_amount = int(data.get("amount", 0))
    if room_code not in games:
        return
    game = games[room_code]
    if game["phase"] != "auction":
        return

    sid = request.sid
    sid_info = game["connected_sids"].get(sid, {})
    team = sid_info.get("team")
    if not team or team not in game["teams"]:
        emit("error", {"msg": "You don't own a team!"})
        return

    cp = current_player(game)
    if not cp:
        return

    budget_left = game["teams"][team]["budget_left"]
    min_bid = game["current_bid"] + (25 if game["current_bid"] < 200 else 50 if game["current_bid"] < 500 else 100)

    if bid_amount < min_bid:
        emit("bid_error", {"msg": f"Minimum bid is {fmt(min_bid)}"})
        return
    if bid_amount > budget_left:
        emit("bid_error", {"msg": f"Not enough budget! You have {fmt(budget_left)}"})
        return

    game["current_bid"] = bid_amount
    game["current_winner"] = team
    msg = f"💰 {game['teams'][team]['owner']} ({team}) bids {fmt(bid_amount)}"
    game["auction_log"].append(msg)
    broadcast(room_code, "game_state", game_state_payload(game))
    start_bid_timer(room_code, 12)  # reset timer on new bid

@socketio.on("disconnect")
def on_disconnect():
    sid = request.sid
    for room_code, game in games.items():
        if sid in game["connected_sids"]:
            info = game["connected_sids"].pop(sid)
            if game["phase"] == "lobby":
                broadcast(room_code, "lobby_update", {
                    "players": [v["name"] for v in game["connected_sids"].values()],
                    "teams": list(game["teams"].keys()),
                    "team_owners": {k: v["owner"] for k, v in game["teams"].items()}
                })
            break

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port, debug=False, allow_unsafe_werkzeug=True)
