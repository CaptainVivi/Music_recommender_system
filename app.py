from os import name
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import OneHotEncoder
from scipy.spatial import distance
from flask import Flask, request, render_template

app = Flask(__name__)


data = pd.read_csv("SpotifyFeatures.csv")
data.head()
data.info()

data = data.drop(["track_id","key","mode","time_signature"],1)
df = data.copy()
df = df.drop(["artist_name","track_name"],1)

col = ['popularity', 'acousticness', 'danceability', 'duration_ms',
       'energy', 'instrumentalness', 'liveness', 'loudness', 'speechiness',
       'tempo', 'valence']
scaler = StandardScaler()
df[col] = scaler.fit_transform(df[col])

encoder = OneHotEncoder(sparse=False, handle_unknown="ignore")
enc = pd.DataFrame(encoder.fit_transform(np.array(df["genre"]).reshape(-1,1)))
enc.columns = df["genre"].unique()

enc.head()

df[enc.columns] = enc
df = df.drop("genre",1)
df.head()

df["name"] = data["track_name"]
df["artist"] = data["artist_name"]

df_2 = df.drop(["artist","name"],1)

@app.route("/", methods=["GET"])
def index():
    return render_template("recsyst.html")


def find_song(word,artist):
    a = 0
    b = 0
    if word is not None and artist is not None:
        for i in data["track_name"]:
            if word.lower() in i.lower() and artist.lower() in data["artist_name"][a].lower():
                print("Song Name: ",data["track_name"][a],", Artists: ",data["artist_name"][a])
                b+=1
            a+=1
    if b == 0:
        print("Nothing found. Please try something else :)")


def sim_track_find(word,artist):
    a = 0
    b = 0
    song = []
    indexes = []
    if word is not None and artist is not None:
        for i in data["track_name"]:
            if word.lower() in i.lower() and artist.lower() in data["artist_name"][a].lower():
                song.append(df_2[a:a+1].values)
                indexes.append(a)
                b+=1
            a+=1
    if b == 0:
        print("Nothing found. Please try something else :)")
        return 0
        
    return song[0][0], indexes[0]



@app.route("/similar_tracks", methods=["POST"])
def recommendation():
    song = request.form.get("song")
    artist = request.form.get("artist")
    num=5
    similar_songs = similar_tracks(df, int(num), song, artist)
    print(similar_songs)
    return render_template("recsyst.html", song=song, artist=artist, similar_songs=similar_songs)


def similar_tracks(data,number,song="",artist=""):
    
    
    if (sim_track_find(song,artist) == 0):
        # return 0
        return "Nothing found. Please try something else :)"
    else:
        x=sim_track_find(song,artist)[0]
        index = sim_track_find(song,artist)[1]
    p = []
    count=0
    for i in df_2.values:
        p.append([distance.cosine(x,i),count])
        count+=1
    p.sort()
    song_names = df["name"]
    artist_names = df["artist"]
    similar_songs = []

    print("\nSimilar songs to ",song_names[index]," by ", artist_names[index],"\n")
    for i in range(1,number+1):
        print(i,"- ",song_names[p[i][1]],", ",artist_names[p[i][1]])
        similar_songs.append([song_names[p[i][1]], artist_names[p[i][1]]])
    return similar_songs



if __name__ == '__main__':
    app.run(debug=True)
