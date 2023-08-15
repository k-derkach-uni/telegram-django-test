from bot.main import ask_confirm, ask_quantity, cart_add, \
                     cart_del, cart_show, check_sub, clear_cart, \
                     get_faq, handle_address, mark_order_as_paid, register_by_message, save_address, save_order, send_invoice, \
                     send_main_menu, show_cats, show_products, show_subcats  

from bot.main import bot 


@bot.inline_handler(lambda query: True)
def query_text(inline_query):
    '''Отвечает на inline запросы'''
    bot.answer_inline_query(
            inline_query.id,
            get_faq(inline_query.query)
        )


@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    '''Изменяет статус оплаты, очищает корзину'''
    order_id = int(message.successful_payment.invoice_payload)
    user_id = message.from_user.id
    
    mark_order_as_paid(order_id)
    save_order(order_id)
    clear_cart(user_id)
    
    user_id = message.from_user.id
    
    bot.send_message(message.chat.id, 'Спасибо за покупку')


@bot.pre_checkout_query_handler(func=lambda call: True)
def checkout(pre_checkout_query):
    '''Проверка перед оплатой. Здесь просто отвечает.'''
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    '''Обработка первого сообщения'''
    if register_by_message(message):
        bot.reply_to(message, 'Снова здравствуйте!')
    else:
        bot.reply_to(message, 'Здравствуйте!')

    if check_sub(message.chat.id):
        send_main_menu(message.chat.id)


@bot.message_handler(content_types=['text'])
def handle_text(message):
    '''Обработка текстовых сообщений'''
    if 'каталог' in message.text.lower():
        show_cats(message.chat.id, 4, 0)
    if 'корзина' in message.text.lower():
        cart_show(message.chat.id, 5, 0)


@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    '''Обработка всех callback'''

    # Кнопка подтверждения
    if callback.data == 'check':
        check_sub(callback.message.chat.id)
        bot.delete_message(message_id=callback.message.id,
                           chat_id=callback.message.chat.id)
        bot.send_message(callback.message.chat.id,
                         'Спасибо за подписку! Можете пользоваться ботом')

        send_main_menu(callback.message.chat.id)

    # Пагинация категорий
    elif callback.data.startswith('cats_'):
        count, page = callback.data.split('_')[1:]
        count, page = int(count), int(page)
        bot.delete_message(message_id=callback.message.id,
                           chat_id=callback.message.chat.id)

        show_cats(callback.message.chat.id, count, page)

    # Пагинация подкатегорий
    elif callback.data.startswith('subcats_'):
        cat_id, count, page = callback.data.split('_')[1:]
        cat_id, count, page = int(cat_id), int(count), int(page)
        bot.delete_message(message_id=callback.message.id,
                           chat_id=callback.message.chat.id)

        show_subcats(callback.message.chat.id, cat_id, count, page)

    # Пагинация товаров
    elif callback.data.startswith('products_'):
        subcat_id, count, page = callback.data.split('_')[1:]
        subcat_id, count, page = int(subcat_id), int(count), int(page)
        try:
            bot.delete_message(message_id=callback.message.id,
                               chat_id=callback.message.chat.id)
            bot.delete_message(message_id=callback.message.id-1,
                               chat_id=callback.message.chat.id)
            bot.delete_message(message_id=callback.message.id-2,
                               chat_id=callback.message.chat.id)
        except Exception as e:
            print(e)

        show_products(callback.message.chat.id, subcat_id, count, page)

    # Кнопка указания количества выбранного товара
    elif callback.data.startswith('cart_add_q_'):
        product_id, quantity = callback.data.split('_')[3:]
        product_id, quantity = int(product_id), int(quantity)

        try:
            bot.delete_message(message_id=callback.message.id,
                               chat_id=callback.message.chat.id)
            bot.delete_message(message_id=callback.message.id-1,
                               chat_id=callback.message.chat.id)
            bot.delete_message(message_id=callback.message.id-2,
                               chat_id=callback.message.chat.id)
        except Exception as e:
            print(e)

        ask_confirm(callback.message.chat.id, product_id, quantity)

    # Кнопка добавление товара
    elif callback.data.startswith('cart_add_'):
        product_id = int(callback.data.split('_')[-1])

        try:
            bot.delete_message(message_id=callback.message.id,
                               chat_id=callback.message.chat.id)
            bot.delete_message(message_id=callback.message.id-1,
                               chat_id=callback.message.chat.id)
            bot.delete_message(message_id=callback.message.id-2,
                               chat_id=callback.message.chat.id)
        except Exception as e:
            print(e)

        ask_quantity(callback.message.chat.id, product_id)

    # Кнопка подтверждения добавления
    elif callback.data.startswith('cart_confirm_add_'):
        product_id, quantity = callback.data.split('_')[3:]
        product_id, quantity = int(product_id), int(quantity)

        bot.delete_message(message_id=callback.message.id,
                           chat_id=callback.message.chat.id)

        cart_add(callback.message.chat.id, product_id, quantity)

    # Пагинация корзины (кнопки удаления товаров)
    elif callback.data.startswith('cart_show_'):
        count, page = callback.data.split('_')[2:]
        count, page = int(count), int(page)
        bot.delete_message(message_id=callback.message.id,
                           chat_id=callback.message.chat.id)

        cart_show(callback.message.chat.id, count, page)

    # Кнопка удаления товара
    elif callback.data.startswith('cart_del_'):
        product_id = int(callback.data.split('_')[-1])
        cart_del(callback.message.chat.id, product_id)
        bot.delete_message(message_id=callback.message.id,
                           chat_id=callback.message.chat.id)

        cart_show(callback.message.chat.id, 5, 0)

    # Кнопка "Оплатить" в корзине
    elif callback.data.startswith('cart_buy'):
        bot.delete_message(message_id=callback.message.id,
                           chat_id=callback.message.chat.id)
        bot.send_message(callback.message.chat.id,
                         'Введите свой домашний адрес')
        bot.register_next_step_handler(callback.message, handle_address)

    # Кнопка подтверждения адреса
    elif callback.data.startswith('confirm_address_'):
        address = callback.data.split('_')[-1]
        bot.delete_message(message_id=callback.message.id,
                           chat_id=callback.message.chat.id)

        save_address(callback.message.chat.id, address)
        send_invoice(callback.message.chat.id)