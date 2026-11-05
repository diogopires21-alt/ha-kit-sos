# Changelog

## 1.0.0

- Primeira versão: artigos com quantidade, unidade, mínimo, categoria, local, validade (data exata ou só mês/ano) e notas.
- Importação do Grocy (produtos, lotes, validades, grupos, locais, unidades, stock mínimo).
- Avisos por artigo X dias antes da validade (Telegram ou qualquer ação do HA) e evento `kit_sos_expiring`.
- Sensores `sensor.kit_sos_expiring`, `sensor.kit_sos_expired`, `sensor.kit_sos_low_stock`, `sensor.kit_sos_items`.
- Exportar/restaurar cópia em JSON.
- Interface em Português e Inglês, modo claro/escuro.
