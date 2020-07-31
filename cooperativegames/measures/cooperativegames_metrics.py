
__author__ = 'To\xc3\xb1o G. Quintela (tgq.spm@gmail.com)'

"""
Main cooperative games measures
-------------------------------
Module which groups functions useful for the study of cooperative games.

TODO:
----
shapley index, too much time.

shapley_value
assimetric shapley Index


"""

import numpy as np
from itertools import permutations, combinations
from collections import Counter
import math
from cooperativegames.measures.cooperativegames_tools import all_subsets_it,\
    winning_coalitions_it, get_critical_players, weight_coalition, all_subsets


def weighted_winning_coalitions(distrib_repr, weights, win_thr=0.5):
    """Weight measure of the possible coalitions regarding how natural are the
    possible winning coalitions.

    Parameters
    ----------
    distrib_repr: list or np.ndarray
        the distribution representation.
    weights: list or np.ndarray
        the weight of each possible pair oc coalitions.
    win_thr: float (default=0.5)
        the winner threshold in proportion.

    Returns
    -------
    power: float
        the power index.

    """
    ## 0. Initalization of variables
    distrib_repr = np.array(distrib_repr)
    n = distrib_repr.shape[0]
    n_v = np.sum(distrib_repr)
    win_v = n_v*win_thr
    power = np.zeros(n)

    ## Compute all the winning coalitions
    coalitions = all_subsets_it(range(n))
    for coalition in coalitions:
        if np.sum(distrib_repr[coalition]) > win_v:
            # Compute weights of the coalition
            w_c = weight_coalition(coalition, weights)
            power[coalition] += w_c

    ## Normalize measure
    if power.sum():
        power = power/power.sum()

    return power


def weighted_worsable_coalitions(distrib_repr, weights, win_thr=0.5):
    """Weight measure of the power to break the winning coalitions regarding
    how probable the coalition is.

    Parameters
    ----------
    distrib_repr: list or np.ndarray
        the distribution representation.
    weights: list or np.ndarray
        the weight of each possible pair oc coalitions.
    win_thr: float (default=0.5)
        the winner threshold in proportion.

    Returns
    -------
    power: float
        the power index.

    """
    ## 0. Initalization of variables
    distrib_repr = np.array(distrib_repr)
    n = distrib_repr.shape[0]
    n_v = np.sum(distrib_repr)
    win_v = n_v*win_thr
    power = np.zeros(n)
    # temp
    powers_coal = []

    ## Compute all the winning coalitions
    w_coalitions = winning_coalitions_it(range(n), distrib_repr, win_v)
    for w_coalition in w_coalitions:
        cri = get_critical_players(w_coalition, distrib_repr, win_v)
        cri = [w_coalition[i] for i in cri]
        if cri:
            # Evaluate winning coalition weight
            w_wc = weight_coalition(w_coalition, weights)
            if w_wc == 0:
                continue
            powers_coal.append((w_coalition, w_wc))
            # Evaluate consequent losing coalitions
            coal_los = [[i for i in cri if i != e] for e in cri]
            w_lc = [weight_coalition(l_coal, weights) for l_coal in coal_los]
            # Normalize over critical parties
            w_lc = [w_wc/w_lc[i] for i in range(len(cri))]
            w_lc = np.array(w_lc) / np.array(w_lc).sum()
            for i in range(len(cri)):
#                print cri, cri[i], w_lc[i]
                power[cri[i]] += w_wc*w_lc[i]

    ## Normalize measure over coalitions weights
    if power.sum():
        power = power/power.sum()

    return power


def shapley_index(distrib_repr, win_thr=0.5):
    """The Shapley index of power.

    Parameters
    ----------
    distrib_repr: list or np.ndarray
        the distribution representation.
    win_thr: float (default=0.5)
        the winner threshold in proportion.

    Returns
    -------
    shapley_ind: float
        the shapley power index.

    References
    ----------
    .. [1] Shapley, L. S.; Shubik, M. (1954). "A Method for Evaluating the
    Distribution of Power in a Committee System". American Political Science
    Review 48 (3): 787-792. doi:10.2307/1951053

    TODO
    ----
    Hu, X. (2006). "An Asymmetric Shapley-Shubik Power Index". International
    Journal of Game Theory 34 (2): 229-240. doi:10.1007/s00182-006-0011-z.

    """
    distrib_repr = np.array(distrib_repr)
    n = distrib_repr.shape[0]
    n_v = np.sum(distrib_repr)
    win_v = n_v*win_thr
    p = math.factorial(n)

    cum = []
    perm = permutations(np.arange(n)[distrib_repr > 0], int((distrib_repr > 0).sum()))
    for per in perm:
        idx = np.where(np.cumsum(distrib_repr[list(per)]) >= win_v)[0][0]
        cum.append(per[idx])
    c = Counter(cum)
    # Formatting output
    shapley_ind = np.zeros(n)
    n_out = len(c.values())
    # shapley_ind[:n_out] = np.array(c.values())/float(p)
    for item in c.items():
        shapley_ind[item[0]] = item[1] / float(p)

    return shapley_ind


def banzhaf_index(distrib_repr, win_thr=0.5):
    """The Banzhaf power index.

    Parameters
    ----------
    distrib_repr: list or np.ndarray
        the distribution representation.
    win_thr: float (default=0.5)
        the winner threshold in proportion.

    Returns
    -------
    banzhaf_ind: float
        the Banzhaf power index.

    References
    ----------
    .. [1] Banzhaf, John F. (1965), "Weighted voting doesn't work: A
    mathematical analysis", Rutgers Law Review 19 (2): 317-343

    """

    # Initalization of variables
    distrib_repr = np.array(distrib_repr)
    n = distrib_repr.shape[0]
    n_v = np.sum(distrib_repr)
    win_v = n_v*win_thr

    # Compute subsets and wining subsets
    subsets = all_subsets(list(np.arange(n)[distrib_repr > 0]))
    win_subsets = [subsets[i] for i in range(len(subsets))
                   if np.sum(distrib_repr[subsets[i]]) > win_v]

    # Obtaining swing voters
    swing_voters = []
    for wsset in win_subsets:
        aux = []
        for e in wsset:
            if np.sum(distrib_repr[wsset]) - distrib_repr[e] <= win_v:
                aux.append(e)
        swing_voters.append(aux)

    # Count swing voters
    aux = []
    for e in swing_voters:
        aux += e
    c = Counter(aux)
    nc = len(aux)
    # Computing index
    banzhaf_ind = np.zeros(distrib_repr.shape)
    # banzhaf_ind[c.keys()] = np.array(c.values())/float(nc)
    for item in c.items():
        banzhaf_ind[item[0]] = item[1] / float(nc)

    return banzhaf_ind


def shapley_value(set_, value_func=lambda x: 1):
    """The Shapley value.

    Parameters
    ----------
    set_: list or np.ndarray
        the list of players.
    value_func: function
        the value function of each subset.

    Returns
    -------
    shap_values: np.ndarray
        the computed shapley values.

    References
    ----------
    .. [1] Lloyd S. Shapley. "A Value for n-person Games". In Contributions to
    the Theory of Games, volume II, by H.W. Kuhn and A.W. Tucker, editors.
    Annals of Mathematical Studies v. 28, pp. 307-317. Princeton University
    Press, 1953.

    """

    # Initialization
    set_ = np.array(set_)
    n = set_.shape[0]
    idx = np.array(range(n))
    except_idx = [[j for j in idx if j != i] for i in idx]

    # Computation of the values
    phis = []
    for i in idx:
        ssets = all_subsets(except_idx[i])
        ssets = [] + ssets
        phi = 0
        for j in range(len(ssets)):
            l = len(ssets[j])
            cte = math.factorial(l) * math.factorial(n-l-1)
            cte = np.abs(cte / float(math.factorial(n)))
            idsx1 = list(np.sort(ssets[j]+[i]))
            idsx2 = list(np.sort(ssets[j]))
            phi += cte * (value_func(set_[idsx1])-value_func(set_[idsx2]))
        phis.append(phi)

    shap_values = np.array(phis)
    return shap_values
