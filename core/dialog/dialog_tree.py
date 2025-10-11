"""
Здесь описаны сценарии работы с ботом. Какие переходы в диалоге
являются валидными, а какие - нет; Реализован класс дерева диалога.
"""

import typing

import core.warerobjects.warerobject as warer


class DialogTree(warer.WarerObject):
    """
    Класс дерева диалога бота. Предоставляет интерфейс проверки
    состояний на корректность.

    Родители:
        abc.ABC
        warer.WarerObject

    Аттрибуты класса:
        DIALOG_TREE: дерево диалога, описывает все возможные сценарии
        использования бота.
    """

    class State:
        """
        Класс узла дерева диалога.
        """

        def __init__(self,
                     name: str,
                     parent: typing.Optional['DialogTree.State']|None=None,
                     children: list['DialogTree.State']|None=None):
            """
            Инициализирует self.
            """
            self.name = name
            self.parent = parent
            self.children = children or []

        def __repr__(self):
            """
            Представляет узел в удобном для отладки виде.
            """
            return (f"State("
                    f"name={self.name}, "
                    f"parent.name={self.parent.name if self.parent else None}, "
                    f"children={[child.name for child in self.children]})")

        @property
        def is_nil(self) -> bool:
            """
            Проверяет состояние на конец текущей ветви диалога.
            """
            return not bool(self.children)

    """
    start
    ├── load_image
    │   ├── loading
    │   └── tagging
    ├── make_collage
    │   ├── choose_tags
    │   ├── choose_size
    │   └── choose_effects
    └── delete_data
    """

    DIALOG_ROOT = State("start")

    __LOAD_IMAGE = State("load_image", DIALOG_ROOT)
    __LOADING = State("loading", __LOAD_IMAGE)
    __TAGGING = State("tagging", __LOAD_IMAGE)
    __LOAD_IMAGE.children = [
        __LOADING, __TAGGING
    ]

    __MAKE_COLLAGE = State("make_collage", DIALOG_ROOT)
    __CHOOSE_TAGS = State("choose_tags", __MAKE_COLLAGE)
    __CHOOSE_SIZE = State("choose_size", __MAKE_COLLAGE)
    __CHOOSE_EFFECTS = State("choose_effects", __MAKE_COLLAGE)
    __MAKE_COLLAGE.children = [
        __CHOOSE_TAGS, __CHOOSE_SIZE, __CHOOSE_EFFECTS
    ]

    __DELETE_MY_DATA = State("delete_my_data", DIALOG_ROOT)

    DIALOG_ROOT.children = [
        __LOAD_IMAGE, __MAKE_COLLAGE, __DELETE_MY_DATA
    ]

    def __init__(self):
        """
        Инициализирует self.
        """
        super().__init__()

    @staticmethod
    def next_state(curr: State) -> State:
        """
        Функция возвращает следующий этап диалога
        между пользователем и ботом
        """
        if curr == DialogTree.DIALOG_ROOT:
            """
            В случае неоднозначного перехода к
            следующему состоянию требуется выбор
            пользователя.
            """
            return DialogTree.DIALOG_ROOT

        if bool(curr.children):
            return curr.children[0]

        steps = curr.parent.children
        for i, step in enumerate(steps):
            if step == curr and i + 1 != len(steps):
                return steps[i+1]

        return DialogTree.DIALOG_ROOT

    @staticmethod
    def is_valid_step(last: State, curr: State) -> bool:
        """
        Проверяет валидность перехода между состояниями.
        Не допускается переход вверх по дереву, а так же
        пропуск узлов, дочерних к одному и тому же состоянию.
        """
        if last == DialogTree.DIALOG_ROOT:
            return curr in last.children
        return curr == DialogTree.next_state(last)



if __name__ == "__main__":
    help(DialogTree)

    print("пример использования:")
    states = [v for k,v in DialogTree.__dict__.items()
              if isinstance(v, DialogTree.State)]
    for state in states:
        print(f"следующий шаг для {state}\t=\n\t\t"
              f"{DialogTree.next_state(state)}")
    print()

    print("проверки переходов между состояниями на валидность:")
    import random
    for _ in range(6):
        a, b = random.randint(0, len(states)-1), random.randint(0, len(states)-1)
        last, curr = states[a], states[b]
        print(f"переход от {last} в {curr}:\n\t\t"
              f"{DialogTree.is_valid_step(last, curr)}")
