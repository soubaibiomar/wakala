import fs from "node:fs/promises";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const inputPath = "C:/Users/omar/AppData/Local/Packages/5319275A.WhatsAppDesktop_cv1g1gvanyjgm/LocalState/sessions/E9C2C21E7054FC6217C6DD688546230CBDEA0F0D/transfers/2026-35/wakala-catalogue.xlsx";
const outputDir = "D:/Projet automobile/vente-auto-platform/outputs/wakala-catalogue-prix-a-verifier";
const outputPath = `${outputDir}/wakala-catalogue-prix-a-verifier.xlsx`;
const previewDir = "D:/Projet automobile/vente-auto-platform/_spreadsheet_task/final_previews";

await fs.mkdir(outputDir, { recursive: true });
await fs.mkdir(previewDir, { recursive: true });

const input = await FileBlob.load(inputPath);
const workbook = await SpreadsheetFile.importXlsx(input);
const catalogue = workbook.worksheets.getItem("Catalogue Véhicules");
const usedRange = catalogue.getUsedRange(true);
const values = usedRange.values;
const lastRow = values.length;
const priceIndex = 8;
const npRows = values.slice(1).reduce((count, row) => count + (String(row[priceIndex] ?? "").trim().toUpperCase() === "NP" ? 1 : 0), 0);

// Add a formula-driven flag so the column stays correct if the price is later updated.
catalogue.getRange(`AG2:AG${lastRow}`).copyFrom(catalogue.getRange(`AF2:AF${lastRow}`), "all");
catalogue.getRange(`AG2:AG${lastRow}`).clear({ applyTo: "contents" });
catalogue.getRange("AG1").copyFrom(catalogue.getRange("AF1"), "all");
catalogue.getRange("AG1").values = [["Prix à vérifier"]];
catalogue.getRange("AG2").formulas = [["=IF(UPPER(TRIM(I2))=\"NP\",\"Oui\",\"\")"]];
catalogue.getRange(`AG2:AG${lastRow}`).fillDown();

catalogue.getRange(`AG2:AG${lastRow}`).format = {
  fill: "#FFFFFF",
  font: { color: "#1F2D3D" },
  horizontalAlignment: "center",
  verticalAlignment: "center",
  wrapText: false,
};
catalogue.getRange(`AG1:AG${lastRow}`).format.columnWidth = 18;

const verification = await workbook.inspect({
  kind: "table,formula,match",
  sheetId: "Catalogue Véhicules",
  range: `AG1:AG${lastRow}`,
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 50 },
  maxChars: 5000,
  tableMaxRows: 12,
  tableMaxCols: 2,
});
console.log(`NP_ROWS=${npRows}`);
console.log(verification.ndjson);

const previewCatalogue = await workbook.render({ sheetName: "Catalogue Véhicules", range: "A1:AG25", scale: 1, format: "png" });
await fs.writeFile(`${previewDir}/Catalogue_Vehicules_final.png`, new Uint8Array(await previewCatalogue.arrayBuffer()));
const previewGrid = await workbook.render({ sheetName: "Grille de Notation", range: "A1:E45", scale: 1, format: "png" });
await fs.writeFile(`${previewDir}/Grille_de_Notation_final.png`, new Uint8Array(await previewGrid.arrayBuffer()));

const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);
console.log(`OUTPUT=${outputPath}`);
