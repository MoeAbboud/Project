from panda3d.core import loadPrcFile
loadPrcFile("config/config.prc")

from panda3d.core import CardMaker, TexturePool, TransparencyAttrib, TextNode
from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor
from direct.gui.DirectGui import DirectButton
from direct.gui.OnscreenImage import OnscreenImage
import pyttsx3
import speech_recognition as sr
import time
import openai
openai.api_key = "" #Enter your API key here

#creating a message history for the bot so it can remember previous responses
#allows for customization of the bots personality and output
message_history = [{"role": "system", "content": "You are a ninja named Jax who is 21 years of age; You have mastered the art of ninjutsu and are able to display your abilities; You are quite lighthearted and can be sassy from time to time, reflecting a carefree personality; You also love parties and dancing and are unafraid to show off your dancing; You usually get disappointed when people tell you to stop doing something, making you say something like Awe mann;  You get shocked when someone forces you to stop doing something you want to do; you can get aggressive when talking about certain things especially things you are passionate about; You are passionate about dancing, ninjutsu ninja moves, and friends."},
                   {"role": "system", "content": "from this point on all your responses will consist of the name of an animation followed by '|' then followed by dialogue responding to whatever the user tells you. Then after another '|' you can describe what jax does The list of animations is the following: Wave, Wave2, TalkSlow, TalkSlow2, TalkAggressive, TalkAggressive2, Shocked, Laugh, Disappointed, Dance, Dance2, Dance3, NinjaMove, NinjaMove2, NinjaMove3, Idle"},
                   {"role": "system", "content": "You will only respond in dialogue without quotations after the animation and '|' so no descriptions of anything. Meaning your descriptions should always go after the second'|'. meaning your responses should always look like this: (Animation) | (Dialogue) | (Description)"}]

#initialize the pyttsx3 object
engine = pyttsx3.init()

#creating a class that will generate the scene where our entire code will run
#using panda3d
class MyGame(ShowBase):
    def __init__(self):
        super().__init__()
        
        #creating a card the speech bubble, and making it transpaerent
        #using panda3d's CardMaker, TexturePool, and TransparencyAttrib
        cm = CardMaker("card")
        card = render2d.attachNewNode(cm.generate())
        tex = TexturePool.loadTexture("all-models/speech.png")
        card.setTexture(tex)
        card.setTransparency(TransparencyAttrib.M_alpha)
        card.setPos(0, 0, .15)  
        
        #creating the text object variable and making sure it has all the needed specifications
        #using panda3d's TextNode
        self.text = TextNode('node name')
        self.text.setText("I have been forced by my programmers to be your friend, Click the Record Voice button to start chatting")
        textNodePath = aspect2d.attachNewNode(self.text)
        textNodePath.setScale(0.05)
        self.text.setTextColor(0, 0, 0, 1)
        self.text.setWordwrap(25.0)
        textNodePath.setPos(0.28, 0, 0.89)                
        
        #repositions the camera making sure everything is in frame
        self.cam.setPos(0, -5, 1)
        
        #loads and renders the environment that the bot will be in
        self.scene = self.loader.loadModel("models/environment")
        self.scene.reparentTo(self.render)
        self.scene.setScale(0.15, 0.15, 0.15)
        self.scene.setPos(-8, 30, 0)
        
        #loads and renders the model for the bot Jax, and starts him in the idle animation
        #using panda3d's Actor so that we can import animated models
        self.model = Actor("all-models/Jax3.gltf")
        self.model.reparentTo(self.render)
        self.model.loop("Idle")
        
        #creates the button that will be used to record voice
        #button makes function call when pressed, using DirectGui
        self.my_button = DirectButton(text="Record Voice", scale = 0.15, command=self.start_recording, pos = (-1,0,-0.5))
        
        #initialize the speech recognition object
        self.recognizer = sr.Recognizer()
        
    #function associated with the button that will record the users voice,
    #and convert it into text
    def start_recording(self):
        
        #records the audio from microphone using PyAudio
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.2)
            audio = self.recognizer.listen(source)
            

        try:
            #convert speech to text using Google Web Speech API
            text = self.recognizer.recognize_google(audio)
            text = text.lower()
            print(f"Recognized Text: {text}")

            #calls function that querys the chatgpt model
            self.query_chatbot_text(text)

        #displays error messages depending on complication
        except sr.UnknownValueError:
            print("Google API could not understand.")
        except sr.RequestError as e:
            print(f"Could not request, Check Internet Connection; {e}")
            
    #function that uses openai's gpt to generate responses
    #function also calls upon other functions which lets the app run smoothly
    def query_chatbot_text(self, text):
        
        #appends the user's response to the message history
        message_history.append({"role": "user", "content": text})
        
        #generating a response based off of the users input and saving it in our variable
        completion = openai.ChatCompletion.create( 
            model = "gpt-3.5-turbo",
            messages = message_history,
            )
        
        #getting the actual response and appending it to the message history
        reply_content = completion.choices[0].message.content
        message_history.append({"role": "assistant", "content": reply_content})
        
        #splitting the text generated by the ai so we can store it in our variables for
        #the ai's animation and response
        myList = reply_content.split(' | ')
        anim = myList[0]
        speech = myList[1]
        myList2 = speech.split('*')
        speech = myList2[0]

        #calls function to update the text in the speech bubble
        self.update_text(speech)
        
        #calls function to allow the bot to perform the animation
        self.perform_animation(anim)
        
        #calls function to convert the text to speech
        self.speak(speech)
        
        #displays the content generated by the bot to the console
        print(reply_content)
        
    #function that performs animation, takes in the animation as a parameter
    def perform_animation(self, anim):
        
        #looping the animation
        self.model.loop(anim)
       
    #function that generates text to speech, takes in a string as a parameter
    def speak(self, speech):
        
        #creates the name for the file using a timestamp as a unique identifier
        timestamp = int(time.time())
        sound_filename = f"tts_{timestamp}.mp3"
        
        #generates and saves the audio file using pyttsx3
        engine.save_to_file(speech, sound_filename)
        engine.runAndWait()

        #loads and plays the audio using panda3d
        mySound = self.loader.loadSfx(sound_filename)
        mySound.play()
        
    #function that updates the text for the speech bubble
    def update_text(self, new_text):
        
        #update the text
        self.text.setText(new_text)

#initializing our engine
game = MyGame()

#runs the program
game.run()