import time
import speech_recognition as sr


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
        response["transcription"] += recognizer.recognize_google(audio)
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

    print("Hey you can start taking your notes:")

    file = open("notes.txt", "w")
    start = time.time()

    while True:
        speech = recognize_speech_from_mic(recognizer, microphone)
        end = time.time()
        if((end-start)>5):
            print("Hey! You haven't spoken for a while! Saving your notes. Bye!")
            break

        if speech["transcription"]:
            start = time.time()
            print("You spoke:"+speech["transcription"])
            file.write(speech["transcription"] + "\n")
            if(speech["transcription"]==""):
                print("Hey!! I didn't catch that. What did you say?\n")
            if (speech["transcription"]=="stop"):
                break
        if not speech["success"]:
            break

        if speech["error"]:
            print("ERROR: {}".format(speech["error"]))
    file.close
