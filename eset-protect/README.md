# ESET PROTECT — Gestão e Visibilidade de Endpoints

Este projeto documenta a utilização do **ESET PROTECT** como plataforma centralizada para gestão, monitorização e controlo de segurança dos endpoints de uma organização.

O ESET PROTECT permite administrar computadores e servidores protegidos por soluções como o **ESET Endpoint Security**, oferecendo visibilidade sobre o estado dos dispositivos, deteções de segurança, versões instaladas, políticas aplicadas e falhas de comunicação.

## Objetivo

Centralizar a gestão da segurança dos endpoints e facilitar a identificação de dispositivos:

- desatualizados;
- sem proteção ativa;
- sem comunicação com a consola;
- fora das políticas definidas;
- com ameaças ou deteções não resolvidas;
- com versões antigas dos componentes de segurança.

## Arquitetura simplificada

```text
[ESET PROTECT]
       |
       | Políticas, tarefas e recolha de dados
       |
[ESET Management Agent]
       |
       | Comunicação com a consola
       |
[ESET Endpoint Security]
       |
[Computador ou servidor protegido]
```

O **ESET Management Agent** faz a comunicação entre os dispositivos geridos e a plataforma ESET PROTECT. Por meio dessa comunicação, a consola recebe informações operacionais e envia políticas, configurações e tarefas remotas.

## Gestão centralizada

A plataforma permite:

- criar e aplicar políticas de segurança;
- organizar dispositivos por grupos;
- instalar e atualizar produtos ESET;
- executar tarefas remotamente;
- verificar versões dos componentes;
- controlar configurações dos endpoints;
- acompanhar o estado de proteção dos equipamentos;
- gerar relatórios técnicos e operacionais.

## Visibilidade de segurança

Os painéis e relatórios podem apresentar informações como:

- endpoints geridos, protegidos ou sem agente;
- deteções abertas e respetiva gravidade;
- equipamentos com maior número de incidentes;
- falhas de atualização;
- dispositivos sem comunicação;
- estado dos componentes de segurança;
- nível de conformidade com as políticas internas.

Essa visibilidade ajuda a equipa de segurança a priorizar incidentes, identificar falhas de cobertura e manter um inventário atualizado dos dispositivos protegidos.

## Fluxo operacional

```text
1. O endpoint comunica com o ESET PROTECT.
2. O agente envia o estado do dispositivo e eventos de segurança.
3. A consola apresenta deteções, falhas e informações de conformidade.
4. O administrador analisa o evento.
5. Uma política ou tarefa remota pode ser aplicada.
6. O resultado é registado e acompanhado pela consola.
```

## Monitorização complementar

O ESET PROTECT é direcionado para a gestão da segurança dos endpoints. Ele pode complementar plataformas de infraestrutura e monitorização, como:

- Zabbix;
- PRTG;
- Grafana;
- Prometheus;
- sistemas SIEM;
- plataformas de gestão de incidentes.

Exemplo de utilização conjunta:

```text
Zabbix          → disponibilidade, desempenho e conectividade
ESET PROTECT    → proteção, deteções e conformidade dos endpoints
SIEM            → correlação de eventos e investigação de incidentes
GitHub          → documentação, scripts e controlo de versões
```

## Indicadores recomendados

Alguns indicadores úteis para acompanhamento:

| Indicador | Objetivo |
|---|---|
| Endpoints protegidos | Confirmar a cobertura da solução |
| Dispositivos sem comunicação | Identificar agentes inativos |
| Deteções não resolvidas | Priorizar incidentes de segurança |
| Versões desatualizadas | Reduzir riscos e incompatibilidades |
| Políticas aplicadas | Verificar conformidade |
| Falhas de atualização | Identificar problemas operacionais |
| Equipamentos não geridos | Localizar falhas de cobertura |

## Boas práticas

- Utilizar grupos para separar servidores, estações e departamentos.
- Aplicar políticas com base no perfil e criticidade do dispositivo.
- Rever regularmente deteções não resolvidas.
- Monitorizar endpoints sem comunicação.
- Manter agentes e produtos de segurança atualizados.
- Limitar o acesso administrativo por função.
- Utilizar autenticação multifator nas contas administrativas.
- Registar alterações relevantes e procedimentos operacionais.
- Não armazenar credenciais, tokens ou chaves privadas neste repositório.

## Estrutura sugerida do repositório

```text
cyber-security/
├── README.md
├── docs/
│   ├── arquitetura.md
│   ├── procedimentos.md
│   └── resposta-a-incidentes.md
├── policies/
│   └── exemplos-de-politicas.md
├── scripts/
│   └── automacoes/
├── reports/
│   └── modelos/
└── diagrams/
    └── arquitetura-eset-protect.png
```

## Segurança das informações

Este repositório não deve conter:

- palavras-passe;
- tokens de API;
- chaves privadas;
- ficheiros de configuração com segredos;
- dados pessoais de utilizadores;
- nomes reais de equipamentos internos;
- endereços IP públicos ou internos sensíveis;
- relatórios contendo informações confidenciais.

Sempre que necessário, utilize dados fictícios, variáveis de ambiente e mecanismos próprios para gestão de segredos.

## Referências

- [Documentação oficial do ESET PROTECT](https://help.eset.com/protect_cloud/)
- [Gestão de aplicações Endpoint](https://help.eset.com/protect_cloud/en-US/manage_endpoint.html)
- [Dashboard do ESET PROTECT](https://help.eset.com/protect_cloud/en-US/dashboard.html)
- [Deteções no ESET PROTECT](https://help.eset.com/protect_cloud/en-US/threats.html)

---

> Este conteúdo tem finalidade técnica e documental. As funcionalidades disponíveis podem variar de acordo com a edição, licença e arquitetura utilizada.
