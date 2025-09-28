import React, { useMemo, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { TrendingDown, Coins, Zap, Activity } from "lucide-react";
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  Legend,
} from "recharts";

// =====================================
// Mock de dados (troque pelo seu backend depois)
// Campos: nome, marca, categoria, preco, quantidade_valor, quantidade_unidade, quantidade (string)
// =====================================
const MOCK_DATA = [
  {
    nome: "Sérum Antioxidante",
    marca: "Sallve",
    categoria: "Sérum",
    preco: 89.9,
    quantidade_valor: 30,
    quantidade_unidade: "ml",
    quantidade: "30 ml",
  },
  {
    nome: "Hidratante Facial",
    marca: "Creamy",
    categoria: "Hidratante",
    preco: 59.9,
    quantidade_valor: 40,
    quantidade_unidade: "g",
    quantidade: "40 g",
  },
  {
    nome: "Vitamina C 10%",
    marca: "Ollie",
    categoria: "Sérum",
    preco: 79.9,
    quantidade_valor: 30,
    quantidade_unidade: "ml",
    quantidade: "30 ml",
  },
  {
    nome: "Gel de Limpeza",
    marca: "Beyoung",
    categoria: "Limpeza",
    preco: 49.9,
    quantidade_valor: 120,
    quantidade_unidade: "ml",
    quantidade: "120 ml",
  },
  {
    nome: "Sérum Niacinamida",
    marca: "Creamy",
    categoria: "Sérum",
    preco: 69.9,
    quantidade_valor: 30,
    quantidade_unidade: "ml",
    quantidade: "30 ml",
  },
  {
    nome: "Ácido Hialurônico",
    marca: "Sallve",
    categoria: "Hidratante",
    preco: 74.9,
    quantidade_valor: 40,
    quantidade_unidade: "g",
    quantidade: "40 g",
  },
];

// =====================================
// Paletas (exemplo). Troque pelos nomes e cores do seu arquivo de tema
// =====================================
const PALETTES = {
  "Rosa (Default)": ["#e75480", "#ff8fb1", "#ffc2d1", "#6b6b6b", "#2b2b2b"],
  "Lavanda": ["#6e56cf", "#8e7dff", "#cbbdff", "#6b6b6b", "#2b2b2b"],
  "Terrosos": ["#7b4f2c", "#b07f50", "#e0c3a1", "#7a7a7a", "#2b2b2b"],
};

function usePalette(name) {
  const seq = PALETTES[name] ?? PALETTES[Object.keys(PALETTES)[0]];
  const baseTheme = "Claro"; // poderia vir de contexto
  const pick = (i = 0) => seq[i % seq.length];
  const text = baseTheme === "Claro" ? "#111111" : "#f5f5f5";
  const sub = baseTheme === "Claro" ? "#555555" : "#cfcfcf";
  const panel = baseTheme === "Claro" ? "#ffffff" : "#1f1f1f";
  const border = baseTheme === "Claro" ? "#e6e6e6" : "#2a2a2a";
  return { seq, pick, text, sub, panel, border };
}

// Helpers
const brl = (x) => (x == null || Number.isNaN(x) ? "—" : x.toLocaleString("pt-BR", { style: "currency", currency: "BRL" }));
const pct = (x) => (x == null || Number.isNaN(x) ? "—" : `${(x * 100).toFixed(2)}%`);

function computeMostCommonUnit(rows) {
  const counts = rows.reduce((acc, r) => {
    const u = r.quantidade_unidade;
    if (!u) return acc;
    acc[u] = (acc[u] || 0) + 1;
    return acc;
  }, {});
  return Object.entries(counts).sort((a, b) => b[1] - a[1])[0]?.[0] ?? null;
}

function kBestCostPerUnit(rows) {
  return [...rows]
    .filter((r) => r.quantidade_valor && r.preco)
    .map((r) => ({ ...r, custo_por_unid: r.preco / r.quantidade_valor }))
    .sort((a, b) => a.custo_por_unid - b.custo_por_unid);
}

function groupStats(rows, key, dfCost) {
  const by = {};
  for (const r of rows) {
    const g = r[key];
    if (!by[g]) by[g] = { produtos: new Set(), preco: [] };
    by[g].produtos.add(r.nome);
    by[g].preco.push(r.preco);
  }
  const costBy = {};
  for (const r of dfCost) {
    const g = r[key];
    costBy[g] = costBy[g] || [];
    costBy[g].push(r.custo_por_unid);
  }
  return Object.entries(by).map(([g, v]) => ({
    chave: g,
    produtos: v.produtos.size,
    preco_medio: v.preco.reduce((a, b) => a + b, 0) / v.preco.length,
    preco_min: Math.min(...v.preco),
    preco_max: Math.max(...v.preco),
    custo_por_unid: costBy[g] ? costBy[g].reduce((a, b) => a + b, 0) / costBy[g].length : null,
  }));
}

function Panel({ children, style }) {
  return (
    <div className="rounded-2xl shadow-sm" style={style}>
      {children}
    </div>
  );
}

function KPI({ title, value, icon, color }) {
  return (
    <Card className="h-[110px]">
      <CardContent className="h-full flex items-center gap-3">
        <div className="text-xl" style={{ color }}>{icon}</div>
        <div className="leading-tight">
          <p className="text-xs opacity-80">{title}</p>
          <p className="text-2xl font-bold">{value}</p>
        </div>
      </CardContent>
    </Card>
  );
}

function ScatterTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  const r = payload[0].payload;
  return (
    <div className="rounded-md px-3 py-2 text-sm" style={{ background: "rgba(0,0,0,0.8)", color: "#fff" }}>
      <div className="font-semibold">{r.nome}</div>
      <div>{r.marca} • <span className="opacity-80">{r.categoria}</span></div>
      <div className="opacity-90">{brl(r.preco)} • {r.quantidade}</div>
    </div>
  );
}

export default function SkincareHome() {
  const [paletteName, setPaletteName] = useState(Object.keys(PALETTES)[0]);
  const { seq, pick, text, sub, panel, border } = usePalette(paletteName);

  // Filtros
  const marcas = useMemo(() => Array.from(new Set(MOCK_DATA.map((d) => d.marca))), []);
  const categorias = useMemo(() => Array.from(new Set(MOCK_DATA.map((d) => d.categoria))), []);
  const [selMarcas, setSelMarcas] = useState([]);
  const [selCats, setSelCats] = useState([]);

  const filtered = useMemo(() => {
    return MOCK_DATA.filter((r) => (selMarcas.length ? selMarcas.includes(r.marca) : true) && (selCats.length ? selCats.includes(r.categoria) : true));
  }, [selMarcas, selCats]);

  const precoMedio = useMemo(() => (filtered.length ? filtered.reduce((a, b) => a + b.preco, 0) / filtered.length : null), [filtered]);

  // Unidade referência
  const unitAuto = computeMostCommonUnit(filtered);
  const [unitOverride, setUnitOverride] = useState("(auto)");
  const unit = unitOverride === "(auto)" ? unitAuto : unitOverride;

  const dfCost = useMemo(() => {
    const base = filtered.filter((r) => r.quantidade_valor && r.quantidade_unidade);
    return unit ? base.filter((r) => r.quantidade_unidade === unit).map((r) => ({ ...r, custo_por_unid: r.preco / r.quantidade_valor })) : [];
  }, [filtered, unit]);

  const best = useMemo(() => (dfCost.length ? kBestCostPerUnit(dfCost) : []), [dfCost]);

  const variacao = useMemo(() => {
    if (!filtered.length) return null;
    const ps = filtered.map((r) => r.preco);
    const min = Math.min(...ps);
    const max = Math.max(...ps);
    return min > 0 ? (max - min) / min : null;
  }, [filtered]);

  const oportunidades = useMemo(() => {
    if (filtered.length < 4) return 0;
    const ps = filtered.map((r) => r.preco).sort((a, b) => a - b);
    const q25 = ps[Math.floor(0.25 * (ps.length - 1))];
    return filtered.filter((r) => r.preco <= q25).length;
  }, [filtered]);

  const scatterData = useMemo(() => {
    const rows = unit ? filtered.filter((r) => r.quantidade_unidade === unit) : [];
    return rows.filter((r) => r.quantidade_valor && r.preco);
  }, [filtered, unit]);

  const [compararPor, setCompararPor] = useState("marca");
  const grupos = useMemo(() => groupStats(filtered, compararPor, dfCost), [filtered, dfCost, compararPor]);

  // === Estilos básicos sem CSS global ===
  const panelStyle = { background: panel, border: `1px solid ${border}`, padding: 16 };

  return (
    <div className="p-6" style={{ color: text }}>
      {/* Header */}
      <div className="mb-2 flex items-center justify-between flex-wrap gap-3">
        <h1 className="text-3xl font-extrabold" style={{ color: pick(0) }}>Análise de Preços</h1>
        <div className="flex items-center gap-2">
          <label className="text-sm" style={{ color: sub }}>Paleta:</label>
          <select
            className="border rounded-md px-2 py-1 bg-transparent"
            value={paletteName}
            onChange={(e) => setPaletteName(e.target.value)}
            style={{ borderColor: border }}
          >
            {Object.keys(PALETTES).map((p) => (
              <option key={p} value={p}>{p}</option>
            ))}
          </select>
        </div>
      </div>
      <p className="-mt-1 mb-6" style={{ color: sub }}>
        Compare preços, encontre oportunidades e analise o custo-benefício dos produtos.
      </p>

      {/* Filtros */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4">
        <Panel style={panelStyle}>
          <div className="font-semibold mb-2" style={{ color: pick(0) }}>Categorias</div>
          <select
            multiple
            className="w-full border rounded-md min-h-[100px] p-2 bg-transparent"
            style={{ borderColor: border, color: text }}
            onChange={(e) => setSelCats(Array.from(e.target.selectedOptions).map((o) => o.value))}
          >
            {categorias.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </Panel>
        <Panel style={panelStyle}>
          <div className="font-semibold mb-2" style={{ color: pick(0) }}>Marcas</div>
          <select
            multiple
            className="w-full border rounded-md min-h-[100px] p-2 bg-transparent"
            style={{ borderColor: border, color: text }}
            onChange={(e) => setSelMarcas(Array.from(e.target.selectedOptions).map((o) => o.value))}
          >
            {marcas.map((m) => (
              <option key={m} value={m}>{m}</option>
            ))}
          </select>
        </Panel>
      </div>

      {/* Unidade */}
      <div className="mb-6">
        <div className="flex items-center gap-3">
          <div className="text-sm" style={{ color: sub }}>Unidade para métricas de custo:</div>
          <select
            className="border rounded-md px-2 py-1 bg-transparent"
            style={{ borderColor: border, color: text }}
            value={unitOverride}
            onChange={(e) => setUnitOverride(e.target.value)}
          >
            <option>(auto)</option>
            {Array.from(new Set(filtered.map((r) => r.quantidade_unidade).filter(Boolean)))
              .sort()
              .map((u) => (
                <option key={u}>{u}</option>
              ))}
          </select>
          <Badge variant="secondary" className="ml-1" style={{ background: pick(2), color: "#000" }}>
            atual: {unit ?? "—"}
          </Badge>
        </div>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-3 mb-6">
        <KPI title="Preço Médio" value={brl(precoMedio)} icon={<Coins />} color={pick(1)} />
        <KPI title={`Melhor custo/${unit ?? "—"}`} value={brl(best[0]?.custo_por_unid ?? null)} icon={<TrendingDown />} color={pick(2)} />
        <KPI title="Maior variação" value={pct(variacao)} icon={<Activity />} color={pick(3)} />
        <KPI title="Oportunidades" value={oportunidades} icon={<Zap />} color={pick(4)} />
      </div>

      {/* Scatter + Melhores ofertas */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
        <Panel style={{ ...panelStyle, gridColumn: "span 2 / span 2" }}>
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-xl font-bold" style={{ color: pick(0) }}>Relação Preço × Quantidade</h3>
            <div className="flex items-center gap-2">
              <div className="text-sm" style={{ color: sub }}>Colorir por:</div>
              <select className="border rounded-md px-2 py-1 bg-transparent" style={{ borderColor: border, color: text }} id="colorir-por">
                <option>marca</option>
                <option>categoria</option>
              </select>
            </div>
          </div>
          {scatterData.length === 0 ? (
            <div className="text-sm" style={{ color: sub }}>Sem dados suficientes para esta unidade.</div>
          ) : (
            <div className="h-[380px]">
              <ResponsiveContainer width="100%" height="100%">
                <ScatterChart margin={{ top: 10, right: 10, left: 0, bottom: 10 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke={border} />
                  <XAxis type="number" dataKey="quantidade_valor" name="Quantidade" unit={` ${unit ?? ""}`}
                         stroke={text} tick={{ fill: text }} tickLine={{ stroke: text }} axisLine={{ stroke: text }} />
                  <YAxis type="number" dataKey="preco" name="Preço" unit=" R$"
                         stroke={text} tick={{ fill: text }} tickLine={{ stroke: text }} axisLine={{ stroke: text }} />
                  <Tooltip content={<ScatterTooltip />} />
                  <Scatter data={scatterData} fill={pick(1)} />
                </ScatterChart>
              </ResponsiveContainer>
            </div>
          )}
        </Panel>

        <Panel style={panelStyle}>
          <h3 className="text-xl font-bold mb-2" style={{ color: pick(0) }}>⚡ Melhores Ofertas</h3>
          {best.slice(0, 3).map((r) => (
            <div key={r.nome + r.marca} className="rounded-lg p-3 mb-2 border"
                 style={{ borderColor: border, background: panel }}>
              <div className="flex items-center justify-between">
                <div className="font-semibold" style={{ color: text }}>{r.nome}</div>
                <span className="text-xs border rounded-full px-2 py-0.5" style={{ borderColor: border, color: text }}>{r.categoria}</span>
              </div>
              <div className="text-xs" style={{ color: sub }}>{r.marca}</div>
              <div className="text-sm mt-1" style={{ color: sub }}>{brl(r.preco)} • {r.quantidade}</div>
              <div className="font-semibold mt-1" style={{ color: pick(2) }}>{brl(r.custo_por_unid)}/{unit}</div>
            </div>
          ))}
        </Panel>
      </div>

      {/* Comparações */}
      <Panel style={{ ...panelStyle, marginBottom: 16 }}>
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-xl font-bold" style={{ color: pick(0) }}>Comparação entre Marcas/Categorias</h3>
          <div className="flex items-center gap-2">
            <div className="text-sm" style={{ color: sub }}>Comparar por:</div>
            <select
              className="border rounded-md px-2 py-1 bg-transparent"
              style={{ borderColor: border, color: text }}
              value={compararPor}
              onChange={(e) => setCompararPor(e.target.value)}
            >
              <option value="marca">marca</option>
              <option value="categoria">categoria</option>
            </select>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="h-[320px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={[...grupos].sort((a, b) => b.preco_medio - a.preco_medio)} margin={{ top: 10, right: 10, left: 0, bottom: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke={border} />
                <XAxis dataKey="chave" tick={{ fill: text }} stroke={text} angle={-15} height={60} />
                <YAxis tick={{ fill: text }} stroke={text} />
                <Tooltip formatter={(v, n) => (n.includes("preco") ? brl(v) : v)} />
                <Legend />
                <Bar dataKey="preco_medio" name="Preço médio" fill={pick(1)} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="h-[320px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={[...grupos].sort((a, b) => (a.custo_por_unid ?? Infinity) - (b.custo_por_unid ?? Infinity))} margin={{ top: 10, right: 10, left: 0, bottom: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke={border} />
                <XAxis dataKey="chave" tick={{ fill: text }} stroke={text} angle={-15} height={60} />
                <YAxis tick={{ fill: text }} stroke={text} />
                <Tooltip formatter={(v, n) => (n.includes("custo") ? brl(v) : v)} />
                <Legend />
                <Bar dataKey="custo_por_unid" name={`Custo médio/${unit ?? "unid"}`} fill={pick(2)} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </Panel>

      {/* Tabela */}
      <Panel style={panelStyle}>
        <h3 className="text-xl font-bold mb-2" style={{ color: pick(0) }}>Tabela Detalhada de Comparação</h3>
        {grupos.length === 0 ? (
          <div className="text-sm" style={{ color: sub }}>Aparece quando houver itens selecionados.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="text-left border-b" style={{ borderColor: border, color: sub }}>
                  <th className="py-2 pr-4">{compararPor === "marca" ? "Marca" : "Categoria"}</th>
                  <th className="py-2 pr-4">Produtos</th>
                  <th className="py-2 pr-4">Preço Médio</th>
                  <th className="py-2 pr-4">Menor Preço</th>
                  <th className="py-2 pr-4">Maior Preço</th>
                  <th className="py-2 pr-4">{`Custo/${unit ?? "unid"}`}</th>
                </tr>
              </thead>
              <tbody>
                {grupos.map((g) => (
                  <tr key={g.chave} className="border-b" style={{ borderColor: border }}>
                    <td className="py-2 pr-4">{g.chave}</td>
                    <td className="py-2 pr-4">{g.produtos}</td>
                    <td className="py-2 pr-4">{brl(g.preco_medio)}</td>
                    <td className="py-2 pr-4">{brl(g.preco_min)}</td>
                    <td className="py-2 pr-4">{brl(g.preco_max)}</td>
                    <td className="py-2 pr-4">{g.custo_por_unid == null ? "—" : brl(g.custo_por_unid)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Panel>

      <p className="mt-3 text-xs" style={{ color: sub }}>Dica: passe o mouse nos gráficos para ver detalhes. Esta é uma tela de exemplo em React com Tailwind, shadcn/ui e Recharts.</p>
    </div>
  );
}
