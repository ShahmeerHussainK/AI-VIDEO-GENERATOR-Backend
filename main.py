from pathlib import Path
import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File, Query
import requests
from dotenv import load_dotenv
import os
from uuid import uuid4
from fastapi.responses import FileResponse

app = FastAPI()
load_dotenv()

client = ""
api_key = os.environ.get("OPENAI_API_KEY")
PIXABAY_API_KEY = os.environ.get("PIXABAY_API_KEY")

if api_key is not None:
    from openai import OpenAI

    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

API_KEY = os.getenv("PEXEL")


@app.get("/search/images")
async def search_images(query: str):
    headers = {"Authorization": f"{API_KEY}"}

    # Make a request to the Pexels API
    response = requests.get(
        f"https://api.pexels.com/v1/search?query={query}", headers=headers
    )

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code, detail="Pexels API request failed"
        )
    response = response.json()
    image_url = response["photos"][0]["url"]

    return image_url


async def translate_text(text, language):
    prompt = f"Translate the following English text into {language}: {text}"
    story_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": prompt}],
        max_tokens=150,
    )
    translated_text = story_response.choices[0].message.content
    return translated_text


@app.get("/title")
async def title(text):
    # Define the parameters for the translation request

    prompt = f"Generate a title for following story {text}"
    story_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": prompt}],
        max_tokens=150,
    )
    prompt_title = story_response.choices[0].message.content
    return prompt_title


def search_videos(queries):
    headers = {"Authorization": f"{API_KEY}"}
    urls = []
    # Make a request to the Pexels API
    for query in queries:
        try:
            response = requests.get(
                f"https://api.pexels.com/videos/search?query={query}&per_page=1",
                headers=headers,
            )
        except Exception as e:
            return {"error": e}

        if response.status_code != 200:
            continue
        response = response.json()
        link = response["videos"][0]["video_files"][0]["link"]
        urls.append(link)
    return urls


@app.get("/convert_text_to_speech/")
async def convert_text_to_speech(text: str, voice: str = "onyx", language=""):
    if language != "":
        text = await translate_text(text, language)
    try:
        response = client.audio.speech.create(model="tts-1", voice=voice, input=text)
        unique_filename = f"speech_{uuid4()}.mp3"
        speech_file_path = Path(__file__).parent / unique_filename
        response.stream_to_file(speech_file_path)
        return FileResponse(unique_filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/transcribe_audio/")
async def transcribe_audio(audio_file: UploadFile = File(...)):
    try:
        with audio_file.file as file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1", file=file
            )
        return {"transcription": transcription.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def generate_story(prompt: str = "You're tasked with writing a story script "):
    try:
        prompt = f" generate a story on topic {prompt}"
        story_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": prompt}],
            max_tokens=150,
        )
        story = story_response.choices[0].message.content.replace("\n", " ")
        story = story.replace("\\", "")

        keyword_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You will be provided with a block of text, and your task is to extract keywords "
                               "separated by commas ",
                },
                {"role": "user", "content": story},
            ],
            temperature=0.5,
            max_tokens=64,
            top_p=1,
        )
        queries = keyword_response.choices[0].message.content.split(",")
        headers = {"Authorization": f"{API_KEY}"}
        urls = []
        # Make a request to the Pexels API
        print(queries)
        print("________________________________________________________________________________--")
        # queries = queries[0].split('-')
        print(queries)
        for query in queries:
            print(query)
            pixabay_url = await get_videos(query)
            if pixabay_url["videos"] != []:
                urls.append(pixabay_url["videos"][0])
            else:
                try:
                    response = requests.get(
                        f"https://api.pexels.com/videos/search?query={query}&per_page=1&orientation=landscape&size=small",
                        headers=headers,
                    )
                except Exception as e:
                    return {"error": e}

                if response.status_code != 200:
                    continue
                response = response.json()
                if response["videos"] != []:
                    for video in response["videos"][0]["video_files"]:
                        if video["height"] == 720 and video["width"] == 1280:
                            urls.append(video["link"])
                            break
        return {"urls": urls, "story": story, "keywords": queries}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/regenerate_script")
async def regenerate_script(user_script: str, prompt_type: str):
    # Analyze user_script and determine which prompt to use
    # Based on prompt_type, select the appropriate prompt and generate script
    if prompt_type == "Shorter":
        prompt = "Make the script shorter:\n" + user_script
    elif prompt_type == "Longer":
        prompt = "Make the script longer:\n" + user_script
    elif prompt_type == "Casual":
        prompt = "Make the script sound casual:\n" + user_script
    elif prompt_type == "Professional":
        prompt = "Make the script sound professional:\n" + user_script
    else:
        return {"error": "Invalid prompt type"}

    # Use await to call the asynchronous function
    regenerated_script = await generate_story(prompt)
    return regenerated_script


@app.post("/generate-story/")
async def story_generation(prompt: str):
    return {"response ": await generate_story(prompt)}


async def get_videos(query: str = Query(...)):
    """
    Retrieve videos from Pixabay.
    """

    pixabay_url = (
        f"https://pixabay.com/api/videos/?key={PIXABAY_API_KEY}&q={query}"
    )

    try:
        response = requests.get(pixabay_url)
        response.raise_for_status()
        data = response.json()
        video_urls = [item["videos"]["medium"]["url"] for item in data["hits"]]
        return {"videos": video_urls}
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch videos: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
