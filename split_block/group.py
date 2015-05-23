# -*- coding: utf-8 -*-

import copy
import math

from .item import SplitBlock
from .group_ext import SplitBlockGroupExt
from .group_chapped import SplitBlockGroupChapped
from etl_utils import regexp, is_regular_word


class SplitBlockGroup(list, SplitBlockGroupExt, SplitBlockGroupChapped):

    def __init__(self, sbs=None):
        super(SplitBlockGroup, self).__init__(sbs or [])

        self.original_fillblank_length = self.fillblank_length()

    def is_all_individual_chars(self):
        """ all SplitBlock's length is less or equal than 1. """
        for sb1 in self:
            if sb1.length > 2:
                return False
        return True

    def fillblank_length(self):
        return len(filter(lambda sb1: (not isinstance(sb1, str)) and sb1.can_fill, self))

    def broken_letters_count(self):
        return len(filter(lambda sb1: (not isinstance(sb1, str)) and sb1.is_letter and (sb1.is_regular or sb1.is_abc or (len(str(sb1)) == 2)), self))

    def letters(self):
        return filter(lambda sb1: (not isinstance(sb1, str)) and sb1.is_letter, self)

    def letters_count(self):
        return len(self.letters())

    def strs(self):
        return filter(lambda sb1: isinstance(sb1, str), self)

    def strs_count(self):
        return len(self.strs())

    # compact with ["—Can you             ? —Yes, I can.", ["i", "m", "s", "w"], "—Can you swim ? —Yes, I can."]
    def is_all_broken(self):
        return (self.broken_letters_count() == self.letters_count()) and (len(self) <= 5)

    def index(self, item):
        """ overwrite list#index """
        result = None
        for idx1, sb1 in enumerate(self):
            if hash(item) == hash(sb1):
                result = idx1
                break
        return result

    def deepcopy(self):
        new_list = SplitBlockGroup()
        for i1 in self:
            new_list.append(copy.deepcopy(i1))
        return new_list

    def concat_items(self):
        return ''.join([str(s1 or "") for s1 in self])

    def fix_blanks_if_only_one_item(self):
        if (self.letters_count() == 1) and (len(self.letters()[0]) <= 5):
            self.letters()[0].is_candidate = True

        if (len(self) >= 1):
            # compact with ["amera", ["c"], "camera"]
            if self[0].is_candidate:
                sb1 = self[0]
                sb0 = SplitBlock("", "blank", None, None, None, sb1)
                sb0.can_fill = True
                self.insert(0, sb0)
                sb1.p_sb = sb0
            # compact with ["ch    mn", ["e", "i", "y"], "chimney"]
            if self[-1].is_candidate:
                sb_2 = self[-1]
                sb_1 = SplitBlock("", "blank", None, None, sb_2, None)
                sb_1.can_fill = True
                self.insert(len(self), sb_1)
                sb_2.n_sb = sb_1

        return self

    @classmethod
    def extract(cls, sentence, inspect=False):
        sbs = list()

        pre_type = [None, "letter", "blank", "other"][0]
        current_str = ""
        current_pos_begin = None
        current_pos_end = None
        p_sb = None

        for idx, char1 in enumerate(list(sentence) + [None]):
            # init variables
            current_type = None
            if (char1 == ' ') or (char1 is None):
                current_type = 'blank'
            current_type = current_type or (regexp.alphabet.match(char1) and 'letter')
            current_type = current_type or "other"
            # print "[char1]", char1, "[current_type]", current_type

            if pre_type is None:
                pre_type = current_type
            if current_pos_begin is None:
                current_pos_begin = idx

            # concat str1
            if (current_type == pre_type) and (char1 is not None):  # compact with ender
                current_str += char1
            else:
                # begin process new SplitBlock
                current_pos_end = idx

                # init current SplitBlock
                sb = SplitBlock(current_str, pre_type, current_pos_begin, current_pos_end, p_sb)
                sbs.append(sb)

                # process pre SplitBlock
                if p_sb:
                    p_sb.n_sb = sb

                # for next SplitBlock
                current_pos_begin = None
                p_sb = sb
                current_str = char1
                pre_type    = current_type

        # fill-able blank should be larger than min blank,
        # but there should always exists one fill-able blank.
        filter_sbs = filter(lambda sb1: sb1._type == 'blank', sbs)
        strlen_lambda = lambda sb1: len(str(sb1))
        max_length = 0
        if len(filter_sbs):
            min_length = len(min(filter_sbs, key=strlen_lambda))
            max_length = len(max(filter_sbs, key=strlen_lambda))
            if min_length == max_length:
                min_length -= 1
        else:
            min_length = 0
        if min_length >= math.sqrt(max_length):
            min_length = 0  # compact with ["e    e        ", ["y"], "eye"]

        for idx, sb in enumerate(sbs):
            is_front_and_end_letters = True
            if (idx > 0) and (idx <= (len(sbs) - 1)):
                is_front_and_end_letters = bool(regexp.alphabet.match(str(sb.p_sb or "") + str(sb.n_sb or "")))

            if sb._type == 'blank':
                s1 = sb.length > min_length
                s2 = ((sb.p_sb and not sb.n_sb) and (not is_regular_word(sb.p_sb))) or (is_front_and_end_letters and (sb.length > min_length))
                s3 = (len(sbs) > 1) and (idx == 0) and (not is_regular_word(sb.n_sb))
                if s1 and s2 or s3:
                    sb.can_fill = True

        if inspect:
            print
            for s1 in sbs:
                print repr(s1)
                print

        sbs = SplitBlockGroup(sbs)  # generate some attrs that based on 'sbs'
        sbs.fix_blanks_if_only_one_item()
        return sbs
