import asyncio
from app.config.settings import get_settings
from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    LiveTranscriptionEvents,
    LiveOptions,
    Microphone,
)
from app.voice_agent.agent import call_agent, text_to_speech
import warnings
from fastapi import FastAPI, Request
from sse_starlette.sse import EventSourceResponse
import json
import uvicorn
import os

# Setting the google api key to the environment
os.environ["GOOGLE_API_KEY"] = get_settings().GOOGLE_API_KEY

# Ignore all warnings
warnings.filterwarnings("ignore")


# To collect all the transcriptions parts to get the full sentence
class TranscriptCollector:
    def __init__(self):
        self.reset()

    def reset(self):
        self.transcript_parts = []

    def add_part(self, part):
        self.transcript_parts.append(part)

    def get_full_transcript(self):
        return " ".join(self.transcript_parts)


# Initalizing the transcription collector
transcript_collector = TranscriptCollector()


async def get_transcript(request: Request, session_id: int, user_id: int):
    try:
        message_queue: asyncio.Queue[str] = asyncio.Queue()
        config = DeepgramClientOptions(options={"keepalive": "true"})
        deepgram: DeepgramClient = DeepgramClient(
            api_key=get_settings().DEEPGRAM_API_KEY, config=config
        )

        dg_connection = deepgram.listen.asynclive.v("1")

        async def on_message(self, result, **kwargs):
            sentence = result.channel.alternatives[0].transcript

            if not result.speech_final:
                transcript_collector.add_part(sentence)
                await message_queue.put(("user", sentence))
            else:
                # This is the final part of the current sentence
                transcript_collector.add_part(sentence)
                full_sentence = transcript_collector.get_full_transcript()
                if len(full_sentence.strip()) > 0:
                    # Adding the speaker transcription to the message queue
                    await message_queue.put(("user", full_sentence))
                    async for event in call_agent(
                        query=full_sentence, session_id=session_id, user_id=user_id
                    ):
                        if event.get_function_calls():
                            tool_name = event.content.parts[0].function_call.name
                            args_passed = event.content.parts[0].function_call.args.get(
                                "query"
                            )

                            agent_response = f"Calling tool {tool_name} with query {args_passed} Please Hold On!"
                            # Adding the agent doing tool call in the message queue
                            await message_queue.put(("agent", agent_response))
                            # Converting the text to speech back to elevenlabs to intimate the user about the tool call
                            await asyncio.to_thread(text_to_speech, agent_response)
                        elif event.is_final_response():
                            agent_response = event.content.parts[0].text
                            # Adding the agent response to the message queue
                            await message_queue.put(("agent", agent_response))
                            # Converting the agent response back to audio using elevenlabs
                            await asyncio.to_thread(text_to_speech, agent_response)
                # Reset the collector for the next sentence
                transcript_collector.reset()

        async def on_error(self, error, **kwargs):
            # Adding the errors if there are any
            await message_queue.put(("error", str(error)))

        dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
        dg_connection.on(LiveTranscriptionEvents.Error, on_error)

        options = LiveOptions(
            model="nova-2",
            punctuate=True,
            language="en-US",
            encoding="linear16",
            channels=1,
            sample_rate=16000,
            endpointing=True,
        )

        await dg_connection.start(options)

        # Open a microphone stream on the default input device
        microphone = Microphone(dg_connection.send)

        # start microphone
        microphone.start()

        # Cleanup everything when closing
        async def cleanup():
            """Gracefully stop everything"""
            try:
                if microphone.is_active():
                    microphone.finish()
                # Send a closestream to deepgram and finish
                await dg_connection.send(json.dumps({"type": "CloseStream"}))
                dg_connection.finish()
            except Exception as e:
                print(f"Cleanup error: {e}")

        try:
            while True:
                if await request.is_disconnected():
                    await cleanup()
                    break
                try:
                    event_name, text = await asyncio.wait_for(
                        message_queue.get(), timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue
                payload = {"text": text}
                yield {"event": event_name, "data": json.dumps(payload)}

        finally:
            await cleanup()

    except Exception as e:
        print(f"Could not open socket: {e}")
        return


# Initalizing the fastapi client
app = FastAPI()


# Streaming api to stream the responses from the agent and user
@app.get("/stream")
async def stream_sse(request: Request, session_id: str, user_id: str):
    return EventSourceResponse(
        get_transcript(request, session_id=session_id, user_id=user_id)
    )


# Poetry run to start the voice agent
def start_voice_agent():
    uvicorn.run("app.main:app", host="0.0.0.0", port=8002)
