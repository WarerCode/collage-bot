"""
Здесь описаны сценарии работы с ботом. Какие переходы в диалоге
являются валидными, а какие - нет; Реализован класс дерева диалога.
"""

import core.warerobjects.warerobject as warer


class DialogTree(warer.WarerObject):
    """
    Класс дерева диалога бота. Предоставляет интерфейс проверки
    состояний на корректность.

    Родители:
        abc.ABC
        warer.WarerObject
    """

    class State:
        """
        Класс узла дерева диалога.
        """

        def __init__(self,
                     name: str,
                     parent_name: str|None=None,
                     children: list['DialogTree.State']|None=None):
            """
            Инициализирует self.
            """
            self.name = name
            self.parent_name = parent_name
            self.children = children or []

        def __repr__(self):
            """
            Представляет узел в удобном для отладки виде.
            """
            return (f"State("
                    f"name={self.name}, "
                    f"children={self.children})")

        @property
        def is_nil(self) -> bool:
            """
            Проверяет состояние на конец текущей ветви диалога.
            """
            return not bool(self.children)

    DIALOG_TREE = State("default", None, [
        State("load_image", "default",[
            State("loading", "load_image"),
            State("tagging", "load_image")
        ]),
        State("make_collage", "default",[
            State("choose_tags", "make_collage"),
            State("choose_size", "make_collage"),
            State("choose_effects", "make_collage"),
        ]),
        State("delete_data", "default")
    ])

    def __init__(self):
        """
        Инициализирует self.
        """
        super().__init__()

    @staticmethod
    def is_valid_step(last: State, curr: State) -> bool:
        """
        Проверяет валидность перехода между состояниями.
        Не допускается переход вверх по дереву, а так же
        пропуск узлов, дочерних к одному и тому же состоянию.
        """
        return curr in last.children

#TODO: написать рекурсивную функцию поиска следующего шага диалога
#TODO: закончить is_valid_step  @DanilaEfimov


if __name__ == "__main__":
    help(DialogTree)
