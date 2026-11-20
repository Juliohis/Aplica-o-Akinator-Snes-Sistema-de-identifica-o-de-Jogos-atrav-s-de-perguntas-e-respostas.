#!/usr/bin/env python3
"""
Baixa as capas dos jogos de SNES do projeto libretro-thumbnails (GitHub)
e liga cada jogo da sua base (snes_jogos.json) a uma imagem.

Como usar (Python 3.8+, não precisa instalar nada):
    1. Coloque este arquivo na mesma pasta do snes_jogos.json
    2. python baixar_capas.py
    3. Confira o relatorio_capas.csv (veja os "aproximado" e "nao_encontrado")

Saídas:
    capas/                          -> imagens .png baixadas
    relatorio_capas.csv             -> jogo, metodo, arquivo_origem, caminho_local
    snes_jogos_com_capas.json       -> o mesmo JSON, com o campo "capa" em cada jogo

Se o script for interrompido, é só rodar de novo: ele pula o que já foi baixado.
"""
import csv
import difflib
import json
import re
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

# ----------------------------- configuração -----------------------------
ORG = "libretro-thumbnails"
REPO = "Nintendo_-_Super_Nintendo_Entertainment_System"
PASTA_NO_REPO = "named_boxarts"      # comparado em minúsculas (o repo varia a caixa)
BASE = Path(__file__).resolve().parent   # pasta onde este .py está (não depende de onde você o executa)
ARQ_ENTRADA = BASE / "snes_jogos.json"
ARQ_SAIDA_JSON = BASE / "snes_jogos_com_capas.json"
ARQ_RELATORIO = BASE / "relatorio_capas.csv"
PASTA_CAPAS = BASE / "capas"
CORTE_APROXIMADO = 0.88              # 0 a 1; mais alto = mais rígido (menos erros, mais "não encontrado")

# Nomes que não casam sozinhos. Chave: o nome na SUA base. Valor: nome no libretro (sem região).
# Complete com o que aparecer como "nao_encontrado" no relatório.
APELIDOS = {
    "Final Fantasy IV (Final Fantasy II nos EUA)": "Final Fantasy II",
    "Final Fantasy VI (Final Fantasy III nos EUA)": "Final Fantasy III",
    "Super Mario World 2: Yoshi's Island": "Super Mario World 2 - Yoshi's Island",
    "Mega Man X": "Mega Man X",
}

# Ordem de preferência quando o mesmo jogo existe em várias regiões
PREF_REGIAO = ["usa", "world", "europe", "japan"]
PREF_REGIAO_JAPAO = ["japan", "world", "usa", "europe"]  # para jogos só do Japão


# ----------------------------- normalização -----------------------------
def normalizar(texto):
    """Transforma um título em uma 'chave' comparável.
    'Legend of Zelda, The - A Link to the Past (USA)' e
    'The Legend of Zelda: A Link to the Past' viram a mesma chave."""
    t = unicodedata.normalize("NFKD", texto)
    t = "".join(c for c in t if not unicodedata.combining(c))   # tira acentos
    t = re.sub(r"\([^)]*\)|\[[^\]]*\]", " ", t)                 # tira (USA), (Rev 1), [!]...
    t = t.lower().replace("&", " and ")
    palavras = re.findall(r"[a-z0-9]+", t)                      # só letras e números
    palavras = [p for p in palavras if p != "the"]              # "The" muda de lugar entre as bases
    return "".join(palavras)


def regiao_do_arquivo(nome):
    m = re.search(r"\(([^)]*)\)", nome)
    texto = m.group(1).lower() if m else ""
    for r in PREF_REGIAO:
        if r in texto:
            return r
    return "outra"


def escolher_melhor(arquivos, so_japao):
    """Entre vários arquivos do mesmo jogo, pega o da região preferida."""
    ordem = PREF_REGIAO_JAPAO if so_japao else PREF_REGIAO
    def pontos(nome):
        r = regiao_do_arquivo(nome)
        return ordem.index(r) if r in ordem else len(ordem)
    return sorted(arquivos, key=lambda n: (pontos(n), len(n)))[0]


# ----------------------------- casamento -----------------------------
def casar(jogos, arquivos):
    """Devolve {nome_do_jogo: (arquivo_ou_None, metodo)}.
    arquivos: lista de nomes de arquivo (sem a pasta), ex.: 'Super Mario World (USA).png'"""
    indice = {}                                   # chave normalizada -> [arquivos]
    for a in arquivos:
        indice.setdefault(normalizar(Path(a).stem), []).append(a)
    chaves = list(indice)

    resultado = {}
    for j in jogos:
        nome = j["jogo"]
        so_japao = j.get("so_no_japao") == "Sim"

        # 1) apelido manual
        if nome in APELIDOS:
            k = normalizar(APELIDOS[nome])
            if k in indice:
                resultado[nome] = (escolher_melhor(indice[k], so_japao), "apelido")
                continue

        # 2) nome exato (depois de normalizar)
        k = normalizar(nome)
        if k in indice:
            resultado[nome] = (escolher_melhor(indice[k], so_japao), "exato")
            continue

        # 3) nome só até o primeiro "(": cobre "Jogo (nome alternativo)"
        k2 = normalizar(nome.split("(")[0])
        if k2 and k2 in indice:
            resultado[nome] = (escolher_melhor(indice[k2], so_japao), "exato")
            continue

        # 4) aproximado (difflib compara a semelhança entre textos)
        achados = difflib.get_close_matches(k, chaves, n=1, cutoff=CORTE_APROXIMADO)
        if achados:
            resultado[nome] = (escolher_melhor(indice[achados[0]], so_japao), "aproximado")
            continue

        resultado[nome] = (None, "nao_encontrado")
    return resultado


# ----------------------------- rede -----------------------------
def http_get(url, tentativas=3):
    req = urllib.request.Request(url, headers={"User-Agent": "snes-capas-trabalho-escolar"})
    for i in range(tentativas):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404 or i == tentativas - 1:
                raise
        except urllib.error.URLError:
            if i == tentativas - 1:
                raise
        time.sleep(1.5 * (i + 1))


def listar_arquivos_do_repo():
    """Usa a API do GitHub (1 chamada, sem chave) para listar as capas disponíveis."""
    base = f"https://api.github.com/repos/{ORG}/{REPO}"
    branch = json.loads(http_get(base))["default_branch"]
    arvore = json.loads(http_get(f"{base}/git/trees/{branch}?recursive=1"))
    if arvore.get("truncated"):
        print("AVISO: a lista de arquivos veio truncada; algumas capas podem não ser encontradas.")
    arquivos = []
    for item in arvore["tree"]:
        caminho = item["path"]
        if item["type"] == "blob" and caminho.lower().startswith(PASTA_NO_REPO + "/"):
            arquivos.append(caminho.split("/", 1)[1])
    return branch, arquivos, caminho_pasta_real(arvore)


def caminho_pasta_real(arvore):
    """Descobre como a pasta se escreve de fato no repo (Named_Boxarts ou Named_boxarts)."""
    for item in arvore["tree"]:
        if item["path"].lower() == PASTA_NO_REPO:
            return item["path"]
    return "Named_Boxarts"


def nome_seguro(texto):
    """Nome de arquivo local simples: sem acentos, espaços ou símbolos."""
    t = unicodedata.normalize("NFKD", texto)
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"[^A-Za-z0-9]+", "_", t).strip("_").lower()


# ----------------------------- programa principal -----------------------------
def main():
    if not ARQ_ENTRADA.exists():
        print(f"Não encontrei '{ARQ_ENTRADA.name}' na pasta:\n  {BASE}\n"
              "Copie o snes_jogos.json para essa pasta (a mesma do script) e rode de novo.")
        return
    jogos = json.load(open(ARQ_ENTRADA, encoding="utf-8"))
    print(f"{len(jogos)} jogos na base. Listando capas no GitHub...")
    branch, arquivos, pasta = listar_arquivos_do_repo()
    print(f"{len(arquivos)} capas disponíveis no repositório.")

    resultado = casar(jogos, arquivos)
    PASTA_CAPAS.mkdir(exist_ok=True)

    linhas, baixadas, falhas = [], 0, 0
    for j in jogos:
        nome = j["jogo"]
        arq, metodo = resultado[nome]
        caminho_local = ""
        if arq:
            destino = PASTA_CAPAS / f"{nome_seguro(nome)}.png"
            if not destino.exists():
                url = (f"https://raw.githubusercontent.com/{ORG}/{REPO}/{branch}/"
                       f"{urllib.parse.quote(pasta)}/{urllib.parse.quote(arq)}")
                try:
                    destino.write_bytes(http_get(url))
                    baixadas += 1
                    time.sleep(0.1)          # educação com o servidor
                except Exception as e:
                    print(f"  falhou: {nome} ({e})")
                    falhas += 1
                    metodo = "erro_download"
            if destino.exists():
                caminho_local = destino.relative_to(BASE).as_posix()   # ex.: capas/chrono_trigger.png
        j["capa"] = caminho_local or None
        linhas.append([nome, metodo, arq or "", caminho_local])

    with open(ARQ_RELATORIO, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["jogo", "metodo", "arquivo_origem", "caminho_local"])
        w.writerows(linhas)
    json.dump(jogos, open(ARQ_SAIDA_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    cont = {}
    for _, m, _, _ in linhas:
        cont[m] = cont.get(m, 0) + 1
    print("\nResumo:", cont)
    print(f"Baixadas agora: {baixadas} | falhas: {falhas}")
    print(f"Revise '{ARQ_RELATORIO.name}': confira os 'aproximado' e preencha APELIDOS para os 'nao_encontrado'.")


if __name__ == "__main__":
    main()
