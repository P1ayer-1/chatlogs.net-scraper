# -*- coding: utf-8 -*-

import scrapy
from ..items import ConversationItem
from scrapy.loader import ItemLoader
from scrapy.spidermiddlewares.httperror import HttpError


def clean_post_content(value):
    return value.strip().replace('\n', ' ')

class ChatSpider(scrapy.Spider):
    name = 'chat'
    allowed_domains = ['chatlogs.net']

    def start_requests(self):
        yield scrapy.Request(url='https://chatlogs.net', callback=self.get_most_recent_post)

    def get_most_recent_post(self, response):
        most_recent_post_url = response.css('.col-md-8.mb-3.mb-sm-0 a[href*=posts]').attrib['href']
        most_recent_post_number = int(most_recent_post_url.split('/')[-1])

        for post_number in range(1, most_recent_post_number + 1):
            url = f'https://chatlogs.net/posts/{post_number}'
            yield scrapy.Request(url, callback=self.parse_next, errback=self.handle_error)

    def parse_next(self, response):
        post_number = int(response.url.split('/')[-1])
        conversation = []
        system_message = None
        
        for chat in response.css('.chat-body.clearfix'):
            user = chat.css('.primary-font::text').extract_first()
            message = chat.css('p::text, p code::text').getall()
            message_type = chat.css('p b::text').extract_first()
            message_cleaned = clean_post_content(' '.join(message).strip())


            # check if chatgpt sent a blank message
            if user.strip() == 'Chat GPT' and message_cleaned == '':
                continue
            
            
            if message_type == "System":
                system_message = message_cleaned
                continue


            message_item = {
                'user': user,
                'message': message_cleaned
            }

            conversation.append(message_item)
        # return if conversation is None
        if conversation is None:
            return 
        conversation_loader = ItemLoader(item=ConversationItem())
        conversation_loader.add_value('post_number', post_number)

        conversation_loader.add_value('system_message', system_message if system_message is not None else "")
        conversation_loader.add_value('conversation', conversation)
        yield conversation_loader.load_item()


    def handle_error(self, failure):
        if failure.check(HttpError):
            response = failure.value.response
            if response.status == 404:
                self.logger.warning(f'Skipped page: {response.url}')
            else:
                self.logger.error(f'HttpError occurred on {response.url}')
