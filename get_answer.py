import requests
import json

import speech_recognition as sr
d = dict()
maxScore= 0
def calculate_score(tags,ques,inner):
    global maxScore
    global para
    url = "https://api.datamuse.com/words?ml="
    ques1 = ""
    for word in ques:
        search_query = url + word
        response = requests.get(search_query)
        json_response = json.loads(response.content)[:5]
        d[word] = map(lambda x: str(x['word']), json_response)
        ques1 += " ".join(d[word]) + " " + word + " "

    ques1 = ques1.split()

    score = len(set(ques1).intersection((tags)))
    if score > maxScore:
        maxScore = score
        para = inner

def recognize_speech_from_mic(recognizer, microphone):

    if not isinstance(recognizer, sr.Recognizer):
        raise TypeError("`recognizer` must be `Recognizer` instance")

    if not isinstance(microphone, sr.Microphone):
        raise TypeError("`microphone` must be `Microphone` instance")

    # set up the response object
    response = {
        "success": True,
        "error": None,
        "transcription": ""
    }

    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:

        response["transcription"] = recognizer.recognize_google(audio)
    except sr.RequestError:
        # API was unreachable or unresponsive
        response["success"] = False
        response["error"] = "API unavailable"
    except sr.UnknownValueError:
        # speech was unintelligible
        response["error"] = "Unable to recognize speech"

    return response



if __name__ == "__main__":

    # create recognizer and mic instances
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    url = "https://api.datamuse.com/words?ml="
    similar_words = []

    print("Hey!! What notes do you want to find ?")

    while True:
        speech = recognize_speech_from_mic(recognizer, microphone)

        if speech["transcription"]:
            print("You Spoke: "+ speech["transcription"])
            question = speech["transcription"]
            break

        if not speech["success"]:
            break


        if speech["error"]:
            print("ERROR: {}".format(speech["error"]))
        print("I didn't catch that. What did you say?\n")

    response2 = requests.post("http://api.cortical.io:80/rest/text/keywords?retina_name=en_associative", data=question)
    q_keywords = response2.json()
    f = open("notes.txt", "r")
    para = ""
    while True:
        line = f.readline()
        if not line:
            break
        if line.isspace():
            continue
        line = line.split()
        if line[0].lower() == "topic:":
            inner = f.readline()

            # paragraph read
            response = requests.post("http://api.cortical.io:80/rest/text/keywords?retina_name=en_associative",
                                     data=inner)
            tags = json.loads(response.content)
            tags = map(lambda x: str(x), tags)
            calculate_score(tags, q_keywords, inner)

    print("Here are the notes you searched for : "+para)

    f.close()