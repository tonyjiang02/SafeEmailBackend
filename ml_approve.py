import analyzetext


def approval_request(msg, categories):
    text_results, text_probabilities = analyzetext.analyze_attributes(msg, categories)

    for result in text_results:
        if result:
            return False, text_probabilities

    return True, text_probabilities
