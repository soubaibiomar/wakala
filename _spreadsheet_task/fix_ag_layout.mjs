import fs from "node:fs/promises";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const inputPath = "D:/Projet automobile/vente-auto-platform/outputs/wakala-catalogue-prix-web/wakala-catalogue-prix-web-final.xlsx";
const outputPath = "D:/Projet automobile/vente-auto-platform/outputs/wakala-catalogue-prix-web/wakala-catalogue-prix-web-clean.xlsx";
const previewPath = "D:/Projet automobile/vente-auto-platform/_spreadsheet_task/final_previews_global/AG_AH_clean.png";
const dataPath = "D:/Projet automobile/vente-auto-platform/_spreadsheet_task/np_prices_web.json";

const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(inputPath));
const sheet = workbook.worksheets.getItem("Catalogue Véhicules");
const data = JSON.parse(await fs.readFile(dataPath, "utf8"));
const byGroup = new Map(data.results.map((item) => [`${item.brand}\u0000${item.model}`, item]));
const used = sheet.getUsedRange(true).values;
const lastRow = used.length;
const ag = sheet.getRange(`AG1:AG${lastRow}`).values;
const ah = sheet.getRange(`AH1:AH${lastRow}`).values;

function formatNumber(value) {
  return new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 0 }).format(value).replace(/\u202f/g, " ");
}

for (let i = 1; i < lastRow; i += 1) {
  const row = used[i];
  const item = byGroup.get(`${row[0]}\u0000${row[4]}`);
  const global = item?.global;
  if (!global) continue;
  const sourceLabel = global.sourceLabel || global.label || "Source internationale";
  const landed = Math.round(global.min * global.rate * (1 + (global.scenario?.includes("origine UE") ? 0.2325 : 0.4125)) / 100) * 100;
  ag[i][0] = `Estimation mondiale : ${global.rangeText || `${formatNumber(global.min)} ${global.currency}`} → ${formatNumber(landed)} DH import estimé`;
  ah[i][0] = `${sourceLabel}\n${global.url || "Source à vérifier"}`;
}

sheet.getRange(`AG1:AG${lastRow}`).values = ag;
sheet.getRange(`AH1:AH${lastRow}`).values = ah;
sheet.getRange("AG1").values = [["Prix à vérifier (DH)"]];
sheet.getRange("AH1").values = [["Sources web"]];

sheet.getRange(`AG1:AG${lastRow}`).format.columnWidth = 32;
sheet.getRange(`AH1:AH${lastRow}`).format.columnWidth = 42;
sheet.getRange(`AG1:AH${lastRow}`).format.wrapText = true;
sheet.getRange(`AG1:AH${lastRow}`).format.verticalAlignment = "top";
sheet.getRange(`AG2:AH${lastRow}`).format.autofitRows();
sheet.getRange("AG1").format.fill = "#1F3A63";
sheet.getRange("AG1").format.font = { color: "#FFFFFF", bold: true };
sheet.getRange("AG1").format.horizontalAlignment = "center";
sheet.getRange("AG1").format.verticalAlignment = "center";
sheet.getRange("AG1").format.borders = { preset: "all", style: "thin", color: "#D9D9D9" };
sheet.getRange("AH1").format.fill = "#1F3A63";
sheet.getRange("AH1").format.font = { color: "#FFFFFF", bold: true };
sheet.getRange("AH1").format.horizontalAlignment = "center";
sheet.getRange("AH1").format.verticalAlignment = "center";
sheet.getRange("AH1").format.borders = { preset: "all", style: "thin", color: "#D9D9D9" };

const check = await workbook.inspect({
  kind: "table,formula,match",
  sheetId: "Catalogue Véhicules",
  range: `A1:AH${lastRow}`,
  searchTerm: "undefined|#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 100 },
  maxChars: 5000,
  tableMaxRows: 3,
  tableMaxCols: 3,
});
console.log(check.ndjson);
const preview = await workbook.render({ sheetName: "Catalogue Véhicules", range: "AF1:AH24", scale: 1.3, format: "png" });
await fs.writeFile(previewPath, new Uint8Array(await preview.arrayBuffer()));
await (await SpreadsheetFile.exportXlsx(workbook)).save(outputPath);
console.log(`OUTPUT=${outputPath}`);
