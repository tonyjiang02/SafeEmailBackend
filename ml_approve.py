import analyzetext


def approval_request(msg):
    text_results, text_probabilities = analyzetext.analyze_attributes(msg, ["toxicity"])

    for result in text_results:
        if result:
            return False

    return True
