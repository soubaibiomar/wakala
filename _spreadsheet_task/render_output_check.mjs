import fs from "node:fs/promises";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load("D:/Projet automobile/vente-auto-platform/outputs/wakala-catalogue-prix-web/wakala-catalogue-prix-web.xlsx"));
const catalogue = await workbook.render({ sheetName: "Catalogue Véhicules", range: "AG1:AH18", scale: 1.5, format: "png" });
await fs.writeFile("D:/Projet automobile/vente-auto-platform/_spreadsheet_task/final_previews_web/Catalogue_Vehicules_prix_web_columns.png", new Uint8Array(await catalogue.arrayBuffer()));
const grille = await workbook.render({ sheetName: "Grille de Notation", range: "A1:E45", scale: 1, format: "png" });
await fs.writeFile("D:/Projet automobile/vente-auto-platform/_spreadsheet_task/final_previews_web/Grille_de_Notation_prix_web_check.png", new Uint8Array(await grille.arrayBuffer()));
console.log("rendered");
