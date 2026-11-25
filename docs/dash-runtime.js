/* Minimal runtime that gives the dashboard page the same `dash` API it uses in Claude:
   dash.calc / dash.data / dash.draw / dash.onData / dash.params / dash.setParams / dash.resetParams.
   Data comes from the CSV files in ./data. */
(function () {
  const FILES = {
    cube: 'data/cube.csv', reasons_main: 'data/reasons_main.csv', reasons_detail: 'data/reasons_detail.csv',
    shops: 'data/shops.csv', tat: 'data/tat.csv', staff: 'data/staff.csv'
  };
  const DEFAULTS = { month: '', rr: '', region: '', shop: '' };
  const raw = {}; const state = {}; const calcs = {}; const draws = {}; const dataFns = [];
  let params = Object.assign({}, DEFAULTS); let cache = {}; let ready = false; let pending = false;

  function data(id) {
    if (calcs[id]) {
      if (id in cache) return cache[id];
      const c = calcs[id]; const ins = c.inputs.map(data);
      const bad = ins.find((x) => x.status !== 'ok');
      if (bad) return { status: bad.status, data: null, message: bad.message };
      try { cache[id] = { status: 'ok', data: c.fn(...ins.map((x) => x.data)) }; }
      catch (e) { console.error('calc', id, e); cache[id] = { status: 'error', data: null, message: String(e) }; }
      return cache[id];
    }
    if (state[id] === 'ok') return { status: 'ok', data: raw[id] };
    if (state[id] === 'error') return { status: 'error', data: [], message: 'โหลดไฟล์ไม่สำเร็จ' };
    if (!FILES[id]) return { status: 'missing', data: [] };
    return { status: 'loading', data: [] };
  }
  function runDraw(name) {
    const fn = draws[name]; if (!fn) return;
    document.querySelectorAll('[data-draw="' + name + '"]').forEach((el) => {
      if (el.closest('[hidden]')) return;
      try { fn(el); } catch (e) { console.error('draw', name, e); }
    });
  }
  function render() {
    pending = false; if (!ready) return;
    dataFns.forEach((fn) => { try { fn(); } catch (e) { console.error(e); } });
    Object.keys(draws).forEach(runDraw);
  }
  function schedule() { if (!pending) { pending = true; requestAnimationFrame(render); } }

  window.dash = {
    colors: ['var(--c1)', 'var(--c2)', 'var(--c3)', 'var(--c4)', 'var(--c5)', 'var(--c6)', 'var(--c7)'],
    calc(id, o) { calcs[id] = o; },
    loader() {},
    data,
    params: () => Object.assign({}, params),
    setParams(p) { Object.assign(params, p); cache = {}; schedule(); },
    resetParams() { params = Object.assign({}, DEFAULTS); cache = {}; schedule(); },
    setLink() {},
    refresh() {},
    onData(fn) { dataFns.push(fn); },
    draw(name, fn) { if (fn) { draws[name] = fn; } else { runDraw(name); } }
  };

  Object.entries(FILES).forEach(([id, url]) => {
    fetch(url).then((r) => { if (!r.ok) throw new Error(r.status); return r.text(); })
      .then((t) => { raw[id] = d3.csvParse(t); state[id] = 'ok'; })
      .catch(() => { state[id] = 'error'; })
      .finally(() => { cache = {}; schedule(); });
  });
  document.addEventListener('DOMContentLoaded', () => { ready = true; schedule(); });
  let w = 0; window.addEventListener('resize', () => { if (Math.abs(window.innerWidth - w) > 20) { w = window.innerWidth; schedule(); } });
})();
