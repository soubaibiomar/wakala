import fs from "node:fs/promises";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const inputPath = "D:/Projet automobile/vente-auto-platform/outputs/wakala-catalogue-prix-web/wakala-catalogue-prix-web-rounded-100.xlsx";
const outputPath = "D:/Projet automobile/vente-auto-platform/outputs/wakala-catalogue-prix-web/wakala-catalogue-prix-web-final.xlsx";
const previewPath = "D:/Projet automobile/vente-auto-platform/_spreadsheet_task/final_previews_global/AG_AH_final.png";

const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(inputPath));
const sheet = workbook.worksheets.getItem("Catalogue Véhicules");
const used = sheet.getUsedRange(true).values;
const lastRow = used.length;
const agValues = sheet.getRange(`AG1:AG${lastRow}`).values;
const priceValues = sheet.getRange(`I1:I${lastRow}`).values;
const landedValues = sheet.getRange(`AM1:AM${lastRow}`).values;

// Remove the auxiliary worldwide/import columns from the visible workbook area.
sheet.getRange(`AI1:AO${lastRow}`).clear({ applyTo: "contents" });
for (const col of ["AI", "AJ", "AK", "AL", "AM", "AN", "AO"]) {
  sheet.getRange(`${col}1:${col}${lastRow}`).format.columnWidth = 0;
}

// Match AG to a normal catalogue text column: standard blue header and clean
// white body cells, while retaining AG's verification text.
sheet.getRange("AG1").values = [["Prix à vérifier (DH)"]];
sheet.getRange("AG1").copyFrom(sheet.getRange("AF1"), "all");
sheet.getRange(`AG2:AG${lastRow}`).copyFrom(sheet.getRange(`F2:F${lastRow}`), "formats");
sheet.getRange(`AG1:AG${lastRow}`).values = agValues;
sheet.getRange("AG1").values = [["Prix à vérifier (DH)"]];
for (let i = 1; i < lastRow; i += 1) {
  const text = String(agValues[i][0] ?? "");
  const landed = landedValues[i][0];
  if (text.startsWith("Estimation import mondiale") && typeof landed === "number") {
    agValues[i][0] = `${text} : ${new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 0 }).format(landed).replace(/\\u202f/g, " ")} DH`;
  }
}
sheet.getRange(`AG1:AG${lastRow}`).values = agValues;
// Detach catalogue prices from the removed auxiliary columns.
sheet.getRange(`I1:I${lastRow}`).values = priceValues;
sheet.getRange(`AG1:AG${lastRow}`).format.columnWidth = 28;
sheet.getRange(`AG1:AG${lastRow}`).format.wrapText = true;
sheet.getRange(`AG1:AG${lastRow}`).format.verticalAlignment = "top";
sheet.getRange("AG1").format.fill = "#1F3A63";
sheet.getRange("AG1").format.font = { color: "#FFFFFF", bold: true };
sheet.getRange("AG1").format.horizontalAlignment = "center";
sheet.getRange("AG1").format.verticalAlignment = "center";
sheet.getRange("AG1").format.borders = { preset: "all", style: "thin", color: "#D9D9D9" };

const check = await workbook.inspect({
  kind: "table,formula,match",
  sheetId: "Catalogue Véhicules",
  range: `A1:AH${lastRow}`,
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 50 },
  maxChars: 5000,
  tableMaxRows: 3,
  tableMaxCols: 3,
});
const extraValues = sheet.getRange(`AI1:AO${lastRow}`).values;
const extraNonBlank = extraValues.flat().filter((value) => String(value ?? "").trim() !== "").length;
console.log(JSON.stringify({ extraNonBlank, lastRow }, null, 2));
console.log(check.ndjson);
const preview = await workbook.render({ sheetName: "Catalogue Véhicules", range: "AF1:AH24", scale: 1.3, format: "png" });
await fs.writeFile(previewPath, new Uint8Array(await preview.arrayBuffer()));
await (await SpreadsheetFile.exportXlsx(workbook)).save(outputPath);
console.log(`OUTPUT=${outputPath}`);
