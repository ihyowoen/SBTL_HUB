import fs from "node:fs";

const path = "lib/chat/appCommand.js";
let text = fs.readFileSync(path, "utf8");
const from = 'const CMD_STRATEGIC_SHOW = new RegExp(`(?:(VOL\\\\.\\\\s*\\\\d{2,})|((?:\\\\d{4}년\\\\s*)?\\\\d{1,2}월)\\\\s*)?(?:월간\\\\s*)?전략\\\\s*브리핑(?:을|를)?\\\\s*(?:보여|열어|볼|줘|확인)${VIEW_TAIL}`, "i");';
const to = 'const CMD_STRATEGIC_SHOW = new RegExp(`(?:(VOL\\\\.\\\\s*\\\\d{2,})\\\\s*|((?:\\\\d{4}년\\\\s*)?\\\\d{1,2}월)\\\\s*)?(?:월간\\\\s*)?전략\\\\s*브리핑(?:을|를)?\\\\s*(?:보여|열어|볼|줘|확인)${VIEW_TAIL}`, "i");';
const i = text.indexOf(from);
if (i < 0) throw new Error("VOL selector anchor not found");
if (text.indexOf(from, i + from.length) >= 0) throw new Error("VOL selector anchor not unique");
text = text.slice(0, i) + to + text.slice(i + from.length);
fs.writeFileSync(path, text);
console.log("VOL Strategic Brief selector now consumes following whitespace");
