"""Collection of utility functions."""

def tasting_entry_as_dict(tasting_tuple):
    return {
        'id': tasting_tuple[0],
        'tasting_name': tasting_tuple[1],
        'created_by': tasting_tuple[2],
        'creation_time': tasting_tuple[3],
        'join_code': tasting_tuple[4],
        'grogg_list': tasting_tuple[5],
        'current_grogg_idx': tasting_tuple[6],
        'ratings': tasting_tuple[7],
        'rated_by': tasting_tuple[8],
    }


def update_ratings_list(r_list, grogg_idx, new_rating):
    n_groggs = len(r_list)
    # Extend if this is first rating for the grogg
    if grogg_idx == n_groggs:
        r_list.append([])

    # Add the rating
    r_list[grogg_idx].append(new_rating)

    # Ensure equal number of ratings for all groggs
    dummy_rating = [None, None, None]
    # Remove all [None,None,None]s
    for l in r_list:
        while l.count(dummy_rating) > 0:
            l.remove(dummy_rating)

    n_ratings = [len(l) for l in r_list]
    max_ratings = max(n_ratings)
    for l in r_list:
        while len(l) < max_ratings:
            l.append(dummy_rating)

    return r_list


def update_rated_by_list(r_list, grogg_idx, new_rater):
    n_groggs = len(r_list)
    # Extend if this is first rating for the grogg
    if grogg_idx == n_groggs:
        r_list.append([])

    # Add the rater
    r_list[grogg_idx].append(new_rater)

    # Ensure equal number of raters for all groggs
    # Remove all None raters
    for l in r_list:
        while l.count(None) > 0:
            l.remove(None)

    n_ratings = [len(l) for l in r_list]
    max_ratings = max(n_ratings)
    for l in r_list:
        while len(l) < max_ratings:
            l.append(None)

    return r_list