<!DOCTYPE html>
<html lang="sv">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Bankbevakning – Företagserbjudanden</title>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --bg: #f8f7f4;
    --surface: #ffffff;
    --surface2: #f1efe8;
    --border: rgba(0,0,0,0.1);
    --border-strong: rgba(0,0,0,0.2);
    --text: #1a1a18;
    --text2: #5f5e5a;
    --text3: #888780;
    --accent: #0C447C;
    --success: #27500A;
    --warning: #633806;
    --danger: #791F1F;
    --info: #0C447C;
    --radius: 10px;
    --radius-sm: 6px;
  }

  @media (prefers-color-scheme: dark) {
    :root {
      --bg: #1a1a18;
      --surface: #242422;
      --surface2: #2c2c2a;
      --border: rgba(255,255,255,0.1);
      --border-strong: rgba(255,255,255,0.2);
      --text: #e8e6de;
      --text2: #b4b2a9;
      --text3: #888780;
    }
  }

  body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
         background: var(--bg); color: var(--text); font-size: 14px; line-height: 1.5; }

  header { background: var(--surface); border-bottom: 1px solid var(--border);
           padding: 16px 24px; display: flex; align-items: center;
           justify-content: space-between; flex-wrap: wrap; gap: 10px; }

  .logo { font-size: 17px; font-weight: 600; color: var(--text); letter-spacing: -0.3px; }

  .header-right { display: flex; align-items: center; gap: 12px; font-size: 12px; color: var(--text3); }

  .pulse { width: 7px; height: 7px; border-radius: 50%; background: #27ae60;
           animation: pulse 2.5s ease-in-out infinite; }
  @keyframes pulse { 0%,100%{opacity:1}50%{opacity:0.3} }

  .badge { display: inline-flex; align-items: center; gap: 5px; padding: 4px 10px;
           border-radius: 20px; font-size: 11px; font-weight: 500; white-space: nowrap; }
  .badge-green { background: #d4edda; color: #155724; }
  .badge-amber { background: #fff3cd; color: #856404; }
  .badge-red   { background: #f8d7da; color: #721c24; }
  .badge-gray  { background: var(--surface2); color: var(--text3); }

  @media (prefers-color-scheme: dark) {
    .badge-green { background: #1a3d22; color: #7fcf93; }
    .badge-amber { background: #3d2f0a; color: #e8a931; }
    .badge-red   { background: #3d1010; color: #e87a7a; }
  }

  main { max-width: 1280px; margin: 0 auto; padding: 20px 16px; }

  .alert-bar { display: flex; align-items: flex-start; gap: 12px; padding: 14px 18px;
               background: #fff3cd; border: 1px solid #ffc107; border-radius: var(--radius);
               margin-bottom: 20px; font-size: 13px; color: #664d03; }
  @media (prefers-color-scheme: dark) {
    .alert-bar { background: #3d2f0a; border-color: #856404; color: #e8c56a; }
  }
  .alert-icon { font-size: 16px; flex-shrink: 0; }

  .toolbar { display: flex; align-items: center; gap: 10px; flex-wrap: wrap;
             margin-bottom: 16px; }

  .tab-group { display: flex; gap: 3px; background: var(--surface2);
               border-radius: var(--radius-sm); padding: 3px; }
  .tab { padding: 6px 14px; border-radius: 5px; border: none; background: transparent;
         color: var(--text2); cursor: pointer; font-size: 13px; font-weight: 500; }
  .tab.active { background: var(--surface); color: var(--text);
                box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
  .tab:hover:not(.active) { color: var(--text); }

  .filter-chips { display: flex; gap: 6px; flex-wrap: wrap; }
  .chip { padding: 5px 12px; border-radius: 20px; border: 1px solid var(--border);
          background: var(--surface); color: var(--text2); cursor: pointer; font-size: 12px; }
  .chip.active { background: var(--accent); border-color: var(--accent); color: #fff; }
  .chip:hover:not(.active) { border-color: var(--border-strong); color: var(--text); }

  /* OVERVIEW CARDS */
  .overview-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 12px; }
  .bank-card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius);
               padding: 16px; cursor: pointer; transition: border-color 0.15s, box-shadow 0.15s; }
  .bank-card:hover { border-color: var(--border-strong); box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
  .bank-card-head { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; }
  .bank-avatar { width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center;
                 justify-content: center; font-size: 10px; font-weight: 700; flex-shrink: 0; }
  .bank-name { font-size: 14px; font-weight: 600; }
  .bank-type { font-size: 11px; color: var(--text3); }
  .bank-divider { height: 1px; background: var(--border); margin: 10px 0; }
  .bank-stat { display: flex; justify-content: space-between; align-items: baseline; margin-top: 5px; }
  .bank-stat-label { font-size: 11px; color: var(--text2); }
  .bank-stat-value { font-size: 12px; font-weight: 600; color: var(--text); }

  /* COMPARE TABLE */
  .tbl-wrap { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius);
              overflow: auto; }
  table { width: 100%; border-collapse: collapse; font-size: 12px; }
  thead th { position: sticky; top: 0; background: var(--surface2); padding: 9px 12px;
             font-size: 11px; font-weight: 600; color: var(--text2); text-align: left;
             border-bottom: 1px solid var(--border); white-space: nowrap; }
  thead th:first-child { min-width: 160px; width: 160px; }
  thead th:not(:first-child) { min-width: 130px; }
  tbody tr:hover td { background: var(--surface2); }
  tbody td { padding: 8px 12px; border-bottom: 1px solid var(--border); vertical-align: top;
             color: var(--text); line-height: 1.4; }
  tbody tr:last-child td { border-bottom: none; }
  .td-label { font-size: 11px; color: var(--text2); }
  .td-unknown { color: var(--text3); font-style: italic; }
  .td-yes { color: var(--success); font-weight: 500; }
  .td-no  { color: var(--danger); }

  /* NEWS */
  .news-list { display: flex; flex-direction: column; gap: 8px; }
  .news-item { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius);
               padding: 14px 16px; display: flex; gap: 12px; align-items: flex-start; }
  .news-avatar { width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center;
                 justify-content: center; font-size: 10px; font-weight: 700; flex-shrink: 0; }
  .news-body { flex: 1; min-width: 0; }
  .news-title { font-size: 13px; font-weight: 600; color: var(--text); margin-bottom: 3px; }
  .news-desc { font-size: 12px; color: var(--text2); }
  .news-meta { margin-top: 6px; display: flex; align-items: center; gap: 8px; }
  .news-date { font-size: 11px; color: var(--text3); }
  .news-link { font-size: 11px; color: var(--info); text-decoration: none; }
  .news-link:hover { text-decoration: underline; }

  .empty { padding: 48px; text-align: center; color: var(--text3); font-size: 13px; }
  .spinner { display: inline-block; width: 20px; height: 20px; border: 2px solid var(--border);
             border-top-color: var(--accent); border-radius: 50%; animation: spin 0.7s linear infinite; }
  @keyframes spin { to { transform: rotate(360deg); } }

  .loading-state { display: flex; align-items: center; justify-content: center;
                   gap: 12px; padding: 60px; color: var(--text2); }

  footer { text-align: center; padding: 24px; font-size: 11px; color: var(--text3); }
  footer a { color: var(--info); text-decoration: none; }
</style>
</head>
<body>

<header>
  <div class="logo">Bankbevakning</div>
  <div class="header-right">
    <span id="scan-date" style="display:none">
      <span class="pulse"></span>
      Senast skannad: <span id="scan-date-val">—</span>
    </span>
    <span id="diff-badge"></span>
  </div>
</header>

<main>
  <div id="alert-container"></div>

  <div class="toolbar">
    <div class="tab-group">
      <button class="tab active" onclick="setView('overview', this)">Översikt</button>
      <button class="tab" onclick="setView('compare', this)">Jämför</button>
      <button class="tab" onclick="setView('changes', this)">Ändringar</button>
    </div>
    <div class="filter-chips" id="bank-chips"></div>
  </div>

  <div id="view-container">
    <div class="loading-state"><span class="spinner"></span> Laddar bankdata…</div>
  </div>
</main>

<footer>
  Data verifierad mot bankernas officiella webbplatser · Räntor publiceras ej (individuella) ·
  <a href="https://github.com/YOUR_USER/bankbevakning" target="_blank">Källkod på GitHub</a>
</footer>

<script>
let DATA = null;
let DIFF = null;
let currentView = 'overview';
let activeBanks = new Set();

const COMPARE_CATEGORIES = [
  {
    id: 'konto', label: 'Konton & avgifter',
    fields: ['monthly_fee', 'setup_fee', 'onboarding_digital'],
  },
  {
    id: 'kredit', label: 'Krediter & finansiering',
    fields: ['credit_limit', 'factoring', 'leasing', 'loan'],
  },
  {
    id: 'betalning', label: 'Betalningar',
    fields: ['swish', 'swish_fee', 'ecommerce'],
  },
  {
    id: 'digital', label: 'Digitala verktyg',
    fields: ['platform', 'bookkeeping_integration', 'financial_overview',
             'cashflow_tool', 'automatic_vat', 'expense_categorization',
             'dedicated_advisor'],
  },
  {
    id: 'intl', label: 'Internationellt',
    fields: ['trade_finance', 'fx_tool', 'nordic_presence', 'international'],
  },
  {
    id: 'extra', label: 'Mervärde',
    fields: ['pension', 'sustainability_tool', 'combined_offering',
             'insurance_discount', 'trustpilot'],
  },
];

async function init() {
  try {
    const [dataResp, diffResp] = await Promise.all([
      fetch('data/data.json?v=' + Date.now()),
      fetch('data/diff.json?v=' + Date.now()),
    ]);
    DATA = await dataResp.json();
    DIFF = diffResp.ok ? await diffResp.json() : null;
  } catch (e) {
    document.getElementById('view-container').innerHTML =
      '<div class="empty">Kunde inte ladda bankdata. Kör skrapan för att generera data.json.</div>';
    return;
  }

  activeBanks = new Set(Object.keys(DATA.banks));

  // Header
  const dateEl = document.getElementById('scan-date');
  dateEl.style.display = 'flex';
  document.getElementById('scan-date-val').textContent = DATA.scan_date;

  // Diff-badge
  if (DIFF && DIFF.changes_count > 0) {
    document.getElementById('diff-badge').innerHTML =
      `<span class="badge badge-amber">${DIFF.changes_count} förändring${DIFF.changes_count > 1 ? 'ar' : ''} sedan förra skanningen</span>`;

    document.getElementById('alert-container').innerHTML = `
      <div class="alert-bar">
        <span class="alert-icon">⚠</span>
        <div>
          <strong>${DIFF.changes_count} förändring${DIFF.changes_count > 1 ? 'ar' : ''} detekterade</strong> sedan förra skanningen (${DIFF.scan_date}).
          <a href="#" onclick="setView('changes', document.querySelector('.tab:nth-child(3)'));return false"
             style="color:inherit;text-decoration:underline;margin-left:4px">Visa detaljer →</a>
        </div>
      </div>`;
  }

  // Bank-chips
  const chips = document.getElementById('bank-chips');
  chips.innerHTML = Object.values(DATA.banks).map(b => `
    <div class="chip active" onclick="toggleBank('${b.id}', this)"
         style="border-color:${b.color}20">
      ${b.name}
    </div>`).join('');

  render();
}

function toggleBank(id, el) {
  if (activeBanks.has(id)) {
    if (activeBanks.size <= 2) return;
    activeBanks.delete(id);
    el.classList.remove('active');
  } else {
    activeBanks.add(id);
    el.classList.add('active');
  }
  render();
}

function setView(v, el) {
  currentView = v;
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  el.classList.add('active');
  render();
}

function render() {
  const container = document.getElementById('view-container');
  const banks = Object.values(DATA.banks).filter(b => activeBanks.has(b.id));
  if (currentView === 'overview') container.innerHTML = renderOverview(banks);
  else if (currentView === 'compare') container.innerHTML = renderCompare(banks);
  else if (currentView === 'changes') container.innerHTML = renderChanges();
}

function renderOverview(banks) {
  const cards = banks.map(b => {
    const fee = b.fields.monthly_fee?.value || '—';
    const onb = b.fields.onboarding_digital?.value || '—';
    const adv = b.fields.dedicated_advisor?.value || '—';
    return `
      <div class="bank-card" onclick="setView('compare', document.querySelector('.tab:nth-child(2)'))">
        <div class="bank-card-head">
          <div class="bank-avatar" style="background:${b.bg};color:${b.color}">${b.id.substring(0,2).toUpperCase()}</div>
          <div>
            <div class="bank-name">${b.name}</div>
            <div class="bank-type">${b.type}</div>
          </div>
        </div>
        <div class="bank-divider"></div>
        <div class="bank-stat">
          <span class="bank-stat-label">Månadsavgift</span>
          <span class="bank-stat-value">${fee.split('(')[0].trim()}</span>
        </div>
        <div class="bank-stat">
          <span class="bank-stat-label">Digital onboarding</span>
          <span class="bank-stat-value" style="font-size:11px">${onb.substring(0,20)}</span>
        </div>
        <div class="bank-stat">
          <span class="bank-stat-label">Rådgivare</span>
          <span class="bank-stat-value" style="font-size:11px">${adv.substring(0,12)}</span>
        </div>
        <div style="margin-top:10px">
          ${Object.values(b.urls).slice(0,1).map(u =>
            `<a href="${u.startsWith('http') ? u : 'https://'+u}" target="_blank"
                style="font-size:11px;color:var(--info);text-decoration:none">
               Officiell webbsida →</a>`).join('')}
        </div>
      </div>`;
  }).join('');

  return `
    <div class="overview-grid">${cards}</div>
    <div style="margin-top:16px;padding:12px 16px;background:var(--surface);
                border:1px solid var(--border);border-radius:var(--radius);
                font-size:12px;color:var(--text2)">
      Alla avgifter verifierade mot bankernas officiella webbplatser (maj 2025).
      Räntor på kredit och inlåning publiceras inte som listpriser – de är individuella.
      Klicka på ett kort för att se detaljerad jämförelse.
    </div>`;
}

function renderCompare(banks) {
  const rows = COMPARE_CATEGORIES.flatMap(cat => {
    const fieldRows = cat.fields
      .map(fid => {
        const hasSomeValue = banks.some(b => b.fields[fid]?.value);
        if (!hasSomeValue) return null;

        const labelSrc = banks.find(b => b.fields[fid])?.fields[fid]?.label || fid;
        const cells = banks.map(b => {
          const field = b.fields[fid];
          if (!field) return '<td class="td-unknown">—</td>';
          const v = field.value || '';
          const isYes = v.toLowerCase().startsWith('ja');
          const isNo = v.toLowerCase() === 'nej';
          const isUnknown = v.toLowerCase().includes('okänt') || v === '—' || !v;
          let cls = isYes ? 'td-yes' : isNo ? 'td-no' : isUnknown ? 'td-unknown' : '';
          const unit = field.unit ? ' ' + field.unit : '';
          return `<td class="${cls}">${v}${unit}</td>`;
        }).join('');

        return `<tr><td class="td-label">${labelSrc}</td>${cells}</tr>`;
      })
      .filter(Boolean);

    if (!fieldRows.length) return [];

    const catHeader = `<tr><td colspan="${banks.length + 1}"
      style="background:var(--surface2);padding:6px 12px;font-size:10px;font-weight:700;
             color:var(--text3);text-transform:uppercase;letter-spacing:0.6px">
      ${cat.label}</td></tr>`;

    return [catHeader, ...fieldRows];
  }).join('');

  const headers = banks.map(b =>
    `<th style="text-align:left">
       <div style="display:flex;align-items:center;gap:6px">
         <div style="width:18px;height:18px;border-radius:50%;background:${b.bg};
                     color:${b.color};font-size:8px;font-weight:700;
                     display:flex;align-items:center;justify-content:center;flex-shrink:0">
           ${b.id.substring(0,2).toUpperCase()}
         </div>
         ${b.name}
       </div>
     </th>`
  ).join('');

  return `
    <div class="tbl-wrap">
      <table>
        <thead><tr><th>Tjänst / villkor</th>${headers}</tr></thead>
        <tbody>${rows}</tbody>
      </table>
    </div>
    <div style="margin-top:10px;font-size:11px;color:var(--text3)">
      Grön text = bekräftat Ja · Röd text = bekräftat Nej · Kursiv = ej verifierat
    </div>`;
}

function renderChanges() {
  if (!DIFF || !DIFF.changes || DIFF.changes.length === 0) {
    return `<div class="empty">Inga förändringar detekterades vid senaste skanningen (${DIFF?.scan_date || '—'}).</div>`;
  }

  const items = DIFF.changes.map(c => {
    const bank = DATA?.banks[c.bank_id];
    return `
      <div class="news-item">
        <div class="news-avatar" style="background:${bank?.bg || '#eee'};color:${bank?.color || '#333'}">
          ${c.bank_id.substring(0,2).toUpperCase()}
        </div>
        <div class="news-body">
          <div class="news-title">${c.bank_name} – ${c.field_label || c.type}</div>
          ${c.old_value ? `
            <div class="news-desc">
              <span style="color:var(--danger);text-decoration:line-through">${c.old_value}</span>
              <span style="margin:0 6px">→</span>
              <span style="color:var(--success)">${c.new_value}</span>
            </div>` : `<div class="news-desc">${c.message}</div>`}
          <div class="news-meta">
            <span class="news-date">${DIFF.scan_date}</span>
            ${bank ? `<a class="news-link" href="${Object.values(bank.urls)[0]}" target="_blank">Källa →</a>` : ''}
          </div>
        </div>
      </div>`;
  }).join('');

  return `
    <div style="margin-bottom:12px;font-size:13px;color:var(--text2)">
      ${DIFF.changes_count} förändring${DIFF.changes_count > 1 ? 'ar' : ''} sedan förra skanningen (${DIFF.scan_date})
    </div>
    <div class="news-list">${items}</div>`;
}

init();
</script>
</body>
</html>
