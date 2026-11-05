# Kit SOS

**🇵🇹 Português** · [🇬🇧 English](#english)

Uma app simples para gerir o kit de emergência (ou a despensa, ou os medicamentos): o que tens, quanto tens, onde está e quando expira. Avisa-te antes de as coisas passarem de validade.

## Primeiros passos

1. Inicia a app e liga **Mostrar na barra lateral**.
2. Abre **Kit SOS** na barra lateral.
3. Começa a adicionar artigos com o botão **Adicionar** (ou a tecla **N** no PC).
4. Se vens do Grocy: **Definições → Grocy**, escreve a chave API e carrega em **Verificar ligação** e depois **Importar**.

## Validades

- **Sem validade** – pilhas recarregáveis, lanternas, etc.
- **Mês e ano** – quando a embalagem só diz "03/2027". Conta como dia **01** desse mês.
- **Data exata** – quando tens o dia.

Cada lote com validade diferente é um artigo à parte. Usa **Duplicar (novo lote)** para criar um lote novo do mesmo produto em segundos.

## Avisos

Todos os dias, à **Hora do aviso**, a app vê os artigos que expiram dentro dos **Dias de antecedência** (por defeito 30) e envia **um aviso por artigo**. Cada validade só é avisada uma vez; se mudares a data, volta a avisar quando chegar a altura. Artigos com quantidade 0 não geram avisos.

Por defeito usa `telegram_bot.send_message` (com formatação Markdown). Também funciona com qualquer outra ação do Home Assistant, por exemplo `notify.mobile_app_iphone` ou `persistent_notification.create`.

Em **Definições → Avisos** podes enviar um aviso de teste ou forçar a verificação.

Além do aviso, a app dispara o evento `kit_sos_expiring` (com nome, validade, dias, quantidade, local e categoria), para quem quiser montar automações próprias.

## Sensores

| Sensor | O que mostra |
| --- | --- |
| `sensor.kit_sos_expiring` | Artigos a expirar dentro da antecedência configurada (lista nos atributos) |
| `sensor.kit_sos_expired` | Artigos fora de validade |
| `sensor.kit_sos_low_stock` | Artigos em falta ou abaixo do mínimo |
| `sensor.kit_sos_items` | Total de artigos com stock |

## Importar do Grocy

- Endereço: normalmente `http://a0d7b954-grocy` (a app oficial do Grocy no HA). Se não der, usa o IP interno do Grocy.
- Chave API: no Grocy, menu de utilizador → **Gerir chaves API** → **Adicionar**.
- Importa produtos, lotes (com as validades de cada um), grupos de produtos (ficam como categorias), locais, unidades, stock mínimo e descrições (ficam nas notas).
- Produtos inativos são ignorados. Produtos sem stock entram com quantidade 0 ("Em falta").
- Atenção: importar **substitui tudo** o que estiver no Kit SOS.

## Cópias de segurança

Os dados ficam dentro da app, por isso entram automaticamente nas cópias de segurança do Home Assistant. Em **Definições → Cópia** podes ainda exportar/restaurar um ficheiro JSON.

## Opções

| Opção | Por defeito | Descrição |
| --- | --- | --- |
| `language` | `auto` | `auto`, `pt` ou `en` |
| `notify_enabled` | `true` | Liga/desliga os avisos |
| `notify_days` | `30` | Dias de antecedência |
| `notify_time` | `10:00` | Hora diária da verificação |
| `notify_service` | `telegram_bot.send_message` | Ação usada para avisar |
| `notify_target` | vazio | Opcional: chat_id do Telegram ou outro destino |
| `sensors` | `true` | Cria os sensores |

---

<a name="english"></a>
## 🇬🇧 English

A simple app to keep track of your emergency kit (or pantry, or medicine cabinet): what you have, how much, where it is and when it expires — with an alert before things expire.

**Getting started:** start the app, enable **Show in sidebar**, open **Kit SOS** and add items with **Add** (or press **N**). Coming from Grocy? Go to **Settings → Grocy**, paste an API key, **Check connection**, then **Import** (this replaces everything in Kit SOS).

**Expiry dates:** *No expiry*, *Month & year* (counted as the 1st of that month) or *Exact date*. Each batch with a different date is a separate item — use **Duplicate (new batch)**.

**Alerts:** every day at `notify_time`, one alert per item expiring within `notify_days` (default 30), sent once per expiry date through `notify_service` (default `telegram_bot.send_message`; any Home Assistant action works). The `kit_sos_expiring` event is also fired.

**Sensors:** `sensor.kit_sos_expiring`, `sensor.kit_sos_expired`, `sensor.kit_sos_low_stock`, `sensor.kit_sos_items`.

**Backups:** data lives inside the app, so it is part of Home Assistant backups. You can also export/restore JSON from **Settings → Backup**.
