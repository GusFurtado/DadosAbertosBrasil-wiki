from datetime import date

import mwparserfromhell

from dab_wiki.datasets.municipios import (
    Municipios,
    aniversario,
    comando_suspeito,
    fundacao_wikidata,
    gentilicos,
    gentilicos_infobox,
    gentilicos_wikidata,
    suspeito,
)


def test_extrair(brutos):
    dataset = Municipios()
    por_nome = {m.artigo: m for m in dataset.gerar(brutos("municipios"), validar_conjunto=False).dados}
    santos = por_nome["Santos"]
    assert (santos.codigo_ibge, santos.uf, santos.regiao) == (3548500, "SP", "Sudeste")
    assert santos.gentilicos == ["santista"]
    # Wikidata só tem o ano; a data completa vem da infobox
    assert santos.fundacao == date(1546, 1, 26)
    campinas = por_nome["Campinas"]
    assert (campinas.aniversario_dia, campinas.aniversario_mes) == (14, 7)


def test_lacunas(brutos):
    comandos = Municipios().comandos_lacunas(brutos("municipios"))
    assert comandos
    assert all(c.startswith("Q") and "\tS143\tQ11921" in c for c in comandos)
    assert all('\tpt-br:"' in c for c in comandos if "\tP1549\t" in c)


def test_gentilicos():
    assert gentilicos("acriano ou acreano") == ["acriano", "acreano"]
    assert gentilicos("belenense, belemense ou belenhense (mais usado)") == ["belenense", "belemense", "belenhense"]
    assert gentilicos(None) == []


def test_fundacao_wikidata():
    assert fundacao_wikidata({"fundacao": "1546-01-01T00:00:00Z", "precisao": "9"}) == (None, 1546)
    assert fundacao_wikidata({"fundacao": "1949-01-20T00:00:00Z", "precisao": "11"}) == (date(1949, 1, 20), 1949)
    assert fundacao_wikidata({"fundacao": "1906-07-16T00:00:00Z|11"}) == (date(1906, 7, 16), 1906)
    assert fundacao_wikidata({"fundacao": "1985-01-01T00:00:00Z|9"}) == (None, 1985)
    assert fundacao_wikidata({}) == (None, None)


def test_aniversario():
    assert aniversario("25 de abril") == (25, 4)
    assert aniversario("1.º de janeiro") == (1, 1)
    assert aniversario(None) == (None, None)


def test_gentilicos_compostos():
    assert gentilicos("são franciscano") == ["são franciscano"]
    # Parte toda entre parênteses só fica se for uma palavra.
    assert gentilicos("(jorge-teixeirense) ou (pedra branca)") == ["jorge-teixeirense"]


def test_gentilicos_infobox_quebrados():
    assert gentilicos("jordaniense IBGE") == ["jordaniense"]
    assert gentilicos("rosasserrense - Santarosensse") == ["rosasserrense", "santarosensse"]
    assert gentilicos("tatuiano | tatuiense") == ["tatuiano", "tatuiense"]
    assert gentilicos("isaiense, coelhense, ou isaiascoelhense (em desuso)") == [
        "isaiense",
        "coelhense",
        "isaiascoelhense",
    ]
    assert gentilicos("tibagiense ou tibagiano, gentílico mais usado pela população local") == [
        "tibagiense",
        "tibagiano",
    ]
    assert gentilicos("macedonienses") == ["macedoniense"]
    assert gentilicos("{{Lista simples|") == []


def test_gentilicos_lista_simples():
    valor = mwparserfromhell.parse(
        "{{Lista simples|\n* pindamonhangabense\n* pindense<ref>[https://x.y Pinda]</ref>\n}}"
    )
    assert gentilicos_infobox(valor) == ["pindamonhangabense", "pindense"]
    assert gentilicos_infobox(None) == []


def test_gentilicos_wikidata():
    assert gentilicos_wikidata({"gentilicos": "mineiro|Mineiro|mineira"}) == ["mineiro", "mineira"]
    # Ordem alfabética dos valores: o GROUP_CONCAT não tem ordem garantida.
    assert gentilicos_wikidata({"gentilicos": "nova-mamonense ou nova-mamorense|baianos"}) == [
        "baiano",
        "nova-mamonense",
        "nova-mamorense",
    ]
    assert gentilicos_wikidata({}) == []


def test_suspeito():
    assert not suspeito("santista")
    assert not suspeito("são-paulino")
    assert not suspeito("montês")
    assert suspeito("alto horizontino")
    assert suspeito("colorados")
    assert suspeito("tatuí(ano)")
    assert comando_suspeito('Q1\tP1549\tpt-br:"colorados"\tS143\tQ11921')
    assert not comando_suspeito("Q1\tP571\t+1900-00-00T00:00:00Z/9\tS143\tQ11921")


def test_coordenadas_do_wikidata():
    from dab_wiki.datasets._wikidata import coordenadas

    assert coordenadas("Point(-48.549166666 -27.596944444)") == (-27.596944444, -48.549166666)
    assert coordenadas(None) == (None, None)
