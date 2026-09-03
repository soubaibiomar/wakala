import fs from "node:fs/promises";

const dataPath = "D:/Projet automobile/vente-auto-platform/_spreadsheet_task/np_prices_web.json";
const data = JSON.parse(await fs.readFile(dataPath, "utf8"));

const aliases = {
  "Mercedes-Benz": ["mercedes-benz", "mercedes"],
  "Alfa Romeo": ["alfa-romeo"],
  "Lynk & Co": ["lynk-co", "lynk-and-co"],
  "DEEPAL": ["deepal"],
  "iCAUR": ["icaur"],
  "Neo Motors": ["neo-motors", "neo"],
  "Ssangyong": ["ssangyong", "kgm"],
  "KG Mobility": ["kgm", "kg-mobility", "ssangyong"],
  "Soueast": ["soueast"],
  "GWM": ["gwm"],
  "MG": ["mg"],
  "DS": ["ds"],
};

function slugify(value) {
  return String(value ?? "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/&/g, "and").replace(/[^a-zA-Z0-9]+/g, "-").replace(/^-+|-+$/g, "").toLowerCase();
}

function compact(value) {
  return String(value ?? "").toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/[^a-z0-9]/g, "");
}

function decode(value) {
  return String(value).replace(/&nbsp;|&#160;|&#xA0;/gi, " ").replace(/&amp;/gi, "&").replace(/&#(\d+);/g, (_, n) => String.fromCodePoint(Number(n)));
}

function visible(html) {
  return decode(html.replace(/<script[\s\S]*?<\/script>/gi, " ").replace(/<style[\s\S]*?<\/style>/gi, " ").replace(/<[^>]+>/g, " ").replace(/\s+/g, " ")).trim();
}

function number(value) {
  const n = Number(String(value).replace(/[\s\u00a0]/g, "").replace(/\./g, "").replace(/,/g, ""));
  return Number.isFinite(n) ? n : null;
}

function normalizeToken(value) {
  const direct = number(value);
  if (direct !== null && direct >= 50000 && direct <= 10000000) return direct;
  const pieces = String(value).trim().split(/[\s\u00a0]+/).filter(Boolean);
  if (pieces.length > 2) {
    const withoutPrefix = number(pieces.slice(1).join(" "));
    if (withoutPrefix !== null && withoutPrefix >= 50000 && withoutPrefix <= 10000000) return withoutPrefix;
  }
  return direct;
}

function parsePrice(site, html, model) {
  const text = visible(html);
  const marker = text.search(site === "moteur" ? /\b202\d\s*:/i : /prix et versions|tarifs et versions/i);
  if (marker < 0) return null;
  const section = text.slice(marker, marker + 1400);
  if (/n'est pas commercialis[ée]|pas référenc[ée]|n'est pas disponible|non disponible/i.test(section)) return null;
  if (site === "moteur") {
    const title = decode(html.match(/<title[^>]*>([\s\S]*?)<\/title>/i)?.[1] ?? "");
    if (!compact(title).includes(compact(model))) return null;
  }
  const pricePattern = /(\d[\d\s\u00a0.,]*\d|\d{2,})(?:\s*-\s*(\d[\d\s\u00a0.,]*\d|\d{2,}))?\s*(?:Dhs?|DH)\b/gi;
  for (const match of section.matchAll(pricePattern)) {
    if (match.index > 900) break;
    const min = normalizeToken(match[1]);
    const max = normalizeToken(match[2] ?? match[1]);
    if (min !== null && max !== null && min >= 50000 && max >= min && max <= 10000000) {
      return { site, rangeText: match[0].trim(), min, max };
    }
  }
  return null;
}

async function fetchPage(url) {
  try {
    const response = await fetch(url, { signal: AbortSignal.timeout(15000), headers: { "user-agent": "Mozilla/5.0 Wakala Moroccan price verification" } });
    return { url, status: response.status, html: response.ok ? await response.text() : "" };
  } catch {
    return { url, status: 0, html: "" };
  }
}

function extractLinks(html, site, brandSlug) {
  const links = [];
  const re = /<a[^>]+href=["']([^"']+)["'][^>]*>([\s\S]*?)<\/a>/gi;
  for (const match of html.matchAll(re)) {
    const href = decode(match[1]);
    const text = visible(match[2]);
    const absolute = href.startsWith("http") ? href : `${site === "moteur" ? "https://www.moteur.ma" : "https://www.wandaloo.com"}${href.startsWith("/") ? "" : "/"}${href}`;
    const path = absolute.toLowerCase();
    const expected = site === "moteur" ? `/fr/neuf/voiture/${brandSlug}/` : `/neuf/${brandSlug}/`;
    if (!path.includes(expected) || path.split("/").filter(Boolean).length < (site === "moteur" ? 6 : 4)) continue;
    if (!links.some((item) => item.url === absolute)) links.push({ url: absolute, text });
  }
  return links;
}

const unresolved = data.results.filter((item) => !item.moteur && !item.wandaloo);
const brandEntries = [...new Map(unresolved.map((item) => [item.brand, item])).values()];
const discovered = new Map();

for (const item of brandEntries) {
  const brandSlugs = aliases[item.brand] ?? [slugify(item.brand)];
  for (const brandSlug of brandSlugs) {
    const pages = await Promise.all([
      fetchPage(`https://www.moteur.ma/fr/neuf/voiture/${brandSlug}/`),
      fetchPage(`https://www.wandaloo.com/neuf/${brandSlug}/`),
    ]);
    const links = [
      ...extractLinks(pages[0].html, "moteur", brandSlug).map((link) => ({ ...link, site: "moteur" })),
      ...extractLinks(pages[1].html, "wandaloo", brandSlug).map((link) => ({ ...link, site: "wandaloo" })),
    ];
    for (const target of unresolved.filter((row) => row.brand === item.brand)) {
      const key = `${target.brand}\u0000${target.model}`;
      const wanted = compact(target.model);
      const candidates = links.filter((link) => compact(`${link.text} ${link.url}`).includes(wanted));
      if (!candidates.length) continue;
      const pagesForModel = await Promise.all(candidates.slice(0, 3).map((candidate) => fetchPage(candidate.url).then((page) => ({ ...candidate, ...page }))));
      for (const page of pagesForModel) {
        const price = parsePrice(page.site, page.html, target.model);
        if (price) {
          discovered.set(key, { ...target, [page.site]: { ...price, url: page.url } });
          break;
        }
      }
    }
  }
}

for (const item of data.results) {
  const found = discovered.get(`${item.brand}\u0000${item.model}`);
  if (!found) continue;
  if (found.moteur) item.moteur = found.moteur;
  if (found.wandaloo) item.wandaloo = found.wandaloo;
}

data.generatedAt = new Date().toISOString();
data.moteurMatches = data.results.filter((item) => item.moteur).length;
data.wandalooMatches = data.results.filter((item) => item.wandaloo).length;
data.anyMatches = data.results.filter((item) => item.moteur || item.wandaloo).length;
await fs.writeFile(dataPath, JSON.stringify(data, null, 2), "utf8");
console.log(JSON.stringify({ discovered: discovered.size, moteurMatches: data.moteurMatches, wandalooMatches: data.wandalooMatches, anyMatches: data.anyMatches }, null, 2));
