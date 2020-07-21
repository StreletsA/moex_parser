import Neuro
import MoexParser
import asyncio
import time
import datetime

async def main():

    mp = MoexParser.MoexParser()
    await mp.save_all_stocks_hystoryinfo()
    await mp.close()

if __name__ == '__main__':

    #loop = asyncio.get_event_loop()
    #loop.run_until_complete(main())

    #print(Neuro.get_prediction('AFLT'))

    d = datetime.datetime.now()
    print(d.weekday())