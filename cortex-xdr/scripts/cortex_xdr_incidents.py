#!/usr/bin/env python3
"""
cortex_xdr_incidents.py

Consulta a API REST do Cortex XDR (Palo Alto Networks) e devolve o numero de
incidentes que correspondem a um filtro. Pensado para ser consumido pelo Zabbix
(item "External check") ou enviado via zabbix_sender (item "Zabbix trapper").

Autenticacao: Advanced API Key (assinatura SHA256 por pedido).

Variaveis de ambiente (NUNCA colocar chaves no codigo nem no repositorio):
  CORTEX_API_KEY     - a Advanced API Key
  CORTEX_API_KEY_ID  - o ID da chave  (cabecalho x-xdr-auth-id)
  CORTEX_FQDN        - ex.: api-eu.xdr.paloaltonetworks.com

Exemplos:
  ./cortex_xdr_incidents.py --status new
  ./cortex_xdr_incidents.py --status new --severity critical
  ./cortex_xdr_incidents.py --discovery        # JSON de Low-Level Discovery
"""

import os
import sys
import json
import string
import secrets
import hashlib
import argparse
import urllib.request
from datetime import datetime, timezone

API_PATH = "/public_api/v1/incidents/get_incidents/"


def get_env(name):
    value = os.environ.get(name)
    if not value:
        sys.stderr.write("Variavel de ambiente em falta: %s\n" % name)
        sys.exit(1)
    return value


def build_headers(api_key, api_key_id):
    """Monta os cabecalhos de Advanced Authentication do Cortex XDR."""
    alphabet = string.ascii_letters + string.digits
    nonce = "".join(secrets.choice(alphabet) for _ in range(64))
    timestamp = str(int(datetime.now(timezone.utc).timestamp() * 1000))
    auth = hashlib.sha256((api_key + nonce + timestamp).encode("utf-8")).hexdigest()
    return {
        "x-xdr-auth-id": str(api_key_id),
        "x-xdr-nonce": nonce,
        "x-xdr-timestamp": timestamp,
        "Authorization": auth,
        "Content-Type": "application/json",
    }


def count_incidents(fqdn, headers, filters):
    """Devolve o total de incidentes que correspondem aos filtros."""
    url = "https://%s%s" % (fqdn, API_PATH)
    body = {
        "request_data": {
            "filters": filters,
            "search_from": 0,
            "search_to": 1,
            "sort": {"field": "modification_time", "keyword": "desc"},
        }
    }
    req = urllib.request.Request(
        url, data=json.dumps(body).encode("utf-8"), headers=headers, method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return int(data.get("reply", {}).get("total_count", 0))


def build_filters(status, severity):
    filters = []
    if status:
        filters.append({"field": "status", "operator": "eq", "value": status})
    if severity:
        filters.append({"field": "severity", "operator": "in", "value": [severity]})
    return filters


def main():
    parser = argparse.ArgumentParser(description="Cortex XDR -> Zabbix")
    parser.add_argument("--status", help="ex.: new, under_investigation, resolved")
    parser.add_argument("--severity", help="ex.: low, medium, high, critical")
    parser.add_argument(
        "--discovery",
        action="store_true",
        help="Devolve JSON de Low-Level Discovery por severidade",
    )
    args = parser.parse_args()

    if args.discovery:
        severities = ["low", "medium", "high", "critical"]
        print(json.dumps({"data": [{"{#SEVERITY}": s} for s in severities]}))
        return

    api_key = get_env("CORTEX_API_KEY")
    api_key_id = get_env("CORTEX_API_KEY_ID")
    fqdn = get_env("CORTEX_FQDN")

    headers = build_headers(api_key, api_key_id)
    filters = build_filters(args.status, args.severity)

    try:
        print(count_incidents(fqdn, headers, filters))
    except Exception as exc:  # noqa: BLE001
        # Em caso de erro devolve ZBX_NOTSUPPORTED-friendly e sai com codigo != 0
        sys.stderr.write("Erro ao consultar o Cortex XDR: %s\n" % exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
