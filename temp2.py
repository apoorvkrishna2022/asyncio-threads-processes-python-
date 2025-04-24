import asyncio

async def fetch_data(delay):
    print(f"waiting {delay} seconds")
    await asyncio.sleep(delay)
    print(f"waited {delay} seconds")
    return {"data": "some data"}


async def main():
   print("start of main coroutine")
   result = await fetch_data(2)
   print(f"Received result: {result}")
   print("end of main coroutine")

if __name__ == "__main__":
    print("start of program")
    asyncio.run(main())
    print("end of program")



    
    