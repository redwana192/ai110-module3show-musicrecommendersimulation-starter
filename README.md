# Music Recommender Simulation — VibeFinder

A CLI-first Python simulator that ranks 18 synthetic songs and explains each result. Prepared with ChatGPT assistance for CEN4010 Week 6.

## Getting Started
Requires Python 3.10 or newer. In this project folder, run these commands one at a time.

```bat
python -m pip install -r requirements.txt
python -m src.main
python -m src.main --evaluate --experiment
python -m pytest -q
```

The application prints results in the terminal. It needs no account, API key, or external music service. The CLI finds its CSV relative to the module, so it also works when imported from another working directory. Launch the command from the project folder so Python can find src.

## How The System Works
Content-based recommendations compare item attributes with a person's preferences. Collaborative filtering instead learns patterns from many users' interactions, such as likes, skips, and listening histories. Large services can retrieve candidates, score them, and then re-rank them for additional goals. This simulator compares explicit taste preferences with a small song catalog, using exact genre and mood labels plus energy closeness. It creates an explained ranking without training a machine-learning model.

Primary references
- https://developers.google.com/machine-learning/recommendation/content-based/basics
- https://developers.google.com/machine-learning/recommendation/collaborative/basics
- https://developers.google.com/machine-learning/recommendation/overview/types

### Data and profile objects
`Song` contains id, title, artist, genre, mood, energy, tempo_bpm, valence, danceability, and acousticness. The loader returns dictionaries with id as an integer and numerical attributes as floats. The starter's `UserProfile` holds favorite_genre, favorite_mood, target_energy, and likes_acoustic. The functional API accepts the starter CLI's genre/mood/energy dictionary keys as well as the equivalent profile field names. The CLI defines five explicit preference dictionaries in src/main.py.

### Algorithm Recipe
A genre match earns 2 points. A mood match earns 1 point. Energy contributes `1 - abs(song_energy - target_energy)`, so closer values earn more. The default examples score from 0 to 4. If likes_acoustic is true, `0.5 * acousticness` adds up to 0.5 points. False disables the optional bonus. Tempo, valence, and danceability are validated but unused in this recipe.

For Sunrise City and the default pop/happy/0.8 profile, the score is `2 + 1 + (1 - abs(0.82 - 0.8)) = 3.98`. Each component also produces an explanation. Scoring judges one track. Ranking scores every track, sorts the results highest first, and takes the top K. Equal scores keep CSV order. `sorted()` creates a new list, whereas `.sort()` changes an existing list and returns None. The implementation uses sorted() to preserve the input order.

The flow is preferences plus catalog, then per-song scoring, then sorting, then the top five with reasons. Sorting is O(n log n) and scores every catalog entry once. Working memory is O(n).

### Dataset and expected bias
The first 10 starter tracks remain unchanged. Eight AI-generated synthetic rows add six previously absent genres and two additional pop/rock options. Exact genre labels and the two-point genre weight can favor familiar styles and reduce exploration. Energy alone also cannot represent a listener's whole musical taste.

## Sample Recommendation Output
Actual output of `python -m src.main` follows.

```text
Loaded songs: 18

Profile: High-Energy Pop
Preferences: genre=pop, mood=happy, energy=0.8
1. Sunrise City — Neon Echo | score=3.98
   Because: genre match (+2.00); mood match (+1.00); energy 0.82 vs target 0.80 (+0.98)
2. Gym Hero — Max Pulse | score=2.87
   Because: genre match (+2.00); mood mismatch (+0.00); energy 0.93 vs target 0.80 (+0.87)
3. Paper Hearts — June Signal | score=2.75
   Because: genre match (+2.00); mood mismatch (+0.00); energy 0.55 vs target 0.80 (+0.75)
4. Rooftop Lights — Indigo Parade | score=1.96
   Because: genre mismatch (+0.00); mood match (+1.00); energy 0.76 vs target 0.80 (+0.96)
5. Havana Morning — Isla Clara | score=0.98
   Because: genre mismatch (+0.00); mood mismatch (+0.00); energy 0.78 vs target 0.80 (+0.98)
```

## Evaluation Profiles and Experiment Output
Actual output of `python -m src.main --evaluate --experiment` follows. It contains the top five results for three core tastes and two edge cases, followed by the experiment. Pairwise comparisons and limitations appear in model_card.md.

```text
Loaded songs: 18

Profile: High-Energy Pop
Preferences: genre=pop, mood=happy, energy=0.8
1. Sunrise City — Neon Echo | score=3.98
   Because: genre match (+2.00); mood match (+1.00); energy 0.82 vs target 0.80 (+0.98)
2. Gym Hero — Max Pulse | score=2.87
   Because: genre match (+2.00); mood mismatch (+0.00); energy 0.93 vs target 0.80 (+0.87)
3. Paper Hearts — June Signal | score=2.75
   Because: genre match (+2.00); mood mismatch (+0.00); energy 0.55 vs target 0.80 (+0.75)
4. Rooftop Lights — Indigo Parade | score=1.96
   Because: genre mismatch (+0.00); mood match (+1.00); energy 0.76 vs target 0.80 (+0.96)
5. Havana Morning — Isla Clara | score=0.98
   Because: genre mismatch (+0.00); mood mismatch (+0.00); energy 0.78 vs target 0.80 (+0.98)

Profile: Chill Lofi
Preferences: genre=lofi, mood=chill, energy=0.35
1. Library Rain — Paper Lanterns | score=4.00
   Because: genre match (+2.00); mood match (+1.00); energy 0.35 vs target 0.35 (+1.00)
2. Midnight Coding — LoRoom | score=3.93
   Because: genre match (+2.00); mood match (+1.00); energy 0.42 vs target 0.35 (+0.93)
3. Focus Flow — LoRoom | score=2.95
   Because: genre match (+2.00); mood mismatch (+0.00); energy 0.40 vs target 0.35 (+0.95)
4. Spacewalk Thoughts — Orbit Bloom | score=1.93
   Because: genre mismatch (+0.00); mood match (+1.00); energy 0.28 vs target 0.35 (+0.93)
5. Coffee Shop Stories — Slow Stereo | score=0.98
   Because: genre mismatch (+0.00); mood mismatch (+0.00); energy 0.37 vs target 0.35 (+0.98)

Profile: Deep Intense Rock
Preferences: genre=rock, mood=intense, energy=0.9
1. Storm Runner — Voltline | score=3.99
   Because: genre match (+2.00); mood match (+1.00); energy 0.91 vs target 0.90 (+0.99)
2. River of Glass — Stone Arcade | score=3.94
   Because: genre match (+2.00); mood match (+1.00); energy 0.84 vs target 0.90 (+0.94)
3. Gym Hero — Max Pulse | score=1.97
   Because: genre mismatch (+0.00); mood match (+1.00); energy 0.93 vs target 0.90 (+0.97)
4. Iron Horizon — Ash Compass | score=1.92
   Because: genre mismatch (+0.00); mood match (+1.00); energy 0.98 vs target 0.90 (+0.92)
5. Afterglow Circuit — Prism Harbor | score=0.94
   Because: genre mismatch (+0.00); mood mismatch (+0.00); energy 0.96 vs target 0.90 (+0.94)

Profile: Conflicting Sad Energy
Preferences: genre=pop, mood=sad, energy=0.95
1. Paper Hearts — June Signal | score=3.60
   Because: genre match (+2.00); mood match (+1.00); energy 0.55 vs target 0.95 (+0.60)
2. Gym Hero — Max Pulse | score=2.98
   Because: genre match (+2.00); mood mismatch (+0.00); energy 0.93 vs target 0.95 (+0.98)
3. Sunrise City — Neon Echo | score=2.87
   Because: genre match (+2.00); mood mismatch (+0.00); energy 0.82 vs target 0.95 (+0.87)
4. Afterglow Circuit — Prism Harbor | score=0.99
   Because: genre mismatch (+0.00); mood mismatch (+0.00); energy 0.96 vs target 0.95 (+0.99)
5. Iron Horizon — Ash Compass | score=0.97
   Because: genre mismatch (+0.00); mood mismatch (+0.00); energy 0.98 vs target 0.95 (+0.97)

Profile: Unseen Genre
Preferences: genre=opera, mood=chill, energy=0.3
1. Spacewalk Thoughts — Orbit Bloom | score=1.98
   Because: genre mismatch (+0.00); mood match (+1.00); energy 0.28 vs target 0.30 (+0.98)
2. Library Rain — Paper Lanterns | score=1.95
   Because: genre mismatch (+0.00); mood match (+1.00); energy 0.35 vs target 0.30 (+0.95)
3. Midnight Coding — LoRoom | score=1.88
   Because: genre mismatch (+0.00); mood match (+1.00); energy 0.42 vs target 0.30 (+0.88)
4. Desert Strings — Saffron Trail | score=1.00
   Because: genre mismatch (+0.00); mood mismatch (+0.00); energy 0.30 vs target 0.30 (+1.00)
5. Coffee Shop Stories — Slow Stereo | score=0.93
   Because: genre mismatch (+0.00); mood mismatch (+0.00); energy 0.37 vs target 0.30 (+0.93)

WEIGHT EXPERIMENT: genre 2.0 -> 1.0; energy 1.0 -> 2.0; mood stays 1.0

Profile: High-Energy Pop / energy-focused
Preferences: genre=pop, mood=happy, energy=0.8
1. Sunrise City — Neon Echo | score=3.96
   Because: genre match (+1.00); mood match (+1.00); energy 0.82 vs target 0.80 (+1.96)
2. Rooftop Lights — Indigo Parade | score=2.92
   Because: genre mismatch (+0.00); mood match (+1.00); energy 0.76 vs target 0.80 (+1.92)
3. Gym Hero — Max Pulse | score=2.74
   Because: genre match (+1.00); mood mismatch (+0.00); energy 0.93 vs target 0.80 (+1.74)
4. Paper Hearts — June Signal | score=2.50
   Because: genre match (+1.00); mood mismatch (+0.00); energy 0.55 vs target 0.80 (+1.50)
5. Havana Morning — Isla Clara | score=1.96
   Because: genre mismatch (+0.00); mood mismatch (+0.00); energy 0.78 vs target 0.80 (+1.96)
```

## Experiments You Tried
Default genre weight is 2, mood is 1, and energy is 1. The energy-focused experiment changes genre to 1 and energy to 2. Rooftop Lights rises from fourth to second for happy pop because its matching mood and close energy can now beat a genre match alone. The same five songs remain in the list. This shows sensitivity to weighting, with no claim of improved real-world accuracy. Both settings use the same scoring function through explicit weight values.

## Testing
The two starter tests are preserved. The added tests cover CSV numeric conversion, eight added tracks, exact score math and reasons, energy closeness, five profile winners, an actual ranking change, acoustic preference, matching OOP/functional results, stable ties, input preservation, empty catalogs, top-K bounds, and invalid data. Run `python -m pytest`.

```text
============================= test session starts ==============================
platform linux -- Python 3.12.14, pytest-9.2.0, pluggy-1.7.0
rootdir: /workspace/scratch/2e3d487317db/week6-music
plugins: anyio-4.14.2
collected 27 items

tests/test_recommender.py ..                                             [  7%]
tests/test_scoring.py .........................                          [100%]

=============================== warnings summary ===============================
../../../../opt/codex/runtimes/codex-primary-runtime/dependencies/python/lib/python3.12/site-packages/anyio/pytest_plugin.py:14
  /opt/codex/runtimes/codex-primary-runtime/dependencies/python/lib/python3.12/site-packages/anyio/pytest_plugin.py:14: PytestRemovedIn10Warning: _pytest.python.CallSpec2 has been renamed to CallSpec.
  The CallSpec2 alias will be removed in pytest 10.
  Update imports to use CallSpec instead.
  See https://docs.pytest.org/en/stable/deprecations.html#callspec2-renamed
    from _pytest.python import CallSpec2

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================== 27 passed, 1 warning in 0.04s =========================
```

## Limitations and Risks
The catalog and annotations are synthetic and small. Genre labels have no hierarchy. Preferences are explicit and static. There is no audio analysis, listening history, trained model, or feedback-based accuracy measurement. Exact labels and catalog imbalance can lead to repetitive results. See model_card.md for the evaluation and intended-use boundaries.

## Reflection
The simulation makes it clear how a few weights can create personalized-looking recommendations. Its counterintuitive rankings show why numerical output needs review. Changing the weights changes what the system rewards. A human reviewer should inspect the reasons and compare them with their own preferences before describing the experience in Canvas.

The full Model Card includes the engineering reflection and future improvements. Local student verification, GitHub fork creation, pushing, and CodePath submission remain pending.
