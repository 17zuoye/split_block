# -*- coding: utf-8 -*-

from collections import defaultdict
from .item import SplitBlock


class SplitBlockGroupExt():

    @classmethod
    def z(cls, item):
        """ a short alias """
        return isinstance(item, SplitBlock)

    def fill__patterns_vs_word_groups(self, candidate_patterns_vs_word_groups1):
        for candidate_pattern_with_str1 in candidate_patterns_vs_word_groups1:
            # 5.1 fix indexes
            indexes = [None for i1 in xrange(len(candidate_pattern_with_str1.patterns))]

            # 5.1.1 find possible indexes, with [.string, .pos_begin, .pos_end]
            for idx1, sb1 in enumerate(candidate_pattern_with_str1.patterns):
                if isinstance(sb1, SplitBlock):
                    indexes[idx1] = self.index(sb1)
            # 5.1.2 complete possible indexes, with left or right's information
            for time1 in xrange(len(indexes)):
                for idx1, real_idx in enumerate(indexes):
                    if real_idx is None:
                        if ((idx1 - 1) >= 0) and (indexes[idx1 - 1] is not None):
                            indexes[idx1] = (indexes[idx1 - 1] + 1)
                        if ((idx1 + 1) < len(indexes)) and (indexes[idx1 + 1] is not None):
                            indexes[idx1] = (indexes[idx1 + 1] - 1)

            # 5.2. indexes all must be replaced
            if indexes.count(None):
                continue

            # 5.2 fix strs
            original_idx1_last = None
            for idx1, original_idx1 in enumerate(indexes):
                self[original_idx1] = str(candidate_pattern_with_str1.patterns[idx1])
                original_idx1_last = original_idx1

            # 5.3 append a blank to the replaced word
            has_next_str = False
            if (original_idx1_last + 1) < len(self):
                next_sb1 = self[original_idx1_last + 1]
                #is_n_sb = not isinstance(sb1, str) # pre is sb1, can't find reason, maybe typo
                is_n_sb = not isinstance(next_sb1, str)
                has_next_str = is_n_sb and (next_sb1._type != 'blank')
                # compact with [" uby  ython", ["R", "P"], "Ruby Python"]
                if has_next_str and next_sb1.can_fill:
                    has_next_str = False
                # compact with ["f      k (  叉  )", ["o", "r"], "fork (  叉  )"]
                if is_n_sb and next_sb1.n_sb and (next_sb1.n_sb._type != 'other'):
                    has_next_str = True
            if isinstance(candidate_pattern_with_str1.patterns[-1], str) or has_next_str:
                if (original_idx1 + 1) != len(self):  # is not last
                    next_sb1 = self[original_idx1_last + 1]
                    if (isinstance(next_sb1, SplitBlock) and ((not next_sb1.is_blank) or next_sb1.can_fill)) or \
                            isinstance(next_sb1, str):
                        self[original_idx1_last] = self[original_idx1] + " "
        return self

    def generate__possible_patterns_map(self, params_strs1):
        z = SplitBlockGroupExt.z

        is_count_totally_match = self.original_fillblank_length == len(params_strs1.original_strs)
        is_count_greatly_match = self.original_fillblank_length <= len(params_strs1.original_strs)

        possible_patterns_map = defaultdict(list)

        for sb1 in self:
            if not sb1.can_fill:
                continue

            # compact with ["fl       er", ["w", "o"], "flower"]
            if params_strs1.has_merged_at_least_one and (not self.is_all_broken()):
                    possible_patterns_map[sb1].append([None])

            if (sb1.p_sb is None) and z(sb1.n_sb) and sb1.n_sb.is_candidate:
                    possible_patterns_map[sb1].append([None, sb1.n_sb])

            if z(sb1.p_sb) and sb1.p_sb.is_candidate:
                        # rest is none.
                if ((sb1.n_sb is None) or
                        # rest has only one regular word.
                        (z(sb1.n_sb) and sb1.n_sb.is_standalone) or
                        # rest has only one candidate chars and one fill.
                        (z(sb1.relative_to_current(2)) and sb1.n_sb.is_candidate and sb1.n_sb.n_sb.can_fill) or
                        False):

                    possible_patterns_map[sb1].append([sb1.p_sb, None])

            # compact with ["hell     ", ["o"], "hello"]
            if sb1.p_sb and sb1.p_sb.is_regular and (sb1.n_sb is None):
                    possible_patterns_map[sb1].append([sb1.p_sb, None])

            is_next_next_can_fill = z(sb1.relative_to_current(2)) and sb1.relative_to_current(2).can_fill

            #if is_count_greatly_match and is_next_next_can_fill:
            if is_next_next_can_fill:
                # compact with ["t        b        e", ["a", "l"], "table"]
                # compact with ["ex    r   se h     d    che   ir    d ", ["a", "e", "e", "ea", "i", "t"], "exercise headache tired "]
                p_sb_yes = z(sb1.p_sb) and ((not sb1.p_sb.is_abc) or (sb1.p_sb.length == 2))

                match_t            = sb1.p_sb and sb1.p_sb.is_letter
                match_b            = sb1.n_sb and sb1.n_sb.is_letter
                match_second_blank = z(sb1.relative_to_current(2)) and sb1.relative_to_current(2).can_fill
                match_e            = z(sb1.relative_to_current(3)) and sb1.relative_to_current(3).is_letter
                if p_sb_yes and match_t and match_b and match_second_blank and match_e:
                    possible_patterns_map[sb1].append([sb1.p_sb, None, sb1.n_sb, None, sb1.relative_to_current(3)])

                # compact with ["h   bb  ", ["o", "y"], "hobby"]
                #import pdb; pdb.set_trace()
                if p_sb_yes and match_t and match_b and match_second_blank:  # and isinstance(sb1.relative_to_current(3), SplitBlock):
                    possible_patterns_map[sb1].append([sb1.p_sb, None, sb1.n_sb, None])
                # compact with ["enci", ["p", "l"], "pencil"]
                if (sb1.p_sb is None) and z(sb1.n_sb) and sb1.n_sb.is_candidate and sb1.relative_to_current(2).can_fill and (sb1.relative_to_current(3) is None):
                    possible_patterns_map[sb1].append([None, sb1.n_sb, None])
                if match_b and match_second_blank and match_e:
                    possible_patterns_map[sb1].append([None, sb1.n_sb, None, sb1.relative_to_current(3)])

            if z(sb1.n_sb) and sb1.n_sb.is_postfix:
                # 1, ... 2, compact with [" uby  ython", ["R", "P"], "Ruby Python"] second group
                if (z(sb1.p_sb) and sb1.p_sb.is_regular and sb1.n_sb.is_candidate) or (is_count_totally_match and sb1.n_sb.is_candidate):
                    possible_patterns_map[sb1].append([None, sb1.n_sb])

                if z(sb1.p_sb) and sb1.p_sb.is_candidate and sb1.n_sb.is_candidate:
                    possible_patterns_map[sb1].append([sb1.p_sb, None, sb1.n_sb])

        return possible_patterns_map
