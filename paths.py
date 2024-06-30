spans_path = ('xpath', "//div[starts-with(@class, 'chat-message-message-')]//span")
unread_chat_path = ('xpath', './/ancestor::a')
icon_chats_path = ('xpath', '//a[@href="/profile/messenger" and @data-marker="header/messenger"]')
any_chat_path = ('xpath', "//div[starts-with(@class, 'chat-message-message-')]//span")
username_path = ('xpath', '//a[starts-with(@class, "header-view-name-")]')
unread_messages_path = ('xpath', """//div[starts-with(@class,
            'new-messages-delimiter-root-')]/following-sibling::
            div[starts-with(@class, 'message-base-root-')]//span[@data-marker='messageText']""")