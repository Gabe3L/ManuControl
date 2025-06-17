import logging
import asyncio

from video_ai import Webcam

##############################################################################################

async def main() -> None:
    cam = Webcam()
    try:
        await cam.process_video()
    except KeyboardInterrupt:
        logging.info("Interrupted by user.")

##############################################################################################

if __name__ == '__main__':
    asyncio.run(main())