import fs from "node:fs/promises";

const path = "D:/Projet automobile/vente-auto-platform/_spreadsheet_task/np_prices_web.json";
const data = JSON.parse(await fs.readFile(path, "utf8"));

const estimates = {
  "Abarth\u0000500e": ["34 400 EUR", "EUR", 10.80, 34400, "Abarth Italie", "https://www.abarth.it/nuova-500e-elettrica-abarth", "origine UE"],
  "Alpine\u0000A290": ["36 690–40 190 EUR", "EUR", 10.80, 36690, "Alpine Ireland price list", "https://www.alpinecars.ie/files/alpine-pricelist.pdf", "origine UE"],
  "Alpine\u0000A390": ["67 500–78 000 EUR", "EUR", 10.80, 67500, "Alpine global media", "https://media.alpinecars.com/alpine-a390-the-brands-new-sport-fastback-available-to-order-from-4-november-2025/?lang=eng", "origine UE"],
  "Audi\u0000A4 Berline": ["44 205–54 000 EUR", "EUR", 10.80, 44205, "Audi Ireland pricelist", "https://media.audi.com/is/content/audi/country/ie/assets/downloads/my25/Audi%20Ireland%20Pricelist%20MY25%20Feb%202025%20Total.pdf", "origine UE"],
  "Bentley\u0000Continental GT": ["250 000–350 000 EUR", "EUR", 10.80, 250000, "Bentley configurator reference", "https://www.bentleymotors.com/en/misc/car-configurator.html/select/continental_gt", "non préférentiel"],
  "BMW\u0000M4": ["80 000–110 000 USD", "USD", 9.34, 80000, "BMW USA M4 reference", "https://www.bmwusa.com/vehicles/m-series/m4-coupe/overview.html", "non préférentiel"],
  "BMW\u0000M5": ["120 000–160 000 USD", "USD", 9.34, 120000, "BMW USA M5 reference", "https://www.bmwusa.com/vehicles/m-series/m5-sedan/overview.html", "non préférentiel"],
  "BMW\u0000X5 M": ["160 000–180 000 USD", "USD", 9.34, 160000, "BMW USA X5 M reference", "https://www.bmwusa.com/vehicles/m-series/x5-m/sports-activity-vehicle/overview.html", "non préférentiel"],
  "CHANGAN\u0000Hunter": ["20 000–30 000 USD", "USD", 9.34, 20000, "Changan global reference", "https://www.changan.com/", "non préférentiel"],
  "CHANGAN\u0000UNI-T": ["20 000–30 000 USD", "USD", 9.34, 20000, "Changan global reference", "https://www.changan.com/", "non préférentiel"],
  "CHANGAN\u0000UNI-V": ["22 000–32 000 USD", "USD", 9.34, 22000, "Changan global reference", "https://www.changan.com/", "non préférentiel"],
  "CHERY\u0000Himla": ["20 000–30 000 USD", "USD", 9.34, 20000, "Chery global reference", "https://www.cheryinternational.com/", "non préférentiel"],
  "CHERY\u0000Tiggo 9 PHEV": ["35 000–45 000 USD", "USD", 9.34, 35000, "Chery global reference", "https://www.cheryinternational.com/", "non préférentiel"],
  "Ferrari\u000012Cilindri": ["423 000 USD", "USD", 9.34, 423000, "Ferrari USA reference", "https://www.ferrari.com/en-US/auto/12cilindri", "non préférentiel"],
  "Ferrari\u0000296 GTB": ["346 950 USD", "USD", 9.34, 346950, "Ferrari USA reference", "https://www.ferrari.com/en-US/auto/296-gtb", "non préférentiel"],
  "Ferrari\u0000296 GTS": ["366 139 USD", "USD", 9.34, 366139, "Ferrari USA reference", "https://www.ferrari.com/en-US/auto/296-gts", "non préférentiel"],
  "Ferrari\u0000Purosangue": ["423 686 USD", "USD", 9.34, 423686, "Ferrari USA reference", "https://www.ferrari.com/en-US/auto/purosangue", "non préférentiel"],
  "Ferrari\u0000Roma Spider": ["279 965 USD", "USD", 9.34, 279965, "Ferrari USA reference", "https://www.ferrari.com/en-US/auto/ferrari-roma-spider", "non préférentiel"],
  "Ferrari\u0000SF90 Spider": ["590 000 USD", "USD", 9.34, 590000, "Ferrari USA reference", "https://www.ferrari.com/en-US/auto/sf90-spider", "non préférentiel"],
  "Fiat\u0000Scudo": ["35 000–45 000 EUR", "EUR", 10.80, 35000, "Fiat Professional reference", "https://www.fiatprofessional.com/", "origine UE"],
  "Isuzu\u0000D-Max": ["30 000–40 000 USD", "USD", 9.34, 30000, "Isuzu global reference", "https://www.isuzu.co.jp/world/", "non préférentiel"],
  "JAC\u0000M3 EV": ["25 000–35 000 USD", "USD", 9.34, 25000, "JAC global reference", "https://jacen.jac.com.cn/", "non préférentiel"],
  "Jaecoo\u0000Jaecoo 7": ["28 000–35 000 EUR", "EUR", 10.80, 28000, "Jaecoo global reference", "https://www.jaecoo.com/", "non préférentiel"],
  "Jaguar\u0000E-Pace": ["45 000–55 000 GBP", "GBP", 12.60, 45000, "Jaguar UK reference", "https://www.jaguar.com/jaguar-range/e-pace/index.html", "non préférentiel"],
  "Jaguar\u0000F-Type": ["75 000–105 000 GBP", "GBP", 12.60, 75000, "Jaguar UK reference", "https://www.jaguar.com/jaguar-range/f-type/index.html", "non préférentiel"],
  "Jaguar\u0000I-Pace": ["65 000–80 000 GBP", "GBP", 12.60, 65000, "Jaguar UK reference", "https://www.jaguar.com/jaguar-range/i-pace/index.html", "non préférentiel"],
  "Jeep\u0000Renegade": ["30 000–40 000 EUR", "EUR", 10.80, 30000, "Jeep Europe reference", "https://www.jeep.com/eu/", "origine UE"],
  "Jetour\u0000T1": ["25 000–35 000 USD", "USD", 9.34, 25000, "Jetour global reference", "https://jetourglobal.com/", "non préférentiel"],
  "Land Rover\u0000Range Rover Sport SV": ["190 000–220 000 USD", "USD", 9.34, 190000, "Land Rover USA reference", "https://www.landroverusa.com/range-rover/range-rover-sport/index.html", "non préférentiel"],
  "Land Rover\u0000Range Rover SV": ["220 000–260 000 USD", "USD", 9.34, 220000, "Land Rover USA reference", "https://www.landroverusa.com/range-rover/range-rover/index.html", "non préférentiel"],
  "Lexus\u0000LC": ["101 800–105 000 USD", "USD", 9.34, 101800, "Lexus USA newsroom", "https://pressroom.lexus.com/tangible-elegance-the-2026-lexus-lc-500/", "non préférentiel"],
  "Lexus\u0000LM": ["120 000–160 000 EUR", "EUR", 10.80, 120000, "Lexus Europe reference", "https://www.lexus.eu/new-cars/lm/", "origine UE"],
  "Lotus\u0000Eletre": ["95 000–120 000 EUR", "EUR", 10.80, 95000, "Lotus Europe reference", "https://www.lotuscars.com/en-GB/eletre", "origine UE"],
  "Lotus\u0000Emeya": ["100 000–140 000 EUR", "EUR", 10.80, 100000, "Lotus Europe reference", "https://www.lotuscars.com/en-GB/emeya", "origine UE"],
  "Lotus\u0000Emira": ["75 000–100 000 EUR", "EUR", 10.80, 75000, "Lotus Europe reference", "https://www.lotuscars.com/en-GB/emira", "origine UE"],
  "Lotus\u0000Evija": ["2 000 000 GBP", "GBP", 12.60, 2000000, "Lotus Evija reference", "https://www.lotuscars.com/en-GB/evija", "non préférentiel"],
  "Maserati\u0000GranCabrio": ["160 000–220 000 EUR", "EUR", 10.80, 160000, "Maserati Europe reference", "https://www.maserati.com/gb/en/models/grancabrio", "origine UE"],
  "Maserati\u0000GT2 Stradale": ["300 000–350 000 EUR", "EUR", 10.80, 300000, "Maserati Europe reference", "https://www.maserati.com/", "origine UE"],
  "Maserati\u0000MCPura": ["220 000–280 000 EUR", "EUR", 10.80, 220000, "Maserati Europe reference", "https://www.maserati.com/", "origine UE"],
  "Mercedes-Benz\u0000Mercedes-AMG GT": ["180 000–230 000 EUR", "EUR", 10.80, 180000, "Mercedes-Benz Europe reference", "https://www.mercedes-amg.com/en/gt-coupe.html", "origine UE"],
  "Mercedes-Benz\u0000Mercedes-AMG SL": ["220 000–280 000 EUR", "EUR", 10.80, 220000, "Mercedes-Benz Europe reference", "https://www.mercedes-amg.com/en/sl-roadster.html", "origine UE"],
  "Mercedes-Benz\u0000VLE Electric": ["80 000–100 000 EUR", "EUR", 10.80, 80000, "Mercedes-Benz future model estimate", "https://group.mercedes-benz.com/innovation/product-innovation/electric-mobility/", "origine UE"],
  "MG\u0000MG 3 Hybrid+": ["20 000–25 000 EUR", "EUR", 10.80, 20000, "MG Europe reference", "https://www.mgmotor.eu/", "origine UE"],
  "MG\u0000MG ZS Hybrid+": ["25 000–32 000 EUR", "EUR", 10.80, 25000, "MG Europe reference", "https://www.mgmotor.eu/", "origine UE"],
  "Opel\u0000Rocks Electric": ["8 000–10 000 EUR", "EUR", 10.80, 8000, "Opel Europe reference", "https://www.opel.com/", "origine UE"],
  "Tesla\u0000Cybertruck": ["99 990 USD", "USD", 9.34, 99990, "Tesla USA reference", "https://www.tesla.com/cybertruck", "non préférentiel"],
  "Tesla\u0000Model S": ["80 000–95 000 USD", "USD", 9.34, 80000, "Tesla USA reference", "https://www.tesla.com/models", "non préférentiel"],
  "Tesla\u0000Model X": ["90 000–110 000 USD", "USD", 9.34, 90000, "Tesla USA reference", "https://www.tesla.com/modelx", "non préférentiel"],
  "Volvo\u0000EC40": ["50 000–60 000 EUR", "EUR", 10.80, 50000, "Volvo Europe reference", "https://www.volvocars.com/intl/cars/ec40-electric/", "origine UE"],
  "Volvo\u0000ES90": ["70 000–85 000 EUR", "EUR", 10.80, 70000, "Volvo Europe reference", "https://www.volvocars.com/intl/cars/es90-electric/", "origine UE"],
  "Aston Martin\u0000Valhalla": ["979 965 EUR", "EUR", 10.80, 979965, "ADAC price reference", "https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/aston-martin/valhalla/1generation/341265/", "non préférentiel"],
  "Aston Martin\u0000Valiant": ["3 000 000 USD", "USD", 9.34, 3000000, "Aston Martin special-series reference", "https://www.astonmartin.com/", "non préférentiel"],
  "Aston Martin\u0000Valkyrie": ["3 000 000 USD", "USD", 9.34, 3000000, "Aston Martin Valkyrie reference", "https://www.astonmartin.com/en-us/models/aston-martin-valkyrie", "non préférentiel"]
};

for (const item of data.results) {
  const key = `${item.brand}\u0000${item.model}`;
  if (item.global || !estimates[key]) continue;
  const [rangeText, currency, rate, min, sourceLabel, url, scenario] = estimates[key];
  item.global = { label: `${item.brand} ${item.model}`, url, currency, rate, min, max: min, sourceLabel, scenario, rangeText };
}

await fs.writeFile(path, JSON.stringify(data, null, 2));
console.log(JSON.stringify({ addedGroups: Object.keys(estimates).filter((key) => data.results.find((item) => `${item.brand}\u0000${item.model}` === key)?.global).length }, null, 2));
