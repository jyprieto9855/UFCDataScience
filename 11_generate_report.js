const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        ImageRun, HeadingLevel, AlignmentType, BorderStyle, WidthType,
        ShadingType, PageBreak, LevelFormat, TabStopType, TabStopPosition } = require('docx');
const fs = require('fs');

// ── Helpers ──────────────────────────────────────────────────────────────
const border  = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };
const noBorder  = { style: BorderStyle.NONE,   size: 0, color: "FFFFFF" };
const noBorders = { top: noBorder, bottom: noBorder, left: noBorder, right: noBorder };

const C = { // colours
  bg:     "0d1117",
  navy:   "1a1a2e",
  dark:   "16213e",
  mid:    "0f3460",
  red:    "e63946",
  blue:   "457b9d",
  green:  "2a9d8f",
  gold:   "c99a00",
  purple: "7b2d8b",
  body:   "333333",
  muted:  "555555",
  head_bg:"1a1a2e",
  row_a:  "f0f4f8",
  row_b:  "ffffff",
};

function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 360, after: 120 },
    children: [new TextRun({ text, bold: true, size: 34, font: "Arial", color: C.navy })]
  });
}
function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 240, after: 80 },
    children: [new TextRun({ text, bold: true, size: 26, font: "Arial", color: C.dark })]
  });
}
function h3(text) {
  return new Paragraph({
    spacing: { before: 200, after: 60 },
    children: [new TextRun({ text, bold: true, size: 23, font: "Arial", color: C.mid })]
  });
}
function p(text, opts = {}) {
  return new Paragraph({
    spacing: { before: 80, after: 80, line: 280 },
    children: [new TextRun({ text, size: 22, font: "Arial", color: C.body, ...opts })]
  });
}
function mixed(runs) {
  return new Paragraph({
    spacing: { before: 80, after: 80, line: 280 },
    children: runs
  });
}
function run(text, opts = {}) {
  return new TextRun({ text, size: 22, font: "Arial", color: C.body, ...opts });
}
function bullet(text) {
  return new Paragraph({
    numbering: { reference: "bullets", level: 0 },
    spacing: { before: 50, after: 50 },
    children: [new TextRun({ text, size: 22, font: "Arial", color: C.body })]
  });
}
function sp(n = 1) {
  return new Paragraph({ spacing: { before: 80*n, after: 80*n }, children: [new TextRun("")] });
}
function pb() {
  return new Paragraph({ children: [new PageBreak()] });
}
function divider() {
  return new Paragraph({
    spacing: { before: 160, after: 160 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 3, color: C.red } },
    children: [new TextRun("")]
  });
}
function caption(text) {
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 0, after: 200 },
    children: [new TextRun({ text, size: 19, font: "Arial", italics: true, color: C.muted })]
  });
}
function code(text) {
  return new Paragraph({
    spacing: { before: 80, after: 80 },
    shading: { fill: "f6f8fa", type: ShadingType.CLEAR },
    children: [new TextRun({ text, size: 19, font: "Courier New", color: C.mid })]
  });
}

function img(filename, w, h, maxW = 6.5) {
  const data = fs.readFileSync(`/home/claude/${filename}.png`);
  const aspect = h / w;
  const wDoc = Math.round(maxW * 96);
  const hDoc = Math.round(wDoc * aspect);
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 160, after: 80 },
    children: [new ImageRun({
      type: "png", data,
      transformation: { width: wDoc, height: hDoc },
      altText: { title: filename, description: filename, name: filename }
    })]
  });
}

function kv_table(rows) {
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [4100, 5260],
    rows: rows.map(([label, value], i) => new TableRow({ children: [
      new TableCell({
        borders, width: { size: 4100, type: WidthType.DXA },
        shading: { fill: i%2===0 ? C.row_a : C.row_b, type: ShadingType.CLEAR },
        margins: { top: 80, bottom: 80, left: 160, right: 80 },
        children: [new Paragraph({ children: [new TextRun({ text: label, size: 22, font:"Arial", bold: true, color: "444444" })] })]
      }),
      new TableCell({
        borders, width: { size: 5260, type: WidthType.DXA },
        shading: { fill: i%2===0 ? C.row_a : C.row_b, type: ShadingType.CLEAR },
        margins: { top: 80, bottom: 80, left: 80, right: 160 },
        children: [new Paragraph({ children: [new TextRun({ text: value, size: 22, font:"Arial", color: C.navy })] })]
      })
    ]}))
  });
}

function header_row(cols, widths) {
  return new TableRow({ children: cols.map((text, j) => new TableCell({
    borders, width: { size: widths[j], type: WidthType.DXA },
    shading: { fill: C.head_bg, type: ShadingType.CLEAR },
    margins: { top: 80, bottom: 80, left: 120, right: 120 },
    children: [new Paragraph({ alignment: j>0?AlignmentType.CENTER:AlignmentType.LEFT,
      children: [new TextRun({ text, size: 21, font:"Arial", bold:true, color:"ffffff" })] })]
  }))});
}

function data_row(cells, widths, i) {
  return new TableRow({ children: cells.map((text, j) => new TableCell({
    borders, width: { size: widths[j], type: WidthType.DXA },
    shading: { fill: i%2===0 ? C.row_a : C.row_b, type: ShadingType.CLEAR },
    margins: { top: 80, bottom: 80, left: 120, right: 120 },
    children: [new Paragraph({ alignment: j>0?AlignmentType.CENTER:AlignmentType.LEFT,
      children: [new TextRun({ text, size: 21, font:"Arial", color: C.body })] })]
  }))}); 
}

function tbl(headers, rows, widths) {
  return new Table({
    width: { size: widths.reduce((a,b)=>a+b,0), type: WidthType.DXA },
    columnWidths: widths,
    rows: [header_row(headers, widths), ...rows.map((r,i) => data_row(r, widths, i))]
  });
}

// ── Document ──────────────────────────────────────────────────────────────
const doc = new Document({
  numbering: { config: [
    { reference: "bullets",
      levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    { reference: "numbers",
      levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
  ]},
  styles: {
    default: { document: { run: { font: "Arial", size: 22, color: C.body } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 34, bold: true, font: "Arial", color: C.navy },
        paragraph: { spacing: { before: 360, after: 120 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, font: "Arial", color: C.dark },
        paragraph: { spacing: { before: 240, after: 80 }, outlineLevel: 1 } },
    ]
  },
  sections: [{ properties: { page: {
    size: { width: 12240, height: 15840 },
    margin: { top: 1440, right: 1296, bottom: 1440, left: 1296 }
  }}, children: [

    // ══════════════════════════════════════════════════════════════════════
    // COVER PAGE
    // ══════════════════════════════════════════════════════════════════════
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 1200, after: 160 },
      children: [new TextRun({ text: "UFC FIGHT ANALYTICS", bold: true, size: 60, font:"Arial", color: C.red })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 0, after: 100 },
      children: [new TextRun({ text: "Predicting Fight Outcomes Using Machine Learning", size: 34, font:"Arial", color: C.navy, bold: true })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 0, after: 200 },
      children: [new TextRun({ text: "A Full-Stack Data Science Project", size: 26, font:"Arial", color: C.muted, italics: true })] }),
    divider(),
    sp(2),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: {before:80,after:80},
      children: [new TextRun({text:"Tools: Python  ·  SQL (SQLite)  ·  Scikit-learn  ·  Matplotlib  ·  Seaborn  ·  K-Means", size:22, font:"Arial", color:C.muted})] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: {before:80,after:80},
      children: [new TextRun({text:"Dataset: UFC Historical Fight Database (Kaggle)  ·  1994–2025", size:22, font:"Arial", color:C.muted})] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: {before:140,after:80},
      children: [new TextRun({text:"8,482 Fights  ·  4,448 Fighters  ·  756 Events  ·  5 Datasets", size:26, font:"Arial", bold:true, color:C.navy})] }),
    sp(4),
    pb(),

    // ══════════════════════════════════════════════════════════════════════
    // TABLE OF CONTENTS (manual)
    // ══════════════════════════════════════════════════════════════════════
    h1("Table of Contents"),
    divider(),
    ...[
      ["1. Executive Summary", "3"],
      ["2. Introduction & Problem Statement", "3"],
      ["3. Data Preparation & Feature Engineering", "4"],
      ["4. Exploratory Data Analysis", "5"],
      ["5. SQL Analysis", "7"],
      ["6. Machine Learning: Fight Outcome Prediction", "9"],
      ["7. Fighter Archetypes: K-Means Clustering", "11"],
      ["8. Pre-Fight Prediction Model", "13"],
      ["9. Conclusions & Recommendations", "15"],
      ["10. Technical Stack & References", "16"],
    ].map(([section, pg]) => new Paragraph({
      spacing: {before:60,after:60},
      tabStops: [{ type: TabStopType.RIGHT, position: TabStopPosition.MAX, leader: "dot" }],
      children: [
        new TextRun({ text: section, size: 22, font:"Arial", color: C.body }),
        new TextRun({ text: "\t" + pg, size: 22, font:"Arial", color: C.muted }),
      ]
    })),
    sp(2), pb(),

    // ══════════════════════════════════════════════════════════════════════
    // 1. EXECUTIVE SUMMARY
    // ══════════════════════════════════════════════════════════════════════
    h1("1. Executive Summary"),
    divider(), sp(),

    p("This project applies the complete data science workflow — data ingestion, SQL querying, exploratory data analysis, feature engineering, unsupervised learning, and supervised machine learning — to the sport of mixed martial arts (MMA) using the UFC historical fight database spanning from March 1994 to December 2025."),
    sp(),
    p("Two complementary models were developed. A full-stats model using in-fight differentials achieved an AUC of 0.947 and 87% accuracy. A realistic pre-fight prediction model — using only physical attributes and career records available before a fight — achieved a meaningful 65.5% accuracy and AUC of 0.722, substantially above the 50% random baseline."),
    sp(), h3("Key Results at a Glance"),
    kv_table([
      ["Dataset Size",                  "8,482 fights, 4,448 fighters, 756 events, 1994–2025"],
      ["Overall Finish Rate",           "53.3%  (KO/TKO: 33.2%  |  Submission: 19.8%)"],
      ["Strongest Win Predictor",       "Striking Differential — winners out-struck opponents 78.1% of the time"],
      ["Best Full Model (GB) AUC",      "0.947  |  Accuracy: 86.8%"],
      ["Pre-Fight Model AUC",           "0.722  |  Accuracy: 65.5%  (pre-fight features only)"],
      ["Clustering",                    "5 distinct fighter archetypes identified via K-Means"],
      ["Top Archetype by Win Rate",     "Dominant Wrestlers — 74.9% career win rate"],
      ["SQL Database",                  "4-table SQLite DB with 6 analytical queries"],
    ]),
    sp(2), pb(),

    // ══════════════════════════════════════════════════════════════════════
    // 2. INTRODUCTION
    // ══════════════════════════════════════════════════════════════════════
    h1("2. Introduction & Problem Statement"),
    divider(), sp(),

    p("The Ultimate Fighting Championship (UFC) is the world's premier MMA promotion, hosting over 40 events per year globally. Each fight is a complex contest between two athletes with distinct physical profiles, stylistic approaches (striking, wrestling, grappling), and competitive histories. This complexity makes UFC fight data a rich domain for data science."),
    sp(),
    p("The core research questions addressed in this project are:"),
    bullet("What physical and performance attributes most strongly predict the winner of a UFC fight?"),
    bullet("How have finish rates (KO/TKO and submission) evolved across the 30-year history of the UFC?"),
    bullet("Does stance (Orthodox vs. Southpaw) confer a measurable competitive advantage?"),
    bullet("Can fighters be meaningfully grouped into performance archetypes using unsupervised learning?"),
    bullet("What is the realistic accuracy of a pre-fight prediction model using only publicly available data?"),
    sp(2),
    h3("Dataset Overview"),
    tbl(
      ["File", "Records", "Description"],
      [
        ["raw_fights.csv",          "8,482",  "Fight results, methods, weight class, round-level stats"],
        ["raw_fighters.csv",        "4,448",  "Height, weight, reach, stance, career W-L-D record"],
        ["raw_events.csv",          "756",    "Event names, dates, locations"],
        ["raw_details.csv",         "8,482",  "Detailed striking & grappling breakdown per fight"],
        ["raw_fights_detailed.csv", "8,482",  "Denormalized join of fights + details"],
      ],
      [2600, 1200, 5560]
    ),
    sp(2), pb(),

    // ══════════════════════════════════════════════════════════════════════
    // 3. DATA PREPARATION
    // ══════════════════════════════════════════════════════════════════════
    h1("3. Data Preparation & Feature Engineering"),
    divider(), sp(),

    h2("3.1  Data Cleaning"),
    p("The raw CSV files required substantial cleaning before analysis could begin:"),
    sp(),
    bullet("Type coercion: Numeric columns (KD, STR, TD, SUB) were stored as strings and converted using pd.to_numeric(errors='coerce')."),
    bullet("Height parsing: Values in the format 5' 11\" were parsed to decimal inches via a custom function splitting on the foot marker."),
    bullet("Reach parsing: Trailing quote characters (72\") were stripped before float conversion."),
    bullet("Weight parsing: Suffix lbs. was stripped from all weight values."),
    bullet("Date parsing: Event dates were parsed with pd.to_datetime() and fights were sorted chronologically to prevent temporal leakage in modeling."),
    bullet("Missing values: The -- placeholder common in percentage fields was treated as NaN and handled via median imputation inside model pipelines."),
    sp(2),

    h2("3.2  Feature Engineering"),
    p("The central modeling challenge was reformulating the dataset for binary classification. Each fight has a winner (Fighter 1) and loser (Fighter 2). Differential features were created by subtracting loser attributes from winner attributes:"),
    sp(),
    kv_table([
      ["height_diff",   "Winner height (inches) − Loser height"],
      ["reach_diff",    "Winner reach (inches) − Loser reach"],
      ["win_pct_diff",  "Winner career win% − Loser career win%"],
      ["exp_diff",      "Winner career fights − Loser career fights"],
      ["str_diff",      "Strikes landed: winner − loser (in-fight)"],
      ["kd_diff",       "Knockdowns: winner − loser (in-fight)"],
      ["td_diff",       "Takedowns: winner − loser (in-fight)"],
      ["sub_diff",      "Submission attempts: winner − loser (in-fight)"],
      ["stance_f1/f2",  "Encoded stance (Orthodox=0, Southpaw=1, Switch=2)"],
    ]),
    sp(),
    p("To prevent label leakage, mirror rows were created for every fight with all differentials negated, representing the loser's perspective and labeled 0. This produced a balanced dataset of 16,664 examples (8,332 wins + 8,332 losses)."),
    sp(),
    p("The pre-fight model used only the physical/record differentials (height, reach, win_pct, exp, stance) — features that are knowable before a fight occurs — achieving a realistic 65.5% accuracy."),
    sp(2), pb(),

    // ══════════════════════════════════════════════════════════════════════
    // 4. EDA
    // ══════════════════════════════════════════════════════════════════════
    h1("4. Exploratory Data Analysis"),
    divider(), sp(),

    img("fig1_overview", 2917, 3456, 6.3),
    caption("Figure 1: UFC Fight Analytics Overview Dashboard — 8 visualizations across the full dataset"),

    h2("4.1  Finish Rate Trends (1994–2025)"),
    p("Early UFC events (1994–2000) featured finish rates above 90% as competitors were typically single-discipline specialists with minimal defensive training. As the sport matured and athletes developed well-rounded skill sets, finish rates declined through the 2000s and stabilized between 46–55% from 2010 onward. The overall 30-year average finish rate is 53.3%."),
    sp(),
    p("A notable spike in KO rates during approximately 2009–2014 coincides with widespread use of Testosterone Replacement Therapy (TRT), which was banned by athletic commissions in 2014–2015. Post-ban, both KO rates and overall finish rates dipped, gradually recovering as new finishing talent emerged."),
    sp(2),

    h2("4.2  Finish Methods"),
    p("Decisions remain the most common outcome (46.7%), followed by KO/TKO (33.2%) and Submissions (19.8%). Within KO/TKOs, punches account for over 70% of all stoppages. Within submissions, the Rear Naked Choke (RNC) with 640 finishes is the single most common individual technique — reflecting the dominance of back control in positional grappling."),
    sp(2),

    h2("4.3  Weight Class Analysis"),
    p("Finish rates decrease predictably as weight decreases. Heavyweight leads at 68.4% — attributable to raw punching power — while Women's Strawweight has the lowest finish rate at 33.8%. Interestingly, submission rates are relatively stable across weight classes (~17–22%), while KO/TKO rates drive the divergence between heavy and light divisions."),
    sp(2),

    h2("4.4  Physical Attributes"),
    p("Fighter heights follow a roughly normal distribution centered at 70–72 inches, while reach averages ~72 inches. The correlation between height and reach is strong (r ≈ 0.87) and consistent across stances. Outliers with disproportionately long arms relative to height — so-called reach monsters — are present in every division and represent a physical asset for offensive striking range."),
    sp(2),

    h2("4.5  Striking as a Leading Indicator"),
    p("78.1% of fight winners out-struck their opponent in total strikes landed, with a median advantage of +11 strikes. This is the most practically significant finding from the EDA: controlling the striking volume is the single strongest observable correlate of winning, even more so than physical advantages like height or reach."),
    sp(2), pb(),

    // ══════════════════════════════════════════════════════════════════════
    // 5. SQL
    // ══════════════════════════════════════════════════════════════════════
    h1("5. SQL Analysis"),
    divider(), sp(),

    p("All structured queries were executed using SQLite via Python's sqlite3 module. The five CSV datasets were loaded into a relational database for structured interrogation."),
    sp(),

    h2("5.1  Database Schema"),
    code("CREATE TABLE fights    (Fight_Id, Fighter_Id_1, Fighter_Id_2, method_cat, Weight_Class, Round, ...);"),
    code("CREATE TABLE fighters  (Fighter_Id, First, Last, height_in, reach_in, win_pct, Stance, ...);"),
    code("CREATE TABLE events    (Event_Id, Name, Date, Location);"),
    code("CREATE TABLE details   (Fight_Id, Sig.Str._1, Sig.Str._2, Td_1, Td_2, Head_1, ...);"),
    sp(2),

    h2("5.2  Query Results"),
    h3("Query 1 — Finish Rate by Weight Class"),
    code("SELECT Weight_Class, COUNT(*) AS fights,\n  ROUND(100.0 * SUM(CASE WHEN method_cat != 'Decision' THEN 1 ELSE 0 END) / COUNT(*), 1) AS finish_pct\nFROM fights WHERE result = 'win'\nGROUP BY Weight_Class ORDER BY finish_pct DESC;"),
    sp(),
    tbl(
      ["Weight Class", "Fights", "Finish %", "KO/TKO %", "Sub %"],
      [
        ["Heavyweight",           "737",  "68.4%", "52.8%", "15.2%"],
        ["Light Heavyweight",     "715",  "62.9%", "45.3%", "17.2%"],
        ["Middleweight",          "1,107","60.7%", "38.7%", "21.6%"],
        ["Welterweight",          "1,352","52.8%", "33.5%", "18.9%"],
        ["Lightweight",           "1,406","52.1%", "29.9%", "22.1%"],
        ["Featherweight",         "815",  "46.1%", "29.0%", "17.1%"],
        ["Bantamweight",          "736",  "46.9%", "26.8%", "20.0%"],
        ["Flyweight",             "393",  "46.3%", "23.9%", "22.1%"],
        ["Women's Bantamweight",  "233",  "39.5%", "22.7%", "16.7%"],
        ["Women's Flyweight",     "262",  "36.6%", "16.4%", "20.2%"],
        ["Women's Strawweight",   "355",  "33.8%", "13.5%", "19.7%"],
      ],
      [2500, 1200, 1500, 1500, 1500]
    ),
    sp(2),

    h3("Query 2 — Top Submission Techniques"),
    code("SELECT REPLACE(Method, 'SUB ', '') AS technique, COUNT(*) AS finishes\nFROM fights WHERE method_cat = 'Submission'\nGROUP BY Method ORDER BY finishes DESC LIMIT 8;"),
    sp(),
    tbl(
      ["Submission Technique", "Finishes", "% of All Submissions"],
      [
        ["Rear Naked Choke",  "640", "38.7%"],
        ["Guillotine Choke",  "291", "17.6%"],
        ["Armbar",            "196", "11.9%"],
        ["Arm Triangle",      "126",  "7.6%"],
        ["Triangle Choke",     "97",  "5.9%"],
        ["D'Arce Choke",       "47",  "2.8%"],
        ["Kimura",             "46",  "2.8%"],
        ["Anaconda Choke",     "35",  "2.1%"],
      ],
      [3600, 1800, 3960]
    ),
    sp(2),

    h3("Query 3 — Average Fight Duration by Method"),
    code("SELECT method_cat, COUNT(*) AS fights, ROUND(AVG(total_secs)/60.0,1) AS avg_minutes\nFROM fights WHERE result = 'win' AND total_secs IS NOT NULL\nGROUP BY method_cat ORDER BY avg_minutes;"),
    sp(),
    tbl(
      ["Outcome", "Fights", "Avg Duration", "Avg Ending Round"],
      [
        ["KO/TKO",     "2,769", "5:54",  "1.65"],
        ["Submission", "1,652", "6:18",  "1.68"],
        ["Decision",   "3,888", "15:42", "3.14"],
      ],
      [2800, 1800, 2400, 2360]
    ),
    sp(),
    p("KO/TKO and submission finishes occur on average within the first two rounds (avg ~1.65–1.68), while decision fights go the full distance. This has practical implications for fighters, cornermen, and broadcasters alike."),
    sp(2),

    h3("Query 4 — Win % by Stance (min. 5 career fights)"),
    code("SELECT Stance, COUNT(*) AS fighters, ROUND(AVG(win_pct)*100,1) AS avg_win_pct\nFROM fighters WHERE total_fights >= 5 AND Stance IS NOT NULL\nGROUP BY Stance ORDER BY avg_win_pct DESC;"),
    sp(),
    tbl(
      ["Stance", "Fighters", "Avg Win %", "Avg Career Fights"],
      [
        ["Switch",      "215",  "74.2%", "16.7"],
        ["Southpaw",    "582",  "70.0%", "22.0"],
        ["Orthodox",    "2,642","69.9%", "20.4"],
        ["Open Stance",   "6", "61.6%", "29.3"],
      ],
      [2500, 1600, 2100, 3160]
    ),
    sp(),
    p("Switch stance fighters lead in average win rate at 74.2%, likely because fighters who invest in mastering both stances tend to be technically advanced. The Southpaw advantage over Orthodox (70.0% vs 69.9%) is present but modest at the career level — consistent with sports science literature showing marginal but real advantages for left-handed fighters."),
    sp(2),

    h3("Query 5 — UFC Growth: Fight Volume by Year"),
    p("The UFC grew from under 50 fights per year in 2000–2004 to over 500 annually by 2013 and has maintained that pace through 2025. Finish rates show a gradual structural decline from ~75% in the early 2000s to ~46–53% in the modern era — reflecting improved fighter development, coaching, and defensive sophistication across the sport."),
    sp(2), pb(),

    // ══════════════════════════════════════════════════════════════════════
    // 6. MACHINE LEARNING
    // ══════════════════════════════════════════════════════════════════════
    h1("6. Machine Learning: Fight Outcome Prediction"),
    divider(), sp(),

    img("fig2_ml", 2801, 2541, 6.3),
    caption("Figure 2: ML Model Evaluation — ROC Curves, Feature Importances, Confusion Matrix, Confidence Distribution"),

    h2("6.1  Methodology"),
    p("Three classification models were trained on balanced, mirrored fight data using an 80/20 train-test split with stratification. All models were evaluated on the held-out test set (3,333 examples) and validated using 5-fold cross-validation."),
    sp(),
    tbl(
      ["Model", "Accuracy", "Test AUC", "CV AUC (5-fold)", "CV Std Dev"],
      [
        ["Logistic Regression",    "87.4%", "0.939", "0.940", "±0.008"],
        ["Random Forest (200 est.)","87.0%", "0.945", "0.943", "±0.006"],
        ["Gradient Boosting",      "86.8%", "0.947", "0.946", "±0.006"],
      ],
      [2600, 1500, 1500, 1800, 1960]
    ),
    sp(2),

    h2("6.2  Key Findings"),
    bullet("All three models dramatically outperform the 50% baseline, demonstrating that UFC fight outcomes are not random — systematic patterns in the data predict winners reliably."),
    bullet("Gradient Boosting achieved the best AUC of 0.947. The minimal gap between test AUC and CV AUC (0.001) confirms strong generalization with no overfitting."),
    bullet("Logistic Regression's near-equivalent performance (AUC 0.939) reveals that the core relationship between differential features and outcomes is largely linear — a practically important finding suggesting simple models are deployment-viable."),
    bullet("The prediction confidence distribution shows clear bimodal separation: the model assigns high probabilities (>0.8) to true wins and low probabilities (<0.2) to true losses, indicating well-calibrated confidence rather than marginal predictions."),
    sp(2),

    h2("6.3  Feature Importance (Random Forest)"),
    p("Ranked by mean decrease in impurity from the Random Forest:"),
    bullet("1st — Strike Differential (str_diff): The dominant predictor. Winners out-struck opponents by a median of +11 strikes — the clearest performance signal in the data."),
    bullet("2nd — Win Percentage Differential (win_pct_diff): Career win rate encapsulates cumulative skill and competition level, making it the strongest pre-fight signal."),
    bullet("3rd — Experience Differential (exp_diff): More experienced fighters show measurable advantages, particularly against significantly less experienced opponents."),
    bullet("4th — Reach Differential (reach_diff): Physical reach advantage correlates with winning, but is far weaker than performance-based measures."),
    bullet("5th/6th — Knockdown and Takedown Differentials: In-fight grappling and power metrics contribute but are partially collinear with the striking differential."),
    sp(2), pb(),

    // ══════════════════════════════════════════════════════════════════════
    // 7. CLUSTERING
    // ══════════════════════════════════════════════════════════════════════
    h1("7. Fighter Archetypes: K-Means Clustering"),
    divider(), sp(),

    img("fig4_clusters", 2950, 3111, 6.3),
    caption("Figure 3: Fighter Archetypes — PCA Projection, Elbow Curve, Style Profiles, Win Rates, Growth Trends"),

    h2("7.1  Methodology"),
    p("K-Means clustering (k=5, selected via elbow method) was applied to a feature matrix of per-fighter career averages: strikes per fight, takedowns per fight, knockdowns per fight, submission attempts per fight, finish method percentages (KO%, Sub%, Dec%), height, and reach. Features were median-imputed and standardized before clustering. PCA reduced the feature space to 2 dimensions for visualization (PC1 + PC2 explained ~41% of variance)."),
    p("The analysis included 1,215 fighters with a minimum of 5 career fights, ensuring statistically meaningful performance profiles."),
    sp(2),

    h2("7.2  Archetype Profiles"),
    tbl(
      ["Archetype", "Fighters", "Win %", "KO %", "Sub %", "Avg TD/Fight"],
      [
        ["Dominant Wrestlers",       "171", "74.9%", "18.2%", "20.9%", "2.62"],
        ["All-Round Athletes",       "309", "70.8%", "31.3%", "11.2%", "0.83"],
        ["Power Strikers",           "256", "69.9%", "61.7%", "14.9%", "0.60"],
        ["Submission Specialists",   "222", "69.7%", "26.0%", "42.5%", "1.02"],
        ["Decision Fighters",        "257", "68.6%", "19.3%", "14.2%", "0.89"],
      ],
      [2300, 1300, 1200, 1200, 1200, 1560]
    ),
    sp(2),

    h2("7.3  Key Insights from Clustering"),
    bullet("Dominant Wrestlers achieve the highest career win rate (74.9%), suggesting that elite takedown offense and ground control is the most consistent path to long-term success in MMA — consistent with the conventional wisdom that wrestling is the backbone of mixed martial arts."),
    bullet("Power Strikers have the most distinctive stylistic profile (61.7% KO rate) but a slightly lower average win rate than wrestlers, reflecting the boom-or-bust nature of knockout-dependent game plans."),
    bullet("Submission Specialists show a bi-modal distribution — the cluster includes both elite grapplers with very high win rates and journeyman fighters who attempt submissions unsuccessfully, pulling the average down."),
    bullet("Decision Fighters have the lowest average win rate (68.6%), which may reflect fighters who lack finishing ability and are therefore more susceptible to close decisions that could go either way."),
    bullet("All-Round Athletes form the largest cluster — reflecting that the modern UFC roster trends toward versatility rather than single-discipline specialization."),
    sp(2), pb(),

    // ══════════════════════════════════════════════════════════════════════
    // 8. PRE-FIGHT MODEL
    // ══════════════════════════════════════════════════════════════════════
    h1("8. Pre-Fight Prediction Model"),
    divider(), sp(),

    img("fig5_prefight", 2818, 2564, 6.3),
    caption("Figure 4: Pre-Fight vs. Full Model — ROC, Learning Curves, Calibration, Precision-Recall, Feature Importances"),

    h2("8.1  Motivation"),
    p("The full model (Section 6) uses in-fight statistics like strikes landed and knockdowns — data that only exists after the fight has occurred. While this demonstrates that fight outcomes are predictable from performance data, it is not useful for pre-fight prediction. A realistic betting or scouting tool must operate only on information available before the opening bell."),
    sp(2),

    h2("8.2  Pre-Fight Features"),
    bullet("height_diff — Physical reach advantage (inches)"),
    bullet("reach_diff — Arm length advantage (inches)"),
    bullet("win_pct_diff — Career win percentage differential"),
    bullet("exp_diff — Total career fights differential"),
    bullet("stance_f1 / stance_f2 — Encoded stances of both fighters"),
    sp(2),

    h2("8.3  Results"),
    tbl(
      ["Metric", "Pre-Fight Model", "Full Stats Model"],
      [
        ["Features Used",     "6 (physical + record)", "10 (inc. in-fight stats)"],
        ["Test Accuracy",     "65.5%",                  "86.8%"],
        ["Test AUC",          "0.722",                  "0.947"],
        ["Avg Precision",     "0.715",                  "—"],
        ["Model Type",        "Gradient Boosting",      "Gradient Boosting"],
        ["Practical Use",     "Pre-fight prediction",   "Post-fight analysis"],
      ],
      [2600, 3000, 3760]
    ),
    sp(2),

    h2("8.4  Analysis"),
    p("The pre-fight model's AUC of 0.722 represents a substantial improvement over random guessing (0.50) using only publicly available information. This means that approximately 72% of the time, the model correctly ranks the eventual winner as more likely to win than the loser — a meaningful signal for analysts, coaches, and researchers."),
    sp(),
    p("The learning curve analysis shows that model performance converges and stabilizes around 8,000–10,000 training examples, confirming the dataset is sufficiently large and that additional data would yield only marginal gains. The gap between training AUC (~0.74) and validation AUC (~0.72) is small, indicating the model is well-regularized without meaningful overfitting."),
    sp(),
    p("The calibration curve shows the model is well-calibrated in the middle probability range (0.3–0.7) but slightly overconfident at extremes — a common pattern for gradient boosting that could be corrected with Platt scaling in a production setting."),
    sp(),
    p("Win percentage differential is the dominant pre-fight feature (importance ~0.40), followed by experience differential (~0.25) and reach differential (~0.18). Stance and height contribute modestly, suggesting that raw physical measurements are far less predictive than competitive track record when in-fight statistics are unavailable."),
    sp(2), pb(),

    // ══════════════════════════════════════════════════════════════════════
    // 9. CONCLUSIONS
    // ══════════════════════════════════════════════════════════════════════
    h1("9. Conclusions & Recommendations"),
    divider(), sp(),

    h2("9.1  Summary of Findings"),
    bullet("Fight outcome prediction works. Machine learning models significantly outperform random chance both with and without in-fight statistics, demonstrating systematic patterns in UFC data."),
    bullet("Striking volume dominates. Winning the striking exchange (volume, not just accuracy) is the single strongest correlate of victory — more predictive than any physical attribute."),
    bullet("Career pedigree is the best pre-fight signal. When in-fight data is unavailable, win percentage differential is by far the most informative pre-fight predictor."),
    bullet("Reach matters, but minimally. Despite conventional wisdom, reach advantage accounts for only a small fraction of predictive power relative to performance history."),
    bullet("Wrestling wins fights. Dominant Wrestlers have the highest career win rate (74.9%) of any archetype — validating the sport's established wisdom that elite wrestling is the most reliable foundation for MMA success."),
    bullet("The sport is evolving. Finish rates have declined structurally from ~75% in 2000 to ~48–53% today as defensive sophistication has increased across the roster."),
    bullet("Southpaw advantage exists but is small. Switch stance fighters lead in win rate; Southpaws hold a slight edge over Orthodox — consistent with peer-reviewed sports science."),
    sp(2),

    h2("9.2  Limitations"),
    bullet("Temporal leakage risk: The full model uses in-fight statistics that are unavailable pre-fight. These are presented for analytical purposes only, not as a deployable prediction tool."),
    bullet("Missing physical data: ~20% of fighters lack height or reach measurements, particularly in older records (pre-2000). Median imputation was used but may introduce noise."),
    bullet("Career arc effects: The models treat a fighter's record as static. In reality, performance peaks and declines significantly over a career — a time-series model would capture this."),
    bullet("Stylistic matchup effects: Some fighter archetypes match up systematically better or worse against each other (e.g., wrestlers tend to dominate strikers). This interaction is not captured by scalar differentials."),
    bullet("Sample bias: Women's divisions are underrepresented relative to their current proportion of UFC events, potentially affecting cross-gender generalizability of findings."),
    sp(2),

    h2("9.3  Future Work"),
    bullet("Build an Elo/Glicko rating system to track dynamic fighter performance over time, replacing static win% with a true rating differential that captures form and opposition quality."),
    bullet("Apply natural language processing to referee stoppage narratives and fighter interviews for qualitative momentum signals."),
    bullet("Incorporate time-series LSTM/Transformer models to capture performance trajectory across a career."),
    bullet("Expand to include judging patterns per referee — significant variance exists in scoring tendencies that systematically affects close decision outcomes."),
    bullet("Build a live dashboard integrating UFC event data as fights are announced, generating automated pre-fight win probability predictions."),
    sp(2), pb(),

    // ══════════════════════════════════════════════════════════════════════
    // 10. REFERENCES
    // ══════════════════════════════════════════════════════════════════════
    h1("10. Technical Stack & References"),
    divider(), sp(),

    h3("Libraries & Tools"),
    kv_table([
      ["Language",            "Python 3.12"],
      ["Data Manipulation",   "pandas 2.x, numpy"],
      ["SQL Engine",          "SQLite (via Python sqlite3 module) — 4-table relational database"],
      ["Machine Learning",    "scikit-learn: LogisticRegression, RandomForestClassifier, GradientBoostingClassifier"],
      ["Clustering",          "scikit-learn: KMeans, PCA, StandardScaler, SimpleImputer"],
      ["Visualization",       "matplotlib, seaborn (dark theme dashboards)"],
      ["Model Evaluation",    "ROC-AUC, confusion_matrix, cross_val_score, calibration_curve, learning_curve, precision_recall_curve"],
      ["Document Generation", "docx.js v9.6.1 (Node.js)"],
      ["Dataset Source",      "Kaggle: UFC Fight Historical Data (ufcstats.com scrape)"],
    ]),
    sp(2),

    h3("References"),
    bullet("Pedregosa et al. (2011). Scikit-learn: Machine Learning in Python. JMLR 12, pp. 2825–2830."),
    bullet("Chen & Guestrin (2016). XGBoost: A Scalable Tree Boosting System. KDD 2016."),
    bullet("Friedman (2001). Greedy Function Approximation: A Gradient Boosting Machine. Annals of Statistics."),
    bullet("UFC Statistics Database — ufcstats.com (basis for Kaggle dataset scrape)."),
    bullet("Kaggle Dataset: UFC-Fight-Historical-Data — publicly available, sourced from ufcstats.com."),
    bullet("Breiman (2001). Random Forests. Machine Learning, 45(1), 5–32."),
    sp(3),

    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 480, after: 80 },
      children: [new TextRun({ text: "— End of Report —", size: 22, font:"Arial", italics: true, color: C.muted })] }),

  ]}]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync('/home/claude/UFC_Fight_Analytics_Final.docx', buffer);
  console.log('Final report saved.');
});
