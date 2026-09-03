import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const inputPath = "C:/Users/omar/AppData/Local/Packages/5319275A.WhatsAppDesktop_cv1g1gvanyjgm/LocalState/sessions/E9C2C21E7054FC6217C6DD688546230CBDEA0F0D/transfers/2026-35/wakala-catalogue.xlsx";
const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(inputPath));
const sheet = workbook.worksheets.getItem("Catalogue Véhicules");
const rows = sheet.getUsedRange(true).values;
const groups = new Map();
for (let i = 1; i < rows.length; i += 1) {
  const row = rows[i];
  if (String(row[8] ?? "").trim().toUpperCase() !== "NP") continue;
  const key = `${row[0]}\u0000${row[4]}`;
  if (!groups.has(key)) groups.set(key, { brand: row[0], model: row[4], rows: [], variants: [] });
  const item = groups.get(key);
  item.rows.push(i + 1);
  if (!item.variants.includes(row[5])) item.variants.push(row[5]);
}
const output = [...groups.values()].sort((a, b) => `${a.brand} ${a.model}`.localeCompare(`${b.brand} ${b.model}`, "fr"));
console.log(`UNIQUE_GROUPS=${output.length}`);
console.log(JSON.stringify(output, null, 2));
