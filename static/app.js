let state = null;
let presets = {};
let records = [];
let currentSection = 0;
let selectedFieldRow = -1;
let selectedSectionRow = -1;
let selectedSectionColumn = -1;

const $ = (id) => document.getElementById(id);
const status = (msg) => { $('status').innerHTML = msg || ''; };
const clone = (x) => JSON.parse(JSON.stringify(x));

function stop(e) {
  e.preventDefault();
  e.stopPropagation();
}

async function api(url, opts = {}) {
  const res = await fetch(url, opts);
  if (!res.ok) {
    let msg = res.statusText;
    try {
      msg = (await res.json()).detail || msg;
    } catch (e) {}
    throw new Error(msg);
  }
  return res.json();
}

/*
  PRODUCT SPECIFICATION MODE CHECK

  This checks whether the selected document title is Product Specification.
  If yes, the application should not show the Results column.
*/
function isProductSpecificationMode() {
  const titleFromState = state ? String(state.document_title || "") : "";
  const titleFromInput = $("documentTitle") ? String($("documentTitle").value || "") : "";
  const title = (titleFromInput || titleFromState).toUpperCase();

  return title.includes("PRODUCT SPECIFICATION");
}

/*
  REMOVE RESULTS COLUMN FOR PRODUCT SPECIFICATION SHEET

  Example:
  Before:
  Parameter | Specification | Results | Test Methods

  After:
  Parameter | Specification | Test Methods
*/
function normalizeSectionsForDocumentTitle() {
  if (!state || !state.sections) return;

  if (!isProductSpecificationMode()) return;

  state.sections = state.sections.map((section) => {
    const columns = section.columns || [];

    const resultsIndex = columns.findIndex((col) =>
      String(col).trim().toLowerCase() === "results"
    );

    if (resultsIndex === -1) return section;

    const newColumns = columns.filter((_, index) => index !== resultsIndex);

    const newRows = (section.rows || []).map((row) => {
      const safeRow = row || [];
      return safeRow.filter((_, index) => index !== resultsIndex);
    });

    return {
      ...section,
      columns: newColumns,
      rows: newRows,
    };
  });
}

/*
  DEFAULT COLUMNS FOR NEW SECTION

  COA:
  Parameter | Specification | Results | Test Methods

  Product Specification:
  Parameter | Specification | Test Methods
*/
function defaultSectionColumns() {
  if (isProductSpecificationMode()) {
    return ["Parameter", "Specification", "Test Methods"];
  }

  return ["Parameter", "Specification", "Results", "Test Methods"];
}

function renderRecords() {
  const sel = $("recordSelect");
  sel.innerHTML = '<option value="">Select saved record...</option>';

  records.forEach((r) => {
    const opt = document.createElement("option");
    opt.value = r.id;
    opt.textContent = `#${r.id} | ${r.display_name || "Untitled"}`;
    sel.appendChild(opt);
  });
}

function renderSetup() {
  const title = state.document_title || "CERTIFICATE OF ANALYSIS";

  $("documentTitle").value = title.toUpperCase().includes("PRODUCT SPECIFICATION")
    ? "PRODUCT SPECIFICATION SHEET"
    : "CERTIFICATE OF ANALYSIS";

  $("website").value = state.website || "www.medikonda.com";
  $("templatePreset").value = state.template_name || Object.keys(presets)[0] || "";
}

function readSetup() {
  state.document_title = $("documentTitle").value || "CERTIFICATE OF ANALYSIS";
  state.website = $("website").value.trim() || "www.medikonda.com";
  state.border_color = "#6dbb43";
  state.logo_width_mm = "66";
  state.logo_height_mm = "24";
  state.logo_path = "assets/medikonda_logo.png";
  state.template_name = $("templatePreset").value;
  state.brand_name = "medikonda";
  state.footer_left_1 = "Electronic document valid without signature.";
  state.footer_left_2 = "Copyright © All rights reserved.";
  state.footer_right_1 = "Department of Quality Control";
  state.footer_right_2 = state.website || "www.medikonda.com";
}

function moveArrayItem(arr, from, to) {
  if (!arr || from < 0 || to < 0 || from >= arr.length || to >= arr.length) {
    return false;
  }

  const item = arr.splice(from, 1)[0];
  arr.splice(to, 0, item);
  return true;
}

function makeMiniButton(label, title, onClick) {
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "mini-move-btn";
  btn.textContent = label;
  btn.title = title;

  btn.addEventListener("mousedown", stop);
  btn.addEventListener("click", (e) => {
    stop(e);
    onClick();
  });

  return btn;
}

function renderFields() {
  const tbody = $("fieldsTable").querySelector("tbody");
  tbody.innerHTML = "";

  (state.product_fields || []).forEach((row, idx) => {
    const tr = document.createElement("tr");

    if (idx === selectedFieldRow) {
      tr.classList.add("selected");
    }

    const handleTd = document.createElement("td");
    handleTd.className = "handle-cell";

    const handle = document.createElement("button");
    handle.type = "button";
    handle.className = "six-dot-handle";
    handle.title = "Select this field row for moving";
    handle.innerHTML = "⋮⋮";

    handle.addEventListener("mousedown", stop);
    handle.addEventListener("click", (e) => {
      stop(e);
      selectedFieldRow = idx;
      renderFields();
    });

    handleTd.appendChild(handle);

    if (idx === selectedFieldRow) {
      const actions = document.createElement("span");
      actions.className = "move-mini-actions";
      actions.appendChild(makeMiniButton("↑", "Move field up", () => moveProductField(-1)));
      actions.appendChild(makeMiniButton("↓", "Move field down", () => moveProductField(1)));
      handleTd.appendChild(actions);
    }

    tr.appendChild(handleTd);

    for (let c = 0; c < 2; c++) {
      const td = document.createElement("td");

      const input = document.createElement("input");
      input.value = row[c] || "";

      input.onfocus = () => {
        selectedFieldRow = idx;
      };

      input.oninput = () => {
        state.product_fields[idx][c] = input.value;
      };

      td.appendChild(input);
      tr.appendChild(td);
    }

    tbody.appendChild(tr);
  });
}

function moveProductField(direction) {
  const from = selectedFieldRow;
  const to = from + direction;

  if (moveArrayItem(state.product_fields, from, to)) {
    selectedFieldRow = to;
    renderFields();
  }
}

function renderTabs() {
  const tabs = $("sectionTabs");
  tabs.innerHTML = "";

  (state.sections || []).forEach((s, idx) => {
    const div = document.createElement("div");
    div.className = "tab" + (idx === currentSection ? " active" : "");
    div.textContent = s.title || `Section ${idx + 1}`;

    div.onclick = () => {
      currentSection = idx;
      selectedSectionRow = -1;
      selectedSectionColumn = -1;
      renderSections();
    };

    tabs.appendChild(div);
  });
}

function renderSectionEditor() {
  const wrap = $("sectionEditor");
  wrap.innerHTML = "";

  if (!state.sections || !state.sections.length) return;

  const sec = state.sections[currentSection];
  sec.columns = sec.columns || ["Column 1"];
  sec.rows = sec.rows || [];

  const table = document.createElement("table");
  table.className = "editable-table";

  const thead = document.createElement("thead");
  const hr = document.createElement("tr");

  const rowHandleHead = document.createElement("th");
  rowHandleHead.className = "handle-head";
  rowHandleHead.textContent = "Move";
  hr.appendChild(rowHandleHead);

  sec.columns.forEach((h, c) => {
    const th = document.createElement("th");

    if (c === selectedSectionColumn) {
      th.classList.add("selected-column");
    }

    const headWrap = document.createElement("div");
    headWrap.className = "column-head-wrap";

    const handle = document.createElement("button");
    handle.type = "button";
    handle.className = "six-dot-handle column-handle";
    handle.title = "Select this column for moving";
    handle.innerHTML = "⋮⋮";

    handle.addEventListener("mousedown", stop);
    handle.addEventListener("click", (e) => {
      stop(e);
      selectedSectionColumn = c;
      selectedSectionRow = -1;
      renderSectionEditor();
    });

    headWrap.appendChild(handle);

    const label = document.createElement("span");
    label.textContent = h || `Column ${c + 1}`;
    headWrap.appendChild(label);

    if (c === selectedSectionColumn) {
      const actions = document.createElement("span");
      actions.className = "move-mini-actions";
      actions.appendChild(makeMiniButton("←", "Move column left", () => moveSectionColumn(-1)));
      actions.appendChild(makeMiniButton("→", "Move column right", () => moveSectionColumn(1)));
      headWrap.appendChild(actions);
    }

    th.appendChild(headWrap);
    hr.appendChild(th);
  });

  thead.appendChild(hr);
  table.appendChild(thead);

  const tbody = document.createElement("tbody");

  sec.rows.forEach((row, r) => {
    const tr = document.createElement("tr");

    if (r === selectedSectionRow) {
      tr.classList.add("selected");
    }

    const handleTd = document.createElement("td");
    handleTd.className = "handle-cell";

    const handle = document.createElement("button");
    handle.type = "button";
    handle.className = "six-dot-handle";
    handle.title = "Select this row for moving";
    handle.innerHTML = "⋮⋮";

    handle.addEventListener("mousedown", stop);
    handle.addEventListener("click", (e) => {
      stop(e);
      selectedSectionRow = r;
      selectedSectionColumn = -1;
      renderSectionEditor();
    });

    handleTd.appendChild(handle);

    if (r === selectedSectionRow) {
      const actions = document.createElement("span");
      actions.className = "move-mini-actions";
      actions.appendChild(makeMiniButton("↑", "Move row up", () => moveSectionRow(-1)));
      actions.appendChild(makeMiniButton("↓", "Move row down", () => moveSectionRow(1)));
      handleTd.appendChild(actions);
    }

    tr.appendChild(handleTd);

    for (let c = 0; c < sec.columns.length; c++) {
      const td = document.createElement("td");

      if (c === selectedSectionColumn) {
        td.classList.add("selected-column");
      }

      const input = document.createElement("input");
      input.value = row[c] || "";

      input.onfocus = () => {
        selectedSectionRow = r;
      };

      input.oninput = () => {
        sec.rows[r][c] = input.value;
      };

      td.appendChild(input);
      tr.appendChild(td);
    }

    tbody.appendChild(tr);
  });

  table.appendChild(tbody);
  wrap.appendChild(table);
}

function moveSectionRow(direction) {
  const sec = state.sections[currentSection];
  if (!sec) return;

  const from = selectedSectionRow;
  const to = from + direction;

  if (moveArrayItem(sec.rows, from, to)) {
    selectedSectionRow = to;
    renderSectionEditor();
  }
}

function moveSectionColumn(direction) {
  const sec = state.sections[currentSection];
  if (!sec) return;

  const from = selectedSectionColumn;
  const to = from + direction;

  if (from < 0 || to < 0 || from >= sec.columns.length || to >= sec.columns.length) {
    return;
  }

  [sec.columns[from], sec.columns[to]] = [sec.columns[to], sec.columns[from]];

  sec.rows = sec.rows.map((row) => {
    const copy = row.slice();

    while (copy.length < sec.columns.length) {
      copy.push("");
    }

    [copy[from], copy[to]] = [copy[to], copy[from]];
    return copy;
  });

  selectedSectionColumn = to;
  renderSectionEditor();
}

function renderSections() {
  renderTabs();
  renderSectionEditor();
}

function renderAll() {
  renderSetup();
  renderFields();
  renderSections();
}

function collectState() {
  readSetup();
  normalizeSectionsForDocumentTitle();
  return clone(state);
}

async function init() {
  const data = await api("/api/bootstrap");

  presets = data.template_presets;
  records = data.records || [];
  state = data.default_data;

  const presetSel = $("templatePreset");
  presetSel.innerHTML = "";

  Object.keys(presets).forEach((name) => {
    const opt = document.createElement("option");
    opt.value = name;
    opt.textContent = name;
    presetSel.appendChild(opt);
  });

  renderRecords();
  renderAll();

  status("Ready. Select a preset, edit fields/sections, then generate PDF. Use the ⋮⋮ handles to move fields, rows, and columns.");
}

$("templatePreset").onchange = () => {
  const name = $("templatePreset").value;

  if (!presets[name]) return;

  if (!confirm("Apply this template preset? Current unsaved fields/sections will be replaced.")) {
    renderSetup();
    return;
  }

  const base = collectState();
  state = Object.assign(base, clone(presets[name]));
  state.template_name = name;

  normalizeSectionsForDocumentTitle();

  currentSection = 0;
  selectedFieldRow = -1;
  selectedSectionRow = -1;
  selectedSectionColumn = -1;

  renderAll();
};

$("documentTitle").onchange = () => {
  readSetup();
  normalizeSectionsForDocumentTitle();

  selectedSectionRow = -1;
  selectedSectionColumn = -1;

  renderSections();

  if (isProductSpecificationMode()) {
    status("Product Specification Sheet mode applied. Results column removed from application tables.");
  } else {
    status("Certificate of Analysis mode applied.");
  }
};

$("newBtn").onclick = async () => {
  const data = await api("/api/bootstrap");

  state = data.default_data;

  currentSection = 0;
  selectedFieldRow = -1;
  selectedSectionRow = -1;
  selectedSectionColumn = -1;

  renderAll();
  status("New document started.");
};

$("saveBtn").onclick = async () => {
  try {
    const res = await api("/api/save", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(collectState()),
    });

    state = res.record;
    records = res.records;

    renderRecords();
    renderAll();

    status(`Saved record #${res.record_id}.`);
  } catch (e) {
    status("Save error: " + e.message);
  }
};

$("generateBtn").onclick = async () => {
  try {
    status("Generating PDF and uploading to Google Drive...");

    const res = await api("/api/generate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(collectState()),
    });

    let message = "";

    if (res.drive_url) {
      message = `
        <strong>Your PDF has been uploaded on the Drive - COA & SPECS PDF GENERATOR.</strong><br>
        PDF generated:
        <a href="${res.download_url}">Download ${res.file_name}</a>
        |
        <a href="${res.open_url}" target="_blank">Open preview</a>
        |
        <a href="${res.drive_url}" target="_blank">Open in Google Drive</a>
      `;
    } else {
      message = `
        <strong>PDF generated successfully, but Google Drive upload was not completed.</strong><br>
        PDF generated:
        <a href="${res.download_url}">Download ${res.file_name}</a>
        |
        <a href="${res.open_url}" target="_blank">Open preview</a>
      `;

      if (res.drive_error) {
        message += `<br><span style="color:#b42318;">Drive upload error: ${res.drive_error}</span>`;
      }
    }

    status(message);
    window.open(res.open_url, "_blank");
  } catch (e) {
    status("PDF error: " + e.message);
  }
};

$("recordSelect").onchange = async () => {
  const id = $("recordSelect").value;
  if (!id) return;

  const res = await api(`/api/records/${id}`);

  state = res.record;

  normalizeSectionsForDocumentTitle();

  currentSection = 0;
  selectedFieldRow = -1;
  selectedSectionRow = -1;
  selectedSectionColumn = -1;

  renderAll();

  status(`Loaded record #${id}.`);
};

$("addFieldBtn").onclick = () => {
  state.product_fields.push(["New Field", ""]);
  selectedFieldRow = state.product_fields.length - 1;
  renderFields();
};

$("removeFieldBtn").onclick = () => {
  if (selectedFieldRow >= 0) {
    state.product_fields.splice(selectedFieldRow, 1);
    selectedFieldRow = -1;
    renderFields();
  }
};

$("addSectionBtn").onclick = () => {
  const title = prompt("Section name:", "New Section");
  if (!title) return;

  const columns = defaultSectionColumns();

  state.sections.push({
    title,
    columns,
    rows: [new Array(columns.length).fill("")],
  });

  currentSection = state.sections.length - 1;
  selectedSectionRow = -1;
  selectedSectionColumn = -1;

  renderSections();
};

$("removeSectionBtn").onclick = () => {
  if (!state.sections.length) return;
  if (!confirm("Remove current section?")) return;

  state.sections.splice(currentSection, 1);

  currentSection = Math.max(0, currentSection - 1);
  selectedSectionRow = -1;
  selectedSectionColumn = -1;

  renderSections();
};

$("renameSectionBtn").onclick = () => {
  const sec = state.sections[currentSection];
  if (!sec) return;

  const title = prompt("Section name:", sec.title);

  if (title) {
    sec.title = title;
    renderSections();
  }
};

$("addRowBtn").onclick = () => {
  const sec = state.sections[currentSection];
  if (!sec) return;

  sec.rows.push(new Array(sec.columns.length).fill(""));

  selectedSectionRow = sec.rows.length - 1;
  selectedSectionColumn = -1;

  renderSectionEditor();
};

$("removeRowBtn").onclick = () => {
  const sec = state.sections[currentSection];

  if (sec && selectedSectionRow >= 0) {
    sec.rows.splice(selectedSectionRow, 1);
    selectedSectionRow = -1;
    renderSectionEditor();
  }
};

$("addColumnBtn").onclick = () => {
  const sec = state.sections[currentSection];
  if (!sec) return;

  sec.columns.push(`Column ${sec.columns.length + 1}`);
  sec.rows.forEach((r) => r.push(""));

  selectedSectionColumn = sec.columns.length - 1;

  renderSections();
};

$("removeColumnBtn").onclick = () => {
  const sec = state.sections[currentSection];

  if (!sec || sec.columns.length <= 1) return;

  const index = selectedSectionColumn >= 0 ? selectedSectionColumn : sec.columns.length - 1;

  sec.columns.splice(index, 1);
  sec.rows.forEach((r) => r.splice(index, 1));

  selectedSectionColumn = -1;

  renderSections();
};

$("editColumnsBtn").onclick = () => {
  const sec = state.sections[currentSection];
  if (!sec) return;

  const txt = prompt("Enter column names separated by comma:", sec.columns.join(", "));
  if (!txt) return;

  const cols = txt
    .split(",")
    .map((x) => x.trim())
    .filter(Boolean);

  if (!cols.length) return;

  sec.columns = cols;

  sec.rows = sec.rows.map((r) => {
    const nr = r.slice(0, cols.length);

    while (nr.length < cols.length) {
      nr.push("");
    }

    return nr;
  });

  normalizeSectionsForDocumentTitle();

  selectedSectionColumn = -1;

  renderSections();
};

// Logo upload is disabled in the final branded version; Medikonda logo is fixed for consistency.

init().catch((e) => status("Startup error: " + e.message));