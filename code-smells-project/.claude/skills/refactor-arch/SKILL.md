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