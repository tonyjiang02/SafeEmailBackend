from googleapiclient import discovery

def probability_of(text, attribute="TOXICITY"):
  # main attribute: TOXCICITY SEVERE_TOXICITY
  # experimental attributes: IDENTITY_ATTACK INSUlT PROFANINTY THREAT SEXUALLY_EXPLICIT FLIRTATION
  API_KEY='AIzaSyAZh9GRVK3fgqZNwdhtqcy8k7BFOVCK7_8'

  # Generates API client object dynamically based on service name and version.
  service = discovery.build('commentanalyzer', 'v1alpha1', developerKey=API_KEY)

  analyze_request = {
    'comment': { 'text': text},
    'requestedAttributes': {attribute.upper(): {}}
  }

  response = service.comments().analyze(body=analyze_request).execute()
  probability = float(response["attributeScores"][attribute.upper()]["summaryScore"]["value"]);
  
  print(attribute + " probability of '" + text + "': " + str(probability*100) + "%")

  return probability

def analyze_attributes(text, attributes, threshold=0.7):
  results = []
  probabilities = []

  # give function lists of attributes
  for attribute in attributes:
    prob = probability_of(text, attribute)
    probabilities.append(prob)
    
    if (prob > threshold):
      results.append(True)
    else:
      results.append(False)

  return results, probabilities

if __name__ == "__main__":
  print(analyze_attributes('i hate you', ["toxicity", "severe_toxicity", "IDENTITY_ATTACK", "INSUlT"]))