import fs from "node:fs/promises";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const inputPath = "C:/Users/omar/AppData/Local/Packages/5319275A.WhatsAppDesktop_cv1g1gvanyjgm/LocalState/sessions/E9C2C21E7054FC6217C6DD688546230CBDEA0F0D/transfers/2026-35/wakala-catalogue.xlsx";
const outputDir = "D:/Projet automobile/vente-auto-platform/_spreadsheet_task/inspection";
await fs.mkdir(outputDir, { recursive: true });

const input = await FileBlob.load(inputPath);
const workbook = await SpreadsheetFile.importXlsx(input);

const summary = await workbook.inspect({
  kind: "workbook,sheet,table",
  maxChars: 10000,
  tableMaxRows: 8,
  tableMaxCols: 20,
  tableMaxCellChars: 120,
});
console.log(summary.ndjson);

const sheets = workbook.worksheets.items;
for (const sheet of sheets) {
  const used = sheet.getUsedRange(true);
  console.log(`SHEET ${sheet.name} used=${used ? used.address : "none"}`);
  if (used) {
    const region = await workbook.inspect({
      kind: "region",
      sheetId: sheet.name,
      range: used.address,
      maxChars: 12000,
      tableMaxRows: 30,
      tableMaxCols: 30,
      tableMaxCellChars: 120,
    });
    console.log(region.ndjson);
    const previewRange = sheet.name === "Catalogue Véhicules" ? "A1:AF25" : "A1:E45";
    const preview = await workbook.render({ sheetName: sheet.name, range: previewRange, scale: 1, format: "png" });
    await fs.writeFile(`${outputDir}/${sheet.name.replace(/[^a-z0-9_-]+/gi, "_")}.png`, new Uint8Array(await preview.arrayBuffer()));
  }
}

const catalogue = workbook.worksheets.getItem("Catalogue Véhicules");
const catalogueValues = catalogue.getUsedRange(true).values;
const headers = catalogueValues[0];
console.log("HEADERS=" + JSON.stringify(headers));
const priceColumn = headers.findIndex((value) => String(value ?? "").toLowerCase().includes("prix"));
const sourcePattern = /wandaloo|moteur\.ma/i;
const matches = [];
let npCount = 0;
for (let index = 1; index < catalogueValues.length; index += 1) {
  const row = catalogueValues[index];
  const price = String(row[priceColumn] ?? "").trim();
  if (price.toUpperCase() === "NP") {
    npCount += 1;
    const sourceCells = row
      .map((value, columnIndex) => ({ value: String(value ?? ""), columnIndex }))
      .filter(({ value }) => sourcePattern.test(value));
    if (sourceCells.length > 0) {
      matches.push({ row: index + 1, brand: row[0], model: row[4], variant: row[5], price, sources: sourceCells.map(({ value, columnIndex }) => ({ column: headers[columnIndex], value })) });
    }
  }
}
console.log(`NP_COUNT=${npCount}`);
console.log(`NP_WANDALOO_MOTEUR_COUNT=${matches.length}`);
console.log(JSON.stringify(matches, null, 2));
console.log(workbook.help("table.resize", { include: "index,examples,notes", maxChars: 3000 }).ndjson);
