import sys
import numpy as np


def simple_base_compare_score(b1, b2):
    if b1 == b2:
        return 1
    else:
        return -2


def max_alignment_score_above_cutoff(s1, s2, base_compare_func, sigma, cutoff):
    # Score alignment paths. s1 is first dimension, s2 second

    max_paths = np.zeros((len(s1)+1, len(s2)+1))
    for i in range(1, len(s1)+1):
        for j in range(1, len(s2)+1):
            max_paths[i, j] = max(max_paths[i, j-1] - sigma, max_paths[i-1, j] - sigma,
                                  max_paths[i-1, j-1] + base_compare_func(s1[i-1], s2[j-1]), 0)
            if max_paths[i, j] >= cutoff:
                return True
    return False


def max_path_matrix(s1, s2, base_compare_func, sigma):
    # Score alignment paths. s1 is first dimension, s2 second

    max_paths = np.zeros((len(s1)+1, len(s2)+1))
    for i in range(1, len(s1)+1):
        for j in range(1, len(s2)+1):
            max_paths[i, j] = max(max_paths[i, j-1] - sigma, max_paths[i-1, j] - sigma,
                                  max_paths[i-1, j-1] + base_compare_func(s1[i-1], s2[j-1]), 0)

    return max_paths


def local_alignment(s1, s2, scoring_dict, sigma):  # Sigma is penalty for indels. Must be positive.
    max_paths = max_path_matrix(s1, s2, scoring_dict, sigma)

    # Backtrack through max_paths to find best substring
    s1_align_str = ''
    s2_align_str = ''
    # max_paths[i,j] is place to start for max alignment. Strings start at i-1 and j-1
    i, j = np.unravel_index(max_paths.argmax(), max_paths.shape)

    while max_paths[i, j] > 0:
        if max_paths[i, j] == max_paths[i-1, j-1] + simple_base_compare_score(s1[i-1], s2[j-1]):
            # Match or mismatch
            s1_align_str = s1[i-1] + s1_align_str
            s2_align_str = s2[j-1] + s2_align_str
            i -= 1
            j -= 1
        elif max_paths[i, j] == max_paths[i-1, j] - sigma:  # Deletion
            s1_align_str = s1[i-1] + s1_align_str
            s2_align_str = '-' + s2_align_str
            i -= 1
        elif max_paths[i, j] == max_paths[i, j-1] - sigma:  # Insertion
            s1_align_str = '-' + s1_align_str
            s2_align_str = s2[j-1] + s2_align_str
            j -= 1
        else:
            sys.exit("Backtracking error.")

    print '%g' % max_paths.max()
    print s1_align_str
    print s2_align_str

if __name__ == "__main__":
    s1 = 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
    s2 = 'AA1AA2AAAAAAAAAAAAAAAAAAAA3AAAAAA4AAAAAAAAAAAAAAAA5AAAAAAAAAAAAAAAAAAAAAA6AAAAAAA7A8AAAAAAAA9A0AAA'
    sigma = 3   # Penalty for gap opening/extension. Should be positive.
    cutoff = 6
    local_alignment(s1, s2, simple_base_compare_score, sigma)
    print 'Longer than ', cutoff,
    print max_alignment_score_above_cutoff(s1, s2, simple_base_compare_score, sigma, cutoff)

    import contaminants_cython
    print 'Longer than ', cutoff,
    print contaminants_cython.max_alignment_score_above_cutoff(s1, s2, cutoff)
