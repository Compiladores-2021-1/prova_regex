import builtins
import math
import sys
from typing import Any
from lark import Lark, InlineTransformer, LarkError, Token, Tree

"""Constantes (algumas tarefas pedem para incluir variáveis específicas nesta"""
"""parte do arquivo)"""
NAME = "Meu nome"
MATRICULA = "01/2345678"
...


"""Gramática do Ruspy. (não modifique o nome desta variável, testes dependem disto!)"""
GRAMMAR = r"""
// Copie o conteúdo completo de ruspy.lark dentro desta string ou somente as
// partes relevantes para cada atividade. 
// 
// Você pode trabalhar no arquivo separadamente, mas copie e cole o conteúdo
// aqui dentro antes de submeter a tarefa. 
mod: "TODO :)"
seq: "TODO :)"
"""
grammar_expr = Lark(GRAMMAR, parser="lalr", start="seq")
grammar_mod = Lark(GRAMMAR, parser="lalr", start="mod")


"""(não modifique o nome desta classe, fique livre para alterar as implementações!)"""
class RuspyTransformer(InlineTransformer):
    from operator import add, sub, mul, truediv as div, pow, neg, pos
    from operator import rshift, lshift, or_, and_, xor
    from operator import eq, ne, gt, lt, ge, le

    global_names = {
        **vars(math),  # Inclui todas funções do módulo math
        **vars(builtins),  # Inclui todas funções padrão do python
        "answer": 42,
        "println": print,
        "true": True,
        "false": False,
        "null": None,
    }

    """Estas declarações de tipo existem somente para deixar o VSCode feliz."""
    _transform_children: Any
    _call_userfunc: Any
    transform: Any

    """Construtor"""
    def __init__(self):
        super().__init__()
        self.env = self.global_names.copy()

    """Trata símbolos terminais -------------------------------------------------"""
    def INT(self, tk):
        """Às vezes precisamos nos esforçar um pouquinho mais para obter o """
        """resultado que simplesmente fazer a conversão int(x)"""
        data = tk.replace('_', '')
        if set(data) == {'0'}:
            raise ValueError('FIXME!')  # (a solução aqui é trivial :) 
        return int(data)

    def FLOAT(self, tk):
        return int(tk)

    """Trata símbolos não-terminais ---------------------------------------------"""
    def lit(self, tk):
        if not isinstance(tk, Token):
            return tk
        try:
            return getattr(self, tk.type)(tk)
        except AttributeError:
            raise NotImplementedError(f"Implemente a regra def {tk.type}(self, tk): ... no transformer")

    def name(self, name):
        raise NotImplementedError("name")

    def assign(self, name, value):
        raise NotImplementedError("assign")

    ...

    """Formas especiais --------------------------------------------------------"""

    """Não-terminais normais recebem argumentos já transformados. As formas"""
    """especiais exigem a avaliação manual, o que pode ser útil para controlar"""
    """com mais precisão quantas vezes cada argumento deve ser avaliado. Isto é"""
    """útil em laços, execução condicional etc."""
    """"""
    """A lista de formas especiais precisa ser declarada explicitamente"""
    special = {"if_", "for_", "while_", "fn", "lambd", "and_e", "or_e"}

    """Sobrescrevemos este método para habilitar formas especiais no transformer."""
    def _transform_tree(self, tree):
        if tree.data in self.special:
            children = tree.children
        else:
            children = list(self._transform_children(tree.children))
        return self._call_userfunc(tree, children)

    """A avaliação é feita pelo método eval."""
    def eval(self, obj):
        """
        Força a avaliação de um nó da árvore sintática em uma forma especial.
        """
        if isinstance(obj, Tree):
            return self.transform(obj)
        elif isinstance(obj, Token):
            try:
                return getattr(self, obj.type)(obj)
            except AttributeError:
                return obj
        else:
            return obj

    """Lista de formas especiais"""
    def and_e(self, x, y):
        """Esta é a forma mais simples. Avaliamos explicitamente cada argumento."""
        """Note que "x and y" em Python avalia x e somente avalia y caso o primeiro"""
        """argumento seja verdadeiro. Este é exatamente o comportamento desejado."""
        return self.eval(x) and self.eval(y)

    def or_e(self, x, y):
        raise NotImplementedError("or_e")

    def if_(self, cond, then, else_=None):
        raise NotImplementedError("if")

    def while_(self, cond, block):
        raise NotImplementedError("while")

    def for_(self, id, expr, block):
        raise NotImplementedError("for")

    def fn(self, name, args, block):
        """Dica: reaproveite a implementação de lambd"""
        raise NotImplementedError("fn")

    def lambd(self, args, block):
        raise NotImplementedError("fn")


def eval(src):
    """
    Avalia uma expressão ruspy.

    >>> eval("1 + 1")
    2
    """
    return _eval_or_exec(src, is_exec=False)


def module(src) -> dict:
    """
    Avalia um módulo ruspy e retorna um dicionário com as funções definidas
    no módulo.

    Você pode utilizar estas funções a partir de código Python.

    >>> dic = module("fn incr(n: int) { n + 1 }")
    >>> f = dic["incr"]
    >>> f(1)
    2
    """
    return _eval_or_exec(src, is_exec=True)


def run(src):
    """
    Avalia um módulo ruspy e executa automaticamente a função main.

    >>> src = '''
    ... fn main() {
    ...     print("hello world!")
    ... }
    ... '''
    hello world!
    """
    mod = module(src)
    main = mod.get("main")
    if not main:
        raise RuntimeError('módulo não define uma função "main()"')
    main()


def _eval_or_exec(src: str, is_exec=False) -> Any:
    """Função utilizada internamente por eval/module/run."""
    if is_exec:
        grammar = grammar_mod
    else:
        grammar = grammar_expr
    try:

        tree = grammar.parse(src)
    except LarkError:
        print(f"Erro avaliando a expressão: \n{src}")
        print("\nImprimindo tokens")
        for i, tk in enumerate(grammar.lex(src), start=1):
            print(f" - {i}) {tk} ({tk.type})")
        raise
    transformer = RuspyTransformer()
    result = transformer.transform(tree)

    if isinstance(result, Tree):
        print(tree.pretty())
        bads = [*tree.find_pred(lambda x: not hasattr(transformer, x.data))]
        bad = bads[0] if bads else tree
        raise NotImplementedError(
            f"""
não implementou regra para lidar com: {tree.data!r}.
Crie um método como abaixo na classe do transformer.
    def {bad.data}(self, ...): 
        return ... 
"""
        )
    return result


"""Interface de linha de comando. Lê um arquivo ruspy e passa para a função"""
"""eval ou equivalente. Você pode modificar o conteúdo dentro do "if" para"""
"""executar outros códigos de teste quando for rodar o arquivo. O exemplo abaixo"""
"""fornece uma interface de linha de comando minimamente decente para interagir"""
"""com o ruspy."""
if __name__ == "__main__":
    if "--help" in sys.argv:
        print("Digite python ruspy.py [ARQUIVO] [--script]")
        print("")
        print("Opções:")
        print("  --help:")
        print("         mostra mensagem de ajuda")
        print("  --script:")
        print("         avalia como expressão no modo script, como se")
        print("         estivéssemos executando o código dentro da função main()")
        exit()
    elif "--script" in sys.argv:
        do_eval = True
        del sys.argv[sys.argv.index("--script")]
    else:
        do_eval = False
    with open(sys.argv[-1]) as fd:
        src = fd.read()
        if do_eval:
            print(f"\n> {eval(src)}")
        else:
            run(src)
