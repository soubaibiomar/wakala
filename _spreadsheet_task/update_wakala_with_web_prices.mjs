import fs from "node:fs/promises";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const inputPath = "C:/Users/omar/AppData/Local/Packages/5319275A.WhatsAppDesktop_cv1g1gvanyjgm/LocalState/sessions/E9C2C21E7054FC6217C6DD688546230CBDEA0F0D/transfers/2026-35/wakala-catalogue.xlsx";
const priceDataPath = "D:/Projet automobile/vente-auto-platform/_spreadsheet_task/np_prices_web.json";
const outputDir = "D:/Projet automobile/vente-auto-platform/outputs/wakala-catalogue-prix-web";
const outputPath = `${outputDir}/wakala-catalogue-prix-web.xlsx`;
const previewDir = "D:/Projet automobile/vente-auto-platform/_spreadsheet_task/final_previews_web";

await fs.mkdir(outputDir, { recursive: true });
await fs.mkdir(previewDir, { recursive: true });

const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(inputPath));
const catalogue = workbook.worksheets.getItem("Catalogue Véhicules");
const usedRange = catalogue.getUsedRange(true);
const values = usedRange.values;
const lastRow = values.length;
const priceIndex = 8;
const research = JSON.parse(await fs.readFile(priceDataPath, "utf8"));
const byGroup = new Map(research.results.map((item) => [`${item.brand}\u0000${item.model}`, item]));

function formatNumber(value) {
  return new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 0 }).format(value).replace(/\u202f/g, " ");
}

function formatRange(item) {
  if (!item) return "";
  if (item.min === item.max) return `${formatNumber(item.min)} DH`;
  return `${formatNumber(item.min)}–${formatNumber(item.max)} DH`;
}

function formatPrice(item) {
  const entries = [];
  if (item.wandaloo) entries.push(`Wandaloo : ${formatRange(item.wandaloo)}`);
  if (item.moteur) entries.push(`Moteur.ma : ${formatRange(item.moteur)}`);
  if (item.other) entries.push(`${item.other.label} : ${formatRange(item.other)}`);
  return entries.join("\n") || "Non trouvé";
}

function formatSources(item) {
  const urls = [];
  if (item.wandaloo) urls.push(item.wandaloo.url);
  if (item.moteur) urls.push(item.moteur.url);
  if (item.other) urls.push(item.other.url);
  return urls.join("\n") || "Aucune correspondance trouvée";
}

const priceValues = [];
const sourceValues = [];
const originalPriceValues = [];
let npRows = 0;
let matchedRows = 0;
let unmatchedRows = 0;
for (let rowIndex = 1; rowIndex < lastRow; rowIndex += 1) {
  const row = values[rowIndex];
  const isNp = String(row[priceIndex] ?? "").trim().toUpperCase() === "NP";
  if (!isNp) {
    priceValues.push([""]);
    sourceValues.push([""]);
    originalPriceValues.push([row[priceIndex]]);
    continue;
  }
  npRows += 1;
  const item = byGroup.get(`${row[0]}\u0000${row[4]}`);
  if (item?.moteur || item?.wandaloo || item?.other) matchedRows += 1;
  else unmatchedRows += 1;
  priceValues.push([formatPrice(item ?? {})]);
  sourceValues.push([formatSources(item ?? {})]);
  const verifiedStartingPrice = item?.wandaloo?.min ?? item?.moteur?.min ?? item?.other?.min ?? null;
  originalPriceValues.push([verifiedStartingPrice ?? row[priceIndex]]);
}

// Copy the existing header/body style into the two new columns, then replace contents.
catalogue.getRange("AG1").copyFrom(catalogue.getRange("AF1"), "all");
catalogue.getRange("AH1").copyFrom(catalogue.getRange("AF1"), "all");
catalogue.getRange(`AG2:AG${lastRow}`).copyFrom(catalogue.getRange(`A2:A${lastRow}`), "all");
catalogue.getRange(`AH2:AH${lastRow}`).copyFrom(catalogue.getRange(`B2:B${lastRow}`), "all");
catalogue.getRange("AG1").values = [["Prix à vérifier (DH)"]];
catalogue.getRange("AH1").values = [["Sources web"]];
catalogue.getRange(`I2:I${lastRow}`).values = originalPriceValues;
catalogue.getRange(`AG2:AG${lastRow}`).values = priceValues;
catalogue.getRange(`AH2:AH${lastRow}`).values = sourceValues;

const dataColumns = catalogue.getRange(`AG2:AH${lastRow}`);
dataColumns.format.wrapText = true;
dataColumns.format.horizontalAlignment = "left";
dataColumns.format.verticalAlignment = "top";
catalogue.getRange(`AG1:AH1`).format.wrapText = true;
catalogue.getRange("AG1:AG1").format.columnWidth = 28;
catalogue.getRange("AH1:AH1").format.columnWidth = 62;
catalogue.getRange(`AG2:AG${lastRow}`).format.columnWidth = 28;
catalogue.getRange(`AH2:AH${lastRow}`).format.columnWidth = 62;

const verification = await workbook.inspect({
  kind: "table,formula,match",
  sheetId: "Catalogue Véhicules",
  range: `A1:AH${lastRow}`,
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 100 },
  maxChars: 12000,
  tableMaxRows: 10,
  tableMaxCols: 4,
});
console.log(JSON.stringify({ npRows, matchedRows, unmatchedRows, matchedGroups: research.anyMatches, moteurGroups: research.moteurMatches, wandalooGroups: research.wandalooMatches }, null, 2));
console.log(verification.ndjson);

const cataloguePreview = await workbook.render({ sheetName: "Catalogue Véhicules", range: "A1:AH18", scale: 1, format: "png" });
await fs.writeFile(`${previewDir}/Catalogue_Vehicules_prix_web.png`, new Uint8Array(await cataloguePreview.arrayBuffer()));
const grillePreview = await workbook.render({ sheetName: "Grille de Notation", range: "A1:E45", scale: 1, format: "png" });
await fs.writeFile(`${previewDir}/Grille_de_Notation_prix_web.png`, new Uint8Array(await grillePreview.arrayBuffer()));

const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);
console.log(`OUTPUT=${outputPath}`);
