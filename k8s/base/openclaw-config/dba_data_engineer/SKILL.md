---
name: dba_data_engineer_schema
description: Skill DBA/DataEngineer para schema, migrations, otimização de queries e compliance LGPD
---

# Skills do DBA_DataEngineer

Use este documento como skill única para orientar design de schema, migrations e otimização.

---

## Criar Schema / Migration

Workflow:
1. Ler TASK-XXX.md e US-XXX.md para entender o modelo de dados necessário.
2. Pesquisar na web engines e padrões para o domínio (ex: time-series, documentos, relacional).
3. Projetar schema com ERD em Markdown/Mermaid.
4. Identificar dados pessoais → documentar data map LGPD.
5. Criar migration up + down com ferramentas do projeto.
6. Testar migration em dev: `migrate up` + validar dados + `migrate down` + validar rollback.
7. Documentar custo estimado de storage.
8. Persistir artefatos em `/data/openclaw/backlog/database/`.
9. Reportar ao Arquiteto com evidências (migration status, ERD, LGPD map).

---

## Otimizar Query

Workflow:
1. Capturar EXPLAIN PLAN da query problemática (before).
2. Identificar: full table scan, missing index, N+1, subquery ineficiente.
3. Propor e aplicar otimização (índice, reescrita, denormalização pontual).
4. Capturar EXPLAIN PLAN after + benchmark de latência p95.
5. Verificar que não há regressão em queries relacionadas.
6. Documentar decisão em ADR se for mudança de estrutura.
7. Reportar ao Dev_Backend e Arquiteto com evidências.

---

## Agendamento de 4h (Obrigatório)

1. A cada 4h (offset :30), consultar GitHub por issues abertas com label `dba`.
2. Se houver issue elegível, iniciar execução.
3. Se não houver, registrar standby e encerrar ciclo sem processamento desnecessário.
