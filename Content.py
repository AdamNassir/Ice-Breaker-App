"""Nine starter rounds: seven images and two short news articles.

UI, titles and introductions are English; the news articles, Macron post and Teams messages are French.
questions.json takes priority. The presenter-selected timer applies to all rounds.
For social screenshots, classify only the post text or specified manager reply.
Sources, fictional status and classifications: ContentSources.md.
"""

ROUNDS = [{'title': 'LinkedIn Post by a Manager',
  'kind': 'image',
  'seconds': 25,
  'context': 'Post text: AI or HUMAN?',
  'answer': 'AI',
  'explanation': 'The post is an original AI-written satire. The interface is a fictional '
                 'reconstruction, not a real LinkedIn account.',
  'discussion': '',
  'source': 'Original AI-written fictional LinkedIn-style post. Layout drawn in Python with '
            'Pillow; all names and avatars are fictional and blurred. No real account or public '
            'figure is depicted.',
  'media': '/static/images/sample18.png',
  'alt': 'A professional-network post with a blurred profile picture and identity.',
  'image_fit': 'contain'},
 {'title': 'Michael Jordan’s Free-Throw-Line Dunk',
  'kind': 'image',
  'seconds': 25,
  'context': 'Photograph: AI or HUMAN?',
  'media': '/static/images/sample26.jpg',
  'alt': 'Michael Jordan airborne during a free-throw-line dunk, with the court, hoop and crowd '
         'visible.',
  'image_fit': 'contain',
  'answer': 'HUMAN',
  'explanation': 'Authentic photograph of Michael Jordan’s iconic free-throw-line dunk at the 1988 '
                 'NBA Slam Dunk Contest. The full image shows his airborne body, the court, hoop '
                 'and crowd. This identifies a documented dunk; it does not claim a measured '
                 'greatest-ever jump.',
  'discussion': '',
  'source': 'Walter Iooss Jr. / Sports Illustrated, NBA Slam Dunk Contest, Chicago, February 6, '
            '1988. Full-frame source JPEG retained without cropping or generative editing. '
            'Copyrighted sports photograph; no Creative Commons or public-domain licence claimed.',
  'source_url': 'https://www.si.com/nba/2015/02/17/walter-iooss-jr-michael-jordan-1988-nba-dunk-contest-photo',
  'image_reveal': 'Michael Jordan’s free-throw-line dunk — Chicago, February 6, 1988.\n'
                  'Photo: Walter Iooss Jr. / Sports Illustrated.'},
 {'title': 'SQL Query for Employee Data',
  'kind': 'image',
  'media': '/static/images/sample23.png',
  'image_fit': 'contain',
  'alt': 'A commented SQL query combining employee, payroll, department and certification tables.',
  'seconds': 25,
  'answer': 'AI',
  'context': 'SQL code: AI or HUMAN?',
  'explanation': 'Original AI-written SQL with two common table expressions, four source tables, '
                 'explanatory comments and a conditional-aggregate pivot. It summarizes a payroll '
                 'month by department and highest valid certification rank. Pre-aggregation '
                 'prevents multiplying payroll totals when employees have several certifications.',
  'source': 'Original AI-written SQL, October 5, 2026. Formatting and SQL feature references: '
            'PostgreSQL official Aggregate Functions tutorial and WITH Queries documentation. Uses '
            'monthly_pay and highest_level CTEs, '
            'employees/payroll/departments/employee_certifications joins, and FILTER aggregates '
            'for pivot-style columns. The HR use case is implied by identifiers and filters. No '
            'real employee data; not copied source code.',
  'source_url': 'https://www.postgresql.org/docs/current/tutorial-agg.html',
  'discussion': ''},
 {'title': 'Photograph of Nikola Tesla in His Laboratory',
  'kind': 'image',
  'seconds': 25,
  'context': 'Photograph: AI or HUMAN?',
  'media': '/static/images/sample16.jpg',
  'alt': 'A seated person reading near large electrical equipment and bright arcs in a historical '
         'photograph.',
  'image_fit': 'contain',
  'answer': 'HUMAN',
  'explanation': 'The famous Tesla laboratory publicity photograph dates to December 1899. It is a '
                 'human-made double exposure: the electrical arcs and Tesla were photographed '
                 'separately. HUMAN does not mean the scene happened exactly as pictured.',
  'discussion': '',
  'source': 'Dickenson V. Alley, Tesla laboratory photograph, December 1899; Commons '
            'public-domain-US record. Historical double exposure, resized/re-encoded for this app; '
            'no generative edits.',
  'source_url': 'https://commons.wikimedia.org/wiki/File:Tesla_colorado.jpg',
  'image_reveal': 'Nikola Tesla in his Colorado Springs laboratory — December 1899.\n'
                  'Source: Dickenson V. Alley. Historical double exposure.'},
 {'title': 'News Article About a Bitcoin Price Drop',
  'context': 'Article text: AI or HUMAN?',
  'kind': 'text',
  'answer': 'AI',
  'seconds': 25,
  'body': 'Le bitcoin affiché en baisse de 50 % sur une plateforme après un incident technique\n'
          '\n'
          'Une plateforme d’échange a suspendu les transactions pendant vingt minutes lundi matin '
          'après avoir affiché un cours du bitcoin inférieur de moitié à celui des autres marchés. '
          'L’écart serait lié à un problème de synchronisation de son flux de prix.\n'
          '\n'
          'L’anomalie est apparue peu après une opération de maintenance. Des utilisateurs ont '
          'partagé des captures d’écran montrant une chute brutale, alors que les principales '
          'plateformes ne signalaient aucun mouvement comparable. Les ordres en attente ont été '
          'bloqués le temps de rétablir la cotation.\n'
          '\n'
          'Le service a ensuite repris avec un cours corrigé. La plateforme examine les '
          'transactions exécutées pendant l’incident et doit contacter les clients concernés. '
          'Certains avaient cru profiter d’une occasion exceptionnelle avant de voir leur achat '
          'disparaître de l’historique.',
  'explanation': 'Original AI-written French fiction for the game. The story is invented, not a '
                 'report or quotation from the publication whose interface is reconstructed.',
  'source': 'Original AI-written French news-style fiction for the quiz, October 5, 2026. The '
            'incidents, platform/partner statements and quotes are invented. Le Parisien is the '
            'layout reference only. Displayed journalist names are borrowed solely for the '
            'requested mock byline; neither journalist wrote or published this story. Actual '
            'neighbouring news photos and their origins are documented in LayoutSources.md.',
  'discussion': '',
  'reveal_sources': [],
  'text_style': 'news'},
 {'title': 'Painting of Napoleon’s Coronation',
  'kind': 'image',
  'seconds': 25,
  'context': 'Painting: AI or HUMAN?',
  'media': '/static/images/sample13.jpg',
  'alt': 'A painting of an imperial ceremony with guests in ornate robes.',
  'image_fit': 'contain',
  'answer': 'AI',
  'explanation': 'This is an original AI-generated historical pastiche. Inspector Gadget has '
                 'slipped into the crowd, complete with a mechanical arm. It is not an authentic '
                 'Napoleon painting, and no museum record is claimed.',
  'discussion': '',
  'source': 'OpenAI built-in image generation, October 4, 2026. Original fictional imperial '
            'ceremony; Inspector Gadget cameo. Resized/re-encoded; full prompt in '
            'ContentSources.md.',
  'image_highlight': {'x': 35.5, 'y': 43, 'radius': 7.5}},
 {'title': 'Macron Post About AI in Hospitals',
  'kind': 'image',
  'media': '/static/images/sample27.png',
  'image_fit': 'contain',
  'alt': 'A French-language X-style post displaying Emmanuel Macron’s name, handle and portrait.',
  'seconds': 25,
  'answer': 'AI',
  'context': 'Post text: AI or HUMAN?',
  'explanation': 'Original AI-written fictional French post announcing a ten-hospital trial of '
                 'French-developed AI to anticipate emergency-department demand using anonymized '
                 'data. Emmanuel Macron did not write, announce or post this invented trial. '
                 'Players judge the writing, not the real supplied profile photograph.',
  'source': 'Original AI-written French fiction created for this game, October 5, 2026. Not a '
            'genuine Macron post or verified government programme. Style reference: public Élysée '
            'writing about health and AI; no quotation copied. Native X-style UI with visible '
            'name, @EmmanuelMacron and the exact profile picture supplied by the presenter. '
            'Hashtags are original. No posting date or fabricated engagement counts. Source '
            'picture retained as profile-source.png.',
  'discussion': ''},
 {'title': 'News Article About a Ballon d’Or Leak',
  'context': 'Article text: AI or HUMAN?',
  'kind': 'text',
  'answer': 'AI',
  'seconds': 25,
  'body': 'Ballon d’or : une page publiée par erreur relance la rumeur d’une victoire de Mbappé\n'
          '\n'
          'Une page présentant Kylian Mbappé comme lauréat du Ballon d’or a été brièvement '
          'accessible sur le site d’un partenaire de la cérémonie. Retirée quelques minutes plus '
          'tard, elle a suffi à déclencher une vague de réactions sur les réseaux sociaux.\n'
          '\n'
          'Le texte, accompagné d’une photographie du joueur, portait un titre de félicitations et '
          'un bouton renvoyant vers la retransmission de la soirée. Plusieurs internautes en ont '
          'conservé des captures avant sa suppression. Aucun classement ni détail sur le vote du '
          'jury n’était visible.\n'
          '\n'
          'Le partenaire évoque un contenu de préparation mis en ligne prématurément. Des pages '
          'similaires auraient été prévues pour plusieurs candidats afin de permettre une '
          'publication rapide après l’annonce du résultat. Cela n’a pas empêché des supporters de '
          'célébrer une victoire encore non confirmée.',
  'explanation': 'Original AI-written French fiction for the game. The story is invented, not a '
                 'report or quotation from the publication whose interface is reconstructed.',
  'source': 'Original AI-written French news-style fiction for the quiz, October 5, 2026. The '
            'incidents, platform/partner statements and quotes are invented. Le Parisien is the '
            'layout reference only. Displayed journalist names are borrowed solely for the '
            'requested mock byline; neither journalist wrote or published this story. Actual '
            'neighbouring news photos and their origins are documented in LayoutSources.md.',
  'discussion': '',
  'reveal_sources': [],
  'text_style': 'news'},
 {'title': 'Teams Conversation With an Internship Manager',
  'kind': 'image',
  'media': '/static/images/sample19.png',
  'image_fit': 'contain',
  'alt': 'A French Teams conversation with Adam’s blurred identity: his document submission is on '
         'the right in blue, and the manager’s reply is on the left in grey.',
  'context': 'Manager’s reply: AI or HUMAN?',
  'answer': 'AI',
  'explanation': 'AI wrote the manager’s mistaken French validation reply. The first message '
                 'concerns searching technical documents; the manager imagines flight monitoring, '
                 'repair decisions and propulsion switching. Both messages and the attachment are '
                 'fictional, inspired by the supplied internship topics, not a transcript or an '
                 'allegation about an actual colleague.',
  'source': 'Original AI-written fictional French manager reply inspired by the presenter’s '
            'aerospace document-search/GraphRAG internship. Less technical wording requested; '
            'reply invents aircraft operations instead of discussing document retrieval. The PDF '
            'and anonymized identities are fictional; its contents are not displayed. Judge only '
            'the manager’s reply. Adam Nassir is the presenter-supplied sender name, blurred in '
            'the outgoing message header. The outgoing document message is on the right in light '
            'blue; the incoming manager reply is on the left in light grey. The manager identity '
            'remains fictional and blurred.',
  'discussion': '',
  'seconds': 25}]
