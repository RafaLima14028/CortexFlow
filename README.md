# Plataforma de RAG Completa

## Visão Geral

Uma plataforma completa de RAG (Retrieval-Augmented Generation) construída com:

- Python
- FastAPI
- Agno
- PostgreSQL
- pgvector/Qdrant
- Redis
- Docker
- Workers assíncronos

O objetivo do projeto é demonstrar:

- arquitetura backend moderna
- sistemas de IA em produção
- ingestão de documentos
- embeddings
- busca vetorial
- agentes de IA
- observabilidade
- processamento assíncrono
- streaming
- boas práticas de engenharia

---

# Objetivo do Projeto

Permitir que usuários:

1. enviem documentos
2. processem os arquivos
3. gerem embeddings
4. conversem com os documentos
5. obtenham respostas contextualizadas
6. acompanhem métricas e execuções

---

# Principais Funcionalidades

## Core

- Upload de documentos
- Processamento assíncrono
- Extração de texto
- Chunking
- Embeddings
- Busca vetorial
- Chat contextual
- Streaming de respostas
- Histórico de conversas
- Multiusuário
- API REST
- WebSockets

---

## IA

- Agentes com Agno
- RAG
- Ferramentas customizadas
- Memória curta
- Memória longa
- Query rewriting
- Re-ranking
- Context compression
- Citation/source tracking

---

## Engenharia

- Docker
- Docker Compose
- AsyncIO
- Workers
- Retry
- Logs estruturados
- Observabilidade
- Métricas
- Healthcheck
- Rate limiting
- Cache
- Testes
- CI/CD

---

# Arquitetura Ideal

```txt
                ┌──────────────────┐
                │      Cliente      │
                │ Web / Mobile/API │
                └────────┬─────────┘
                         │
                    HTTP/WebSocket
                         │
                ┌────────▼─────────┐
                │     FastAPI      │
                │   API Gateway    │
                └────────┬─────────┘
                         │
          ┌──────────────┼──────────────┐
          │              │              │
          ▼              ▼              ▼
   ┌──────────┐   ┌──────────┐   ┌──────────┐
   │ PostgreSQL│  │  Redis   │   │ VectorDB │
   │ Metadata │   │ Cache/Fila│  │ Embeddings│
   └──────────┘   └──────────┘   └──────────┘
          │                              │
          └──────────────┬───────────────┘
                         │
                  ┌──────▼──────┐
                  │   Workers   │
                  │ Background  │
                  └──────┬──────┘
                         │
                  ┌──────▼──────┐
                  │ Agentes IA  │
                  │    Agno     │
                  └─────────────┘
```

---

# Fluxo de Funcionamento

## Upload

```txt
Usuário envia arquivo
        ↓
FastAPI salva metadata
        ↓
Arquivo vai para storage
        ↓
Worker é acionado
        ↓
Texto é extraído
        ↓
Chunking
        ↓
Embeddings
        ↓
Salva no banco vetorial
        ↓
Documento pronto para chat
```

---

# Fluxo do Chat

```txt
Usuário faz pergunta
        ↓
Sistema gera embedding da pergunta
        ↓
Busca vetorial
        ↓
Re-ranking
        ↓
Monta contexto
        ↓
Agente responde
        ↓
Streaming da resposta
        ↓
Salva histórico
```

---

# Estrutura do Projeto

```txt
app/
├── api/
│   ├── v1/
│   ├── dependencies/
│   └── middlewares/
│
├── agents/
│   ├── rag/
│   ├── tools/
│   ├── memory/
│   └── prompts/
│
├── core/
│   ├── config/
│   ├── security/
│   ├── logging/
│   └── telemetry/
│
├── db/
│   ├── models/
│   ├── repositories/
│   ├── migrations/
│   └── session/
│
├── services/
│   ├── embeddings/
│   ├── chunking/
│   ├── extraction/
│   ├── reranking/
│   └── vector_search/
│
├── workers/
│   ├── ingestion/
│   ├── processing/
│   └── cleanup/
│
├── websocket/
├── schemas/
├── tests/
├── utils/
└── main.py
```

---

# Banco de Dados

## users

| Campo         | Tipo      |
| ------------- | --------- |
| id            | UUID      |
| name          | VARCHAR   |
| email         | VARCHAR   |
| password_hash | VARCHAR   |
| created_at    | TIMESTAMP |

---

## documents

| Campo        | Tipo      |
| ------------ | --------- |
| id           | UUID      |
| user_id      | UUID      |
| filename     | VARCHAR   |
| status       | VARCHAR   |
| storage_path | TEXT      |
| created_at   | TIMESTAMP |

Status:

- uploaded
- processing
- completed
- failed

---

## document_chunks

| Campo        | Tipo    |
| ------------ | ------- |
| id           | UUID    |
| document_id  | UUID    |
| chunk_index  | INTEGER |
| content      | TEXT    |
| token_count  | INTEGER |
| embedding_id | UUID    |

---

## chats

| Campo      | Tipo      |
| ---------- | --------- |
| id         | UUID      |
| user_id    | UUID      |
| title      | VARCHAR   |
| created_at | TIMESTAMP |

---

## messages

| Campo      | Tipo      |
| ---------- | --------- |
| id         | UUID      |
| chat_id    | UUID      |
| role       | VARCHAR   |
| content    | TEXT      |
| created_at | TIMESTAMP |

---

## agent_runs

| Campo       | Tipo      |
| ----------- | --------- |
| id          | UUID      |
| chat_id     | UUID      |
| latency_ms  | INTEGER   |
| token_usage | INTEGER   |
| model       | VARCHAR   |
| created_at  | TIMESTAMP |

---

# Banco Vetorial

## Opções

### pgvector

Prós:

- simples
- integrado ao PostgreSQL
- ótimo para começar

Contras:

- menor escalabilidade

---

### Qdrant

Prós:

- especializado
- rápido
- filtros avançados
- alta performance

Contras:

- infraestrutura separada

---

# Estratégia de Chunking

## Estratégia recomendada

### Chunk Size

```txt
500 ~ 1000 tokens
```

### Overlap

```txt
50 ~ 150 tokens
```

### Tipos

- recursive chunking
- semantic chunking
- markdown-aware chunking
- code-aware chunking

---

# Pipeline de Ingestão

## Etapas

### 1. Upload

- validação
- antivírus
- metadata

### 2. Extração

- PDF
- DOCX
- TXT
- CSV
- HTML

### 3. Limpeza

- remoção de caracteres
- normalização
- deduplicação

### 4. Chunking

### 5. Embeddings

### 6. Persistência

### 7. Indexação

---

# Sistema de Agentes

## Agente Principal

Responsável por:

- responder usuário
- coordenar ferramentas
- recuperar contexto

---

## Ferramentas

### Search Tool

Busca vetorial.

### Citation Tool

Rastreia fontes.

### Summarization Tool

Resume contexto.

### Query Rewriter

Melhora buscas.

---

# Segurança

## Implementar

- JWT
- RBAC
- rate limiting
- CORS
- validação de arquivos
- sanitização
- limites de upload
- proteção contra prompt injection

---

# Processamento Assíncrono

## Workers

### Funções

- embeddings
- OCR
- parsing
- limpeza
- reindexação

---

# API Endpoints

## Auth

```txt
POST   /auth/register
POST   /auth/login
POST   /auth/refresh
```

---

## Documents

```txt
POST   /documents/upload
GET    /documents
GET    /documents/{id}
DELETE /documents/{id}
```

---

## Chat

```txt
POST   /chat
GET    /chat/{id}
GET    /chat
WS     /chat/stream
```

---

## Models

```txt
GET /models/embeddings
GET /models/rerancking
GET /models/chat
```

---

# Variáveis de Ambiente

```env
DATABASE_URL=
REDIS_URL=
OPENAI_API_KEY=
QDRANT_URL=
JWT_SECRET=
S3_ENDPOINT=
LOG_LEVEL=
```

---

# Roadmap

# MVP

- [x] Upload de arquivos
- [x] Extração de texto
- [x] Listar os modelos de rerank
- [x] Listar os modelos de embeddings
- [x] Listar os modelos de textos
- [x] Criar usuário
- [x] JWT (Multi-usários)
- [x] Chunking
- [x] Embeddings
- [x] Chat básico
- [x] Streaming (WebSocket)
- [ ] Busca vetorial
- [ ] Chat RAG

---

# V1

- [ ] Histórico
- [ ] Redis cache
- [ ] Workers
- [ ] Retry
- [ ] Logs estruturados
- [ ] Métricas

---

# V2

- [ ] Multiagentes
- [ ] Re-ranking
- [ ] Query rewriting
- [ ] Context compression
- [ ] Memória longa

---

# V3

- [ ] Dashboard
- [ ] Analytics

---

# Tecnologias Recomendadas

| Categoria | Tecnologia |
| --------- | ---------- |
| API       | FastAPI    |
| IA        | Agno       |
| Banco     | PostgreSQL |
| Vetorial  | Qdrant     |
| Cache     | Redis      |
| ORM       | SQLAlchemy |

---

# Diferenciais Que Impressionam Empresas

## Muito fortes

- streaming de resposta
- tracing
- observabilidade
- retry automático
- arquitetura assíncrona
- documentação excelente
- testes
- docker compose completo
- métricas de IA
- multiagentes

---

# Futuras Expansões

## Possíveis ideias

- agentes autônomos
- integração Slack
- integração Discord
- integração WhatsApp
- busca híbrida
- fine-tuning
- knowledge graph
- multimodal
- OCR avançado
- voice RAG

---

# README Profissional

## O README deve conter

- objetivo
- arquitetura
- imagens
- GIFs
- fluxo
- instalação
- exemplos
- endpoints
- stack
- decisões técnicas
- roadmap
- benchmarks

---

# Estrutura de Commits

```txt
feat:
fix:
refactor:
docs:
test:
chore:
```

---

# Objetivo Final

Criar uma plataforma que pareça:

- produto real
- SaaS moderno
- sistema enterprise
- arquitetura escalável
- solução de IA em produção

Esse tipo de projeto muda completamente como recrutadores enxergam um desenvolvedor júnior.
