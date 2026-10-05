/* Full news website document shared by the game and local question manager. */
(() => {
  'use strict';
  const SECTIONS = ['À la une', 'En continu', 'Paris & Île-de-France', 'Faits divers', 'Politique', 'International', 'Économie', 'Société', 'Sports', 'Culture'];
  // Photos copied unchanged from recent Le Parisien stories; private credits in LayoutSources.md.
  const RELATED = [
    {section:'VIE ÉTUDIANTE', title:'Aides au logement : ce qui change en octobre', image:'housing', alt:'Étudiants près du campus de l’UTC à Compiègne'},
    {section:'SPORTS', title:'France-Belgique : les Bleus préparent leur prochain match', image:'football', alt:'Zinedine Zidane en conférence de presse'},
    {section:'HIGH-TECH', title:'OpenAI se sépare de trois chercheurs en sécurité', image:'ai', alt:'Logo OpenAI lors d’un événement'}
  ];
  function node(tag, name, value) {
    const el = document.createElement(tag);
    el.className = name;
    if (value !== undefined) el.textContent = value;
    return el;
  }
  function logo() {
    const image = node('img', 'news-publication-logo');
    image.src = '/static/branding/publication.svg';
    image.alt = 'Le Parisien';
    image.width = 512; image.height = 160;
    return image;
  }
  function icon(type) {
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('viewBox', '0 0 24 24'); svg.setAttribute('aria-hidden', 'true');
    svg.classList.add('news-icon');
    const path = document.createElementNS(svg.namespaceURI, 'path');
    path.setAttribute('d', {menu:'M2 5h20M2 12h20M2 19h20', search:'M16 16l6 6M18 10a8 8 0 1 1-16 0 8 8 0 0 1 16 0', mail:'M2 4h20v16H2zM2 4l10 9L22 4', share:'M12 16V2m-5 5 5-5 5 5M4 13v9h16v-9'}[type]);
    path.setAttribute('fill','none'); path.setAttribute('stroke','currentColor');
    path.setAttribute('stroke-width','1.8'); path.setAttribute('stroke-linejoin','round');
    svg.append(path); return svg;
  }
  function card(item, compact) {
    const result = node('div', compact ? 'news-trending-item' : 'news-related-item');
    const thumb = node('img', 'news-thumb');
    thumb.src = `/static/news/${item.image}.jpg`;
    thumb.alt = item.alt;
    thumb.width = 240; thumb.height = 160;
    thumb.loading = 'lazy'; thumb.decoding = 'async';
    const text = node('div', 'news-card-copy');
    text.append(node('span', 'news-card-section', item.section), node('h4', 'news-card-headline', item.title));
    result.append(thumb, text); return result;
  }
  function create(question) {
    const parts = String(question.body || '').split(/\n\s*\n/).filter(p => p.trim());
    const headline = parts.shift() || question.title || '';
    const section = /bitcoin/i.test(headline) ? 'Économie' : /ballon|trophée/i.test(headline) ? 'Sports' : 'Actualités';
    // A bounded, independently scrollable document keeps game voting reachable.
    const site = node('section', 'news-site');
    site.tabIndex = 0; site.lang = 'fr';
    site.setAttribute('aria-label', 'Page d’actualité ; faites défiler pour lire');
    const masthead = node('header', 'news-masthead');
    masthead.setAttribute('aria-label', 'Le Parisien');
    const tools = node('div', 'news-header-tools'); tools.setAttribute('aria-hidden','true');
    const menu = node('span', 'news-sections-control'); menu.append(icon('menu'), node('span', '', 'Menu'));
    tools.append(menu, icon('search'));
    const account = node('div', 'news-account'); account.setAttribute('aria-hidden','true');
    account.append(node('span', 'news-login', 'Se connecter'), node('span', 'news-subscribe', 'S’abonner'));
    masthead.append(tools, logo(), account);
    const edition = node('div', 'news-edition', 'Paris & Île-de-France');
    edition.setAttribute('aria-hidden','true');
    edition.append(node('span', '', 'Paris · Essonne · Hauts-de-Seine · Seine-Saint-Denis · Val-de-Marne · Val-d’Oise'));
    const nav = node('nav', 'news-navigation'); nav.setAttribute('aria-label','Rubriques');
    for (const label of SECTIONS) {
      const item = node('span', 'news-nav-item', label);
      if (label === section) item.classList.add('news-nav-active');
      nav.append(item);
    }
    const ad = node('div', 'news-advertisement', 'PUBLICITÉ'); ad.setAttribute('aria-hidden','true');
    const grid = node('div', 'news-page-grid');
    const article = node('article', 'news-article'); article.setAttribute('aria-label','Article');
    const trail = node('div', 'news-breadcrumb', `Accueil / ${section === 'Sports' ? 'Sports / Football' : section === 'Économie' ? 'Économie / Votre argent' : 'Actualités'}`);
    const heading = node('header', 'news-article-header');
    heading.append(node('h3', 'news-headline', headline));
    // The first story paragraph is the chapo, followed by the byline and body.
    if (parts.length) heading.append(node('p', 'news-paragraph news-chapo', parts.shift()));
    const byline = node('div', 'news-byline');
    byline.append(node('span', '', 'Par '), node('span', 'news-author', section === 'Sports' ? 'Dominique Sévérac' : 'Sébastien Lernould'));
    const share = node('div', 'news-sharebar'); share.setAttribute('aria-hidden','true');
    for (const label of ['f', 'X', '✉']) share.append(node('span', 'news-share-symbol', label));
    share.append(icon('share'));
    heading.append(byline, node('div', 'news-dateline', section === 'Sports' ? 'Le 5 octobre 2026 à 09h24' : 'Le 5 octobre 2026 à 08h12'), share);
    const body = node('div', 'news-body');
    for (const part of parts) body.append(node('p', 'news-paragraph', part));
    const topics = node('div', 'news-topics');
    topics.append(node('span', 'news-topics-label', 'Sur le même sujet'), node('span', 'news-topic', section === 'Économie' ? 'Bitcoin' : section === 'Sports' ? 'Football · Ballon d’or' : 'Actualités'));
    const more = node('section', 'news-related');
    more.append(node('h4', 'news-module-title', 'À lire aussi'));
    const cards = node('div', 'news-related-grid');
    for (const item of RELATED) cards.append(card(item, false));
    more.append(cards);
    article.append(trail, heading, body, topics, more);
    const sidebar = node('aside', 'news-sidebar'); sidebar.setAttribute('aria-label', 'Les articles les plus lus');
    sidebar.append(node('h4', 'news-module-title', 'Les plus lus'), node('span', 'news-sidebar-caption', 'L’actualité en direct'));
    for (const item of RELATED) sidebar.append(card(item, true));
    const sidebarAd = node('div', 'news-sidebar-ad', 'PUBLICITÉ'); sidebarAd.setAttribute('aria-hidden','true');
    sidebar.append(sidebarAd);
    grid.append(article, sidebar);
    const footer = node('footer', 'news-footer');
    const brand = node('div', 'news-footer-brand');brand.append(logo());
    const columns = node('div', 'news-footer-columns');
    for (const [label, items] of [
      ['Actualités', ['Politique','Économie','Société','Sports','Culture','International']],
      ['Le Parisien', ['Nous écrire','Qui sommes-nous ?','Nos chartes','Espace presse','Newsletters']],
      ['Services', ['S’abonner','Nos applications','Mots fléchés','Sudoku','Archives']]
    ]) {
      const column = node('div', 'news-footer-column');column.append(node('h4','',label));
      for (const item of items) column.append(node('span','',item));
      columns.append(column);
    }
    const legal = node('div', 'news-footer-legal');
    for (const item of ['CGU','Politique de confidentialité','Accessibilité','Gestion des cookies']) legal.append(node('span','',item));
    footer.append(brand, columns, legal);
    site.append(masthead, nav, edition, ad, grid, footer);
    return site;
  }
  window.IcebreakerNews = Object.freeze({create});
})();
