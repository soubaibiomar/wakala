import fs from "node:fs/promises";

const dataPath = "D:/Projet automobile/vente-auto-platform/_spreadsheet_task/np_prices_web.json";
const data = JSON.parse(await fs.readFile(dataPath, "utf8"));
const globalPrices = {
  "BMW\u0000iX3": { label: "BMW USA", url: "https://faq.bmwusa.com/s/article/BMW-iX3-Pricing-US-availability-LARmC?language=en_US", currency: "USD", rate: 9.34, min: 60000, max: 60000, scenario: "Non préférentiel : DI 17,5% + TVA 20% + PFI 0,25%" },
  "Aston Martin\u0000DB12": { label: "MotorTrend", url: "https://www.motortrend.com/cars/aston-martin", currency: "USD", rate: 9.34, min: 266000, max: 381007, scenario: "Non préférentiel : DI 17,5% + TVA 20% + PFI 0,25%" },
  "Aston Martin\u0000DBX": { label: "MotorTrend", url: "https://www.motortrend.com/cars/aston-martin", currency: "USD", rate: 9.34, min: 276500, max: 282000, scenario: "Non préférentiel : DI 17,5% + TVA 20% + PFI 0,25%" },
  "Aston Martin\u0000Vantage": { label: "MotorTrend", url: "https://www.motortrend.com/cars/aston-martin", currency: "USD", rate: 9.34, min: 194500, max: 214500, scenario: "Non préférentiel : DI 17,5% + TVA 20% + PFI 0,25%" },
  "Aston Martin\u0000Vanquish": { label: "MotorTrend", url: "https://www.motortrend.com/cars/aston-martin", currency: "USD", rate: 9.34, min: 436500, max: 489700, scenario: "Non préférentiel : DI 17,5% + TVA 20% + PFI 0,25%" },
  "Volvo\u0000EX90": { label: "Volvo Cars USA", url: "https://www.volvocars.com/us/cars/ex90-electric/", currency: "USD", rate: 9.34, min: 78090, max: 78090, scenario: "Non préférentiel : DI 17,5% + TVA 20% + PFI 0,25%" },
  "Lexus\u0000LC": { label: "Lexus USA Newsroom", url: "https://pressroom.lexus.com/tangible-elegance-the-2026-lexus-lc-500/", currency: "USD", rate: 9.34, min: 101800, max: 101800, scenario: "Non préférentiel : DI 17,5% + TVA 20% + PFI 0,25%" },
  "Skoda\u0000Kodiaq Sportline": { label: "Škoda Europe", url: "https://ru-lv.skoda-auto.com/models/jaunais_kodiaq/kodiaq_sportline", currency: "EUR", rate: 10.80, min: 41770, max: 41770, scenario: "Hypothèse origine UE : DI 2,5% + TVA 20% + PFI 0,25%" },
  "Land Rover\u0000Discovery Sport": { label: "Land Rover Europe", url: "https://croatia.landrover.com/land-rover-offers/discovery-offers/discovery-sport-s-offer", currency: "EUR", rate: 10.80, min: 56900, max: 56900, scenario: "Hypothèse origine UE : DI 2,5% + TVA 20% + PFI 0,25%" },
};

let applied = 0;
for (const item of data.results) {
  const global = globalPrices[`${item.brand}\u0000${item.model}`];
  if (!global || item.moteur || item.wandaloo || item.other) continue;
  item.global = { ...global, rangeText: `${global.min} - ${global.max} ${global.currency}` };
  applied += 1;
}
data.generatedAt = new Date().toISOString();
await fs.writeFile(dataPath, JSON.stringify(data, null, 2), "utf8");
console.log(JSON.stringify({ applied }, null, 2));
