"""Apply the two revised French quiz articles to the latest nine-round app.

Put this file inside Ice_Breaker_Game_App and run: python UpdateArticles.py
Or run: python UpdateArticles.py /path/to/Ice_Breaker_Game_App
Uses only Python's standard library. No deployment or database changes.
"""
from __future__ import annotations
import ast
import copy
from datetime import datetime, timezone
import json
from pathlib import Path
import pprint
import re
import sys

BITCOIN = """Bitcoin : une chute de 50 % en vingt-quatre heures secoue les marchés

Le bitcoin a perdu la moitié de sa valeur en une journée. La cryptomonnaie est passée de 110 000 à 55 000 dollars, entraînant dans sa chute les principales monnaies numériques et les actions de plusieurs entreprises du secteur.

Le mouvement s’est accéléré pendant la nuit, lorsque les premières ventes importantes ont déclenché une série de liquidations automatiques. Les investisseurs qui avaient emprunté pour augmenter leurs positions ont vu leurs garanties devenir insuffisantes. Leurs avoirs ont alors été vendus, alimentant à leur tour la baisse.

Au réveil, de nombreux particuliers ont découvert un portefeuille amputé de plusieurs mois de gains. Les plateformes d’échange ont enregistré une forte hausse des connexions, tandis que les autres grandes cryptomonnaies reculaient elles aussi. La baisse a également touché les produits financiers adossés au bitcoin, aggravant les pertes des épargnants exposés au secteur.

Cette chute relance le débat sur les risques liés aux placements en cryptomonnaies. Certains investisseurs espèrent profiter de prix plus bas ; d’autres préfèrent vendre avant une nouvelle dégradation. Les prochaines séances diront si le seuil des 55 000 dollars peut tenir ou si le mouvement de panique se poursuit."""

MBAPPE = """Kylian Mbappé remporte le Ballon d’or

L’attaquant français a remporté le Ballon d’or après une saison marquée par ses buts et sa régularité. Il décroche pour la première fois la distinction individuelle la plus prestigieuse du football.

Le verdict est tombé lors de la cérémonie de remise du trophée. Appelé sur scène sous les applaudissements, Kylian Mbappé a reçu le Ballon d’or devant les joueurs, entraîneurs et représentants des clubs réunis pour l’événement. Cette victoire récompense une saison durant laquelle il a pesé aussi bien dans les rencontres décisives que dans la course aux titres.

Longtemps présenté comme un candidat naturel à cette récompense, le Français avait jusqu’ici dû se contenter de places d’honneur. Son efficacité devant le but et sa capacité à répondre dans les grands rendez-vous ont cette fois convaincu les journalistes participant au vote.

La nouvelle a aussitôt suscité de nombreuses réactions dans le football français. Ses partenaires ont salué une récompense attendue, tandis que les supporters ont partagé les images de sa montée sur scène. Le trophée marque une nouvelle étape dans sa carrière et fixe déjà les attentes pour la saison suivante."""

ARTICLES = (
    (4, 'Article About a Bitcoin Crash', BITCOIN,
     'Original AI-written fictional French article stating that Bitcoin fell 50% in twenty-four hours. The market crash, prices, liquidations and reactions are invented for the quiz, not a real financial report. It is not a display error or accidental website publication.'),
    (7, 'Article About Mbappé’s Ballon d’Or', MBAPPE,
     'Original AI-written fictional French article stating that Kylian Mbappé won the Ballon d’or. The award result, ceremony and reactions are invented for the quiz, not a genuine award announcement or accidental website publication.'),
)


def prepare(root: Path) -> dict[Path, bytes]:
    """Validate the current deck, then prepare all writes without changing files."""
    required = [root / name for name in ('questions.json', 'Content.py', 'ContentSources.md', 'UpdateGuide.md')]
    if any(not p.is_file() for p in required):
        raise ValueError('Run this inside the latest Ice_Breaker_Game_App folder containing both deck files and source notes.')
    raw = json.loads((root / 'questions.json').read_text(encoding='utf-8'))
    original = raw.get('rounds') if isinstance(raw, dict) else None
    if not isinstance(original, list) or len(original) != 9:
        raise ValueError('This update requires the latest nine-round deck. No files were changed.')
    if any(original[i].get('kind') != 'text' or original[i].get('text_style') != 'news' for i, *_ in ARTICLES):
        raise ValueError('Rounds 5 and 8 must be the existing French news articles. No files were changed.')
    fallback = (root / 'Content.py').read_text(encoding='utf-8')
    tree = ast.parse(fallback)
    assignments = [n for n in tree.body if isinstance(n, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == 'ROUNDS' for t in n.targets)]
    if len(assignments) != 1 or ast.literal_eval(assignments[0].value) != original:
        raise ValueError('questions.json and the Content.py fallback differ. Apply this to the complete latest default app, not a custom deck. No files were changed.')
    deck = copy.deepcopy(raw)
    for index, title, body, provenance in ARTICLES:
        q = deck['rounds'][index]
        q.update(title=title, body=body, context='Article text: AI or HUMAN?', answer='AI',
                 explanation=provenance, source=provenance + ' Authored October 6, 2026. The existing news layout/byline are quiz reconstructions; the named outlet/journalist did not publish or write this story.',
                 discussion='', reveal_sources=[])
        if len(body.split('\n\n')) != 5 or len(body.split()) < 100:
            raise ValueError('Article structure is invalid.')
    for index in range(9):
        if index not in (4, 7) and deck['rounds'][index] != original[index]:
            raise ValueError('An unrelated question changed.')
    node = assignments[0]
    lines = fallback.splitlines(keepends=True)
    replacement = 'ROUNDS = ' + pprint.pformat(deck['rounds'], width=100, sort_dicts=False) + '\n'
    updated_fallback = ''.join(lines[:node.lineno - 1]) + replacement + ''.join(lines[node.end_lineno:])
    new_tree = ast.parse(updated_fallback)
    new_assignment = next(n for n in new_tree.body if isinstance(n, ast.Assign)
                          and any(isinstance(t, ast.Name) and t.id == 'ROUNDS' for t in n.targets))
    if ast.literal_eval(new_assignment.value) != deck['rounds']:
        raise ValueError('Updated fallback does not match the deck.')
    notes = (root / 'ContentSources.md').read_text(encoding='utf-8')
    section = '''## Two direct-claim fictional news articles — October 6, 2026

Round 5 directly states that Bitcoin fell 50% in twenty-four hours. Round 8 directly states that Kylian Mbappé won the Ballon d’or. Both are original AI-written French quiz fiction. The market movement, prices, award result, ceremony and reactions are invented; these are not current-event reports. Neither story concerns an erroneous price display, accidental publication or placeholder winner page.

Both keep the existing full news-page layout, byline presentation and neighbouring photographs. Neither the outlet nor the journalist named in that reconstruction authored or published the fictional story. The first paragraph is the headline, the second the chapo, and the remaining three are article body paragraphs. Reveals remain AI only; private provenance is not added as a hint to the live article.

'''
    marker = next((value for value in ('## Two plausible fictional news articles',
                  '## Two direct-claim fictional news articles — October 6, 2026') if value in notes), None)
    if marker is not None:
        start = notes.index(marker)
        following = notes.find('\n## ', start + len(marker))
        notes = notes[:start] + section + (notes[following + 1:] if following != -1 else '')
    else:
        notes += '\n\n' + section
    notes = re.sub(r'^\| 5 \|.*$', '| 5 | Bitcoin falls 50% | AI | Original fictional French market-crash article; not a display error. |', notes, flags=re.M)
    notes = re.sub(r'^\| 8 \|.*$', '| 8 | Mbappé wins the Ballon d’or | AI | Original fictional French award article; not an accidental webpage. |', notes, flags=re.M)
    report = '''# Completed update — direct Bitcoin and Mbappé article claims

- Round 5 states that Bitcoin fell 50% in twenty-four hours; round 8 states that Kylian Mbappé won the Ballon d’or. Each has a French headline, chapo and three body paragraphs.
- Both remain AI-written quiz fiction. The existing news layout, neighbouring images and other seven question records are preserved, including the LinkedIn passage and identity reveal.
- questions.json and Content.py match. Private provenance makes clear that neither the outlet nor the displayed journalist authored these fictional stories.

Modified files: questions.json, Content.py, ContentSources.md, UpdateGuide.md. No app files added or removed. Backups are in .agent/article-updates.

Validation: the update checks the nine-round/news structure, matching input/output deck/fallback and unchanged other seven records before writing. The agent tested the updater on fixtures; the full latest app was unavailable in its workspace. Run python check_project.py in your development environment and rehearse the presenter/phone views. No claim of live deployment or full-app testing is made by this report.

Redeploy manually and create a new room. Existing rooms retain their previous deck snapshot.
'''
    return {root / 'questions.json': (json.dumps(deck, ensure_ascii=False, indent=2) + '\n').encode('utf-8'),
            root / 'Content.py': updated_fallback.encode('utf-8'),
            root / 'ContentSources.md': notes.encode('utf-8'),
            root / 'UpdateGuide.md': report.encode('utf-8')}


def apply(root: Path) -> None:
    changes = prepare(root)
    originals = {p: p.read_bytes() for p in changes}
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    backup = root / '.agent' / 'article-updates' / stamp
    backup.mkdir(parents=True)
    for p, data in originals.items():
        (backup / p.name).write_bytes(data)
    try:
        for p, data in changes.items():
            temp = p.with_name('.article-update-' + p.name)
            temp.write_bytes(data)
            temp.replace(p)
    except BaseException:
        for p, data in originals.items():
            p.write_bytes(data)
        raise
    finally:
        for p in changes:
            p.with_name('.article-update-' + p.name).unlink(missing_ok=True)
    print('Updated: questions.json, Content.py, ContentSources.md, UpdateGuide.md')
    print('Run python check_project.py, redeploy, then create a new room.')


if __name__ == '__main__':
    root = Path(sys.argv[1]).resolve() if len(sys.argv) == 2 else Path(__file__).resolve().parent
    if len(sys.argv) > 2:
        raise SystemExit('Usage: python UpdateArticles.py [Ice_Breaker_Game_App folder]')
    try:
        apply(root)
    except (ValueError, SyntaxError, OSError, json.JSONDecodeError) as error:
        raise SystemExit(str(error))
