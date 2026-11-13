# Aplica-o-Akinator-Snes-Sistema-de-identifica-o-de-Jogos-atrav-s-de-perguntas-e-respostas.
# Aplicação Akinator SNES
### Sistema de Identificação de Jogos através de Perguntas e Respostas

**Equipe:** Júlio de Almeida Prazeres

## 1. Objetivo Geral

Desenvolver uma aplicação web com o objetivo de ajudar usuários a recordar e identificar jogos da plataforma Super Nintendo Entertainment System (SNES), utilizando um sistema interativo de perguntas e respostas.

A escolha do SNES como objeto de estudo se deve à sua biblioteca de jogos amplamente documentada, permitindo o levantamento e a organização de informações de maneira estruturada e rastreável.

A identificação dos jogos será realizada por meio de características como:

- Perspectiva e visão do jogador;
- Estilo e tipo de arte;
- Gênero ou categoria do jogo;
- Paleta de cores predominante;
- Características visuais e mecânicas;
- Outras propriedades relevantes para a identificação.

## 2. Etapas de Desenvolvimento

O projeto será dividido inicialmente em três etapas principais:

### 2.1. Coleta de Dados — Web Scraping

Utilização de Python para coleta automatizada de informações sobre jogos de SNES em fontes públicas e documentadas.

Os dados coletados serão tratados, organizados e preparados para armazenamento.

### 2.2. Modelagem e Criação do Banco de Dados

Desenvolvimento de um banco de dados relacional para armazenar as informações dos jogos e suas respectivas características.

Essa estrutura permitirá realizar consultas, comparações e filtros durante o processo de identificação.

### 2.3. Sistema de Tomada de Decisões

Desenvolvimento da lógica responsável por conduzir a identificação dos jogos.

O sistema utilizará as respostas fornecidas pelo usuário para comparar características e reduzir progressivamente o conjunto de jogos candidatos.

A busca começará de maneira abrangente e se tornará cada vez mais específica conforme as respostas forem fornecidas.

## 3. Lógica de Funcionamento

A primeira versão da aplicação não utilizará Inteligência Artificial ou modelos de Machine Learning.

O mecanismo de identificação será baseado em:

- Comparação de características;
- Consultas ao banco de dados;
- Aplicação de filtros progressivos;
- Eliminação de possibilidades incompatíveis com as respostas.

Dessa forma, o sistema buscará identificar o jogo mais compatível com as características informadas pelo usuário.

## 4. Perspectivas Futuras

A implementação de técnicas de Machine Learning está prevista como uma possibilidade de evolução do projeto.

Entretanto, essas técnicas não farão parte da primeira versão.

A prioridade inicial será construir uma aplicação funcional, com uma base de dados consistente e uma lógica de identificação compreensível, permitindo futuras expansões e melhorias.

## 5. Status do Projeto

<em>Em planejamento e desenvolvimento.</em>

O desenvolvimento será realizado de maneira incremental, priorizando a construção e validação de cada etapa antes da integração com as demais.
