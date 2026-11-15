from copy import deepcopy
from dataclasses import asdict
from pathlib import Path
import pytest
from src.recommender import (
    Song, UserProfile, Recommender, ScoreWeights, load_songs,
    score_song, recommend_songs, ENERGY_FOCUSED,
)
from src.main import PROFILES

CATALOG = Path(__file__).resolve().parents[1] / 'data/songs.csv'


def catalog():
    return load_songs(CATALOG)


def test_catalog_preserves_starter_and_adds_eight_songs():
    songs = catalog()
    assert len(songs) == 18
    assert [song['id'] for song in songs] == list(range(1, 19))
    assert songs[0]['title'] == 'Sunrise City'
    assert isinstance(songs[0]['energy'], float)
    assert isinstance(songs[0]['tempo_bpm'], float)
    assert len({song['genre'] for song in songs[10:]}) == 8


def test_score_math_and_explanation():
    score, reasons = score_song(PROFILES['High-Energy Pop'], catalog()[0])
    assert score == pytest.approx(3.98)
    assert reasons == ['genre match (+2.00)', 'mood match (+1.00)',
                       'energy 0.82 vs target 0.80 (+0.98)']


def test_closer_energy_beats_higher_energy():
    song = catalog()[0]
    perfect = dict(song, energy=0.35)
    high = dict(song, energy=0.9)
    profile = dict(PROFILES['High-Energy Pop'], energy=0.35)
    assert score_song(profile, perfect)[0] > score_song(profile, high)[0]


@pytest.mark.parametrize('label,title', [
    ('High-Energy Pop', 'Sunrise City'), ('Chill Lofi', 'Library Rain'),
    ('Deep Intense Rock', 'Storm Runner'), ('Conflicting Sad Energy', 'Paper Hearts'),
    ('Unseen Genre', 'Spacewalk Thoughts')])
def test_profile_winners(label, title):
    ranked = recommend_songs(PROFILES[label], catalog())
    assert ranked[0][0]['title'] == title
    assert len(ranked) == 5
    assert [r[1] for r in ranked] == sorted([r[1] for r in ranked], reverse=True)


def test_weight_experiment_changes_order():
    songs = catalog()
    default = recommend_songs(PROFILES['High-Energy Pop'], songs)
    shifted = recommend_songs(PROFILES['High-Energy Pop'], songs, weights=ENERGY_FOCUSED)
    assert default[1][0]['title'] == 'Gym Hero'
    assert shifted[1][0]['title'] == 'Rooftop Lights'
    assert shifted[0][1] == pytest.approx(3.96)


def test_acoustic_preference_is_shared_by_both_interfaces():
    songs = catalog()
    user = UserProfile('lofi', 'chill', 0.35, True)
    model = Recommender([Song(**song) for song in songs])
    functional = recommend_songs(asdict(user), songs)
    assert [s.id for s in model.recommend(user)] == [s['id'] for s, _, _ in functional]
    assert 'acoustic preference' in model.explain_recommendation(user, model.songs[0])
    base = score_song(dict(asdict(user), likes_acoustic=False), songs[0])[0]
    assert score_song(asdict(user), songs[0])[0] == pytest.approx(base + 0.09)


def test_stable_ties_and_input_unchanged():
    song = catalog()[0]
    songs = [dict(song, id=2), dict(song, id=1)]
    original = deepcopy(songs)
    assert [s['id'] for s, _, _ in recommend_songs(PROFILES['High-Energy Pop'], songs)] == [2, 1]
    assert songs == original


def test_empty_zero_and_large_k():
    assert recommend_songs(PROFILES['High-Energy Pop'], []) == []
    assert recommend_songs(PROFILES['High-Energy Pop'], catalog(), 0) == []
    assert len(recommend_songs(PROFILES['High-Energy Pop'], catalog(), 50)) == 18


@pytest.mark.parametrize('k', [-1, 2.5, True])
def test_invalid_k(k):
    with pytest.raises(ValueError):
        recommend_songs(PROFILES['High-Energy Pop'], catalog(), k)


@pytest.mark.parametrize('energy', [-0.1, 1.1, float('nan'), float('inf'), 'bad', None])
def test_invalid_energy(energy):
    with pytest.raises(ValueError):
        score_song(dict(PROFILES['High-Energy Pop'], energy=energy), catalog()[0])


def test_case_and_space_normalization():
    profile = dict(PROFILES['High-Energy Pop'], genre=' POP ', mood='HAPPY')
    assert score_song(profile, catalog()[0])[0] == pytest.approx(3.98)


def test_csv_errors_include_row_number(tmp_path):
    source = CATALOG.read_text().splitlines()
    fields = source[1].split(',')
    fields[5] = 'nan'
    path = tmp_path / 'bad.csv'
    path.write_text(source[0] + '\n' + ','.join(fields) + '\n')
    with pytest.raises(ValueError, match='CSV row 2'):
        load_songs(path)


def test_missing_columns_and_duplicate_ids(tmp_path):
    path = tmp_path / 'bad.csv'
    path.write_text('id,title\n1,Title\n')
    with pytest.raises(ValueError, match='columns'):
        load_songs(path)
    source = CATALOG.read_text().splitlines()
    path.write_text('\n'.join([source[0], source[1], source[1]]))
    with pytest.raises(ValueError, match='unique'):
        load_songs(path)


def test_invalid_weights():
    with pytest.raises(ValueError):
        ScoreWeights(energy=-1)
