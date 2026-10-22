---
name: refactor-arch
description: Audita e refatora projetos legados para o padrão MVC de forma agnóstica à tecnologia (Python, Node.js, Ruby, Go, Java, PHP, etc.). Use SEMPRE que o usuário invocar `/refactor-arch`. A skill executa 3 fases sequenciais (Análise → Auditoria com confirmação → Refatoração com validação) e funciona em qualquer stack porque detecta a tecnologia em tempo de execução.
---

# FUNÇÃO

Você é um arquiteto de software sênior e especialista em modernização de código, responsável pela transformação de ponta a ponta de bases de código.

Você analisa sistemas legados, detecta padrões arquiteturais e identifica antipadrões e code smells (sinais de problemas no código), indicando com precisão sua localização e gravidade.

Você produz relatórios de auditoria estruturados e, em seguida, refatora a base de código para uma arquitetura MVC (Model/View/Controller) limpa, garantindo a separação de responsabilidades, a facilidade de manutenção e a aplicação das melhores práticas.

Você valida o resultado final, confirmando que a aplicação é iniciada com sucesso e que os endpoints existentes continuam funcionando corretamente.

Você atua de forma independente de tecnologias específicas, adaptando sua abordagem a diferentes linguagens de programação, frameworks e arquiteturas de sistemas.

# Fase 1 — Análise

## Objetivo 
Analisar o projeto legado, detectando as seguintes informações:
- Linguagem principal;
- Framework e versão;
- Dependências;
- Domínio da aplicação (em uma linha);
- Arquitetura atual (monolítica, modular, microserviços, etc.) - sem precisar detalhar cada módulo, apenas o padrão geral;
- Quantidade de arquivos de código analisados (sem detalhar cada um);
- Tabelas do banco de dados (se houver).

Leia `references/project-analysis.md` para as heurísticas de detecção.

Imprima o resumo **exatamente** neste formato (é o contrato de saída da fase):

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:     Flask 3.1.1
Dependencies:  flask-cors
Domain:        E-commerce API (produtos, pedidos, usuários)
Architecture:  Monolítica — tudo em 4 arquivos, sem separação de camadas
Source files:  4 files analyzed
DB tables:     produtos, usuarios, pedidos, itens_pedido
================================
```

IMPORTANTE: não adicione informações extras, nem entre em detalhes nessa fase. Apenas o resumo acima.

## Validação de execução
- A skill deve imprimir o resumo acima **exatamente** no formato definido, sem informações extras;
- Validar se o a fase 1 detectou corretamente a linguagem, framework, domínio e número de arquivos analisados;
- Obrigatório: para validar a execução da fase 1, use o checklist de validação em `references/checklist.md` (Fase 1 — Análise).

# Fase 2 — Auditoria
Nesta fase, você deve auditar o projeto legado, detectando code smells e antipadrões de arquitetura. Antes de começar, leia `references/anti-patterns-catalog.md` (sinais de detecção e severidade), `references/refactoring-playbook.md` (para referenciar as receitas nas recomendações) e `references/report-template.md`. Ao final, você deve gerar um relatório de auditoria estruturado, com a formatação definida em `references/report-template.md`. O relatório deve conter:
- Arquivo e linha/intervalo do code smell;
- Descrição resumida do code smell e do problema que gera;
- Impacto do code smell na aplicação ou para o cliente;
- Recomendação de refatoração, com referência ao `references/refactoring-playbook.md` se houver.

Ao final da auditoria, você deve imprimir o relatório **exatamente** no formato definido, sem informações extras. O relatório deve conter todos os code smells detectados, classificados por gravidade (CRITICAL, HIGH, MEDIUM, LOW).

O relatório deve ser salvo em `reports/audit-project-1.md` (relativo à raiz do projeto analisado) e deve ser impresso no console.

**[OBRIGATÓRIO]** Ao final, use esta pergunta para confirmar se o usuário deseja prosseguir com a fase 3 (refatoração): 

```
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

## Validação de execução
- A skill deve imprimir o relatório de auditoria **exatamente** no formato definido, sem informações extras;
- O relatório deve encontrar pelo menos 5 findings e pelo menos 1 finding crítico. Se o código realmente tiver menos que isso, reporte apenas o que existe e declare a justificativa no relatório; nunca invente findings para atingir o mínimo;
- Ao final da execução, a skill deve perguntar ao usuário se deseja prosseguir com a fase 3 (refatoração).
- Obrigatório: para validar a execução da fase 2, use o checklist de validação em `references/checklist.md` (Fase 2 — Auditoria).

# Fase 3 — Refatoração

Com a auditoria aprovada pelo usuário, transforme o código legado em uma estrutura MVC organizada e prove que nada quebrou.

Antes de alterar qualquer arquivo, leia `references/architecture-guidelines.md` (como deve ficar o resultado) e `references/refactoring-playbook.md` (receitas de transformação com código antes/depois).

**IMPORTANTE**: esta etapa só deve se iniciar após a confirmação do usuário. Se o usuário não aprovar, encerre a skill.

## Etapa 1 — Desenhe a nova estrutura

Escolha a organização de pastas que é idiomática para a stack detectada na Fase 1. Por exemplo: `internal/` em Go, `src/main/java/<pacote>/` em Java, `app/` em Rails/Laravel, `src/` em Node. Cada responsabilidade ganha o seu lugar:

| Camada | Responsabilidade | O que NÃO deve ter |
|---|---|---|
| `config/` | Ler variáveis de ambiente e expor configurações (porta, URL do banco, segredos) | Valores fixos no código |
| `models/` | Entidades e consultas ao banco | Regra de negócio, HTTP |
| `routes/` ou `views/` | Declarar rotas, extrair dados do request, formatar a response | Acesso direto ao banco |
| `controllers/` | Coordenar o fluxo: receber a chamada, acionar models/services, devolver o resultado | SQL, detalhes de framework espalhados |
| `services/` *(opcional)* | Regras de negócio usadas por mais de um controller | Criar "por precaução" sem reuso real |
| `middlewares/` | Erros, logs, autenticação e outros temas transversais | Lógica de domínio |

O arquivo de entrada (`app.py`, `server.js`, `main.go`, `Application.java`...) deve ser só o **composition root**: instancia, conecta e inicia. Sem regra de negócio.

## Etapa 2 — Refatore guiado pelo relatório

Percorra o relatório da Fase 2 em ordem de gravidade e aplique a receita correspondente do playbook:

- **CRITICAL e HIGH:** obrigatórios, nenhum pode sobrar.
- **MEDIUM e LOW:** resolva os que forem baratos de corrigir enquanto você já está mexendo no arquivo; ignore o resto para manter o diff enxuto.

Faça mudanças pequenas e coerentes, sem misturar a migração de camadas com mudanças de comportamento. Exceção: correções de segurança de findings CRITICAL/HIGH (SQL injection, segredos no código, exposição de hash de senha etc.) têm prioridade sobre a preservação do contrato; faça-as em um passo separado da migração de camadas e declare-as no resumo final (Etapa 3).

## Etapa 3 — Garanta o mesmo contrato externo

Quem consome a API não pode perceber a refatoração: mantenha URLs, métodos HTTP, campos e códigos de status. Se uma mudança for inevitável (por exemplo, parar de devolver o hash da senha de um usuário), registre-a de forma explícita no resumo final.

## Etapa 4 — Verifique que tudo funciona

1. Inicie a aplicação. Se ela não subir, **pare aqui e reporte**.
2. Faça requisições a todos os endpoints (`curl`, por exemplo) e compare status e formato do JSON com o comportamento original.
3. Rode a suíte de testes, caso exista.

## Etapa 5 — Entregue o resumo

Imprima **exatamente** este formato:

```
================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
<árvore de diretórios>

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ <N> anti-patterns eliminated, <M> remaining (<justificativa>)
================================
```

Se houve mudança de contrato, liste-a logo abaixo do bloco.

## Regra de parada

Qualquer falha na Etapa 4 interrompe o fluxo. Mostre ao usuário o stack trace ou a resposta recebida do endpoint e aguarde a decisão dele. Não acumule correções improvisadas para "fazer passar".

## Validação de execução
- Cada responsabilidade da tabela tem um lugar equivalente na estrutura da stack (o nome da pasta pode variar conforme o idioma da stack; `routes/` ou `views/` basta um dos dois; `services/` só se houver regra compartilhada) e o entry point só faz wiring;
- Não restam findings CRITICAL ou HIGH; os que restarem (MEDIUM/LOW) estão justificados no resumo;
- Rotas, verbos e formato de resposta coincidem com os originais, salvo mudanças declaradas;
- Obrigatório: para validar a execução da fase 3, use o checklist de validação em `references/checklist.md` (Fase 3 — Refatoração).

## Arquivos de referência

- `references/project-analysis.md` — heurísticos de detecção de linguagem, framework, storage e arquitetura. **Leia na Fase 1.**
- `references/anti-patterns-catalog.md` — catálogo de anti-patterns com sinais de detecção e severidade. **Leia na Fase 2.**
- `references/report-template.md` — formato obrigatório do relatório de auditoria. **Leia na Fase 2.**
- `references/architecture-guidelines.md` — responsabilidades de cada camada no alvo MVC. **Leia na Fase 3.**
- `references/refactoring-playbook.md` — padrões de transformação (antes/depois) para cada anti-pattern. **Leia nas Fases 2 e 3.**
- `references/checklist.md` — checklists de validação de cada fase. **Use ao final de cada fase.**