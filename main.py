import math,sys,json,os

#ans = input("What do you want to see?\n1. Create Video From List\n2. Create fresh video\n3. Open web browser download")
colors=["DeepSkyBlue1","DarkViolet","turquoise1","#ff006f","#ff7b00"]



try:
  import keybert
except:
  os.system("pip install keybert")
try:
  import moviepy
except:
  os.system("pip install moviepy")

from keybert import KeyBERT
import time
kw_model = KeyBERT()

bannedList = ["bribery"]
from moviepy.editor import AudioFileClip,TextClip,CompositeAudioClip,CompositeVideoClip,AudioClip,concatenate_audioclips,VideoFileClip,ImageClip
from moviepy.video.fx.resize import resize
#from moviepy.video.fx.all import *

#javascript:onbeforeunload=i=>1
import requests,os,random,json
unsplash_access_key = "2158d1296amsh6ca2c42e2e47890p185142jsn47c122b4c69a"#os.environ["unsplash"]
query_url = "https://api.unsplash.com/search/photos"


def get_amt():

  return len(os.listdir("images"))


def create_clip(textData):
    
      loop =get_amt()
    
      # Make the text. Many more options are available.
      timetoAdd=0
      audios=[]
      length=[]
      for i in range(loop):
        au=AudioFileClip(f"audio/{i}.mp3").set_start(timetoAdd)
        audios.append(au)
        timetoAdd+=au.duration
        length.append(au.duration)
      
      audios = CompositeAudioClip([AudioFileClip("backgroundMusic.mp3").subclip(0, sum(length)).volumex(0.5)] + audios)
    
      video = resize(VideoFileClip("start.mp4").subclip(5,5+sum(length)),width=1080,height=1920).set_audio(audios)
      
      start_time=0
      textStart=0
      all_clips=[]
      for i in range(loop):      
        all_clips.append(resize(ImageClip(f"images/{i}.png").set_duration(length[i]).set_start(start_time).set_position(("center",400)), width=500, height=500))
    
        words=textData[i].split()
        colorChosen = random.choice(colors)
        duration=(length[i]-1)/len(words)
        for word in words:
      
          text_clip = TextClip(word,font="Fredoka-Bold.ttf",fontsize=150,color=colorChosen).set_duration(duration).set_start(textStart).set_pos(("center",1000))
          all_clips.append(text_clip)
    
          textStart+=duration
        textStart+=1 
          # Concatenate all the TextClips into one video
        start_time=start_time+length[i]
    
    
      all_clips.insert(0,video)
      result = CompositeVideoClip(all_clips)
    
      result.write_videofile("output.mp4",fps=30,threads=4,preset="ultrafast")
      
def remove_images():
  directory = "images"
  print("DELETING current images")
  for filename in os.listdir(directory):
      file_path = os.path.join(directory, filename)
      try:
          if os.path.isfile(file_path):
              os.unlink(file_path)
      except Exception as e:
          print(f"Failed to delete {file_path}. Reason: {e}")
  directory = "audio"
  print("DELETING current audio")
  for filename in os.listdir(directory):
      file_path = os.path.join(directory, filename)
      try:
          if os.path.isfile(file_path):
              os.unlink(file_path)
      except Exception as e:
          print(f"Failed to delete {file_path}. Reason: {e}")
  return
def get_tts(text):
  # Set the API endpoint URL and parameters
  
  # Make a GET request to the API endpoint
  return requests.get("http://api.voicerss.org/", params={
      'key':"4c80012ecb4040558cdd6ce8593012b6",#os.environ["ttsApi"],
      'src': text,
      'hl': 'en-us',
      'v':"Mike",
      'c': 'MP3',
      'f': '44khz_16bit_stereo'
  })
  
def get_showerthoughts():
  url = "https://stapi-showerthoughts.p.rapidapi.com/api/v1/stapi/latest"
  
  headers = {
    "X-RapidAPI-Key": "2158d1296amsh6ca2c42e2e47890p185142jsn47c122b4c69a",#os.environ["SHOWERTHOUGHTS"],
    "X-RapidAPI-Host": "stapi-showerthoughts.p.rapidapi.com"
  }
  
  response = requests.get(url, headers=headers)
  data = response.json()
  output=[]
  url = "https://api.apilayer.com/bad_words?censor_character=BAD%20WORD"
  amt = len(data["data"])
  got = []
  for i in range(15):
    if len(output)!=8:
      s=random.randint(i,amt)
      got.append(s)
      text=data["data"][s]["showerthought"]
      payload = text.encode("utf-8")
      headers= {
        "apikey": "Uh6RRpN4F3MycMS0MQFLxaH1fEdfLEKi"#os.environ["apilayer"]
      }
      
      response = requests.request("POST", url, headers=headers, data = payload)
      if "unable to detect" in response.text.lower():
        output.append(text)
      elif "html" in response.text:
        pass
      else:
        result = json.loads(response.text)
  
        try:
          if result["bad_words_total"]==0 and "blood" not in text.lower() and "bribery" not in text.lower():
            output.append(text)
        except Exception as e:
          raise e
          
  return output
def get_keyword(text):

  return kw_model.extract_keywords(text)[0][0]


def get_unsplash(query,fp):
  query_params = {"client_id": unsplash_access_key, "query": query}
  response = requests.get(query_url, params=query_params)
  results = response.json()["results"]
  
  # Download the first image from the search results
  if results:
    image_url = results[0]["urls"]["regular"]
    print(image_url)
    image_response = requests.get(image_url)
    print(image_response)
    try:
      with open(f"images/{fp}", "wb") as f:
        f.write(image_response.content)
    except:
      print(f"Couldn't save for {query}")
    url = results[0]["id"]
    if image_response.content!=None:
      return url
    else:
      print(f"Couldn't find image for {query}")
      return False


from quart import Quart, send_file,redirect,url_for

app=Quart(__name__)
@app.route("/download")
async def download():
  return await send_file("output.mp4", as_attachment=True)
@app.route("/")
async def home():
  with open("data.json") as f:
    data = json.load(f)
    words=data["desc"]
  return f"""<h1><a href="/download">Hello</a></h1>
  <br>
  <hr>
  <p>
  {words}
  <p>
  
  """
@app.route("/make")
async def make():
  print("Getting shower thoughts...")
  output =(get_showerthoughts())
  print("Got shower thoughts")
  
  keywords = []
  for i in range(len(output)-1):
    key = get_keyword(output[i])
    print(key + str(i))
    keywords.append(key)
  print("Got keywords")
  
  remove_images()
  print("Deleted images")
  time.sleep(1)
  desc = "Join the Discord - discord.gg/KsjxVYrvYS\nImages linked to when they're shown in the video\n"
  toPop =[]
  count = -1
  for i in range(len(output)-1):
    count+=1
    try:
      res = get_unsplash(keywords[count],f"{count}.png")
  
      if res !=False:
        desc = f"{desc}unsplash.com/photos/{res}\n"
      else:
        toPop.append(count)
        count+=1
        output.pop(count)
        keywords.pop(count)
        #pops out of i
    except Exception as e:
      print(e)
  data={}
  data["text"]=str(output)
  data["keywords"]=str(keywords)
  data["desc"]=str(desc)
  with open("data.json","w") as f:
    json.dump(data,f,indent=4) 
  for i in range(len(output)-1):
    response = get_tts(output[i])
    with open(f'audio/{i}.mp3', 'wb') as f:
      f.write(response.content)
  create_clip(output)
  return await redirect(url_for("/download"))

app.run(host="0.0.0.0",port=5323)
