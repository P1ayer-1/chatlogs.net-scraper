# -*- coding: utf-8 -*-

from scrapy import Item, Field
from itemloaders.processors import Compose, Join, MapCompose


def clean_post_content(value):
    return value.strip().replace('\n', ' ')


class ChatlogsItem(Item):
    user = Field()
    system_message = Field()
    message = Field(
        input_processor=MapCompose(str.strip),
        output_processor=Compose(Join(), clean_post_content)
    )


class ConversationItem(Item):
    post_number = Field()
    system_message = Field()
    conversation = Field()
