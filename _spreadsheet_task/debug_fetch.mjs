const html = await (await fetch("https://www.moteur.ma/fr/neuf/voiture/abarth/595/")).text();
const text = html
  .replace(/<script[\s\S]*?<\/script>/gi, " ")
  .replace(/<style[\s\S]*?<\/style>/gi, " ")
  .replace(/<[^>]+>/g, " ")
  .replace(/\s+/g, " ");
console.log("marker", text.search(/\b202\d\s*:/i));
console.log(text.slice(text.search(/\b202\d\s*:/i), text.search(/\b202\d\s*:/i) + 400));
const pattern = /(\d[\d\s\u00a0.,]*\d|\d{2,})(?:\s*-\s*(\d[\d\s\u00a0.,]*\d|\d{2,}))?\s*(?:Dhs?|DH)\b/gi;
console.log([...text.matchAll(pattern)].slice(0, 10).map((match) => match[0]));
