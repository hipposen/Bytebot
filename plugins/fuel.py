from irc3.plugins.command import command

from bytebot_config import BYTEBOT_PLUGIN_CONFIG
from irc3 import asyncio
import json
import aiohttp

@command(permission="view")
@asyncio.coroutine
def fuel(bot, mask, target, args):
    """Show the current fuel price for fuelsort

        %%fuel [<fuelsort>]...
    """
    config = BYTEBOT_PLUGIN_CONFIG['fuel']
    if config['apikey'] == "your_apikey":
        return "I don't have your api key!"

    if '<fuelsort>' not in args or len(args['<fuelsort>']) < 1:
        fuelsort = "all"
    else:
        fuelsort = " ".join(args['<fuelsort>'])

    bot.log.info('Fetching fuel info for %s' % fuelsort)  

    url = "https://creativecommons.tankerkoenig.de/json/list.php?" + \
            "lat=50.9827792" + \
            "&lng=11.0394426" + \
            "&rad=1" + \
            "&sort=dist" + \
            "&type=" + fuelsort + "&apikey=" + \
            str(config['apikey'])
            
    with aiohttp.Timeout(10):
        with aiohttp.ClientSession(loop=bot.loop) as session:
            resp = yield from session.get(url)
            if resp.status != 200:
                bot.privmsg(target, "Error while retrieving fuel data")
                raise Exception()
            r = yield from resp.read()

    try:
        j = json.loads(r.decode('utf-8'))
        data= j    
        headline = u"{:23}".format('fuel prices:') + \
                u"{:6} ".format('e5') + \
                u"{:6} ".format('e10') + \
                u"{:6} ".format('diesel')
                
        messages = [] 
        messages.append(headline)
       
        for x in range(len(data['stations'])):
            brand = data[u'stations'][x][u"brand"]
            station_id = data['stations'][x][u"id"]
            postCode = data['stations'][x][u"postCode"]
            e5 = data['stations'][x][u"e5"]
            e10 = data['stations'][x][u"e10"]
            diesel = data['stations'][x][u"diesel"]

            if brand == '':
              brand = 'GLOBUS'
            print_str = \
                    u"   {:20}".format(brand + ', ' + str(postCode) + ': ') + \
                    u"{:5}  ".format(e5) + \
                    u"{:5}  ".format(e10) + \
                    u"{:5}  ".format(diesel)
                    
            messages.append(print_str)
            
    except KeyError:
        bot.privmsg(target, "Error while retrieving fuel data")
        raise Exception()
    return  messages
