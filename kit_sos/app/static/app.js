/* Kit SOS — interface (JavaScript simples, sem dependências) */
(() => {
  "use strict";

  // ------------------------------------------------------------------
  // Textos (PT-PT e EN)
  // ------------------------------------------------------------------
  const I18N = {
    pt: {
      items_n: (n) => (n === 1 ? "1 artigo" : `${n} artigos`),
      add: "Adicionar", settings: "Definições",
      st_total: "Todos", st_soon: "A expirar", st_expired: "Expirados", st_missing: "Em falta",
      search: "Procurar", group_category: "Categoria", group_location: "Local", group_expiry: "Validade",
      no_category: "Sem categoria", no_location: "Sem local",
      sec_expired: "Expirados", sec_soon: (d) => `Nos próximos ${d} dias`, sec_later: "Mais tarde",
      sec_none: "Sem validade", sec_missing: "Em falta",
      showing: "A mostrar:", show_all: "Ver todos",
      expiry: "Validade", no_expiry: "Sem validade",
      d_today: "Hoje", d_tomorrow: "Amanhã", d_in: (n) => `${n} dias`, d_expired: "Expirado",
      d_expired_ago: (n) => (n === 1 ? "Expirou ontem" : `Expirou há ${n} dias`),
      missing: "Em falta", low: "Abaixo do mínimo", low_short: "Abaixo do mín.",
      empty_title: "Ainda não há artigos", empty_text: "Adiciona o primeiro artigo do kit ou importa tudo o que tens no Grocy.",
      empty_add: "Adicionar artigo", empty_import: "Importar do Grocy",
      nores_title: "Nada encontrado", nores_text: "Tenta outra pesquisa ou limpa os filtros.",
      new_item: "Novo artigo", edit_item: "Editar artigo", cancel: "Cancelar", save: "Guardar", done: "OK",
      f_name: "Nome", f_name_ph: "Ex.: Água 1,5 L",
      g_qty: "Quantidade", f_qty: "Quantidade", f_unit: "Unidade", f_min: "Mínimo", f_min_ph: "Opcional",
      g_org: "Organização", f_category: "Categoria", f_location: "Local", none: "Nenhuma", none_m: "Nenhum",
      new_category: "＋ Nova categoria…", new_location: "＋ Novo local…", new_unit: "＋ Nova unidade…",
      g_expiry: "Validade", ex_none: "Sem validade", ex_month: "Mês e ano", ex_day: "Data exata",
      f_month: "Mês", f_year: "Ano", f_date: "Data",
      ex_month_foot: "Quando só há mês e ano, conta como dia 01 desse mês.",
      ex_none_foot: "Este artigo não tem data de validade.",
      ex_day_foot: "",
      notify_foot: (d) => `Recebes um aviso ${d} dias antes.`,
      g_notes: "Notas", f_notes_ph: "Ex.: trocar as pilhas da lanterna",
      duplicate: "Duplicar (novo lote)", delete_item: "Apagar artigo",
      confirm_delete: "Apagar este artigo?", confirm_delete_text: (n) => `“${n}” vai ser apagado. Não dá para desfazer.`,
      delete: "Apagar",
      saved: "Guardado", deleted: "Apagado", created: "Adicionado",
      prompt_category: "Nova categoria", prompt_location: "Novo local", prompt_unit: "Nova unidade",
      prompt_name_ph: "Nome", create: "Criar",
      s_title: "Definições", tab_lists: "Listas", tab_grocy: "Grocy", tab_notify: "Avisos", tab_backup: "Cópia",
      lists_categories: "Categorias", lists_locations: "Locais", lists_units: "Unidades",
      add_category: "Adicionar categoria", add_location: "Adicionar local", add_unit: "Adicionar unidade",
      plural_ph: "Plural", usage: (n) => (n === 1 ? "1 artigo" : `${n} artigos`),
      lists_foot: "Toca no nome para mudar. As alterações ficam guardadas quando sais do campo.",
      confirm_del_lookup: "Apagar?", confirm_del_lookup_text: (n, c) => c ? `“${n}” está em ${c} artigo(s). Esses artigos ficam sem esta opção.` : `“${n}” vai ser apagado.`,
      grocy_intro: "Copia todos os produtos, lotes, validades, categorias, locais e unidades do Grocy.",
      grocy_url: "Endereço", grocy_key: "Chave API", grocy_key_ph: "Grocy → Gerir chaves API",
      grocy_foot: "No Home Assistant o endereço normal é http://a0d7b954-grocy. Se não der, experimenta o IP interno do Grocy (ex.: http://172.30.33.6).",
      grocy_check: "Verificar ligação", grocy_import: "Importar e substituir tudo",
      grocy_found: "Encontrado no Grocy", gs_products: "Produtos", gs_items: "Artigos a criar", gs_with_expiry: "Com validade",
      gs_without_stock: "Sem stock (ficam “Em falta”)", gs_categories: "Categorias", gs_locations: "Locais", gs_units: "Unidades",
      gs_inactive: "Inativos (ignorados)",
      grocy_confirm: "Substituir tudo?", grocy_confirm_text: (n) => `Os ${n} artigos atuais do Kit SOS vão ser apagados e trocados pelos do Grocy.`,
      grocy_done: (n) => `Importados ${n} artigos`,
      n_state: "Avisos", n_on: "Ligados", n_off: "Desligados", n_days: "Antecedência", n_days_v: (d) => `${d} dias`,
      n_time: "Hora do aviso", n_service: "Serviço", n_ha: "Ligação ao HA", n_ha_ok: "OK", n_ha_no: "Indisponível",
      n_foot: "Para mudar, vai a Definições → Apps → Kit SOS → Configuração no Home Assistant.",
      n_test: "Enviar aviso de teste", n_check: "Verificar validades agora", n_test_ok: "Aviso de teste enviado",
      n_check_ok: (s) => (s === 0 ? "Nada para avisar" : `${s} aviso(s) enviado(s)`),
      g_look: "Aspeto", th_auto: "Automático", th_light: "Claro", th_dark: "Escuro",
      sensors_title: "Sensores no Home Assistant",
      b_export: "Exportar cópia (JSON)", b_restore: "Restaurar de ficheiro…",
      b_foot: "A app já entra nas cópias de segurança do Home Assistant. Isto é só uma cópia extra que podes guardar onde quiseres.",
      b_confirm: "Restaurar cópia?", b_confirm_text: "Tudo o que está agora no Kit SOS vai ser substituído pelo conteúdo do ficheiro.",
      b_restore_btn: "Restaurar", b_done: (n) => `Restaurados ${n} artigos`,
      version: (v) => `Kit SOS ${v}`,
      shortcuts: "N novo · / procurar",
      err: {
        invalid_name: "Falta o nome.", invalid_quantity: "Quantidade inválida.", invalid_min_quantity: "Mínimo inválido.",
        invalid_expiry: "Data de validade inválida.", duplicate_name: "Já existe com esse nome.",
        grocy_url_missing: "Falta o endereço do Grocy.", grocy_key_missing: "Falta a chave API do Grocy.",
        grocy_auth: "O Grocy recusou a chave API.", grocy_unreachable: "Não consegui ligar ao Grocy.",
        grocy_http: "O Grocy devolveu um erro.", grocy_invalid: "Resposta estranha do Grocy.",
        ha_unavailable: "Sem ligação ao Home Assistant.", ha_error: "O Home Assistant devolveu um erro.",
        invalid_service: "Serviço de aviso inválido.", invalid_backup: "Este ficheiro não é uma cópia do Kit SOS.",
        not_found: "Já não existe.", network: "Sem ligação à app.", generic: "Algo correu mal.",
      },
    },
    en: {
      items_n: (n) => (n === 1 ? "1 item" : `${n} items`),
      add: "Add", settings: "Settings",
      st_total: "All", st_soon: "Expiring", st_expired: "Expired", st_missing: "Low stock",
      search: "Search", group_category: "Category", group_location: "Location", group_expiry: "Expiry",
      no_category: "No category", no_location: "No location",
      sec_expired: "Expired", sec_soon: (d) => `Next ${d} days`, sec_later: "Later",
      sec_none: "No expiry", sec_missing: "Low stock",
      showing: "Showing:", show_all: "Show all",
      expiry: "Expiry", no_expiry: "No expiry",
      d_today: "Today", d_tomorrow: "Tomorrow", d_in: (n) => `${n} days`, d_expired: "Expired",
      d_expired_ago: (n) => (n === 1 ? "Expired yesterday" : `Expired ${n} days ago`),
      missing: "Out", low: "Below minimum", low_short: "Below min.",
      empty_title: "No items yet", empty_text: "Add your first kit item or import everything you have in Grocy.",
      empty_add: "Add item", empty_import: "Import from Grocy",
      nores_title: "Nothing found", nores_text: "Try another search or clear the filters.",
      new_item: "New item", edit_item: "Edit item", cancel: "Cancel", save: "Save", done: "Done",
      f_name: "Name", f_name_ph: "E.g. Water 1.5 L",
      g_qty: "Quantity", f_qty: "Quantity", f_unit: "Unit", f_min: "Minimum", f_min_ph: "Optional",
      g_org: "Organisation", f_category: "Category", f_location: "Location", none: "None", none_m: "None",
      new_category: "＋ New category…", new_location: "＋ New location…", new_unit: "＋ New unit…",
      g_expiry: "Expiry", ex_none: "No expiry", ex_month: "Month & year", ex_day: "Exact date",
      f_month: "Month", f_year: "Year", f_date: "Date",
      ex_month_foot: "With only month and year, the 1st of that month is used.",
      ex_none_foot: "This item has no expiry date.",
      ex_day_foot: "",
      notify_foot: (d) => `You get a notification ${d} days before.`,
      g_notes: "Notes", f_notes_ph: "E.g. replace the torch batteries",
      duplicate: "Duplicate (new batch)", delete_item: "Delete item",
      confirm_delete: "Delete this item?", confirm_delete_text: (n) => `“${n}” will be deleted. This can't be undone.`,
      delete: "Delete",
      saved: "Saved", deleted: "Deleted", created: "Added",
      prompt_category: "New category", prompt_location: "New location", prompt_unit: "New unit",
      prompt_name_ph: "Name", create: "Create",
      s_title: "Settings", tab_lists: "Lists", tab_grocy: "Grocy", tab_notify: "Alerts", tab_backup: "Backup",
      lists_categories: "Categories", lists_locations: "Locations", lists_units: "Units",
      add_category: "Add category", add_location: "Add location", add_unit: "Add unit",
      plural_ph: "Plural", usage: (n) => (n === 1 ? "1 item" : `${n} items`),
      lists_foot: "Tap a name to change it. Changes are saved when you leave the field.",
      confirm_del_lookup: "Delete?", confirm_del_lookup_text: (n, c) => c ? `“${n}” is used by ${c} item(s). Those items will lose it.` : `“${n}” will be deleted.`,
      grocy_intro: "Copies every product, batch, expiry date, category, location and unit from Grocy.",
      grocy_url: "Address", grocy_key: "API key", grocy_key_ph: "Grocy → Manage API keys",
      grocy_foot: "In Home Assistant the usual address is http://a0d7b954-grocy. If that fails, try Grocy's internal IP (e.g. http://172.30.33.6).",
      grocy_check: "Check connection", grocy_import: "Import and replace everything",
      grocy_found: "Found in Grocy", gs_products: "Products", gs_items: "Items to create", gs_with_expiry: "With expiry",
      gs_without_stock: "No stock (marked “Low stock”)", gs_categories: "Categories", gs_locations: "Locations", gs_units: "Units",
      gs_inactive: "Inactive (skipped)",
      grocy_confirm: "Replace everything?", grocy_confirm_text: (n) => `The ${n} current Kit SOS items will be deleted and replaced with Grocy's.`,
      grocy_done: (n) => `Imported ${n} items`,
      n_state: "Alerts", n_on: "On", n_off: "Off", n_days: "Notice", n_days_v: (d) => `${d} days`,
      n_time: "Time", n_service: "Service", n_ha: "HA connection", n_ha_ok: "OK", n_ha_no: "Unavailable",
      n_foot: "To change these, go to Settings → Apps → Kit SOS → Configuration in Home Assistant.",
      n_test: "Send test notification", n_check: "Check expiry dates now", n_test_ok: "Test notification sent",
      n_check_ok: (s) => (s === 0 ? "Nothing to report" : `${s} notification(s) sent`),
      g_look: "Appearance", th_auto: "Automatic", th_light: "Light", th_dark: "Dark",
      sensors_title: "Home Assistant sensors",
      b_export: "Export backup (JSON)", b_restore: "Restore from file…",
      b_foot: "The app is already included in Home Assistant backups. This is just an extra copy you can keep anywhere.",
      b_confirm: "Restore backup?", b_confirm_text: "Everything currently in Kit SOS will be replaced by the file's content.",
      b_restore_btn: "Restore", b_done: (n) => `Restored ${n} items`,
      version: (v) => `Kit SOS ${v}`,
      shortcuts: "N new · / search",
      err: {
        invalid_name: "Name is missing.", invalid_quantity: "Invalid quantity.", invalid_min_quantity: "Invalid minimum.",
        invalid_expiry: "Invalid expiry date.", duplicate_name: "That name already exists.",
        grocy_url_missing: "Grocy address is missing.", grocy_key_missing: "Grocy API key is missing.",
        grocy_auth: "Grocy rejected the API key.", grocy_unreachable: "Couldn't reach Grocy.",
        grocy_http: "Grocy returned an error.", grocy_invalid: "Unexpected answer from Grocy.",
        ha_unavailable: "No connection to Home Assistant.", ha_error: "Home Assistant returned an error.",
        invalid_service: "Invalid notification service.", invalid_backup: "This file isn't a Kit SOS backup.",
        not_found: "It no longer exists.", network: "Can't reach the app.", generic: "Something went wrong.",
      },
    },
  };

  // ------------------------------------------------------------------
  // Ícones (traço simples, estilo SF Symbols)
  // ------------------------------------------------------------------
  const ICONS = {
    plus: '<path d="M12 5v14M5 12h14"/>',
    minus: '<path d="M5 12h14"/>',
    cross: '<path d="M12 4v16M4 12h16"/>',
    sliders: '<path d="M4 6h9M17 6h3M4 12h3M11 12h9M4 18h11M19 18h1"/><circle cx="15" cy="6" r="2"/><circle cx="9" cy="12" r="2"/><circle cx="17" cy="18" r="2"/>',
    search: '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
    x: '<path d="M6 6l12 12M18 6 6 18"/>',
    clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    alert: '<path d="M12 3.5 21.5 20h-19z"/><path d="M12 10v4M12 17.2v.1"/>',
    box: '<path d="M3.5 8h17v11.5a1 1 0 0 1-1 1h-15a1 1 0 0 1-1-1z"/><path d="M2.5 4.5h19V8h-19z"/><path d="M10 12h4"/>',
    empty: '<circle cx="12" cy="12" r="9"/><path d="M8 12h8"/>',
    trash: '<path d="M4 7h16M10 11v6M14 11v6M9 7V4.5h6V7M6 7l1 13h10l1-13"/>',
    copy: '<rect x="8" y="8" width="12" height="12" rx="2.5"/><path d="M16 8V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h2"/>',
    chevron: '<path d="m9 6 6 6-6 6"/>',
    down: '<path d="M12 4v11M7 10l5 5 5-5M5 20h14"/>',
    up: '<path d="M12 15V4M7 9l5-5 5 5M5 20h14"/>',
    bell: '<path d="M6 16V11a6 6 0 1 1 12 0v5l1.5 2h-15z"/><path d="M10 20.5a2 2 0 0 0 4 0"/>',
    check: '<path d="m5 12.5 4.5 4.5L19 7.5"/>',
  };
  const icon = (n, cls = "") => `<svg class="i ${cls}" viewBox="0 0 24 24" aria-hidden="true">${ICONS[n] || ""}</svg>`;

  // ------------------------------------------------------------------
  // Estado e utilitários
  // ------------------------------------------------------------------
  const S = {
    data: null,
    filter: "all",
    group: lsGet("kitsos.group") || "category",
    search: "",
    theme: lsGet("kitsos.theme") || "auto",
    settingsTab: "lists",
    grocy: { url: "http://a0d7b954-grocy", key: "", preview: null, busy: false },
  };
  let L = I18N.pt;
  let LOCALE = "pt-PT";

  function lsGet(k) { try { return localStorage.getItem(k); } catch { return null; } }
  function lsSet(k, v) { try { localStorage.setItem(k, v); } catch { /* sem armazenamento */ } }

  const $ = (sel, root = document) => root.querySelector(sel);
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const norm = (s) => String(s ?? "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
  const byId = (arr) => Object.fromEntries((arr || []).map((x) => [x.id, x]));

  function applyTheme() {
    const r = document.documentElement;
    if (S.theme === "light" || S.theme === "dark") r.dataset.theme = S.theme;
    else delete r.dataset.theme;
  }
  applyTheme();

  async function api(method, path, body) {
    let res;
    try {
      res = await fetch(path, {
        method,
        credentials: "same-origin",
        headers: body !== undefined ? { "Content-Type": "application/json" } : {},
        body: body !== undefined ? JSON.stringify(body) : undefined,
      });
    } catch {
      throw Object.assign(new Error("network"), { code: "network" });
    }
    let data = null;
    try { data = await res.json(); } catch { /* sem corpo */ }
    if (!res.ok) throw Object.assign(new Error((data && data.error) || "generic"), { code: (data && data.error) || "generic", detail: data && data.detail });
    return data;
  }
  const errText = (e) => (L.err[e && e.code] || L.err.generic) + (e && e.detail && /grocy|ha_/.test(e.code) ? ` (${e.detail})` : "");

  let toastTimer;
  function toast(msg, isError = false) {
    const t = $("#toast");
    t.textContent = msg;
    t.classList.toggle("error", !!isError);
    t.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => t.classList.remove("show"), isError ? 4200 : 2200);
  }

  function fmtNum(n) {
    return new Intl.NumberFormat(LOCALE, { maximumFractionDigits: 3 }).format(Number(n) || 0);
  }
  function parseExpiry(ex) {
    const m = /^(\d{4})-(\d{2})(?:-(\d{2}))?$/.exec(ex || "");
    return m ? { y: +m[1], m: +m[2], d: m[3] ? +m[3] : null } : null;
  }
  function fmtExpiry(ex) {
    const p = parseExpiry(ex);
    if (!p) return L.no_expiry;
    const mon = new Intl.DateTimeFormat(LOCALE, { month: "short", timeZone: "UTC" })
      .format(new Date(Date.UTC(p.y, p.m - 1, 1))).replace(/\./g, "");
    return p.d ? `${p.d} ${mon} ${p.y}` : `${mon} ${p.y}`;
  }
  function unitLabel(it, units) {
    const u = units[it.unit_id];
    if (!u) return "";
    return Number(it.quantity) === 1 || !u.name_plural ? u.name : u.name_plural;
  }
  function statusText(it) {
    const d = it.days_left;
    switch (it.status) {
      case "expired": return d === -1 ? L.d_expired_ago(1) : L.d_expired;
      case "soon": return d === 0 ? L.d_today : d === 1 ? L.d_tomorrow : L.d_in(d);
      case "missing": return L.missing;
      case "low": return L.low_short;
      default: return "";
    }
  }
  function statusPill(it) {
    const d = it.days_left;
    switch (it.status) {
      case "expired": return `<span class="pill s-expired">${esc(d === -1 ? L.d_expired_ago(1) : L.d_expired)}</span>`;
      case "soon": return `<span class="pill s-soon">${esc(d === 0 ? L.d_today : d === 1 ? L.d_tomorrow : L.d_in(d))}</span>`;
      case "missing": return `<span class="pill s-missing hide-sm">${esc(L.missing)}</span>`;
      case "low": return `<span class="pill s-low hide-sm">${esc(L.low)}</span>`;
      default: return "";
    }
  }
  const STATUS_ORDER = { expired: 0, soon: 1, low: 2, ok: 3, none: 4, missing: 5 };
  function sortItems(a, b) {
    const sa = STATUS_ORDER[a.status] ?? 9, sb = STATUS_ORDER[b.status] ?? 9;
    const da = a.days_left ?? 1e9, db = b.days_left ?? 1e9;
    if (a.status === "missing" || b.status === "missing") {
      if (sa !== sb) return sa - sb;
    }
    if (da !== db) return da - db;
    return a.name.localeCompare(b.name, LOCALE, { sensitivity: "base" });
  }

  // ------------------------------------------------------------------
  // Carregar dados
  // ------------------------------------------------------------------
  async function load(silent = false) {
    try {
      S.data = await api("GET", "api/state");
      L = I18N[S.data.language] || I18N.pt;
      LOCALE = S.data.language === "en" ? "en-GB" : "pt-PT";
      document.documentElement.lang = S.data.language === "en" ? "en" : "pt-PT";
      render();
      refreshOpenSheet();
    } catch (e) {
      if (!silent) {
        $("#app").innerHTML = `<div class="empty"><div class="big">⚠️</div><h2>${esc(errText(e))}</h2><p></p>
          <div class="btns"><button class="btn btn-secondary" data-act="reload">↻</button></div></div>`;
      }
    } finally {
      $("#app").setAttribute("aria-busy", "false");
    }
  }

  // ------------------------------------------------------------------
  // Ecrã principal
  // ------------------------------------------------------------------
  function visibleItems() {
    const { items, categories, locations } = S.data;
    const cats = byId(categories), locs = byId(locations);
    const q = norm(S.search.trim());
    return items.filter((it) => {
      if (S.filter === "soon" && it.status !== "soon") return false;
      if (S.filter === "expired" && it.status !== "expired") return false;
      if (S.filter === "missing" && !(it.status === "missing" || it.status === "low")) return false;
      if (!q) return true;
      const hay = norm([it.name, it.notes, cats[it.category_id]?.name, locs[it.location_id]?.name].join(" "));
      return q.split(/\s+/).every((w) => hay.includes(w));
    });
  }

  function groupItems(list) {
    const { categories, locations, notify } = S.data;
    const groups = new Map();
    const add = (key, title, iconHtml, it, order) => {
      if (!groups.has(key)) groups.set(key, { title, iconHtml, items: [], order });
      groups.get(key).items.push(it);
    };
    if (S.group === "expiry") {
      for (const it of list) {
        if (it.status === "missing") add("m", L.sec_missing, "", it, 4);
        else if (it.status === "expired") add("e", L.sec_expired, "", it, 0);
        else if (it.days_left == null) add("n", L.sec_none, "", it, 3);
        else if (it.days_left <= notify.days) add("s", L.sec_soon(notify.days), "", it, 1);
        else add("l", L.sec_later, "", it, 2);
      }
    } else if (S.group === "location") {
      const order = Object.fromEntries(locations.map((l, i) => [l.id, i]));
      for (const it of list) {
        const l = locations.find((x) => x.id === it.location_id);
        add(l ? `l${l.id}` : "none", l ? l.name : L.no_location, "", it, l ? order[l.id] : 1e6);
      }
    } else {
      const order = Object.fromEntries(categories.map((c, i) => [c.id, i]));
      for (const it of list) {
        const c = categories.find((x) => x.id === it.category_id);
        add(c ? `c${c.id}` : "none", c ? c.name : L.no_category, c ? esc(c.icon || "") : "", it, c ? order[c.id] : 1e6);
      }
    }
    return [...groups.values()].sort((a, b) => a.order - b.order).map((g) => ({ ...g, items: g.items.sort(sortItems) }));
  }

  function rowHtml(it, cats, locs, units) {
    const c = cats[it.category_id];
    const color = c && c.color ? `var(--${c.color})` : "var(--gray)";
    const av = c && c.icon ? esc(c.icon) : esc((it.name || "?").trim().charAt(0).toUpperCase());
    const sub = [];
    if (S.group !== "location" && locs[it.location_id]) sub.push(esc(locs[it.location_id].name));
    const dateTxt = it.expiry ? `<span class="pre">${esc(L.expiry)} </span>${esc(fmtExpiry(it.expiry))}` : esc(L.no_expiry);
    const st = statusText(it);
    sub.push(st ? `<span class="exp-date">${dateTxt}</span><span class="exp-status s-${it.status}">${esc(st)}</span>` : dateTxt);
    const unit = unitLabel(it, units);
    return `<div class="row ${it.status === "missing" ? "is-missing" : ""}" data-id="${it.id}">
      <button class="row-main" data-act="edit" data-id="${it.id}">
        <span class="avatar" style="--c:${color}">${av}</span>
        <span class="row-text"><span class="row-title">${esc(it.name)}</span>
        <span class="row-sub">${sub.join('<span class="sep">·</span>')}</span></span>
      </button>
      ${statusPill(it)}
      <div class="stepper" role="group" aria-label="${esc(L.f_qty)}">
        <button data-act="dec" data-id="${it.id}" aria-label="−1">${icon("minus")}</button>
        <span class="qty">${fmtNum(it.quantity)}${unit ? `<small>${esc(unit)}</small>` : ""}</span>
        <button data-act="inc" data-id="${it.id}" aria-label="+1">${icon("plus")}</button>
      </div>
    </div>`;
  }

  function render() {
    const d = S.data;
    if (!d) return;
    const cats = byId(d.categories), locs = byId(d.locations), units = byId(d.units);
    const st = d.stats;
    const stat = (key, n, label, ic, color) => `
      <button class="stat ${S.filter === key ? "on" : ""} ${n === 0 && key !== "all" ? "dim" : ""}" data-act="filter" data-filter="${key}" style="--c:var(--${color})" aria-pressed="${S.filter === key}">
        <span class="dot">${icon(ic)}</span><span class="num">${n}</span><span class="lbl">${esc(label)}</span>
      </button>`;

    const list = visibleItems();
    const groups = groupItems(list);
    let content;
    if (!d.items.length) {
      content = `<div class="empty"><div class="big">🧰</div><h2>${esc(L.empty_title)}</h2><p>${esc(L.empty_text)}</p>
        <div class="btns"><button class="btn btn-primary" data-act="new">${icon("plus")}${esc(L.empty_add)}</button>
        <button class="btn btn-secondary" data-act="open-grocy">${esc(L.empty_import)}</button></div></div>`;
    } else if (!list.length) {
      content = `<div class="empty"><div class="big">🔎</div><h2>${esc(L.nores_title)}</h2><p>${esc(L.nores_text)}</p></div>`;
    } else {
      content = groups.map((g) => `
        <section class="section">
          <div class="section-head">${g.iconHtml ? `<span aria-hidden="true">${g.iconHtml}</span>` : ""}<span>${esc(g.title)}</span><span class="count">${g.items.length}</span></div>
          <div class="group">${g.items.map((it) => rowHtml(it, cats, locs, units)).join("")}</div>
        </section>`).join("");
    }

    const filterLabel = { soon: L.st_soon, expired: L.st_expired, missing: L.st_missing }[S.filter];
    const focused = document.activeElement && document.activeElement.id === "q";
    const selStart = focused ? document.activeElement.selectionStart : null;

    $("#app").innerHTML = `
      <header class="topbar">
        <div>
          <h1><span class="app-badge" aria-hidden="true">${icon("cross")}</span>Kit SOS</h1>
          <p class="sub">${esc(L.items_n(st.total))}</p>
        </div>
        <div class="actions">
          <button class="icon-btn" data-act="settings" aria-label="${esc(L.settings)}" title="${esc(L.settings)}">${icon("sliders")}</button>
          <button class="btn btn-primary" data-act="new" title="${esc(L.add)} (N)">${icon("plus")}<span class="btn-add-label">${esc(L.add)}</span></button>
        </div>
      </header>
      <div class="stats">
        ${stat("all", st.total, L.st_total, "box", "blue")}
        ${stat("soon", st.soon, L.st_soon, "clock", "orange")}
        ${stat("expired", st.expired, L.st_expired, "alert", "red")}
        ${stat("missing", st.missing + st.low, L.st_missing, "empty", "gray")}
      </div>
      <div class="toolbar">
        <label class="search">${icon("search")}<input id="q" type="search" placeholder="${esc(L.search)}" value="${esc(S.search)}" autocomplete="off" aria-label="${esc(L.search)}">
          ${S.search ? `<button class="clear" data-act="clear-search" aria-label="×">${icon("x")}</button>` : ""}</label>
        <div class="segmented" role="group">
          ${["category", "location", "expiry"].map((g) => `<button data-act="group" data-group="${g}" aria-pressed="${S.group === g}">${esc(L["group_" + g])}</button>`).join("")}
        </div>
      </div>
      ${filterLabel ? `<div class="filter-note">${esc(L.showing)} <b>${esc(filterLabel)}</b> · <button data-act="filter" data-filter="all">${esc(L.show_all)}</button></div>` : ""}
      ${content}
      <div class="footer">${esc(L.version(d.version))}<span class="kbd-hint"> · ${esc(L.shortcuts)}</span></div>`;

    if (focused) {
      const q = $("#q");
      q.focus();
      if (selStart != null) q.setSelectionRange(selStart, selStart);
    }
  }

  // ------------------------------------------------------------------
  // Camadas: folhas e alertas
  // ------------------------------------------------------------------
  let openSheet = null; // { kind, el, refresh }

  function showSheet(kind, html, { wide = false, onMount, refresh } = {}) {
    closeSheet(true);
    const bd = document.createElement("div");
    bd.className = "backdrop is-sheet";
    bd.innerHTML = `<div class="sheet ${wide ? "wide" : ""}" role="dialog" aria-modal="true"><div class="grabber"></div>${html}</div>`;
    bd.addEventListener("mousedown", (e) => { if (e.target === bd) bd.dataset.down = "1"; });
    bd.addEventListener("click", (e) => { if (e.target === bd && bd.dataset.down) closeSheet(); delete bd.dataset.down; });
    $("#layer").appendChild(bd);
    openSheet = { kind, el: bd, refresh };
    if (onMount) onMount(bd);
    return bd;
  }
  function closeSheet(instant = false) {
    if (!openSheet) return;
    const el = openSheet.el;
    openSheet = null;
    if (instant) { el.remove(); return; }
    el.classList.add("closing");
    setTimeout(() => el.remove(), 240);
  }
  function refreshOpenSheet() { if (openSheet && openSheet.refresh) openSheet.refresh(); }

  function alertBox({ title, text = "", buttons, input }) {
    return new Promise((resolve) => {
      const bd = document.createElement("div");
      bd.className = "backdrop alert-backdrop";
      bd.innerHTML = `<div class="alert" role="alertdialog" aria-modal="true">
        <div class="body"><h3>${esc(title)}</h3>${text ? `<p>${esc(text)}</p>` : ""}
        ${input ? `<input type="text" placeholder="${esc(input.placeholder || "")}" value="${esc(input.value || "")}" maxlength="60">` : ""}</div>
        <div class="btns">${buttons.map((b, i) => `<button data-i="${i}" class="${b.style || ""}">${esc(b.label)}</button>`).join("")}</div></div>`;
      const done = (val) => { bd.classList.add("closing"); setTimeout(() => bd.remove(), 200); document.removeEventListener("keydown", onKey, true); resolve(val); };
      const inp = $("input", bd);
      const onKey = (e) => {
        if (e.key === "Escape") { e.stopPropagation(); done(null); }
        if (e.key === "Enter") { e.preventDefault(); e.stopPropagation(); const b = buttons.findIndex((x) => x.default); done(b >= 0 ? { i: b, value: inp ? inp.value.trim() : null } : null); }
      };
      document.addEventListener("keydown", onKey, true);
      bd.addEventListener("click", (e) => {
        const b = e.target.closest("button[data-i]");
        if (b) { const i = +b.dataset.i; done(buttons[i].cancel ? null : { i, value: inp ? inp.value.trim() : null }); }
      });
      $("#layer").appendChild(bd);
      (inp || $("button.strong", bd) || $("button", bd)).focus();
    });
  }
  const confirmBox = async (title, text, label, destructive = true) =>
    !!(await alertBox({ title, text, buttons: [{ label: L.cancel, cancel: true }, { label, style: destructive ? "destructive strong" : "strong", default: true }] }));
  async function promptBox(title, value = "") {
    const r = await alertBox({ title, input: { placeholder: L.prompt_name_ph, value }, buttons: [{ label: L.cancel, cancel: true }, { label: L.create, style: "strong", default: true }] });
    return r && r.value ? r.value : null;
  }

  // ------------------------------------------------------------------
  // Folha: novo / editar artigo
  // ------------------------------------------------------------------
  function optionList(list, selected, noneLabel, newLabel, labelFn = (x) => x.name) {
    return `<option value="">${esc(noneLabel)}</option>` +
      list.map((x) => `<option value="${x.id}" ${String(x.id) === String(selected ?? "") ? "selected" : ""}>${esc(labelFn(x))}</option>`).join("") +
      `<option value="__new">${esc(newLabel)}</option>`;
  }

  function openItem(id, preset) {
    const d = S.data;
    const existing = id ? d.items.find((x) => x.id === id) : null;
    const it = existing ? { ...existing } : {
      name: "", quantity: 1, unit_id: null, min_quantity: null, category_id: S.lastCategory || null,
      location_id: S.lastLocation || null, expiry: null, notes: "", ...(preset || {}),
    };
    const p = parseExpiry(it.expiry);
    let mode = !p ? "none" : p.d ? "day" : "month";
    const now = new Date();
    const curY = now.getFullYear();
    const years = [];
    for (let y = curY - 6; y <= curY + 25; y++) years.push(y);
    const months = Array.from({ length: 12 }, (_, i) => new Intl.DateTimeFormat(LOCALE, { month: "long", timeZone: "UTC" }).format(new Date(Date.UTC(2020, i, 1))));
    const selM = p ? p.m : now.getMonth() + 1;
    const selY = p ? p.y : curY + 1;
    const dateVal = p && p.d ? it.expiry : "";

    const html = `
      <header class="sheet-bar">
        <button class="link left" data-sact="close">${esc(L.cancel)}</button>
        <h2>${esc(existing ? L.edit_item : L.new_item)}</h2>
        <button class="link strong right" data-sact="save">${esc(L.save)}</button>
      </header>
      <div class="sheet-body">
        <form id="item-form" autocomplete="off" novalidate>
          <div class="fgroup"><div class="group">
            <div class="field name"><input type="text" name="name" placeholder="${esc(L.f_name_ph)}" value="${esc(it.name)}" maxlength="120" aria-label="${esc(L.f_name)}" required></div>
          </div><div class="err" id="err-name"></div></div>

          <div class="fgroup"><div class="label">${esc(L.g_qty)}</div><div class="group">
            <div class="field"><span class="flabel">${esc(L.f_qty)}</span>
              <div class="qty-input">
                <button type="button" data-sact="qdec" aria-label="−1">${icon("minus")}</button>
                <input type="number" name="quantity" inputmode="decimal" min="0" step="any" value="${esc(it.quantity)}" aria-label="${esc(L.f_qty)}">
                <button type="button" data-sact="qinc" aria-label="+1">${icon("plus")}</button>
              </div></div>
            <div class="field"><label for="f-unit">${esc(L.f_unit)}</label>
              <select id="f-unit" name="unit_id" data-kind="units">${optionList(d.units, it.unit_id, L.none_m, L.new_unit)}</select></div>
            <div class="field"><label for="f-min">${esc(L.f_min)}</label>
              <input id="f-min" type="number" name="min_quantity" inputmode="decimal" min="0" step="any" placeholder="${esc(L.f_min_ph)}" value="${it.min_quantity ?? ""}"></div>
          </div></div>

          <div class="fgroup"><div class="label">${esc(L.g_org)}</div><div class="group">
            <div class="field"><label for="f-cat">${esc(L.f_category)}</label>
              <select id="f-cat" name="category_id" data-kind="categories">${optionList(d.categories, it.category_id, L.none, L.new_category, (c) => `${c.icon ? c.icon + "  " : ""}${c.name}`)}</select></div>
            <div class="field"><label for="f-loc">${esc(L.f_location)}</label>
              <select id="f-loc" name="location_id" data-kind="locations">${optionList(d.locations, it.location_id, L.none_m, L.new_location)}</select></div>
          </div></div>

          <div class="fgroup"><div class="label">${esc(L.g_expiry)}</div>
            <div class="segmented full" role="group" id="ex-mode" style="margin-bottom:10px">
              ${["none", "month", "day"].map((m) => `<button type="button" data-sact="exmode" data-mode="${m}" aria-pressed="${mode === m}">${esc(L["ex_" + m])}</button>`).join("")}
            </div>
            <div class="group" id="ex-fields"></div>
            <div class="foot" id="ex-foot"></div><div class="err" id="err-expiry"></div>
          </div>

          <div class="fgroup"><div class="label">${esc(L.g_notes)}</div><div class="group">
            <div class="field stack"><textarea name="notes" rows="3" maxlength="4000" placeholder="${esc(L.f_notes_ph)}" aria-label="${esc(L.g_notes)}">${esc(it.notes || "")}</textarea></div>
          </div></div>

          ${existing ? `<div class="fgroup"><div class="group">
            <button type="button" class="action-row" data-sact="duplicate">${icon("copy")}${esc(L.duplicate)}</button>
            <button type="button" class="action-row danger" data-sact="delete">${icon("trash")}${esc(L.delete_item)}</button>
          </div></div>` : ""}
        </form>
      </div>`;

    const bd = showSheet("item", html, {
      onMount(root) {
        const form = $("#item-form", root);
        const exFields = $("#ex-fields", root);
        const exFoot = $("#ex-foot", root);
        let curM = selM, curY = selY, curDate = dateVal;

        function drawExpiry() {
          root.querySelectorAll("#ex-mode button").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.mode === mode)));
          if (mode === "none") {
            exFields.style.display = "none";
            exFoot.textContent = L.ex_none_foot;
          } else if (mode === "month") {
            exFields.style.display = "";
            exFields.innerHTML = `<div class="field"><span class="flabel">${esc(L.f_month)}</span><div class="inline-selects">
              <select name="ex_m" aria-label="${esc(L.f_month)}">${months.map((n, i) => `<option value="${i + 1}" ${i + 1 === +curM ? "selected" : ""}>${esc(n.charAt(0).toUpperCase() + n.slice(1))}</option>`).join("")}</select>
              <select name="ex_y" aria-label="${esc(L.f_year)}">${years.map((y) => `<option ${y === +curY ? "selected" : ""}>${y}</option>`).join("")}</select></div></div>`;
            exFoot.textContent = `${L.ex_month_foot} ${L.notify_foot(S.data.notify.days)}`;
          } else {
            exFields.style.display = "";
            if (!curDate) curDate = `${curY}-${String(curM).padStart(2, "0")}-01`;
            exFields.innerHTML = `<div class="field"><label for="f-date">${esc(L.f_date)}</label><input id="f-date" type="date" name="ex_date" value="${esc(curDate)}" min="1900-01-01" max="2999-12-31"></div>`;
            exFoot.textContent = L.notify_foot(S.data.notify.days);
          }
          $("#err-expiry", root).textContent = "";
        }
        drawExpiry();

        exFields.addEventListener("change", (e) => {
          if (e.target.name === "ex_m") curM = e.target.value;
          if (e.target.name === "ex_y") curY = e.target.value;
          if (e.target.name === "ex_date") curDate = e.target.value;
        });

        form.addEventListener("change", async (e) => {
          const sel = e.target;
          if (sel.tagName === "SELECT" && sel.value === "__new") {
            const kind = sel.dataset.kind;
            const title = { categories: L.prompt_category, locations: L.prompt_location, units: L.prompt_unit }[kind];
            const name = await promptBox(title);
            if (!name) { sel.value = ""; return; }
            try {
              const r = await api("POST", `api/${kind}`, { name });
              S.data = await api("GET", "api/state");
              const list = S.data[kind];
              const labelFn = kind === "categories" ? (c) => `${c.icon ? c.icon + "  " : ""}${c.name}` : (x) => x.name;
              sel.innerHTML = optionList(list, r.id, kind === "categories" ? L.none : L.none_m,
                { categories: L.new_category, locations: L.new_location, units: L.new_unit }[kind], labelFn);
              render();
            } catch (err) { toast(errText(err), true); sel.value = ""; }
          }
        });

        root.addEventListener("click", async (e) => {
          const b = e.target.closest("[data-sact]");
          if (!b) return;
          const act = b.dataset.sact;
          const qInput = form.elements.quantity;
          if (act === "close") closeSheet();
          if (act === "qinc" || act === "qdec") {
            const v = parseFloat(String(qInput.value).replace(",", ".")) || 0;
            qInput.value = Math.max(0, Math.round((v + (act === "qinc" ? 1 : -1)) * 1000) / 1000);
          }
          if (act === "exmode") { mode = b.dataset.mode; drawExpiry(); }
          if (act === "save") save();
          if (act === "duplicate") {
            const vals = collect();
            closeSheet(true);
            openItem(null, { ...vals, expiry: null, quantity: vals.quantity ?? 1 });
          }
          if (act === "delete") {
            if (await confirmBox(L.confirm_delete, L.confirm_delete_text(existing.name), L.delete)) {
              try { await api("DELETE", `api/items/${existing.id}`); closeSheet(); toast(L.deleted); load(true); }
              catch (err) { toast(errText(err), true); }
            }
          }
        });

        form.addEventListener("submit", (e) => { e.preventDefault(); save(); });
        form.addEventListener("keydown", (e) => {
          if (e.key === "Enter" && e.target.tagName === "INPUT") { e.preventDefault(); save(); }
          if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) { e.preventDefault(); save(); }
        });

        function collect() {
          const f = form.elements;
          let expiry = null;
          if (mode === "month") expiry = `${curY}-${String(curM).padStart(2, "0")}`;
          if (mode === "day") expiry = (f.ex_date && f.ex_date.value) || curDate || null;
          const num = (v) => (String(v).trim() === "" ? null : String(v).replace(",", "."));
          return {
            name: f.name.value.trim(),
            quantity: num(f.quantity.value) ?? 0,
            unit_id: f.unit_id.value && f.unit_id.value !== "__new" ? +f.unit_id.value : null,
            min_quantity: num(f.min_quantity.value),
            category_id: f.category_id.value && f.category_id.value !== "__new" ? +f.category_id.value : null,
            location_id: f.location_id.value && f.location_id.value !== "__new" ? +f.location_id.value : null,
            expiry,
            notes: f.notes.value.trim(),
          };
        }

        let saving = false;
        async function save() {
          if (saving) return;
          const vals = collect();
          $("#err-name", root).textContent = "";
          if (!vals.name) { $("#err-name", root).textContent = L.err.invalid_name; form.elements.name.focus(); return; }
          if (mode === "day" && !vals.expiry) { $("#err-expiry", root).textContent = L.err.invalid_expiry; return; }
          saving = true;
          $('[data-sact="save"]', root).disabled = true;
          try {
            if (existing) await api("PUT", `api/items/${existing.id}`, vals);
            else await api("POST", "api/items", vals);
            S.lastCategory = vals.category_id; S.lastLocation = vals.location_id;
            closeSheet();
            toast(existing ? L.saved : L.created);
            load(true);
          } catch (err) {
            const target = err.code === "invalid_expiry" ? "#err-expiry" : "#err-name";
            $(target, root).textContent = errText(err);
          } finally {
            saving = false;
            const sb = $('[data-sact="save"]', root);
            if (sb) sb.disabled = false;
          }
        }

        if (!existing) setTimeout(() => form.elements.name.focus(), 60);
      },
    });
    return bd;
  }

  // ------------------------------------------------------------------
  // Folha: definições
  // ------------------------------------------------------------------
  function settingsHtml() {
    const d = S.data;
    const tabs = ["lists", "grocy", "notify", "backup"];
    const usage = (key, id) => d.items.filter((x) => x[key] === id).length;
    let body = "";

    if (S.settingsTab === "lists") {
      const block = (kind, title, addLabel, rowFn) => `
        <div class="fgroup"><div class="label">${esc(title)}</div><div class="group">
          ${d[kind].map(rowFn).join("")}
          <button type="button" class="action-row" data-sact="add-lookup" data-kind="${kind}">${icon("plus")}${esc(addLabel)}</button>
        </div></div>`;
      body = block("categories", L.lists_categories, L.add_category, (c) => `
          <div class="edit-row" data-kind="categories" data-id="${c.id}">
            <input class="emoji" name="icon" value="${esc(c.icon || "")}" maxlength="8" aria-label="Emoji">
            <button type="button" class="swatch" data-sact="color" style="--c:var(--${c.color || "gray"})" aria-label="Cor"></button>
            <input class="name" name="name" value="${esc(c.name)}" maxlength="60" aria-label="${esc(L.f_name)}">
            <span class="usage">${esc(L.usage(usage("category_id", c.id)))}</span>
            <button type="button" class="del" data-sact="del-lookup" aria-label="${esc(L.delete)}">${icon("trash")}</button>
          </div>`) +
        block("locations", L.lists_locations, L.add_location, (l) => `
          <div class="edit-row" data-kind="locations" data-id="${l.id}">
            <input class="name" name="name" value="${esc(l.name)}" maxlength="60" aria-label="${esc(L.f_name)}">
            <span class="usage">${esc(L.usage(usage("location_id", l.id)))}</span>
            <button type="button" class="del" data-sact="del-lookup" aria-label="${esc(L.delete)}">${icon("trash")}</button>
          </div>`) +
        block("units", L.lists_units, L.add_unit, (u) => `
          <div class="edit-row" data-kind="units" data-id="${u.id}">
            <input class="name" name="name" value="${esc(u.name)}" maxlength="60" aria-label="${esc(L.f_name)}">
            <input class="plural" name="name_plural" value="${esc(u.name_plural || "")}" placeholder="${esc(L.plural_ph)}" maxlength="60" aria-label="${esc(L.plural_ph)}">
            <button type="button" class="del" data-sact="del-lookup" aria-label="${esc(L.delete)}">${icon("trash")}</button>
          </div>`) +
        `<div class="fgroup"><div class="foot">${esc(L.lists_foot)}</div></div>`;
    } else if (S.settingsTab === "grocy") {
      const g = S.grocy;
      const pv = g.preview;
      body = `
        <div class="fgroup"><div class="foot" style="padding-top:0;padding-bottom:10px">${esc(L.grocy_intro)}</div><div class="group">
          <div class="field"><label for="g-url">${esc(L.grocy_url)}</label><input id="g-url" type="url" name="g_url" value="${esc(g.url)}" spellcheck="false"></div>
          <div class="field"><label for="g-key">${esc(L.grocy_key)}</label><input id="g-key" type="password" name="g_key" value="${esc(g.key)}" placeholder="${esc(L.grocy_key_ph)}" spellcheck="false" autocomplete="off"></div>
        </div><div class="foot">${esc(L.grocy_foot)}</div></div>
        <div class="fgroup"><button class="btn btn-secondary btn-block" data-sact="grocy-check" ${g.busy ? "disabled" : ""}>${g.busy ? '<span class="spinner" style="width:18px;height:18px;border-width:2px"></span>' : esc(L.grocy_check)}</button></div>
        ${pv ? `<div class="fgroup"><div class="label">${esc(L.grocy_found)}</div><div class="group">
          ${[["gs_products", "products"], ["gs_items", "items"], ["gs_with_expiry", "with_expiry"], ["gs_without_stock", "without_stock"],
             ["gs_categories", "categories"], ["gs_locations", "locations"], ["gs_units", "units"], ["gs_inactive", "skipped_inactive"]]
            .map(([k, f]) => `<div class="kv"><span>${esc(L[k])}</span><span><b>${pv.summary[f]}</b></span></div>`).join("")}
        </div></div>
        <div class="fgroup"><button class="btn btn-primary btn-block" data-sact="grocy-import" ${g.busy ? "disabled" : ""}>${esc(L.grocy_import)}</button></div>` : ""}`;
    } else if (S.settingsTab === "notify") {
      const n = d.notify;
      body = `
        <div class="fgroup"><div class="group">
          <div class="kv"><span>${esc(L.n_state)}</span><span>${esc(n.enabled ? L.n_on : L.n_off)}</span></div>
          <div class="kv"><span>${esc(L.n_days)}</span><span>${esc(L.n_days_v(n.days))}</span></div>
          <div class="kv"><span>${esc(L.n_time)}</span><span>${esc(n.time)}</span></div>
          <div class="kv"><span>${esc(L.n_service)}</span><span><code>${esc(n.service)}</code></span></div>
          <div class="kv"><span>${esc(L.n_ha)}</span><span>${esc(n.ha_connected ? L.n_ha_ok : L.n_ha_no)}</span></div>
        </div><div class="foot">${esc(L.n_foot)}</div></div>
        <div class="fgroup"><div class="group">
          <button type="button" class="action-row" data-sact="notify-test">${icon("bell")}${esc(L.n_test)}</button>
          <button type="button" class="action-row" data-sact="notify-check">${icon("check")}${esc(L.n_check)}</button>
        </div></div>
        <div class="fgroup"><div class="label">${esc(L.sensors_title)}</div><div class="group">
          ${["sensor.kit_sos_expiring", "sensor.kit_sos_expired", "sensor.kit_sos_low_stock", "sensor.kit_sos_items"].map((s) => `<div class="kv"><span><code>${s}</code></span><span></span></div>`).join("")}
        </div></div>
        <div class="fgroup"><div class="label">${esc(L.g_look)}</div>
          <div class="segmented full" role="group">${["auto", "light", "dark"].map((t) => `<button type="button" data-sact="theme" data-theme="${t}" aria-pressed="${S.theme === t}">${esc(L["th_" + t])}</button>`).join("")}</div>
        </div>`;
    } else {
      body = `
        <div class="fgroup"><div class="group">
          <button type="button" class="action-row" data-sact="export">${icon("down")}${esc(L.b_export)}</button>
          <button type="button" class="action-row" data-sact="restore">${icon("up")}${esc(L.b_restore)}</button>
        </div><div class="foot">${esc(L.b_foot)}</div></div>
        <input type="file" id="restore-file" accept="application/json,.json" hidden>`;
    }

    return `
      <header class="sheet-bar">
        <span class="left"></span><h2>${esc(L.s_title)}</h2>
        <button class="link strong right" data-sact="close">${esc(L.done)}</button>
      </header>
      <div class="sheet-tabs"><div class="segmented full" role="tablist">
        ${tabs.map((t) => `<button type="button" role="tab" data-sact="tab" data-tab="${t}" aria-pressed="${S.settingsTab === t}">${esc(L["tab_" + t])}</button>`).join("")}
      </div></div>
      <div class="sheet-body" id="settings-body">${body}
        <div class="footer">${esc(L.version(d.version))}</div>
      </div>`;
  }

  function openSettings(tab) {
    if (tab) S.settingsTab = tab;
    const sheet = showSheet("settings", settingsHtml(), {
      wide: true,
      refresh: () => redrawSettings(),
      onMount(root) {
        root.addEventListener("click", onSettingsClick);
        root.addEventListener("change", onSettingsChange);
        root.addEventListener("input", (e) => {
          if (e.target.name === "g_url") S.grocy.url = e.target.value;
          if (e.target.name === "g_key") S.grocy.key = e.target.value;
        });
      },
    });
    return sheet;
  }
  function redrawSettings() {
    if (!openSheet || openSheet.kind !== "settings") return;
    const sheetEl = $(".sheet", openSheet.el);
    const body = $("#settings-body", sheetEl);
    const scroll = body ? body.scrollTop : 0;
    const active = document.activeElement;
    // não redesenhar enquanto se escreve numa lista (evita perder o cursor)
    if (active && sheetEl.contains(active) && active.tagName === "INPUT" && active.closest(".edit-row")) return;
    sheetEl.innerHTML = `<div class="grabber"></div>${settingsHtml()}`;
    const nb = $("#settings-body", sheetEl);
    if (nb) nb.scrollTop = scroll;
  }

  async function onSettingsClick(e) {
    const b = e.target.closest("[data-sact]");
    if (!b) return;
    const act = b.dataset.sact;
    try {
      if (act === "close") closeSheet();
      if (act === "tab") { S.settingsTab = b.dataset.tab; redrawSettings(); const body = $("#settings-body"); if (body) body.scrollTop = 0; }
      if (act === "theme") { S.theme = b.dataset.theme; lsSet("kitsos.theme", S.theme); applyTheme(); redrawSettings(); }
      if (act === "add-lookup") {
        const kind = b.dataset.kind;
        const name = await promptBox({ categories: L.prompt_category, locations: L.prompt_location, units: L.prompt_unit }[kind]);
        if (name) { await api("POST", `api/${kind}`, { name }); await load(true); }
      }
      if (act === "del-lookup") {
        const row = b.closest(".edit-row");
        const kind = row.dataset.kind, id = +row.dataset.id;
        const obj = S.data[kind].find((x) => x.id === id);
        const key = { categories: "category_id", locations: "location_id", units: "unit_id" }[kind];
        const count = S.data.items.filter((x) => x[key] === id).length;
        if (await confirmBox(L.confirm_del_lookup, L.confirm_del_lookup_text(obj.name, count), L.delete)) {
          await api("DELETE", `api/${kind}/${id}`); await load(true);
        }
      }
      if (act === "color") {
        const row = b.closest(".edit-row");
        const id = +row.dataset.id;
        const c = S.data.categories.find((x) => x.id === id);
        const colors = ["blue", "green", "orange", "purple", "teal", "indigo", "pink", "red", "yellow", "mint", "cyan", "brown"];
        const next = colors[(colors.indexOf(c.color) + 1) % colors.length];
        await api("PUT", `api/categories/${id}`, { color: next });
        await load(true);
      }
      if (act === "grocy-check") {
        S.grocy.busy = true; S.grocy.preview = null; redrawSettings();
        try { S.grocy.preview = await api("POST", "api/import/grocy", { url: S.grocy.url, api_key: S.grocy.key, dry_run: true }); }
        finally { S.grocy.busy = false; redrawSettings(); }
      }
      if (act === "grocy-import") {
        const existing = S.data.items.length;
        if (existing && !(await confirmBox(L.grocy_confirm, L.grocy_confirm_text(existing), L.grocy_import.split(" ")[0]))) return;
        S.grocy.busy = true; redrawSettings();
        try {
          const r = await api("POST", "api/import/grocy", { url: S.grocy.url, api_key: S.grocy.key, dry_run: false });
          S.grocy.preview = null; S.grocy.key = "";
          toast(L.grocy_done(r.imported));
          closeSheet();
          S.filter = "all";
          await load(true);
        } finally { S.grocy.busy = false; redrawSettings(); }
      }
      if (act === "notify-test") { await api("POST", "api/notify/test"); toast(L.n_test_ok); }
      if (act === "notify-check") { const r = await api("POST", "api/notify/check"); toast(L.n_check_ok(r.sent)); }
      if (act === "export") {
        const data = await api("GET", "api/export");
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = `kit-sos-${S.data.today}.json`;
        document.body.appendChild(a); a.click(); a.remove();
        setTimeout(() => URL.revokeObjectURL(a.href), 4000);
      }
      if (act === "restore") $("#restore-file").click();
    } catch (err) {
      toast(errText(err), true);
    }
  }

  async function onSettingsChange(e) {
    const t = e.target;
    try {
      if (t.id === "restore-file" && t.files && t.files[0]) {
        const text = await t.files[0].text();
        t.value = "";
        let payload;
        try { payload = JSON.parse(text); } catch { throw { code: "invalid_backup" }; }
        if (!payload || payload.app !== "kit_sos") throw { code: "invalid_backup" };
        if (!(await confirmBox(L.b_confirm, L.b_confirm_text, L.b_restore_btn))) return;
        const r = await api("POST", "api/import/backup", payload);
        toast(L.b_done(r.counts.items));
        await load(true);
        return;
      }
      const row = t.closest(".edit-row");
      if (row && t.tagName === "INPUT") {
        const kind = row.dataset.kind, id = +row.dataset.id;
        const body = {};
        body[t.name] = t.value.trim();
        if (t.name === "name" && !body.name) { await load(true); return; }
        await api("PUT", `api/${kind}/${id}`, body);
        t.blur();
        await load(true);
        toast(L.saved);
      }
    } catch (err) {
      toast(errText(err), true);
      await load(true);
    }
  }

  // ------------------------------------------------------------------
  // Eventos do ecrã principal
  // ------------------------------------------------------------------
  const pending = new Map();
  async function bump(id, delta) {
    const it = S.data.items.find((x) => x.id === id);
    if (!it) return;
    it.quantity = Math.max(0, Math.round((Number(it.quantity) + delta) * 1000) / 1000);
    render();
    pending.set(id, (pending.get(id) || 0) + delta);
    clearTimeout(bump.t);
    bump.t = setTimeout(async () => {
      const jobs = [...pending.entries()];
      pending.clear();
      try { await Promise.all(jobs.map(([i, d]) => api("POST", `api/items/${i}/adjust`, { delta: d }))); }
      catch (err) { toast(errText(err), true); }
      load(true);
    }, 450);
  }

  document.addEventListener("click", (e) => {
    const b = e.target.closest("[data-act]");
    if (!b || !$("#app").contains(b)) return;
    const act = b.dataset.act;
    const id = b.dataset.id ? +b.dataset.id : null;
    if (act === "new") openItem(null);
    if (act === "edit") openItem(id);
    if (act === "inc") bump(id, 1);
    if (act === "dec") bump(id, -1);
    if (act === "settings") openSettings();
    if (act === "open-grocy") openSettings("grocy");
    if (act === "reload") location.reload();
    if (act === "filter") { const f = b.dataset.filter; S.filter = S.filter === f ? "all" : f; render(); }
    if (act === "group") { S.group = b.dataset.group; lsSet("kitsos.group", S.group); render(); }
    if (act === "clear-search") { S.search = ""; render(); $("#q").focus(); }
  });

  document.addEventListener("input", (e) => {
    if (e.target.id === "q") { S.search = e.target.value; render(); }
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      if (document.querySelector(".alert-backdrop")) return;
      if (openSheet) { e.preventDefault(); closeSheet(); return; }
      if (S.search) { S.search = ""; render(); }
    }
    const typing = /INPUT|TEXTAREA|SELECT/.test((document.activeElement || {}).tagName || "");
    if (typing || openSheet || e.ctrlKey || e.metaKey || e.altKey) return;
    if (e.key === "n" || e.key === "N") { e.preventDefault(); openItem(null); }
    if (e.key === "/") { e.preventDefault(); const q = $("#q"); if (q) q.focus(); }
  });

  // Atualiza quando a janela volta a ter foco e de 5 em 5 minutos (muda o dia, outros dispositivos)
  document.addEventListener("visibilitychange", () => { if (!document.hidden && !openSheet) load(true); });
  setInterval(() => { if (!document.hidden && !openSheet) load(true); }, 5 * 60 * 1000);

  load();
})();
