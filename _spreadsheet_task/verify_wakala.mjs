import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const outputPath = "D:/Projet automobile/vente-auto-platform/outputs/wakala-catalogue-prix-web/wakala-catalogue-prix-web-rounded-100.xlsx";
const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(outputPath));
const sheet = workbook.worksheets.getItem("Catalogue Véhicules");
const values = sheet.getRange("AG1:AH831").values;
const populated = values.slice(1).filter(([price]) => String(price ?? "").trim() !== "").length;
const notFound = values.slice(1).filter(([price]) => price === "Non trouvé").length;
const originalPrices = sheet.getRange("I1:I831").values;
const remainingNp = originalPrices.slice(1).filter(([price]) => String(price ?? "").trim().toUpperCase() === "NP").length;
const globalValues = sheet.getRange("AI1:AO831").values;
const globalPopulated = globalValues.slice(1).filter(([source]) => String(source ?? "").trim() !== "").length;
const check = await workbook.inspect({
  kind: "table,formula,match",
  sheetId: "Catalogue Véhicules",
  range: "A1:AO831",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 50 },
  maxChars: 3500,
  tableMaxRows: 4,
  tableMaxCols: 2,
});
console.log(`EXPORTED_POPULATED=${populated}`);
console.log(`EXPORTED_NOT_FOUND=${notFound}`);
console.log(`REMAINING_NP=${remainingNp}`);
console.log(`GLOBAL_POPULATED=${globalPopulated}`);
console.log(JSON.stringify(globalValues.slice(0, 6), null, 2));
console.log(JSON.stringify(values.slice(0, 8), null, 2));
console.log(check.ndjson);
