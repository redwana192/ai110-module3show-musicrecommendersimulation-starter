"""Explainable weighted song scoring shared by functional and OOP interfaces."""
import csv
import math
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class Song:
    """Store a catalog track and its manually assigned attributes."""
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """Store a listener's genre, mood, energy, and acoustic preferences."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


@dataclass(frozen=True)
class ScoreWeights:
    """Keep the scoring experiment explicit without changing default rules."""
    genre: float = 2.0
    mood: float = 1.0
    energy: float = 1.0
    acoustic: float = 0.5

    def __post_init__(self):
        """Reject invalid weights before any songs are scored."""
        for value in asdict(self).values():
            if not math.isfinite(value) or value < 0:
                raise ValueError('Weights must be finite and nonnegative.')


DEFAULT_WEIGHTS = ScoreWeights()
ENERGY_FOCUSED = ScoreWeights(genre=1.0, mood=1.0, energy=2.0)
UNIT_FEATURES = ('energy', 'valence', 'danceability', 'acousticness')
REQUIRED_COLUMNS = tuple(Song.__dataclass_fields__)


def unit_value(value, label):
    """Convert a feature to a finite number in the inclusive unit interval."""
    try:
        number = float(value)
    except (ValueError, TypeError) as exc:
        raise ValueError(f'{label} must be a number from 0 to 1.') from exc
    if not math.isfinite(number) or not 0 <= number <= 1:
        raise ValueError(f'{label} must be a number from 0 to 1.')
    return number


def load_songs(csv_path):
    """Read validated song dictionaries with numeric feature conversion."""
    songs, seen_ids = [], set()
    with Path(csv_path).open(encoding='utf-8-sig', newline='') as source:
        reader = csv.DictReader(source)
        if not set(REQUIRED_COLUMNS).issubset(reader.fieldnames or []):
            raise ValueError('CSV is missing required Song columns.')
        for line, row in enumerate(reader, start=2):
            try:
                if None in row:
                    raise ValueError('Too many CSV fields.')
                song = {key: row[key] for key in REQUIRED_COLUMNS}
                song['id'] = int(song['id'])
                if song['id'] <= 0 or song['id'] in seen_ids:
                    raise ValueError('Song IDs must be positive and unique.')
                for key in ('title', 'artist', 'genre', 'mood'):
                    if not song[key] or not song[key].strip():
                        raise ValueError(f'{key} cannot be empty.')
                    song[key] = song[key].strip()
                for key in UNIT_FEATURES:
                    song[key] = unit_value(song[key], key)
                song['tempo_bpm'] = float(song['tempo_bpm'])
                if not math.isfinite(song['tempo_bpm']) or song['tempo_bpm'] <= 0:
                    raise ValueError('Tempo must be positive and finite.')
                seen_ids.add(song['id'])
                songs.append(song)
            except (ValueError, TypeError) as exc:
                raise ValueError(f'CSV row {line}: {exc}') from exc
    return songs


def score_song(user_prefs, song, weights=DEFAULT_WEIGHTS):
    """Return a numeric relevance score and the reasons for each contribution."""
    # Accept the starter CLI keys and the explicit UserProfile field names.
    genre = user_prefs.get('genre', user_prefs.get('favorite_genre', ''))
    mood = user_prefs.get('mood', user_prefs.get('favorite_mood', ''))
    target = unit_value(user_prefs.get('energy', user_prefs.get('target_energy')), 'Target energy')
    energy = unit_value(song['energy'], 'Song energy')
    score, reasons = 0.0, []
    for feature, preference, weight in [('genre', genre, weights.genre), ('mood', mood, weights.mood)]:
        if not isinstance(preference, str) or not preference.strip():
            raise ValueError(f'Preferred {feature} is required.')
        if song[feature].strip().casefold() == preference.strip().casefold():
            score += weight
            reasons.append(f'{feature} match (+{weight:.2f})')
        else:
            reasons.append(f'{feature} mismatch (+0.00)')
    contribution = weights.energy * (1 - abs(energy - target))
    score += contribution
    reasons.append(f'energy {energy:.2f} vs target {target:.2f} (+{contribution:.2f})')
    likes_acoustic = user_prefs.get('likes_acoustic', False)
    if type(likes_acoustic) is not bool:
        raise ValueError('likes_acoustic must be true or false.')
    if likes_acoustic:
        acoustic_points = weights.acoustic * unit_value(song['acousticness'], 'Acousticness')
        score += acoustic_points
        reasons.append(f'acoustic preference (+{acoustic_points:.2f})')
    return score, reasons


def recommend_songs(user_prefs, songs, k=5, weights=DEFAULT_WEIGHTS):
    """Score every song once and return top K explained results, highest first."""
    if type(k) is not int or k < 0:
        raise ValueError('k must be a nonnegative integer.')
    results = []
    for song in songs:
        score, reasons = score_song(user_prefs, song, weights)
        results.append((song, score, '; '.join(reasons)))
    # Stable sorting retains CSV order for equal scores, and leaves input unchanged.
    return sorted(results, key=lambda result: result[1], reverse=True)[:k]


class Recommender:
    """Adapt Song objects to the same scorer used by the CLI functions."""
    def __init__(self, songs):
        """Store the catalog without changing the caller's list."""
        self.songs = list(songs)

    def recommend(self, user, k=5):
        """Return the original Song objects ranked for a UserProfile."""
        catalog = [asdict(song) for song in self.songs]
        ranked = recommend_songs(asdict(user), catalog, k)
        by_id = {song.id: song for song in self.songs}
        return [by_id[song['id']] for song, _, _ in ranked]

    def explain_recommendation(self, user, song):
        """Explain one Song with the identical scoring recipe used to rank it."""
        _, reasons = score_song(asdict(user), asdict(song))
        return '; '.join(reasons)
