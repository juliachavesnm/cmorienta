import os
import re
import html
import time
import unicodedata
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from supabase import create_client, Client


BASE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BASE_DIR / ".env"

print(f"Procurando .env em: {ENV_FILE}")

if not ENV_FILE.exists():
    raise RuntimeError(
        f".env não encontrado em: {ENV_FILE}"
    )

load_dotenv(ENV_FILE)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

print(f"SUPABASE_URL encontrada: {bool(SUPABASE_URL)}")
print(f"SUPABASE_KEY encontrada: {bool(SUPABASE_KEY)}")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError(
        "SUPABASE_URL e SUPABASE_KEY precisam estar definidos no .env"
    )

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


LIST_URL = "https://www.ib.usp.br/telefones-ib/docentes-ib.html"
UNIVERSITY = "Universidade de São Paulo"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/140.0 Safari/537.36"
    )
}


def get_soup(url: str) -> BeautifulSoup:
    """
    Baixa uma página e retorna o BeautifulSoup.
    """

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    return BeautifulSoup(
        response.text,
        "html.parser"
    )


def clean_text(text: str | None) -> str | None:
    """
    Normaliza espaços e remove espaços desnecessários.
    """

    if not text:
        return None

    text = text.replace("\xa0", " ")

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    text = text.strip()

    return text or None


def normalize_url(url: str) -> str:
    """
    Normaliza URLs para evitar pequenas diferenças.
    """

    url = url.strip()

    # Remove fragment
    url = url.split("#")[0]

    # Remove query string
    url = url.split("?")[0]

    # Remove trailing slash
    if url.endswith("/"):
        url = url[:-1]

    return url


def normalize_name(name: str) -> str:
    """
    Normaliza nome para comparação.
    """

    name = clean_text(name) or ""

    name = unicodedata.normalize(
        "NFKD",
        name
    )

    name = "".join(
        char
        for char in name
        if not unicodedata.combining(char)
    )

    return name.lower().strip()


def extract_email(text: str | None) -> str | None:
    """
    Tenta encontrar um email no HTML/texto.

    O IB protege alguns emails com JavaScript,
    então pode não ser possível recuperar todos.
    """

    if not text:
        print(f"Not text to extract email from: {text}")
        return None

    match = re.search(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        text
    )

    if match:
        return match.group(0).lower()

    return None


import html
import re


EMAIL_REGEX = re.compile(
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
)


def extract_email_from_soup(soup):

    print("Procurando email no perfil...")

    # ---------------------------------------------------------
    # 1. Email em mailto
    # ---------------------------------------------------------
    for link in soup.select('a[href^="mailto:"]'):
        href = link.get("href", "")
        email = href.replace("mailto:", "").strip()

        print(f"Encontrado mailto: {email}")

        if EMAIL_REGEX.fullmatch(email):
            return email.lower()


    # ---------------------------------------------------------
    # 2. Email diretamente no texto
    # ---------------------------------------------------------
    page_text = soup.get_text(" ", strip=True)

    match = EMAIL_REGEX.search(page_text)

    if match:
        print(f"Email encontrado no texto: {match.group(0)}")
        return match.group(0).lower()


    # ---------------------------------------------------------
    # 3. Joomla Email Cloaking
    # ---------------------------------------------------------
    print("Procurando email oculto pelo Joomla...")

    for script in soup.find_all("script"):

        script_text = script.string or script.get_text()

        if not script_text or "addy" not in script_text:
            continue

        print("Encontrado script com 'addy'")

        # O Joomla coloca o email dentro das atribuições
        # das variáveis addy... e addy_text...

        # Pegamos todas as strings JavaScript do script.
        fragments = re.findall(
            r"""['"]([^'"]*)['"]""",
            script_text
        )

        # Decodifica entidades HTML
        decoded = [
            html.unescape(fragment)
            for fragment in fragments
        ]

        # Junta apenas fragmentos que parecem fazer parte
        # de um email.
        #
        # Procuramos qualquer fragmento que contenha:
        # @, domínio, ou entidades que tenham virado @ / .
        for i, fragment in enumerate(decoded):

            if "@" not in fragment:
                continue

            # Se já houver @, tentamos juntar com os próximos
            candidate = fragment

            for next_fragment in decoded[i + 1:i + 6]:
                candidate += next_fragment

                match = EMAIL_REGEX.search(candidate)

                if match:
                    email = match.group(0).lower()

                    print("EMAIL ENCONTRADO:", email)

                    return email

        # Caso o @ esteja sozinho em um fragmento
        for i in range(len(decoded)):

            if decoded[i] != "@":
                continue

            # Procuramos alguns fragmentos antes e depois
            start = max(0, i - 3)
            end = min(len(decoded), i + 4)

            candidate = "".join(decoded[start:end])

            print("Candidato:", candidate)

            match = EMAIL_REGEX.search(candidate)

            if match:
                email = match.group(0).lower()

                print("EMAIL ENCONTRADO:", email)

                return email

    print("Nenhum email encontrado.")

    return None

def extract_label_value(
    soup: BeautifulSoup,
    label: str
) -> str | None:
    """
    Extrai um valor associado a um label como:

    Departamento:
    Ecologia
    """

    label_normalized = normalize_name(label)

    for text_node in soup.find_all(string=True):

        text = clean_text(text_node)

        if not text:
            continue

        if normalize_name(text).rstrip(":") != label_normalized.rstrip(":"):
            continue

        parent = text_node.parent

        if not parent:
            continue

        # Caso comum:
        # Departamento:
        # Ecologia
        parent_text = clean_text(
            parent.get_text(" ", strip=True)
        )

        if parent_text:
            parent_text = re.sub(
                rf"^{re.escape(text)}\s*",
                "",
                parent_text,
                flags=re.IGNORECASE
            )

            parent_text = clean_text(parent_text)

            if parent_text:
                return parent_text

        # Procurar próximo elemento/texto
        next_element = parent.find_next()

        if next_element:
            value = clean_text(
                next_element.get_text(
                    " ",
                    strip=True
                )
            )

            if value:
                return value

        next_text = text_node.find_next(string=True)

        if next_text:
            value = clean_text(next_text)

            if value:
                return value

    return None


def extract_profile_data(
    profile_url: str,
    list_data: dict
) -> dict:

    print(f"  → Abrindo perfil: {profile_url}")

    soup = get_soup(profile_url)

    # --------------------------------------------------
    # Nome
    # --------------------------------------------------

    name = None

    # Página do IB utiliza h2 para o nome
    heading = soup.find("h2")

    if heading:
        name = clean_text(
            heading.get_text(" ", strip=True)
        )

    if not name:
        name = list_data["name"]

    # --------------------------------------------------
    # Departamento
    # --------------------------------------------------

    department = extract_label_value(
        soup,
        "Departamento"
    )

    if not department:
        department = list_data.get("department")

    # --------------------------------------------------
    # Linha de pesquisa
    # --------------------------------------------------

    research_line = extract_label_value(
        soup,
        "Linha de Pesquisa"
    )

    if not research_line:
        research_line = list_data.get(
            "research_line"
        )

    # --------------------------------------------------
    # Descrição
    # --------------------------------------------------

    description = extract_label_value(
        soup,
        "Resumo da Pesquisa"
    )

    # --------------------------------------------------
    # Email
    # --------------------------------------------------

    email = extract_email_from_soup(soup)

    # --------------------------------------------------
    # Keywords
    # --------------------------------------------------

    keywords = []

    if research_line:
        keywords.append(research_line)

    # Evita duplicatas
    keywords = list(dict.fromkeys(keywords))

    return {
        "name": name,
        "description": description,
        "university": UNIVERSITY,
        "department": department,
        "email": email,
        "profile_url": normalize_url(profile_url),
        "keywords": keywords or None,
    }


def extract_professors_from_list() -> list[dict]:

    print("Baixando lista de docentes...")

    soup = get_soup(LIST_URL)

    professors = []

    # A tabela da página contém os docentes.
    # Procuramos links que apontam para /docentes-ib/
    for link in soup.select(
        'a[href*="/telefones-ib/docentes-ib/"]'
    ):

        name = clean_text(
            link.get_text(" ", strip=True)
        )

        href = link.get("href")

        if not name or not href:
            continue

        profile_url = normalize_url(
            urljoin(
                LIST_URL,
                href
            )
        )

        # Evitar links duplicados
        if any(
            p["profile_url"] == profile_url
            for p in professors
        ):
            continue

        # Encontrar a linha da tabela
        row = link.find_parent("tr")

        research_line = None
        department = None

        if row:

            cells = row.find_all(["td", "th"])

            # Estrutura:
            # Nome | Linha de Pesquisa | Telefone | Sala | Departamento

            if len(cells) >= 5:

                research_line = clean_text(
                    cells[1].get_text(
                        " ",
                        strip=True
                    )
                )

                department = clean_text(
                    cells[4].get_text(
                        " ",
                        strip=True
                    )
                )

        professors.append({
            "name": name,
            "profile_url": profile_url,
            "research_line": research_line,
            "department": department,
        })

    return professors


def get_existing_profiles() -> set[str]:
    """
    Busca as URLs que já existem no Supabase.

    Isso permite evitar requisições desnecessárias
    aos perfis que já foram cadastrados.
    """

    print("Consultando professores existentes no Supabase...")

    existing = set()

    response = (
        supabase
        .table("advisors")
        .select("profile_url")
        .eq("university", UNIVERSITY)
        .execute()
    )

    for row in response.data:

        profile_url = row.get("profile_url")

        if profile_url:
            existing.add(
                normalize_url(profile_url)
            )

    return existing


def save_advisor(advisor: dict) -> None:
    """
    Insere/atualiza um professor no Supabase.

    O profile_url possui UNIQUE constraint,
    portanto não haverá duplicação.
    """

    (
        supabase
        .table("advisors")
        .upsert(
            advisor,
            on_conflict="profile_url"
        )
        .execute()
    )


def scrape_ib():

    print("=" * 60)
    print("SCRAPER - INSTITUTO DE BIOCIÊNCIAS USP")
    print("=" * 60)

    professors = extract_professors_from_list()

    print(
        f"\nEncontrados {len(professors)} docentes na lista."
    )

    existing_profiles = get_existing_profiles()

    print(
        f"Já existem {len(existing_profiles)} "
        "perfis do IB no banco."
    )

    new_professors = [
        professor
        for professor in professors
        if normalize_url(
            professor["profile_url"]
        ) not in existing_profiles
    ]

    print(
        f"Novos perfis a processar: "
        f"{len(new_professors)}"
    )

    if not new_professors:
        print("\nNenhum novo professor encontrado.")
        return

    inserted = 0
    failed = 0

    for index, professor in enumerate(
        new_professors,
        start=1
    ):

        print(
            f"\n[{index}/{len(new_professors)}] "
            f"{professor['name']}"
        )

        try:

            advisor = extract_profile_data(
                professor["profile_url"],
                professor
            )

            print(
                f"  Departamento: "
                f"{advisor['department']}"
            )

            print(
                f"  Pesquisa: "
                f"{advisor['keywords']}"
            )

            print(
                f"  Email: "
                f"{advisor['email'] or 'não encontrado'}"
            )

            save_advisor(advisor)

            inserted += 1

            print("  ✓ Salvo no Supabase")

        except Exception as error:

            failed += 1

            print(
                f"  ✗ Erro: {error}"
            )

        # Pequeno intervalo para não bombardear o servidor
        time.sleep(0.5)

    print("\n" + "=" * 60)
    print("FINALIZADO")
    print("=" * 60)

    print(f"Novos professores inseridos: {inserted}")
    print(f"Erros: {failed}")


if __name__ == "__main__":
    scrape_ib()
