// Claxton — builds the UD Service Agreement and Invoice .docx from a spec JSON.
// Usage: node docs.js spec.json outdir
// Spec is produced by build_deal.py (see that file for the shape). Owner-approved
// format from the utter-declutter-contract-builder skill: Times New Roman, US Letter,
// 10pt body / 11pt headings / 28pt title, 2-page contract, 1-page invoice.
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell,
  WidthType, BorderStyle, AlignmentType, VerticalAlign, ShadingType, LevelFormat,
} = require("docx");

const [specPath, outDir] = process.argv.slice(2);
const S = JSON.parse(fs.readFileSync(specPath, "utf8"));
const logo = fs.readFileSync(path.join(__dirname, "ud_logo.png"));
const FONT = "Times New Roman";
const nb = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const noBorders = { top: nb, bottom: nb, left: nb, right: nb, insideHorizontal: nb, insideVertical: nb };
const ln = { style: BorderStyle.SINGLE, size: 4, color: "1C1C1C" };
const lineBorders = { top: ln, bottom: ln, left: nb, right: nb };

const t = (text, o = {}) => new TextRun({ text, font: FONT, size: 20, ...o });
const p = (children, o = {}) => new Paragraph({ children, spacing: { after: 90 }, keepLines: true, ...o });
const bodyP = (text, o = {}) => p([t(text, o)]);
const heading = (title, initials = false) => {
  const runs = [t(title, { bold: true, size: 22 })];
  if (initials) runs.push(t("  •  INITIALS REQUIRED: _______", { bold: true, size: 22 }));
  return new Paragraph({ children: runs, spacing: { before: 200, after: 100 }, keepNext: true, keepLines: true });
};
const bullet = (text, o = {}) => new Paragraph({ children: [t(text, o)], numbering: { reference: "bullets", level: 0 }, spacing: { after: 60 }, keepLines: true });
const sigLine = (label) => p([t(label + ": ______________________________")], { spacing: { after: 120 }, keepNext: true });
const headerTable = (title) => new Table({
  width: { size: 9360, type: WidthType.DXA }, columnWidths: [7160, 2200], borders: noBorders,
  rows: [new TableRow({ children: [
    new TableCell({ width: { size: 7160, type: WidthType.DXA }, borders: noBorders, verticalAlign: VerticalAlign.CENTER,
      children: [new Paragraph({ children: [t(title, { bold: true, size: 56 })], spacing: { after: 0 } })] }),
    new TableCell({ width: { size: 2200, type: WidthType.DXA }, borders: noBorders, verticalAlign: VerticalAlign.CENTER,
      children: [new Paragraph({ alignment: AlignmentType.RIGHT, spacing: { after: 0 },
        children: [new ImageRun({ type: "png", data: logo, transformation: { width: 90, height: 90 } })] })] }),
  ] })],
});
const numbering = { config: [{ reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 360, hanging: 240 } } } }] }] };
const pageProps = { page: { size: { width: 12240, height: 15840 }, margin: { top: 900, bottom: 900, left: 1440, right: 1440 } } };
const usd = (n) => "$" + Number(n).toLocaleString("en-US");
const usd2 = (n) => (n < 0 ? "-$" : "$") + Math.abs(Number(n)).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

// ---------------- CONTRACT ----------------
function contract() {
  const c = S;
  const scope = c.scopeBullets.map((b) => bullet(b));
  const pay = [];
  pay.push(bullet(`Total Service Fee: ${usd(c.total)} (${c.feeDescription})`, { bold: true }));
  if (c.materials > 0) pay.push(bullet(`Materials Budget: ${usd(c.materials)} flat — covers storage solutions and products for the project`, { bold: true }));
  c.paymentBullets.forEach((b) => pay.push(bullet(b.text, b.bold ? { bold: true } : {})));

  const doc = new Document({ numbering, sections: [{ properties: pageProps, children: [
    headerTable("SERVICE AGREEMENT"),
    p([], { spacing: { after: 60 } }),
    p([t("Utter Declutter")], { spacing: { after: 40 } }),
    p([t("Date: "), t(c.date, { bold: true })], { spacing: { after: 40 } }),
    p([t("Invoice #: "), t(String(c.invoice), { bold: true })], { spacing: { after: 240 } }),
    bodyP("This Service Agreement (“Agreement”) is entered into between:"),
    p([t("Business: "), t("Utter Declutter LLC, a Florida limited liability company")], { spacing: { after: 40 } }),
    p([t("Client: "), t(c.client, { bold: true })], { spacing: { after: 40 } }),
    p([t("Project Address: "), t(c.address, { bold: true })], { spacing: { after: 40 } }),
    p([t("Service Date(s): "), t(c.serviceDatesLong, { bold: true })], { spacing: { after: 200 } }),
    bodyP("By signing below, the Client agrees to the following terms and conditions."),
    heading("SCOPE OF WORK", true),
    bodyP("Utter Declutter LLC (the “Service Provider”) agrees to perform the following services:"),
    ...scope,
    bodyP(c.laborSentence),
    heading("PAYMENT TERMS", true),
    ...pay,
    heading("SCOPE LIMITS & ADDITIONAL WORK"),
    bodyP(c.scopeLimits || `The Service Fee covers ${c.daysWord} ${c.days === 1 ? "eight-hour service day" : "eight-hour service days"} as scoped at the walkthrough. Work beyond the agreed scope or service ${c.days === 1 ? "day" : "days"} will be quoted as a written change order and performed only upon written approval by the Client, billed at ${usd(c.dayRate)} per additional crew day plus applicable at-cost expenses (such as dump or junk-removal fees, billed at cost, with no markup).`),
    heading("BUSINESS NAME CLARIFICATION"),
    bodyP("All references in this Agreement to “Utter Declutter” refer to Utter Declutter LLC, a Florida limited liability company. The Client acknowledges that all services, obligations, liabilities, and rights under this Agreement are solely those of Utter Declutter LLC, and not of its owner in an individual capacity."),
    heading("TRADE NAME / D.B.A. CLAUSE"),
    bodyP("Utter Declutter LLC may conduct business under the trade name “Utter Declutter.” Any use of the trade name in this Agreement or associated materials is for branding purposes only and does not alter the legal identity of the contracting party, which is and shall remain Utter Declutter LLC."),
    heading("MEDIA RIGHTS CLAUSE"),
    bodyP("The Client grants Utter Declutter LLC permission to photograph, record, and/or film the project space before, during, and after services are performed. Utter Declutter LLC may use such media — including photos, videos, audio, and written descriptions — for marketing, advertising, training, and promotional purposes, including but not limited to social media, websites, digital ads, print materials, and portfolio use. No personally identifying information about the Client will be disclosed without the Client’s explicit permission."),
    heading("CLIENT REVIEW & COOPERATION"),
    bodyP("The Client agrees to be reasonably available during the project to answer questions, provide feedback, designate item categories, and make timely decisions necessary for the completion of services."),
    heading("MODIFICATIONS"),
    p([t("Any changes to this Agreement must be agreed to in writing by both parties.")], { keepNext: true }),
    heading("TERMINATION"),
    p([t("If the Agreement is terminated prior to project completion, the Client is responsible for paying for all work and costs incurred up until that date.")], { keepNext: true }),
    heading("SIGNATURES"),
    p([t("Client Name: "), t(c.client, { bold: true })], { spacing: { after: 120 }, keepNext: true }),
    sigLine("Client Signature"), sigLine("Date"),
    p([], { spacing: { after: 60 }, keepNext: true }),
    p([t("Utter Declutter LLC Representative: "), t("Jhen Watson, Owner", { bold: true })], { spacing: { after: 120 }, keepNext: true }),
    sigLine("Signature"), sigLine("Date"),
  ] }] });
  return doc;
}

// ---------------- INVOICE ----------------
function cell(text, o = {}) {
  return new TableCell({
    borders: o.borders || lineBorders,
    shading: o.shade ? { type: ShadingType.CLEAR, fill: "E8E3DC" } : undefined,
    verticalAlign: VerticalAlign.CENTER, margins: { top: 80, bottom: 80, left: 120, right: 120 },
    width: { size: o.w, type: WidthType.DXA },
    children: [new Paragraph({ alignment: o.right ? AlignmentType.RIGHT : AlignmentType.LEFT, spacing: { after: 0 }, children: [t(text, { bold: !!o.bold })] })],
  });
}
function invoice() {
  const c = S;
  const rows = [new TableRow({ children: [
    cell("Description", { bold: true, shade: true, w: 5560 }), cell("Rate", { bold: true, shade: true, right: true, w: 1300 }),
    cell("Qty", { bold: true, shade: true, right: true, w: 1200 }), cell("Amount", { bold: true, shade: true, right: true, w: 1300 }),
  ] })];
  c.invoiceLines.forEach((l) => rows.push(new TableRow({ children: [
    cell(l.desc, { w: 5560 }), cell(usd2(l.rate), { right: true, w: 1300 }), cell(String(l.qty), { right: true, w: 1200 }), cell(usd2(l.amount), { right: true, w: 1300 }),
  ] })));
  rows.push(new TableRow({ children: [
    cell("", { w: 5560, borders: noBorders }), cell("Total", { bold: true, right: true, w: 1300, borders: noBorders }),
    cell("", { w: 1200, borders: noBorders }), cell(usd2(c.total), { bold: true, right: true, w: 1300 }),
  ] }));
  const items = new Table({ width: { size: 9360, type: WidthType.DXA }, columnWidths: [5560, 1300, 1200, 1300], rows });
  const sched = c.schedule.map((s) => p([t(s.label + ": "), t(s.amount, { bold: true })], { spacing: { after: 40 } }));
  sched[sched.length - 1] = p([t(c.schedule[c.schedule.length - 1].label + ": "), t(c.schedule[c.schedule.length - 1].amount, { bold: true })], { spacing: { after: 240 } });

  return new Document({ sections: [{ properties: pageProps, children: [
    headerTable(S.docTitle || "INVOICE"),
    p([], { spacing: { after: 60 } }),
    p([t("Utter Declutter LLC")], { spacing: { after: 40 } }),
    p([t("Invoice #: "), t(String(c.invoice), { bold: true })], { spacing: { after: 40 } }),
    p([t("Invoice Date: "), t(c.date, { bold: true })], { spacing: { after: 40 } }),
    p([t("Service Dates: "), t(c.serviceDatesShort, { bold: true })], { spacing: { after: 240 } }),
    p([t("BILL TO", { bold: true, size: 22 })], { spacing: { after: 60 } }),
    p([t(c.client)], { spacing: { after: 40 } }),
    p([t(c.addr1)], { spacing: { after: 40 } }),
    p([t(c.addr2)], { spacing: { after: 240 } }),
    items,
    p([], { spacing: { after: 120 } }),
    p([t(S.scheduleTitle || "PAYMENT SCHEDULE", { bold: true, size: 22 })], { spacing: { after: 60 } }),
    ...sched,
    p([t(S.footerNote || `Per Service Agreement / Invoice #${c.invoice}. Thank you for your business!`, { italics: true })], { spacing: { after: 200 } }),
    p([t("Utter Declutter LLC • Jhen Watson, Owner • (239) 300-3561")], { spacing: { after: 0 } }),
  ] }] });
}

(async () => {
  fs.mkdirSync(outDir, { recursive: true });
  fs.writeFileSync(path.join(outDir, S.invoiceFile || `UD Invoice ${S.invoice} For ${S.client}.docx`), await Packer.toBuffer(invoice()));
  if (S.skipContract) return console.log("docx written");
  fs.writeFileSync(path.join(outDir, `UD Service Contract For ${S.client}.docx`), await Packer.toBuffer(contract()));
  console.log("docx written");
})();
