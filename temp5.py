import asyncio

async def fetch_data(delay):
    print(f"waiting {delay} seconds")
    await asyncio.sleep(delay)
    print(f"waited {delay} seconds")
    return f"fetched in {delay} seconds"


async def main():
    tasks = [fetch_data(1), fetch_data(2), fetch_data(3)]
    results = await asyncio.gather(*tasks)
    print(results)


if __name__ == "__main__":
    asyncio.run(main())



    
    