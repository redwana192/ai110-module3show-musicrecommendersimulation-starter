"""Run the default profile, diverse evaluations, and one weight experiment."""
import argparse
from pathlib import Path
from .recommender import load_songs, recommend_songs, DEFAULT_WEIGHTS, ENERGY_FOCUSED

CATALOG = Path(__file__).resolve().parents[1] / 'data' / 'songs.csv'
PROFILES = {
    'High-Energy Pop': {'genre': 'pop', 'mood': 'happy', 'energy': 0.8},
    'Chill Lofi': {'genre': 'lofi', 'mood': 'chill', 'energy': 0.35},
    'Deep Intense Rock': {'genre': 'rock', 'mood': 'intense', 'energy': 0.9},
    'Conflicting Sad Energy': {'genre': 'pop', 'mood': 'sad', 'energy': 0.95},
    'Unseen Genre': {'genre': 'opera', 'mood': 'chill', 'energy': 0.3},
}


def print_results(label, profile, songs, weights=DEFAULT_WEIGHTS):
    """Print titles, numeric scores, and transparent contribution reasons."""
    print(f'\nProfile: {label}')
    print(f"Preferences: genre={profile['genre']}, mood={profile['mood']}, energy={profile['energy']}")
    for position, (song, score, explanation) in enumerate(recommend_songs(profile, songs, 5, weights), 1):
        print(f"{position}. {song['title']} — {song['artist']} | score={score:.2f}")
        print(f'   Because: {explanation}')


def main():
    """Expose reproducible default, evaluation, and experiment CLI commands."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evaluate', action='store_true', help='Show five contrasting profiles')
    parser.add_argument('--experiment', action='store_true', help='Halve genre weight and double energy weight')
    args = parser.parse_args()
    songs = load_songs(CATALOG)
    print(f'Loaded songs: {len(songs)}')
    profiles = PROFILES if args.evaluate else {'High-Energy Pop': PROFILES['High-Energy Pop']}
    for label, profile in profiles.items():
        print_results(label, profile, songs)
    if args.experiment:
        print('\nWEIGHT EXPERIMENT: genre 2.0 -> 1.0; energy 1.0 -> 2.0; mood stays 1.0')
        print_results('High-Energy Pop / energy-focused', PROFILES['High-Energy Pop'], songs, ENERGY_FOCUSED)


if __name__ == '__main__':
    main()
