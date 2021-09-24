"""
# lex-re

Criar expressões regulares para que que identifiquem os símbolos terminais
de uma linguagem de programação como passo inicial para criar um analisador
sintático.

* Criar expressões regulares que identifiquem números
* Criar expressões regulares que identifiquem outros símbolos atômicos
  da linguagem
* Evitar colisões entre as expressões regulares ou criar expressões
  que identifiquem incorretamente o tipo de cada terminal. 

---

PARTE 1 (competência básica)


Vamos testar esta habilidade traduzindo as regras para símbolos terminais 
de uma linguagem de programação real, o Rust e criar o arquivo de gramática
Lark correspondente.

Você deve editar a variável "grammar" mostrada no código abaixo:

grammar = r'''
INT          : SIMPLE_INT | BIN_INT | OCT_INT | HEX_INT
FLOAT        : FLOAT_SCI | FLOAT_SIMPLE
FLOAT_SCI    : /.../
FLOAT_SIMPLE : /.../
// continua...
'''

As regras para definição de números e nomes de variáveis estão nas referências
abaixo e utilizam um formato parecido com a definição de uma linguagem livre de
contexto.

* Inteiros: https://doc.rust-lang.org/reference/tokens.html#integer-literals
* Floats: https://doc.rust-lang.org/reference/tokens.html#floating-point-literals
* Comentários no formato C, tanto no estilo // até o fim da linha
  quanto no estilo /* bloco */. O Rust possui regras mais sofisticadas, mas vamos
  ignorá-las na atividade.
* Identificadores: https://doc.rust-lang.org/reference/identifiers.html
  (mas a última é trivial, porque a referência já fornece a expressão regular).


PARTE 2 (competência avançada)

Implemente também a regra de identificação de strings (https://doc.rust-lang.org/reference/tokens.html#string-literals)
"""

# RESPOSTA: INÍCIO -----------------------------------------------------------
grammar = f"""
start        : INT | FLOAT | STRING | ID | RESERVED | COMMENT

// Tipos inteiros
INT          : SIMPLE_INT | BIN_INT | OCT_INT | HEX_INT
SIMPLE_INT   : /0|1|3|42/
BIN_INT      : /0b.../ 
OCT_INT      : /0o.../ 
HEX_INT      : /0x.../ 

// Tipos de ponto-flutante
FLOAT        : FLOAT_SCI | FLOAT_SIMPLE
FLOAT_SCI    : /.../
FLOAT_SIMPLE : /.../

// Strings
STRING       : /"..."/

// Nomes de variáveis, valores especiais
ID           : /.../
RESERVED     : /true|false|null/

// Comentários
COMMENT      : LINE_COMMENT | BLOCK_COMMENT
LINE_COMMENT : "// line comment"
BLOCK_COMMENT: "/* block comment */"
"""
# RESPOSTA: FIM --------------------------------------------------------------

import pytest
import lark

###############################################################################
# Código de correção: NÃO MODIFICAR
###############################################################################
import lark

def lex_list(st):
    g = lark.Lark(grammar)
    return list(g.lex(st))


@pytest.mark.parametrize("grp", "ID INT BIN_INT OCT_INT HEX_INT FLOAT COMMENT".split())
def test_exemplos_positivos(grp, data):
    for ex in sorted(data(grp), key=len):
        typ = None
        if grp.endswith("INT"):
            typ = int
        if grp.endswith("FLOAT"):
            typ = float
        check_valid_token(ex, grp, typ=typ)


def test_comentários(data):
    grp = "COMMENT"
    for ex in sorted(data(grp), key=len):
        print(f"Testando: {ex!r} ({grp})")
        seq = lex_list(ex)
        if seq:
            raise AssertionError(f"erro: esperava comentário, obteve sequência {seq}")


@pytest.mark.parametrize("grp", "ID INT BIN_INT OCT_INT HEX_INT FLOAT COMMENT".split())
def test_exemplos_negativos(grp, data):
    for ex in sorted(data(grp + "_bad"), key=len):
        print(f"Testando: {ex!r} ({grp})")
        try:
            seq = lex_list(ex)
        except lark.LarkError:
            continue

        if grp == "COMMENT" and not seq:
            raise AssertionError(f"aceitou elemento: {ex}")
        elif len(seq) == 1 and seq[0].type == grp and seq[0] == ex:
            raise AssertionError(f"aceitou elemento: {seq}")


def check_valid_token(ex, grp, typ=None):
    print(f"Testando: {ex!r} ({grp})")
    seq = lex_list(ex)
    try:
        [tk] = seq
    except ValueError:
        raise AssertionError(f"erro: esperava token único, obteve sequência {seq}")

    if typ is not None:
        val = typ(tk)
        assert isinstance(
            val, typ
        ), f"tipo errado {tk} ({tk.type}): esperava {typ}, obteve {type(val)}"

    return seq
