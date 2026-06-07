# Lumie RAG chatbot - re-evaluation report

Test units: **200** | Seeds: **[13, 21, 42]** | Judge/decomposer: **gpt-4o-mini** (temp 0.2)
Metrics: atomic Precision/Recall/F1 (vs. the gold answer) and FactScore (grounding vs. the official corpus). All values are percentages, mean ± std across seeds.

## 1. Overall results

| Slice     | Precision   | Recall      | F1          | FactScore   | n   |
|-----------|-------------|-------------|-------------|-------------|-----|
| Overall   | 57.7 ± 0.4  | 31.2 ± 0.4  | 35.4 ± 0.4  | 73.0 ± 0.6  | 200 |
| lang = en | 45.6 ± 38.9 | 24.3 ± 29.8 | 26.4 ± 32.5 | 61.8 ± 40.1 | 126 |
| lang = pt | 60.9 ± 36.0 | 33.1 ± 29.4 | 37.9 ± 31.6 | 76.0 ± 32.9 | 474 |

## 2. What the numbers say

Overall the chatbot reaches an F1 of 35.4 (precision 57.7, recall 31.2) and a FactScore of 73.0. Grounding is weak: about 27% of asserted facts are unsupported by the corpus - hallucination is a real problem and is the first thing to fix. FactScore (73.0) is clearly higher than precision-vs-gold (57.7). That gap means the bot adds true, corpus-grounded details that are not in the short canonical answer - i.e. it is verbose rather than wrong. This is a style issue, not a factual one. Recall is low (31.2): the bot omits a large share of the facts the gold answer contains. In a RAG system this usually points to retrieval gaps - the right chunk was not retrieved or not used. See the missing facts in section 5. Results are stable across seeds (low standard deviation), so the scores are reliable.

## 3. Performance by intent (weakest first)

| Intent                                    | Precision   | Recall      | F1          | FactScore   | n  |
|-------------------------------------------|-------------|-------------|-------------|-------------|----|
| Calendario / datas                        | 11.8 ± 13.7 | 0.0 ± 0.0   | 0.0 ± 0.0   | 63.1 ± 28.0 | 18 |
| Fases e estrutura das provas              | 44.2 ± 31.2 | 9.5 ± 10.6  | 10.0 ± 10.5 | 72.4 ± 23.3 | 18 |
| Recursos de questao                       | 21.1 ± 18.2 | 8.3 ± 14.4  | 10.0 ± 17.3 | 85.6 ± 10.2 | 12 |
| Cadastro da escola pelo INEP              | 34.7 ± 29.0 | 18.8 ± 10.8 | 12.6 ± 15.3 | 100.0 ± 0.0 | 12 |
| Responder todas as questoes               | 23.1 ± 19.5 | 15.0 ± 26.0 | 13.6 ± 23.6 | 56.1 ± 41.1 | 12 |
| Composicao da equipe                      | 27.8 ± 28.3 | 27.8 ± 12.4 | 14.1 ± 19.9 | 88.9 ± 20.8 | 18 |
| Certificados                              | 30.0 ± 26.7 | 11.4 ± 10.7 | 16.0 ± 14.1 | 70.0 ± 26.7 | 15 |
| Temas e ODS das questoes                  | 42.1 ± 22.7 | 17.8 ± 21.0 | 16.5 ± 15.1 | 7.5 ± 9.0   | 18 |
| Diretrizes de elaboracao de questoes      | 31.2 ± 36.0 | 15.2 ± 15.8 | 17.4 ± 16.7 | 35.2 ± 46.0 | 18 |
| Inscricao exclusivamente online           | 30.0 ± 40.0 | 17.3 ± 32.2 | 19.6 ± 35.5 | 90.0 ± 20.0 | 15 |
| Corrigir dados da escola                  | 58.3 ± 48.0 | 14.8 ± 17.1 | 21.7 ± 24.4 | 71.1 ± 21.5 | 15 |
| Envio de respostas                        | 73.6 ± 27.1 | 16.7 ± 16.7 | 22.3 ± 22.6 | 77.5 ± 22.8 | 12 |
| Quem pode ser professor orientador        | 47.0 ± 27.3 | 17.8 ± 14.2 | 24.0 ± 19.0 | 100.0 ± 0.0 | 15 |
| Minimo de membros na presencial           | 33.3 ± 20.4 | 25.0 ± 25.0 | 25.0 ± 25.0 | 41.7 ± 38.2 | 12 |
| Questao anulada                           | 25.0 ± 43.3 | 25.0 ± 43.3 | 25.0 ± 43.3 | 41.7 ± 49.3 | 12 |
| Uso de IA generativa                      | 51.3 ± 40.4 | 20.0 ± 24.5 | 25.5 ± 28.4 | 70.0 ± 41.2 | 12 |
| Valor da inscricao                        | 55.6 ± 45.8 | 33.3 ± 37.3 | 27.8 ± 40.4 | 63.0 ± 45.7 | 18 |
| Cadastro nao e inscricao                  | 37.5 ± 24.7 | 25.0 ± 17.7 | 29.8 ± 20.3 | 75.0 ± 43.3 | 12 |
| Substituicao de membros                   | 67.8 ± 41.5 | 20.0 ± 16.3 | 30.0 ± 24.5 | 74.4 ± 28.5 | 15 |
| E-mail de confirmacao nao chega           | 53.6 ± 27.7 | 23.3 ± 13.3 | 31.2 ± 18.2 | 32.7 ± 30.6 | 15 |
| Contato oficial                           | 66.7 ± 20.4 | 25.0 ± 18.6 | 31.5 ± 20.2 | 100.0 ± 0.0 | 18 |
| Professor gera senha do estudante         | 63.5 ± 9.0  | 21.9 ± 5.4  | 31.9 ± 6.4  | 14.6 ± 14.9 | 12 |
| Selecao para a iGeo                       | 64.4 ± 38.1 | 22.2 ± 15.2 | 31.9 ± 20.4 | 74.1 ± 29.5 | 18 |
| Acesso simultaneo durante a prova         | 66.7 ± 10.2 | 28.8 ± 25.1 | 34.5 ± 27.2 | 79.2 ± 12.5 | 12 |
| Prazo de preenchimento de dados           | 72.5 ± 28.0 | 25.0 ± 17.7 | 34.6 ± 23.8 | 47.9 ± 18.9 | 12 |
| Dados obrigatorios do estudante           | 58.3 ± 38.0 | 31.7 ± 35.5 | 34.8 ± 37.7 | 80.0 ± 40.0 | 15 |
| Classificacao para a presencial           | 39.6 ± 37.0 | 32.2 ± 25.9 | 35.0 ± 30.2 | 54.2 ± 36.1 | 12 |
| Token / link expirado                     | 35.4 ± 26.6 | 37.5 ± 28.0 | 35.9 ± 26.9 | 49.9 ± 25.2 | 12 |
| Senha recuperada incompativel / navegador | 45.8 ± 38.0 | 36.7 ± 34.5 | 36.9 ± 38.5 | 38.0 ± 15.8 | 12 |
| Quem pode participar / series             | 69.8 ± 20.3 | 29.5 ± 13.3 | 37.7 ± 14.6 | 92.9 ± 17.5 | 21 |
| Navegadores suportados                    | 58.3 ± 18.6 | 32.5 ± 27.1 | 38.2 ± 29.0 | 87.5 ± 13.8 | 12 |
| Nome da equipe                            | 100.0 ± 0.0 | 30.7 ± 12.4 | 45.4 ± 16.4 | 100.0 ± 0.0 | 15 |
| Criterios de desempate                    | 92.2 ± 9.3  | 37.5 ± 26.0 | 49.3 ± 25.3 | 97.2 ± 6.2  | 12 |
| Divulgacao do gabarito                    | 81.2 ± 32.5 | 37.5 ± 21.7 | 50.0 ± 28.9 | 95.8 ± 9.3  | 12 |
| Limite de equipes                         | 70.0 ± 24.5 | 50.0 ± 0.0  | 56.7 ± 8.2  | 90.0 ± 20.0 | 15 |
| Certificados de edicoes anteriores        | 81.2 ± 20.7 | 50.0 ± 0.0  | 60.8 ± 6.8  | 81.2 ± 20.7 | 12 |
| Recuperar senha                           | 84.9 ± 12.2 | 58.9 ± 32.1 | 61.5 ± 32.6 | 80.2 ± 11.9 | 15 |
| Equipes de escolas diferentes             | 95.6 ± 11.3 | 60.6 ± 13.8 | 73.3 ± 11.2 | 95.6 ± 11.3 | 15 |
| Nome social                               | 100.0 ± 0.0 | 60.4 ± 12.3 | 74.6 ± 9.4  | 100.0 ± 0.0 | 12 |
| Tipos de escola                           | 91.7 ± 18.6 | 70.8 ± 29.8 | 77.5 ± 24.1 | 100.0 ± 0.0 | 12 |
| Aluno em mais de uma equipe               | 100.0 ± 0.0 | 90.0 ± 20.0 | 93.3 ± 13.3 | 100.0 ± 0.0 | 15 |
| Medalhas fisicas                          | 100.0 ± 0.0 | 100.0 ± 0.0 | 100.0 ± 0.0 | 88.3 ± 14.5 | 15 |

Weakest intents: Calendario / datas, Fases e estrutura das provas, Recursos de questao, Cadastro da escola pelo INEP, Responder todas as questoes.
Strongest intents: Medalhas fisicas, Aluno em mais de uma equipe, Tipos de escola.

## 4. Unsupported facts (hallucination set)

659 of 2048 predicted atomic facts (32.2%) were not supported by the corpus. Examples (intent -> unsupported claim):

- *Minimo de membros na presencial*: As regras estabelecem que as equipes que se classificam para a fase presencial não podem ter menos de três membros.
- *Substituicao de membros*: O professor orientador tem até o dia 01/08 para realizar alterações nos dados dos estudantes.
- *Valor da inscricao*: A informação é do Edital Seleção_EquipeBrasil_iGeo 2025.
- *Token / link expirado*: Se o token está inválido, você deve solicitar um novo.
- *Recuperar senha*: A solicitação de uma nova senha deve ser feita na tela de login.
- *Recuperar senha*: Para solicitar uma nova senha, é necessário clicar em 'Esqueceu a senha?'.
- *Senha recuperada incompativel / navegador*: A nova senha que você recebeu pode não estar funcionando.
- *Senha recuperada incompativel / navegador*: O navegador pode estar utilizando uma senha antiga armazenada.
- *Senha recuperada incompativel / navegador*: É recomendado limpar o cache e o histórico de navegação.
- *Senha recuperada incompativel / navegador*: Você deve tentar acessar novamente com a senha enviada pelo sistema.
- *E-mail de confirmacao nao chega*: Se você não recebeu o e-mail de ativação da conta, pode ser que ele tenha sido direcionado para a caixa de spam.
- *E-mail de confirmacao nao chega*: É recomendado que o cadastro seja feito com um e-mail pessoal.

## 5. Missing facts (recall gaps)

2225 of 3047 gold atomic facts (73.0%) were missing from the answers. Examples (intent -> missing fact the answer should have contained):

- *Composicao da equipe*: Cada equipe é formada por 1 professor(a) orientador(a).
- *Composicao da equipe*: O professor(a) orientador(a) é o responsável pela inscrição.
- *Limite de equipes*: Nao ha limite de equipes que uma escola pode inscrever.
- *Minimo de membros na presencial*: Equipes classificadas para a Fase Presencial nao podem participar com menos de dois membros.
- *Quem pode participar / series*: Sao aceitos ensino regular, profissionalizante, supletivo e EJA.
- *Quem pode participar / series*: Quem ja concluiu o Ensino Medio nao pode participar.
- *Quem pode participar / series*: Quem esta no Ensino Superior nao pode participar.
- *Substituicao de membros*: O professor coordenador pode substituir qualquer membro da equipe antes do início da primeira fase online.
- *Substituicao de membros*: Depois do início da primeira fase online, o sistema permite apenas a exclusão do estudante.
- *Substituicao de membros*: Equipes classificadas para a Presencial nacional não podem substituir membros.
- *Equipes de escolas diferentes*: As escolas diferentes podem ser da mesma rede de ensino ou mantenedora.
- *Nome social*: É garantido o uso do nome social durante toda a prova.

## 6. How these numbers were produced

Each gold and predicted answer was decomposed into atomic facts by gpt-4o-mini. Recall counts gold facts conveyed in the prediction; precision counts predicted facts inferable from the gold answer; FactScore counts predicted facts supported by the official OBG corpus. F1 is the macro-average of per-question harmonic means. PT<->EN paraphrases are treated as equivalent. Sections 2-5 are generated directly from the per-question results, not written in advance.
