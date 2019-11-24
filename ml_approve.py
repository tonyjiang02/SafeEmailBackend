import analyzetext

def approval_request(msg):
    # TODO: use ML to check sentiment of `msg`
    text_results, text_probabilities = analyzetext.analyze_attributes(msg, ["toxicity"])

    for result in text_results:
        if result:
            return False
    
    return True