# -*- coding: utf-8 -*-


class Apart(list):
    """
    Consist of items, used to compare between Aparts
    """

    # hash [string, pos_begin, pos_end]
    str_lambda = lambda list1: ''.join(sorted([str(hash(i1)) for i1 in list1]))

    def __eq__(self, another):
        if type(another) is not type(self):
            return False

        return Apart.str_lambda(self) == Apart.str_lambda(another)

    def __hash__(self):
        return hash(Apart.str_lambda(self))

    @classmethod
    def process(cls, list1):
        a_list, b_list = Apart(), Apart()

        for i1 in list1:
            if isinstance(i1, str):
                b_list.append(i1)
            else:
                a_list.append(i1)

        return ApartList([a_list, b_list])


class ApartList(list):
    def __eq__(self, another):
        return (self[0] == another[0]) and (self[1] == another[1])
