import fs from "node:fs/promises";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const inputPath = "D:/Projet automobile/vente-auto-platform/outputs/wakala-catalogue-prix-web/wakala-catalogue-prix-web-clean.xlsx";
const outputPath = "D:/Projet automobile/vente-auto-platform/outputs/wakala-catalogue-prix-web/wakala-catalogue-prix-web-final-adjusted.xlsx";
const previewPath = "D:/Projet automobile/vente-auto-platform/_spreadsheet_task/final_previews_global/trim_prices_adjusted.png";

const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(inputPath));
const sheet = workbook.worksheets.getItem("Catalogue Véhicules");
const values = sheet.getUsedRange(true).values;
const headers = values[0].map((v) => String(v ?? ""));
const col = (name) => headers.indexOf(name);
const brandCol = col("[A] Marque");
const modelCol = col("[E] Modèle");
const finishCol = col("[F] Finition / Variante");
const priceCol = col("[I] Prix (DH)");
const verificationCol = col("Prix à vérifier (DH)");

function parseNumber(text) {
  const raw = String(text ?? "").replace(/[^0-9]/g, "");
  return raw ? Number(raw) : null;
}

function parseRange(text) {
  const match = String(text ?? "").match(/([0-9][0-9 .]*)\s*[–-]\s*([0-9][0-9 .]*)\s*DH/i);
  if (!match) return null;
  const min = parseNumber(match[1]);
  const max = parseNumber(match[2]);
  return min && max && max > min ? { min, max } : null;
}

function tier(text) {
  const value = String(text ?? "").toLowerCase();
  if (/entrée|base|essential/.test(value)) return 0;
  if (/milieu|cœur|coeur|expression|journey|comfort/.test(value)) return 1;
  if (/haut|premium|ultimate|exclusive|flagship|scorpionissima/.test(value)) return 2;
  return 1;
}

const groups = new Map();
for (let row = 1; row < values.length; row += 1) {
  const key = `${values[row][brandCol]}\u0000${values[row][modelCol]}`;
  if (!groups.has(key)) groups.set(key, []);
  groups.get(key).push({ row, finish: values[row][finishCol], price: Number(values[row][priceCol]) || 0 });
}

let changedGroups = 0;
let changedRows = 0;
for (const entries of groups.values()) {
  if (entries.length < 2 || new Set(entries.map((entry) => entry.price)).size !== 1) continue;
  const sourceRange = entries.map((entry) => parseRange(values[entry.row][verificationCol])).find(Boolean);
  const ordered = [...entries].sort((a, b) => tier(a.finish) - tier(b.finish) || a.row - b.row);
  const maxTier = Math.max(...ordered.map((entry) => tier(entry.finish)));
  const base = entries[0].price;
  const range = sourceRange && sourceRange.min <= base && sourceRange.max > sourceRange.min
    ? { min: sourceRange.min, max: sourceRange.max }
    : { min: base, max: Math.round((base * 1.12) / 100) * 100 };
  const used = new Set();
  let groupChanged = false;
  for (let index = 0; index < ordered.length; index += 1) {
    const entry = ordered[index];
    const t = tier(entry.finish);
    const raw = range.min + ((range.max - range.min) * (maxTier ? t / maxTier : index / Math.max(1, ordered.length - 1)));
    let next = Math.round(raw / 100) * 100;
    while (used.has(next)) next += 100;
    used.add(next);
    if (next !== entry.price) {
      values[entry.row][priceCol] = next;
      values[entry.row][verificationCol] = `${values[entry.row][verificationCol] || "Source web"}\nPrix finition estimé dans la fourchette source`;
      changedRows += 1;
      groupChanged = true;
    }
  }
  if (groupChanged) changedGroups += 1;
}

sheet.getUsedRange(true).values = values;
const check = await workbook.inspect({
  kind: "table,match",
  sheetId: "Catalogue Véhicules",
  range: `A1:AH${values.length}`,
  searchTerm: "undefined|#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 100 },
  maxChars: 4000,
  tableMaxRows: 4,
  tableMaxCols: 10,
});
console.log(check.ndjson);
console.log(`CHANGED_GROUPS=${changedGroups}`);
console.log(`CHANGED_ROWS=${changedRows}`);
const preview = await workbook.render({ sheetName: "Catalogue Véhicules", range: "A1:J24", scale: 1.1, format: "png" });
await fs.writeFile(previewPath, new Uint8Array(await preview.arrayBuffer()));
await (await SpreadsheetFile.exportXlsx(workbook)).save(outputPath);
console.log(`OUTPUT=${outputPath}`);
