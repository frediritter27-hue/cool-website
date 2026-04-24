const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;
const DATA_FILE = path.join('/tmp', 'golf_data.json');

app.use(cors());
app.use(express.json());
app.use(express.static('.'));

// ---------- helpers ----------
function loadData() {
  try {
    if (fs.existsSync(DATA_FILE)) return JSON.parse(fs.readFileSync(DATA_FILE, 'utf8'));
  } catch(e) {}
  return {
    tournament: 'Golf Turnier',
    course: 'Golfplatz',
    currentRound: 1,
    users: {},
    scores: {},
    holes: Array.from({length:18}, (_,i) => ({
      number: i+1,
      par: [4,4,3,5,4,4,3,5,4,4,4,3,5,4,4,3,5,4][i]
    }))
  };
}

function saveData(d) {
  try { fs.writeFileSync(DATA_FILE, JSON.stringify(d, null, 2)); } catch(e) {}
}

function hash(s) {
  let h = 0;
  for (let i = 0; i < s.length; i++) { h = ((h << 5) - h) + s.charCodeAt(i); h |= 0; }
  return h.toString(16);
}

// ---------- routes ----------
// Get all public data (leaderboard, holes, tournament info)
app.get('/api/public', (req, res) => {
  const d = loadData();
  const leaderboard = Object.entries(d.users).map(([u, info]) => {
    const sc = d.scores[u] && d.scores[u][d.currentRound];
    const total = sc ? sc.reduce((a,b) => a+b, 0) : 0;
    const holesPlayed = sc ? sc.filter(s => s > 0).length : 0;
    return { username: u, name: info.name, handicap: info.handicap, total, holesPlayed };
  });
  res.json({
    tournament: d.tournament,
    course: d.course,
    currentRound: d.currentRound,
    holes: d.holes,
    leaderboard
  });
});

// Register
app.post('/api/register', (req, res) => {
  const { username, name, handicap, password } = req.body;
  if (!username || !name || !password) return res.status(400).json({ error: 'Felder fehlen' });
  if (username.length < 3) return res.status(400).json({ error: 'Benutzername mind. 3 Zeichen' });
  if (password.length < 4) return res.status(400).json({ error: 'Passwort mind. 4 Zeichen' });
  const d = loadData();
  const u = username.toLowerCase().trim();
  if (d.users[u]) return res.status(400).json({ error: 'Benutzername bereits vergeben' });
  const isFirstUser = Object.keys(d.users).length === 0;
  d.users[u] = { name: name.trim(), handicap: parseFloat(handicap)||0, passwordHash: hash(password), isAdmin: isFirstUser };
  saveData(d);
  res.json({ success: true, isAdmin: isFirstUser, name: name.trim() });
});

// Login
app.post('/api/login', (req, res) => {
  const { username, password } = req.body;
  const d = loadData();
  const u = username && username.toLowerCase().trim();
  const user = d.users[u];
  if (!user || user.passwordHash !== hash(password)) return res.status(401).json({ error: 'Falscher Benutzername oder Passwort' });
  res.json({ success: true, username: u, name: user.name, isAdmin: user.isAdmin, handicap: user.handicap });
});

// Get my scores
app.get('/api/scores/:username', (req, res) => {
  const d = loadData();
  const u = req.params.username.toLowerCase();
  res.json({ scores: d.scores[u] || {} });
});

// Save my scores
app.post('/api/scores/:username', (req, res) => {
  const { round, scores, passwordHash } = req.body;
  const d = loadData();
  const u = req.params.username.toLowerCase();
  if (!d.users[u] || d.users[u].passwordHash !== passwordHash) return res.status(401).json({ error: 'Nicht autorisiert' });
  if (!d.scores[u]) d.scores[u] = {};
  d.scores[u][round] = scores;
  saveData(d);
  res.json({ success: true });
});

// Admin: update settings
app.post('/api/admin/settings', (req, res) => {
  const { username, passwordHash, tournament, course, currentRound, holes } = req.body;
  const d = loadData();
  const u = username && username.toLowerCase();
  if (!d.users[u] || !d.users[u].isAdmin || d.users[u].passwordHash !== passwordHash) return res.status(403).json({ error: 'Kein Admin-Zugriff' });
  if (tournament) d.tournament = tournament;
  if (course) d.course = course;
  if (currentRound) d.currentRound = parseInt(currentRound);
  if (holes) d.holes = holes;
  saveData(d);
  res.json({ success: true });
});

// Admin: get all users
app.get('/api/admin/users', (req, res) => {
  const { username, passwordHash } = req.query;
  const d = loadData();
  const u = username && username.toLowerCase();
  if (!d.users[u] || !d.users[u].isAdmin || d.users[u].passwordHash !== passwordHash) return res.status(403).json({ error: 'Kein Admin-Zugriff' });
  const users = Object.entries(d.users).map(([un, info]) => ({
    username: un, name: info.name, handicap: info.handicap, isAdmin: info.isAdmin
  }));
  res.json({ users });
});

// Serve frontend
app.get('*', (req, res) => {
  res.sendFile(path.join(process.cwd(), 'index.html'));
});

app.listen(PORT, () => console.log('Golf Scoring Server running on port ' + PORT));
