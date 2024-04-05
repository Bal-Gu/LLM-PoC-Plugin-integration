def jaccard_similarity(text1, text2):
    # Split the texts into sets of words
    set1 = set(text1.split())
    set2 = set(text2.split())
    # Calculate the intersection and the smaller set
    intersection = set1.intersection(set2)
    smaller_set = set1 if len(set1) < len(set2) else set2
    # Calculate the modified Jaccard similarity
    similarity = len(intersection) / len(smaller_set)
    return similarity


def is_text_similar(text1, text2, threshold=0.8):
    # Calculate the Jaccard similarity
    similarity = jaccard_similarity(text1, text2)
    # Check if the similarity is above the threshold
    if similarity > threshold:
        return True
    else:
        return False
