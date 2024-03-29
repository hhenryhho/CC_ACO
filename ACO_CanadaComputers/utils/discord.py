from discord_webhook import DiscordWebhook, DiscordEmbed
from pytz import timezone
from datetime import datetime

import pytz


class Discord:
    def __init__(self):
        self.canadacomputers = DiscordWebhook(
            url="https://discord.com/api/webhooks/818491496264761376/QNO-4s1fO1xwU1b9SMOkd5jXw9iAwCTpgVyrVOJ5Yxpr7blBHIe6D2l-xgeLb_u2-kbV"
        )
        self.processors = DiscordWebhook(
            url="https://discord.com/api/webhooks/818889318306152469/xDkUSGRWkhSgYNGe9Ith3JyLM_UR8D8ALP9PzCQz3uJvbKNBn2KfajscesZcSRWGUgaR"
        )
        self.othercards = DiscordWebhook(
            url="https://discord.com/api/webhooks/818491771251458088/ku3oa1T19XEj3mxl4LJCxJkGs0QF_jZC9DxxvWUolcKoMgOh5WdcgyqvxewT924hDGwF"
        )
        print("Started Discord Connection")

    def post(self, item):
        embed = DiscordEmbed(
            title=item["name"],
            url="https://www.canadacomputers.com/product_info.php?cPath=4_64&item_id={}".format(
                item["item_id"]
            ),
            color="03b2f8",
        )
        embed.set_thumbnail(url=item["img"])
        embed.add_embed_field(
            name="Step 1",
            value="**[Add To Cart](https://www.canadacomputers.com/index.php?action=buy_now&item_id={})**".format(
                item["item_id"]
            ),
            inline=True,
        )
        embed.add_embed_field(
            name="Step 2",
            value="**[Checkout Link](https://www.canadacomputers.com/checkout_method.php)**",
            inline=False,
        )
        for stock in item["stock"]:
            location = list(stock.keys())[0]
            quantity = list(stock.values())[0]
            if quantity != 0:
                embed.add_embed_field(name=location, value=quantity, inline=True)
        if len(embed.get_embed_fields()) == 2:
            embed.add_embed_field(name="Out of stock", value=0, inline=True)
        tz = pytz.timezone("US/Eastern")
        embed.set_footer(
            text="Developed by Hen @ {}".format(
                datetime.now(tz).strftime("%m/%d/%Y %H:%M:%S")
            )
        )
        if "1660" in item["name"] or "6800" in item["name"]:
            self.othercards.add_embed(embed)
            response = self.othercards.execute()
        else:
            self.canadacomputers.add_embed(embed)
            response = self.canadacomputers.execute()


from ACO_CanadaComputers.items import CC_Product

if __name__ == "__main__":
    bot = Discord()
    item = CC_Product()

    item["name"] = "EVGA GeForce RTX 3070 FTW3 ULTRA GAMING 8GB GDDR6 1815 MHz Boost "
    item[
        "img"
    ] = "https://ccimg.canadacomputers.com/Products/505x505/230/522/183498/20944.jpg"
    item["item_id"] = 183498
    item["stock"] = []
    bot.post(item)