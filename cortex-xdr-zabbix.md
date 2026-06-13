# Integração Cortex XDR (Palo Alto Networks) com Zabbix

Documento técnico que descreve uma forma de integrar o **Cortex XDR** com o **Zabbix**, permitindo que indicadores de segurança (incidentes abertos, por gravidade e por estado) sejam monitorizados, alertados e visualizados junto da restante infraestrutura.

> Validado com **Zabbix 7.0 LTS** e a **Cortex XDR REST API** (autenticação *Advanced*).

---

## Objetivo

O Cortex XDR concentra deteções e incidentes de segurança; o Zabbix concentra a monitorização operacional da infraestrutura. Ao ligar os dois, a equipa passa a ter, num único painel:

- número de incidentes **novos** por gravidade (low, medium, high, critical);
- alertas automáticos quando surge um incidente **crítico**;
- histórico e tendência do volume de incidentes ao longo do tempo;
- correlação visual entre eventos de segurança e o estado da infraestrutura.

O resultado prático: **menor tempo de deteção e de resposta a incidentes**, porque o sinal de segurança aparece no mesmo sítio onde a operação já é vigiada 24/7.

---

## Arquitetura simplificada

```
            HTTPS (REST API, Advanced Auth)
[Zabbix Server] ──────────────────────────────► [Cortex XDR Tenant]
       │  script externo / zabbix_sender                 │
       │                                                  │
       ▼                                                  ▼
[Itens, triggers, dashboards]                   [Incidentes e alertas]
```

O Zabbix consulta periodicamente a API do Cortex XDR através de um **script externo** em Python. O script autentica-se, conta os incidentes que correspondem a um filtro e devolve o valor ao Zabbix.

---

## Pré-requisitos

- Servidor Zabbix operacional (server + frontend) com Python 3 instalado.
- Acesso ao tenant Cortex XDR com permissão para criar API Keys.
- Ligação HTTPS (porta 443) do servidor Zabbix para o FQDN da API do Cortex.

---

## Passo 1 — Criar a API Key no Cortex XDR

Na consola do Cortex XDR: **Settings → Configurations → Integrations → API Keys → + New Key**.

- **Security level**: `Advanced` (assina cada pedido e previne *replay attacks*).
- **Role**: `Viewer` (princípio do menor privilégio — apenas leitura).
- Gerar e guardar:
  - a **API Key** (a chave em si);
  - o **ID** correspondente (será o cabeçalho `x-xdr-auth-id`).

Anote também o **FQDN da API** do seu tenant, no formato `api-<região>.xdr.paloaltonetworks.com`.

> **Nunca** guarde estes valores no repositório nem no código. Use variáveis de ambiente.

---

## Passo 2 — Autenticação (Advanced)

A autenticação *Advanced* exige quatro cabeçalhos em cada pedido:

| Cabeçalho | Conteúdo |
|---|---|
| `x-xdr-auth-id` | ID da API Key |
| `x-xdr-timestamp` | hora UTC atual em milissegundos |
| `x-xdr-nonce` | string aleatória de 64 caracteres alfanuméricos |
| `Authorization` | `SHA256( API_KEY + NONCE + TIMESTAMP )` em hexadecimal |

O script incluído ([`scripts/cortex_xdr_incidents.py`](scripts/cortex_xdr_incidents.py)) já implementa esta lógica.

---

## Passo 3 — Endpoint utilizado

```
POST https://<FQDN>/public_api/v1/incidents/get_incidents/
```

Corpo do pedido (exemplo — incidentes novos de gravidade crítica):

```json
{
  "request_data": {
    "filters": [
      { "field": "status",   "operator": "eq", "value": "new" },
      { "field": "severity", "operator": "in", "value": ["critical"] }
    ],
    "search_from": 0,
    "search_to": 1,
    "sort": { "field": "modification_time", "keyword": "desc" }
  }
}
```

A resposta traz `reply.total_count` com o número total de incidentes que correspondem ao filtro — é esse o valor que o script devolve ao Zabbix.

> Os nomes de campos/operadores seguem a documentação da Cortex XDR API e podem variar ligeiramente conforme a versão do tenant. Valide sempre com um pedido de teste.

---

## Passo 4 — Instalar o script no Zabbix

Copie o script para a pasta de *external scripts* (definida em `ExternalScripts` no `zabbix_server.conf`, por predefinição `/usr/lib/zabbix/externalscripts/`):

```bash
sudo cp scripts/cortex_xdr_incidents.py /usr/lib/zabbix/externalscripts/
sudo chown zabbix:zabbix /usr/lib/zabbix/externalscripts/cortex_xdr_incidents.py
sudo chmod 750 /usr/lib/zabbix/externalscripts/cortex_xdr_incidents.py
```

Disponibilize as credenciais como variáveis de ambiente do serviço Zabbix (ex.: através de um *drop-in* do systemd em `/etc/systemd/system/zabbix-server.service.d/cortex.conf`):

```ini
[Service]
Environment="CORTEX_API_KEY=__a_sua_chave__"
Environment="CORTEX_API_KEY_ID=42"
Environment="CORTEX_FQDN=api-eu.xdr.paloaltonetworks.com"
```

Depois: `sudo systemctl daemon-reload && sudo systemctl restart zabbix-server`.

### Testar antes de configurar o Zabbix

```bash
export CORTEX_API_KEY=__a_sua_chave__
export CORTEX_API_KEY_ID=42
export CORTEX_FQDN=api-eu.xdr.paloaltonetworks.com

python3 cortex_xdr_incidents.py --status new --severity critical
# saída esperada: um número (ex.: 3)
```

Se devolver um número, a integração está pronta.

---

## Passo 5 — Configurar os itens no Zabbix

Crie um host (ex.: `Cortex-XDR`) sem interface, ou use um host de "serviços". Em **Items**:

| Nome | Tipo | Chave |
|---|---|---|
| Incidentes novos — críticos | External check | `cortex_xdr_incidents.py["--status","new","--severity","critical"]` |
| Incidentes novos — high | External check | `cortex_xdr_incidents.py["--status","new","--severity","high"]` |
| Incidentes novos — total | External check | `cortex_xdr_incidents.py["--status","new"]` |

- **Type of information**: `Numeric (unsigned)`
- **Update interval**: `5m` (respeite os limites de *rate* da API; evite intervalos muito curtos)

> Em ambientes com muitos itens, prefira um único pedido à API e o envio dos valores via `zabbix_sender` para itens do tipo **Zabbix trapper**. Assim reduz o número de chamadas e não bloqueia os *pollers*.

### Descoberta automática por gravidade (opcional)

O script suporta `--discovery`, devolvendo um JSON de Low-Level Discovery com `{#SEVERITY}`. Pode usá-lo numa *discovery rule* para criar automaticamente um item por gravidade, com um *item prototype*:

- **Key**: `cortex_xdr_incidents.py["--status","new","--severity","{#SEVERITY}"]`

---

## Passo 6 — Triggers recomendadas

```
# Incidente crítico em aberto
last(/Cortex-XDR/cortex_xdr_incidents.py["--status","new","--severity","critical"]) > 0
  → Severity: Disaster

# Acumulação de incidentes high
last(/Cortex-XDR/cortex_xdr_incidents.py["--status","new","--severity","high"]) >= 5
  → Severity: High

# A API deixou de responder (sem dados)
nodata(/Cortex-XDR/cortex_xdr_incidents.py["--status","new"],15m) = 1
  → Severity: Warning
```

Ligue as triggers às ações de notificação do Zabbix (e-mail, Telegram, webhook) para encaminhar o alerta à equipa de resposta.

---

## Método alternativo — Syslog / reenvio de logs

Quando não se pretende consultar a API, o Cortex XDR pode **reenviar alertas e incidentes via syslog** para um coletor. O Zabbix monitoriza então o ficheiro de log com um item do tipo `log[]` e dispara triggers por padrão (ex.: `severity=critical`).

Este método é útil para integração quase em tempo real, mas dá menos controlo sobre contagens e filtros do que a via API. As duas abordagens podem coexistir: syslog para reação imediata, API para indicadores e tendências.

---

## Boas práticas de segurança

- Use uma API Key com *role* **Viewer** (apenas leitura).
- Guarde as credenciais em **variáveis de ambiente** ou num gestor de segredos — nunca no repositório.
- Restrinja, se possível, os IPs de origem com acesso à API.
- Respeite os limites de *rate* da API (intervalos de 5 minutos são, em geral, suficientes).
- Rode (*rotate*) as chaves periodicamente e revogue as que não são usadas.
- Não registe a chave nos logs do script.

---

## Estrutura

```
cortex-xdr/
├── cortex-xdr-zabbix.md            # este documento
└── scripts/
    └── cortex_xdr_incidents.py     # consulta a API e devolve a contagem ao Zabbix
```

---

## Referências

- Cortex XDR REST API — visão geral: https://docs-cortex.paloaltonetworks.com/r/Cortex-XDR-REST-API
- Itens "External check" no Zabbix: https://www.zabbix.com/documentation/current/en/manual/config/items/itemtypes/external
- Low-Level Discovery no Zabbix: https://www.zabbix.com/documentation/current/en/manual/discovery/low_level_discovery

---

*Conteúdo com finalidade técnica e documental. Os campos, operadores e funcionalidades da API podem variar conforme a edição e a versão do tenant Cortex XDR. Utilize sempre dados fictícios nos exemplos e mecanismos próprios de gestão de segredos.*
