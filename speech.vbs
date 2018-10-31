Set objVoice = CreateObject("SAPI.SpVoice")
objVoice.Speak(WScript.Arguments.Item(0))
