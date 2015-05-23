# -*- coding: utf-8 -*-

from etl_utils import is_regular_word, regexp, ld
import re


class SplitBlock:
    """
    A SplitBlock is a struct that contains strings, all blank, or all not blank.

    Notice: Blank is ASCII blank.
    """

    def __init__(self, str1, _type, pos_begin, pos_end, pre_split_block=None, next_split_block=None):
        if isinstance(str1, unicode):
            str1 = str1.encode("UTF-8")

        self.string            = str1
        self.length            = len(str1)
        self._type             = _type

        for type1 in ["blank", "letter", "other"]:
            setattr(self, "is_" + type1, self._type == type1)

        self.is_enough_chars   = len(self.string) > 3
        self.is_regular        = is_regular_word(self.string)
        self.is_abc            = unicode(self.string, "UTF-8") in ld.two_length_words
        self.is_candidate      = self.is_letter and (
                                        #((not self.is_enough_chars) and (not self.is_regular)) or
                                        (not self.is_enough_chars) or
                                        (not self.is_regular) or
                                        # maybe add Trie
                                        (self.string in ["bidden", "instr"])
                                    )

        self.is_chars          = bool(regexp.word.match(self.string))
        first_char             = len(self.string) and list(self.string)[0] or ""
        self.is_upper          = bool(re.compile("[A-Z]").match(first_char))
        self.is_none_letter    = not regexp.alphabet.match(first_char)
        self.is_postfix        = (not self.is_upper) and (not self.is_none_letter)
        self.is_standalone     = (self.string == 'a') or ((len(self.string) >= 2) and self.is_regular or self.is_none_letter)

        self.pos_begin         = pos_begin
        self.pos_end           = pos_end

        self.p_sb              = pre_split_block
        self.n_sb              = next_split_block

        self.can_fill          = False

    def __repr__(self):
        s1 = self.string.decode("UTF-8")
        return (("<<<\"%s\", [%s : %s : %s-%s%s]>>>") % (s1, self._type,
                self.length, self.pos_begin, self.pos_end, ({True:" can_fill",False:""}[self.can_fill]))).encode("UTF-8")

    def __hash__(self):
        return hash(str(self.length) + str(self.pos_begin) + str(self.pos_end)) % 1000000

    def __str__(self):
        return self.string

    def __len__(self):
        return len(str(self))

    def __eq__(self, another):
        if type(another) is not type(self):
            return False
        return (self.string == another.string) and (self.pos_begin == another.pos_begin)

    def utf8low(self):
        return self.string.strip().decode("UTF-8").lower()

    def relative_to_current(self, idx):
        if idx == 0:
            return self

        def get_that_split_block(idx):
            current_split_block = self
            attr = "n_sb" if (idx > 0) else "p_sb"

            for idx1 in xrange(idx):
                current_split_block = getattr(current_split_block, attr)
                if type(current_split_block) is type(self):
                    continue
                else:
                    return None
            return current_split_block
        return get_that_split_block(idx)
    r_sb = relative_to_current

    def siblings_to_item(self, another):
        method = 'n_sb' if (self.pos_begin < another.pos_begin) else 'p_sb'

        siblings = [self]
        current_sb = self
        while getattr(current_sb, method) is not another:
            current_sb = getattr(current_sb, method)
            siblings.append(current_sb)
        siblings.append(another)

        return siblings
