import fs from "node:fs/promises";

const dataPath = "D:/Projet automobile/vente-auto-platform/_spreadsheet_task/np_prices_web.json";
const data = JSON.parse(await fs.readFile(dataPath, "utf8"));
const overrides = {
  "Nissan\u0000Patrol": { label: "Nissan Maroc", url: "https://nissan.ma/vehicules/patrol/", min: 890000, max: 1050000 },
  "Fiat\u0000Doblo Cargo": { label: "Fiat Maroc", url: "https://www.fiat.ma/professional/promotion/Nouveau-Doblo", min: 199900, max: 199900 },
  "Fiat\u0000Titano": { label: "Fiat Maroc", url: "https://www.fiat.ma/offres-particuliers/fiat-titano", min: 199000, max: 199000 },
  "Jaecoo\u0000Jaecoo 7 PHEV": { label: "AutoChine.ma", url: "https://autochine.ma/modeles/j7-phev", min: 369000, max: 375000 },
  "Jetour\u0000T2 i-DM": { label: "Jetour Maroc", url: "https://campagne.jetour-ma.com/", min: 419900, max: 419900 },
  "MG\u0000MG HS Hybrid+": { label: "AutoNews.ma", url: "https://autonews.ma/guide-auto/voitures-neuves/marque/mg/modele/461-mg-hs-hev", min: 278900, max: 312900 },
  "GAC\u0000Emkoo Hybride": { label: "AutoChine.ma", url: "https://autochine.ma/modeles/emkoo", min: 279900, max: 329900 },
  "GAC\u0000S7 PHEV": { label: "AutoChine.ma", url: "https://autochine.ma/modeles", min: 439900, max: 439900 },
  "KG Mobility\u0000Torres Hybrid": { label: "AutoNews.ma (promotion)", url: "https://autonews.ma/guide-auto/voitures-neuves/marque/kgm/modele/495-kgm-torres-hev", min: 269900, max: 314900 },
  "KG Mobility\u0000Grand Musso": { label: "AutoNews.ma", url: "https://apiv2.autonews.ma/wp-content/uploads/2025/12/Autonews-274-BD.pdf", min: 299900, max: 384900 },
  "Omoda\u0000Omoda 3": { label: "AutoChine.ma", url: "https://autochine.ma/comparer?models=s07%2Cmg-3%2Comoda-3", min: 349000, max: 349000 },
  "Omoda\u0000Omoda C5": { label: "AutoChine.ma", url: "https://autochine.ma/modeles/c5-", min: 285000, max: 285000 },
  "Omoda\u0000Omoda E5": { label: "AutoChine.ma", url: "https://autochine.ma/modeles/e5", min: 275000, max: 275000 },
  "Soueast\u0000S05": { label: "AutoChine.ma", url: "https://autochine.ma/marques/soueast", min: 199900, max: 199900 },
  "Soueast\u0000S06": { label: "AutoChine.ma", url: "https://autochine.ma/modeles/soueast-s06", min: 224900, max: 279900 },
  "Soueast\u0000S08": { label: "AutoChine.ma", url: "https://autochine.ma/marques/soueast", min: 379000, max: 379000 },
  "Mercedes-Benz\u0000Mercedes-Maybach Classe S": { label: "Mercedes-Benz Maroc", url: "https://www.mercedes-benz.ma/our-brands/mercedes-maybach/", min: 2600000, max: 3000000 },
  "Mercedes-Benz\u0000Mercedes-Maybach GLS": { label: "Mercedes-Benz Maroc", url: "https://www.mercedes-benz.ma/our-brands/mercedes-maybach/", min: 1850000, max: 1850000 },
};

let applied = 0;
for (const item of data.results) {
  const override = overrides[`${item.brand}\u0000${item.model}`];
  if (!override || item.moteur || item.wandaloo) continue;
  item.other = { ...override, rangeText: `${override.min} - ${override.max} DH` };
  applied += 1;
}
data.moteurMatches = data.results.filter((item) => item.moteur).length;
data.wandalooMatches = data.results.filter((item) => item.wandaloo).length;
data.anyMatches = data.results.filter((item) => item.moteur || item.wandaloo || item.other).length;
data.generatedAt = new Date().toISOString();
await fs.writeFile(dataPath, JSON.stringify(data, null, 2), "utf8");
console.log(JSON.stringify({ applied, moteurMatches: data.moteurMatches, wandalooMatches: data.wandalooMatches, anyMatches: data.anyMatches }, null, 2));
