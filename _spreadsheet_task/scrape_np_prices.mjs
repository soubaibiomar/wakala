import fs from "node:fs/promises";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const inputPath = "C:/Users/omar/AppData/Local/Packages/5319275A.WhatsAppDesktop_cv1g1gvanyjgm/LocalState/sessions/E9C2C21E7054FC6217C6DD688546230CBDEA0F0D/transfers/2026-35/wakala-catalogue.xlsx";
const outputPath = "D:/Projet automobile/vente-auto-platform/_spreadsheet_task/np_prices_web.json";
const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(inputPath));
const sheet = workbook.worksheets.getItem("Catalogue Véhicules");
const rows = sheet.getUsedRange(true).values;

const groups = new Map();
for (let i = 1; i < rows.length; i += 1) {
  const row = rows[i];
  if (String(row[8] ?? "").trim().toUpperCase() !== "NP") continue;
  const key = `${row[0]}\u0000${row[4]}`;
  if (!groups.has(key)) groups.set(key, { brand: row[0], model: row[4] });
}

const brandAliases = {
  "Mercedes-Benz": ["mercedes-benz", "mercedes"],
  "Alfa Romeo": ["alfa-romeo"],
  "Lynk & Co": ["lynk-co", "lynk-and-co"],
  "DEEPAL": ["deepal"],
  "iCAUR": ["icaur"],
  "Neo Motors": ["neo-motors", "neo"],
  "Ssangyong": ["ssangyong", "kgm"],
  "soueast": ["soueast"],
  "GWM": ["gwm"],
  "MG": ["mg"],
  "DS": ["ds"],
};

function slugify(value) {
  return String(value ?? "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/&/g, "and")
    .replace(/[^a-zA-Z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .toLowerCase();
}

function getBrandAliases(brand) {
  return brandAliases[brand] ?? [slugify(brand)];
}

function decodeEntities(value) {
  return value
    .replace(/&nbsp;|&#160;|&#xA0;/gi, " ")
    .replace(/&amp;/gi, "&")
    .replace(/&eacute;/gi, "é")
    .replace(/&egrave;/gi, "è")
    .replace(/&ecirc;/gi, "ê")
    .replace(/&agrave;/gi, "à")
    .replace(/&rsquo;|&#8217;/gi, "’")
    .replace(/&#(\d+);/g, (_, code) => String.fromCodePoint(Number(code)))
    .replace(/&#x([0-9a-f]+);/gi, (_, code) => String.fromCodePoint(parseInt(code, 16)));
}

function visibleText(html) {
  return decodeEntities(html
    .replace(/<script[\s\S]*?<\/script>/gi, " ")
    .replace(/<style[\s\S]*?<\/style>/gi, " ")
    .replace(/<[^>]+>/g, " ")
    .replace(/\\\//g, "/")
  ).replace(/\s+/g, " ").trim();
}

function numberFromPrice(value) {
  const normalized = String(value).replace(/[\s\u00a0]/g, "").replace(/\./g, "").replace(/,/g, "");
  const number = Number(normalized);
  return Number.isFinite(number) ? number : null;
}

function normalizePriceToken(value) {
  const direct = numberFromPrice(value);
  if (direct !== null && direct >= 50000 && direct <= 10000000) return direct;
  const tokens = String(value).trim().split(/[\s\u00a0]+/).filter(Boolean);
  if (tokens.length > 2) {
    const withoutLeadingModel = numberFromPrice(tokens.slice(1).join(" "));
    if (withoutLeadingModel !== null && withoutLeadingModel >= 50000 && withoutLeadingModel <= 10000000) return withoutLeadingModel;
  }
  return direct;
}

function parsePriceRange(text, startAt = 0) {
  const rangePattern = /(\d[\d\s\u00a0.,]*\d|\d{2,})(?:\s*-\s*(\d[\d\s\u00a0.,]*\d|\d{2,}))?\s*(?:Dhs?|DH)\b/gi;
  const candidates = [];
  for (const match of text.matchAll(rangePattern)) {
    if (match.index < startAt) continue;
    const min = normalizePriceToken(match[1]);
    const max = normalizePriceToken(match[2] ?? match[1]);
    if (min !== null && max !== null && min >= 50000 && max >= min && max <= 10000000) {
      candidates.push({ text: match[0].trim(), min, max, index: match.index });
    }
  }
  return candidates[0] ?? null;
}

async function fetchPage(url) {
  try {
    const response = await fetch(url, { signal: AbortSignal.timeout(15000), headers: { "user-agent": "Mozilla/5.0 Wakala catalogue price verification" } });
    if (!response.ok) return { url, status: response.status, html: "" };
    return { url, status: response.status, html: await response.text() };
  } catch (error) {
    return { url, status: 0, html: "", error: error instanceof Error ? error.message : String(error) };
  }
}

function parseSitePrice(site, page) {
  if (!page.html) return null;
  const text = visibleText(page.html);
  const model = page.model ?? "";
  const titleMarker = site === "moteur" ? /\b202\d\s*:/i : /prix et versions|tarifs et versions/i;
  const marker = text.search(titleMarker);
  if (marker < 0) return null;
  const section = text.slice(marker, marker + 1400);
  if (/n'est pas commercialis[ée]|pas référenc[ée]|n'est pas disponible|non disponible/i.test(section)) return null;
  if (/prix et versions|tarifs et versions/i.test(section)) {
    const firstPrice = section.search(/\d[\d\s\u00a0.,]*\d\s*(?:Dhs?|DH)\b/i);
    if (firstPrice < 0 || firstPrice > 900) return null;
  }
  if (site === "moteur") {
    const title = decodeEntities(page.html.match(/<title[^>]*>([\s\S]*?)<\/title>/i)?.[1] ?? "");
    const compactTitle = title.toLowerCase().replace(/[^a-z0-9]+/g, "");
    const compactModel = model.toLowerCase().replace(/[^a-z0-9]+/g, "");
    if (!compactModel || !compactTitle.includes(compactModel)) return null;
  }
  const price = parsePriceRange(text, marker >= 0 ? marker : 0);
  if (!price) return null;
  return { site, url: page.url, rangeText: price.text, min: price.min, max: price.max };
}

const items = [...groups.values()].sort((a, b) => `${a.brand} ${a.model}`.localeCompare(`${b.brand} ${b.model}`, "fr"));
const results = [];
const concurrency = 2;
for (let start = 0; start < items.length; start += concurrency) {
  const batch = items.slice(start, start + concurrency);
  const batchResults = await Promise.all(batch.map(async ({ brand, model }) => {
    const modelSlug = slugify(model);
    const urls = [];
    for (const brandSlug of getBrandAliases(brand)) {
      urls.push({ site: "moteur", url: `https://www.moteur.ma/fr/neuf/voiture/${brandSlug}/${modelSlug}/` });
      urls.push({ site: "wandaloo", url: `https://www.wandaloo.com/neuf/${brandSlug}/${modelSlug}/` });
      urls.push({ site: "wandaloo", url: `https://www.wandaloo.com/archive/${brandSlug}/${modelSlug}/` });
    }
    const pages = await Promise.all(urls.map(async (entry) => ({
      ...entry,
      model,
      ...(await fetchPage(entry.url)),
    })));
    const moteur = pages.filter((page) => page.site === "moteur").map((page) => parseSitePrice("moteur", page)).find(Boolean) ?? null;
    const wandaloo = pages.filter((page) => page.site === "wandaloo").map((page) => parseSitePrice("wandaloo", page)).find(Boolean) ?? null;
    return {
      brand,
      model,
      moteur,
      wandaloo,
      attempted: urls.length,
      attempts: pages.map((page, index) => ({
        site: urls[index].site,
        url: urls[index].url,
        status: page.status,
        bytes: page.html.length,
        error: page.error ?? null,
      })),
    };
  }));
  results.push(...batchResults);
  console.log(`PROGRESS=${Math.min(start + concurrency, items.length)}/${items.length}`);
}

const summary = {
  generatedAt: new Date().toISOString(),
  sourceWorkbook: inputPath,
  uniqueGroups: items.length,
  moteurMatches: results.filter((item) => item.moteur).length,
  wandalooMatches: results.filter((item) => item.wandaloo).length,
  anyMatches: results.filter((item) => item.moteur || item.wandaloo).length,
  results,
};
await fs.writeFile(outputPath, JSON.stringify(summary, null, 2), "utf8");
console.log(`OUTPUT=${outputPath}`);
console.log(JSON.stringify({ uniqueGroups: summary.uniqueGroups, moteurMatches: summary.moteurMatches, wandalooMatches: summary.wandalooMatches, anyMatches: summary.anyMatches }, null, 2));
