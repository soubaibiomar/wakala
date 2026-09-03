import fs from "node:fs/promises";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const inputPath = "D:/Projet automobile/vente-auto-platform/outputs/wakala-catalogue-prix-web/wakala-catalogue-prix-web.xlsx";
const priceDataPath = "D:/Projet automobile/vente-auto-platform/_spreadsheet_task/np_prices_web.json";
const outputDir = "D:/Projet automobile/vente-auto-platform/outputs/wakala-catalogue-prix-web";
const outputPath = `${outputDir}/wakala-catalogue-prix-web-rounded-100.xlsx`;
const previewDir = "D:/Projet automobile/vente-auto-platform/_spreadsheet_task/final_previews_global";

await fs.mkdir(previewDir, { recursive: true });
const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(inputPath));
const catalogue = workbook.worksheets.getItem("Catalogue Véhicules");
const values = catalogue.getUsedRange(true).values;
const lastRow = values.length;
const data = JSON.parse(await fs.readFile(priceDataPath, "utf8"));
const byGroup = new Map(data.results.map((item) => [`${item.brand}\u0000${item.model}`, item]));

function formatNumber(value) { return new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 0 }).format(value).replace(/\u202f/g, " "); }
function formatSourcePrice(global) {
  if (!global) return "";
  const range = global.min === global.max ? formatNumber(global.min) : `${formatNumber(global.min)}–${formatNumber(global.max)}`;
  return `${range} ${global.currency}`;
}

const sourcePrices = [];
const rates = [];
const converted = [];
const duties = [];
const totals = [];
const assumptions = [];
const sources = [];
for (let rowIndex = 1; rowIndex < lastRow; rowIndex += 1) {
  const row = values[rowIndex];
  const item = byGroup.get(`${row[0]}\u0000${row[4]}`);
  const global = item?.global;
  sourcePrices.push([formatSourcePrice(global)]);
  rates.push([global?.rate ?? ""]);
  converted.push([global ? `=ROUND(${global.min}*AJ${rowIndex + 1},-2)` : ""]);
  const dutyRate = global?.scenario?.includes("origine UE") ? 0.2325 : 0.4125;
  duties.push([global ? `=ROUND(AK${rowIndex + 1}*${dutyRate},-2)` : ""]);
  totals.push([global ? `=ROUND(AK${rowIndex + 1}+AL${rowIndex + 1},-2)` : ""]);
  assumptions.push([global ? `${global.scenario}; hors transport, assurance, immatriculation, TIC et valeur ADII.` : ""]);
  sources.push([global ? `${global.label}\n${global.url}` : ""]);
}

// Add columns AI:AO while preserving the workbook's existing table styling.
const headers = ["Prix mondial", "Taux MAD", "Prix mondial (MAD)", "Frais import estimés (MAD)", "Coût import estimé (MAD)", "Hypothèse import", "Source mondiale"];
const newColumns = ["AI", "AJ", "AK", "AL", "AM", "AN", "AO"];
for (let i = 0; i < headers.length; i += 1) {
  const col = newColumns[i];
  catalogue.getRange(`${col}1`).copyFrom(catalogue.getRange("AF1"), "all");
  catalogue.getRange(`${col}2:${col}${lastRow}`).copyFrom(catalogue.getRange(`A2:A${lastRow}`), "formats");
  catalogue.getRange(`${col}1`).values = [[headers[i]]];
}
// Remove values/formulas copied only for styling, keeping unmatched rows blank.
catalogue.getRange(`AI1:AO${lastRow}`).clear({ applyTo: "contents" });
catalogue.getRange("AI1:AO1").values = [headers];
catalogue.getRange(`AI2:AI${lastRow}`).values = sourcePrices;
catalogue.getRange(`AJ2:AJ${lastRow}`).values = rates;
catalogue.getRange(`AK2:AK${lastRow}`).formulas = converted;
catalogue.getRange(`AL2:AL${lastRow}`).formulas = duties;
catalogue.getRange(`AM2:AM${lastRow}`).formulas = totals;
catalogue.getRange(`AN2:AN${lastRow}`).values = assumptions;
catalogue.getRange(`AO2:AO${lastRow}`).values = sources;

// For rows whose Moroccan price is still NP, use the estimated landed cost as
// the operational catalogue value, while documenting that it is an estimate.
for (let rowIndex = 1; rowIndex < lastRow; rowIndex += 1) {
  const row = values[rowIndex];
  const item = byGroup.get(`${row[0]}\u0000${row[4]}`);
  if (!item?.global) continue;
  const excelRow = rowIndex + 1;
  catalogue.getRange(`I${excelRow}`).formulas = [[`=ROUND(AM${excelRow},-2)`]];
  catalogue.getRange(`AG${excelRow}`).values = [[`Estimation import mondiale : ${formatSourcePrice(item.global)} → coût estimé en MAD`]];
  catalogue.getRange(`AH${excelRow}`).values = [[`${item.global.sourceLabel}\n${item.global.url}`]];
}

catalogue.getRange(`AI2:AO${lastRow}`).format.wrapText = true;
catalogue.getRange(`AI2:AO${lastRow}`).format.verticalAlignment = "top";
catalogue.getRange("AI1:AO1").format.wrapText = true;
for (const col of ["AI", "AK", "AL", "AM"]) catalogue.getRange(`${col}1:${col}${lastRow}`).format.columnWidth = 24;
catalogue.getRange(`AJ1:AJ${lastRow}`).format.columnWidth = 12;
catalogue.getRange(`AN1:AN${lastRow}`).format.columnWidth = 58;
catalogue.getRange(`AO1:AO${lastRow}`).format.columnWidth = 58;

// Keep displayed monetary values clean and consistent with the catalogue.
catalogue.getRange(`I1:I${lastRow}`).format.numberFormat = "#,##0";
for (const col of ["AK", "AL", "AM"]) catalogue.getRange(`${col}1:${col}${lastRow}`).format.numberFormat = "#,##0";
catalogue.getRange(`AJ1:AJ${lastRow}`).format.numberFormat = "0.00";

const check = await workbook.inspect({
  kind: "table,formula,match",
  sheetId: "Catalogue Véhicules",
  range: `A1:AO${lastRow}`,
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 100 },
  maxChars: 12000,
  tableMaxRows: 8,
  tableMaxCols: 4,
});
console.log(JSON.stringify({ globalGroups: data.results.filter((item) => item.global).length, globalRows: values.slice(1).filter((row) => byGroup.get(`${row[0]}\u0000${row[4]}`)?.global).length }, null, 2));
console.log(check.ndjson);
const preview = await workbook.render({ sheetName: "Catalogue Véhicules", range: "AI1:AO18", scale: 1.3, format: "png" });
await fs.writeFile(`${previewDir}/Catalogue_Vehicules_global_import.png`, new Uint8Array(await preview.arrayBuffer()));
const grille = await workbook.render({ sheetName: "Grille de Notation", range: "A1:E45", scale: 1, format: "png" });
await fs.writeFile(`${previewDir}/Grille_de_Notation_global_import.png`, new Uint8Array(await grille.arrayBuffer()));
await (await SpreadsheetFile.exportXlsx(workbook)).save(outputPath);
console.log(`OUTPUT=${outputPath}`);
