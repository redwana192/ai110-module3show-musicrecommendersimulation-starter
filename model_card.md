# Model Card — VibeFinder 1.0

## 1. Model Name
VibeFinder 1.0, an explained music recommendation simulation.

## 2. Goal and Intended Use
Suggest five catalog songs that match a listener's stated taste. This is for classroom experiments with scoring rules. It should not be used as evidence of a person's actual taste or as a production music recommendation service. There is no learned model or accuracy claim.

## 3. Algorithm Summary
Each exact genre match earns 2 points. Each exact mood match earns 1 point. Energy earns up to 1 point, with less credit as the gap from the user's target grows. If the optional acoustic preference is enabled, acousticness contributes up to 0.5 extra points. All songs are scored, then ranked from highest to lowest. Equal scores keep catalog order. The normal profiles use genre, mood, and energy only.

## 4. Data Used
The CSV contains 18 synthetic tracks with manually assigned features. The first 10 rows come from the CodePath starter. Eight AI-generated rows were added for folk, latin, edm, classical, pop, metal, reggae, and rock. Six of those genres were absent from the original catalog. Each row has an ID, title, artist, genre, mood, energy, tempo, valence, danceability, and acousticness. Energy, valence, danceability, and acousticness range from 0 to 1. Tempo is measured in beats per minute. Tempo, valence, and danceability are loaded and validated but do not affect the baseline score. The numbers are illustrative annotations, not audio measurements.

## 5. Strengths
The three core profiles have different top results. Happy pop ranks Sunrise City first at 3.98. Chill lofi ranks Library Rain first at 4.00. Intense rock ranks Storm Runner first at 3.99. Every result includes contribution reasons, so the score can be checked by hand. Both the functional and object interfaces use the same scorer.

## 6. Limitations and Bias
Pop and lofi each have three catalog tracks, while many added genres have only one, so those listeners have more matching choices. The exact genre rule treats indie pop and pop as entirely different labels. Paper Hearts, a sad pop song, outranks the happy indie pop song Rooftop Lights for the happy-pop profile because genre has more weight than mood. Repeatedly showing the same matching labels could create a filter bubble. The simulator ignores listening history, language, lyrics, real audio, and feedback, and the evaluation has no human ratings to establish accuracy.

## 7. Evaluation Process
Five profiles were run with top-five output captured in README.md and evidence/evaluation_output.txt. The three core profiles are High-Energy Pop, Chill Lofi, and Deep Intense Rock. The edge profiles are Conflicting Sad Energy and Unseen Genre. The conflicting profile asks for sad pop at energy 0.95. Paper Hearts wins even though its energy is 0.55, because its two label matches outweigh the energy gap. Unseen Genre asks for opera, which the catalog lacks. Spacewalk Thoughts wins using mood and energy alone. That fallback provides results but cannot supply an opera track.

### Comparisons for every pair of tested profiles
- Pop and lofi have no shared top-five songs. Pop favors pop labels and high energy. Lofi favors lofi labels and lower energy.
- Pop and rock share Gym Hero. The rock list rewards its intense mood, while the pop list rewards its genre.
- Pop and conflicting sad energy share Sunrise City, Gym Hero, and Paper Hearts. The sad profile moves Paper Hearts from third to first because mood now matches.
- Pop and unseen opera have no shared top-five songs. The opera request loses all genre points and favors chill, low-energy tracks.
- Lofi and rock have no shared top-five songs. Their preferred genres, moods, and energies differ.
- Lofi and conflicting sad energy have no shared top-five songs. The latter favors pop with much higher energy.
- Lofi and unseen opera share Library Rain, Midnight Coding, Spacewalk Thoughts, and Coffee Shop Stories. Removing lofi genre credit moves Spacewalk Thoughts to first.
- Rock and conflicting sad energy share Gym Hero, Iron Horizon, and Afterglow Circuit. Their similar energy targets produce overlap, but genre and mood make the winners different.
- Rock and unseen opera have no shared top-five songs. Intense high-energy tracks lose to chill low-energy tracks for the opera request.
- Conflicting sad energy and unseen opera have no shared top-five songs. The sad request rewards pop, while the opera request falls back to chill mood and low energy.

### Weight experiment
The experiment halves genre from 2 to 1, doubles energy from 1 to 2, and leaves mood at 1. Sunrise City remains first, with score 3.96. Rooftop Lights moves from fourth to second, Gym Hero moves from second to third, and Paper Hearts moves from third to fourth. All five titles remain the same. This is a change in ordering, not proof of improved accuracy. The default recipe stays unchanged, and the experiment is reproduced with `python -m src.main --experiment`.

### Verification
27 tests pass, including the two unchanged starter tests. Tests cover exact score arithmetic, closer energy values, profile winners, rankings, stable ties, no input mutation, acoustic preferences, both APIs, the weight experiment, CSV parsing, invalid numbers, and top-K boundaries. Actual terminal evidence is included.

## 8. Ideas for Improvement
- Collect explicit listener feedback and compare different weights with held-out ratings.
- Expand underrepresented genres and languages with verified audio features.
- Allow several favorite genres and explore diverse artists in each list.

## 9. Engineering Reflection
The project shows that a small scoring rule can produce recognizable recommendations because it combines labels with numerical closeness. The most revealing result is that Paper Hearts beats a happy indie pop track for a happy-pop listener. This exposes how strongly the chosen genre weight controls the ranking. AI assistance was used to implement the code, expand the synthetic catalog, propose edge profiles, and prepare the tests and documentation. Arithmetic checks and actual CLI runs verified the generated suggestions. A useful next step would be testing the rules against real listener judgments. This reflection describes the AI-assisted build. The student's local run and personal review are still pending.
