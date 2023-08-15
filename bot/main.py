import telebot
from telebot import types

from .models import CartProduct, Category, Channel, Client, Order, \
                    OrderProduct, Product, Question, Subcategory
from django.db.models import Sum
from django.conf import settings
import pandas as pd


bot = telebot.TeleBot(settings.TG_TOKEN)

def register_by_message(message) -> bool:
    '''
    Проверяет наличие пользователя в БД и вносит его, если тот отсутствует.
    Возвращает результат проверки.
    '''
    if Client.objects.filter(id=message.chat.id):
        return True
    else:
        full_name = message.chat.first_name
        if message.chat.last_name:
            full_name += ' '+message.chat.last_name
        Client.objects.create(id=message.chat.id, full_name=full_name)
        return False 
    
def mark_order_as_paid(order_id):
    '''Отмечает заказ как оплаченный'''
    order = Order.objects.get(id=order_id)
    order.pay_status = Order.Status.YES
    order.save()

def clear_cart(user_id):
    '''Очищает корзину пользователя'''
    CartProduct.objects.filter(client_id=user_id).delete()

def save_order(order_id, filename='orders.xlsx'):
    '''Дополняет эксель записью о заказе'''
    order = Order.objects.get(id=order_id)
    try:
        existing_data = pd.read_excel(filename)
    except FileNotFoundError:
        existing_data = pd.DataFrame()

    data = {
        'ID клиента': [],
        'Адрес': [],
        'Товар': [],
        'Количество': [],
        'Общая стоимость': []
    }

    for order_product in order.orderproduct_set.all():
        data['ID клиента'].append(order.client.id)
        data['Адрес'].append(order.client.address)
        data['Товар'].append(order_product.product.name)
        data['Количество'].append(order_product.quantity)
        data['Общая стоимость'].append(order_product.total)

    df = pd.DataFrame(data)
    df = pd.concat([existing_data, df], ignore_index=True)
    df.to_excel(filename, index=False)


def mailing(text, users):
    '''Рассылает указанного текста выбранным клиентам'''
    for u in users:
        try:
            bot.send_message(u.id, text, parse_mode='html')
        except Exception as e:
            print(e)


def check_sub(user_id):
    '''Проверяет подписки на каналы'''
    markup = types.InlineKeyboardMarkup()
    channels = Channel.objects.all()
    for c in channels:
        if bot.get_chat_member(chat_id=c.id,
                               user_id=user_id).status == 'left':
            b = types.InlineKeyboardButton(text=c.name, url=c.url)
            markup.add(b)

    if len(markup.to_dict()['inline_keyboard']):
        markup.add(types.InlineKeyboardButton(
            '🔄 Проверить подписку',
            callback_data='check'
        ))

        bot.send_message(user_id,
                         'Сначала подпишись на наши каналы',
                         reply_markup=markup)
        return False
    else:
        return True


def send_main_menu(user_id):
    '''Отправляет клавиатуру с главным меню'''
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Каталог')
    btn2 = types.KeyboardButton('Моя корзина')
    markup.add(btn1, btn2)
    bot.send_message(user_id, text='Открыто главное меню', reply_markup=markup)


def show_cats(user_id, count, page):
    '''
    Получает категории по количеству и индексу страницы (для пагинации).
    Результат отправляет пользователю.
    '''
    cats = Category.objects.all()
    total_count = cats.count()
    if total_count == 0:
        return None
    cats = cats[count*page:count*(page+1)]
    markup = types.InlineKeyboardMarkup()

    for c in cats:
        markup.add(types.InlineKeyboardButton(
            c.name, callback_data=f'subcats_{c.id}_{count}_0'))

    btns_page = []
    if page > 0:
        btns_page.append(types.InlineKeyboardButton(
                '<< пред. стр.',
                callback_data=f'cats_{count}_{page-1}'
        ))
    if total_count > count:
        btns_page.append(types.InlineKeyboardButton(
                f'{page+1}/{(total_count + count - 1) // count}',
                callback_data=f'cats_{count}_{page}'
        ))

    if count*(page+1) < total_count:
        btns_page.append(types.InlineKeyboardButton(
            'след. стр. >>',  callback_data=f'cats_{count}_{page+1}'))

    markup.row(*btns_page)
    bot.send_message(user_id, 'Выберите категорию', reply_markup=markup)


def show_subcats(user_id, cat_id, count, page):
    '''
    Получает подкатегории по количеству и индексу страницы (для пагинации).
    Результат отправляет пользователю.
    '''
    subcats = Subcategory.objects.filter(category__id=cat_id)
    total_count = subcats.count()

    subcats = subcats[count*page:count*(page+1)]
    markup = types.InlineKeyboardMarkup()

    for s in subcats:
        markup.add(types.InlineKeyboardButton(
            s.name, callback_data=f'products_{s.id}_3_0'))

    btns_page = []
    if page > 0:
        btns_page.append(types.InlineKeyboardButton(
                '<< пред. стр.',
                callback_data=f'subcats_{cat_id}_{count}_{page-1}'
        ))
    if total_count > count:
        btns_page.append(types.InlineKeyboardButton(
                            f'{page+1}/{(total_count + count - 1) // count}',
                            callback_data=f'subcats_{cat_id}_{count}_{page}'
        ))

    if count*(page+1) < total_count:
        btns_page.append(types.InlineKeyboardButton(
                'след. стр. >>',
                callback_data=f'subcats_{cat_id}_{count}_{page+1}'
        ))

    markup.row(*btns_page)
    markup.add(types.InlineKeyboardButton(
                'Вернуться к категориям',
                callback_data=f'cats_{count}_0'
    ))

    bot.send_message(user_id, 'Выберите подкатегорию', reply_markup=markup)


def show_products(user_id, subcat_id, count, page):
    '''
    Получает товары по количеству и индексу страницы (для пагинации).
    Результат отправляет пользователю.
    '''
    products = Product.objects.filter(subcategory__id=subcat_id)
    total_count = products.count()
    if total_count == 0:
        show_cats(user_id, 4, 0)
        return

    products = products[count*page:count*(page+1)]

    rms = []

    for p in products:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(
            'Добавить в корзину', callback_data=f'cart_add_{p.id}'))
        rms.append(markup)

    markup = rms[-1]
    btns_page = []
    if page > 0:
        btns_page.append(types.InlineKeyboardButton(
                '<< пред. стр.',
                callback_data=f'products_{subcat_id}_{count}_{page-1}'
        ))
    if total_count > count:
        btns_page.append(
            types.InlineKeyboardButton(
                f'{page+1}/{(total_count + count - 1) // count}',
                callback_data=f'products_{subcat_id}_{count}_{page}'
            )
        )

    if count*(page+1) < total_count:
        btns_page.append(types.InlineKeyboardButton(
                    'след. стр. >>',
                    callback_data=f'products_{subcat_id}_{count}_{page+1}'
                ))

    markup.row(*btns_page)
    markup.add(
        types.InlineKeyboardButton(
            'Вернуться к подкатегориям',
            callback_data=f'subcats_{products[0].subcategory.category.id}_4_0'
        )
    )

    for i, p in enumerate(products):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(
                    'Добавить в корзину',
                    callback_data=f'cart_add_{p.id}'
        ))
        bot.send_photo(
            chat_id=user_id,
            photo=p.image,
            caption=f'<b>{p.name} - {p.price:.2f} руб.</b>' \
                    f'\n\n{p.description}',
            parse_mode='HTML',
            reply_markup=rms[i]
        )


def ask_quantity(user_id, product_id):
    '''Отправляет сообщение с запросом количества выбранного товара'''
    product = Product.objects.filter(id=product_id).first()

    markup = types.InlineKeyboardMarkup()

    r1 = []
    r2 = []
    for i in range(1, 6):
        r1.append(types.InlineKeyboardButton(
                    f'{i}',
                    callback_data=f'cart_add_q_{product_id}_{i}'
        ))

    for i in range(6, 11):
        r2.append(types.InlineKeyboardButton(
                    f'{i}',
                    callback_data=f'cart_add_q_{product_id}_{i}'
        ))

    markup.row(*r1)
    markup.row(*r2)

    bot.send_photo(
        chat_id=user_id,
        photo=product.image,
        caption=f'<b>{product.name} - {product.price:.2f} руб.</b>' \
                f'\n{product.description}' \
                f'\n\n<b>Укажите количество товара для покупки</b>',
        parse_mode='HTML',
        reply_markup=markup
        )


def ask_confirm(user_id, product_id, quantity):
    '''Отравляет запрос о подтверждении добавления в корзину'''
    product = Product.objects.filter(id=product_id).first()

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Да, добавить в корзину',
               callback_data=f'cart_confirm_add_{product_id}_{quantity}'))
    markup.add(types.InlineKeyboardButton(
        'Отменить', callback_data='cats_4_0'))

    bot.send_photo(
        chat_id=user_id,
        photo=product.image,
        caption=f'<b>{product.name} - {product.price:.2f} руб.\n</b>' \
                f'{product.description}\n\n'\
                f'<b>Количество: {quantity}\n'\
                f'Общая стоимость: ' \
                f'{quantity*product.price:.2f} руб</b>' \
                f'\n<b>Подтвердите добавление товара в корзину</b>', \
        parse_mode='HTML', reply_markup=markup)


def cart_add(user_id, product_id, quantity):
    '''Добавляет в корзину'''
    p = Product.objects.get(id=product_id)
    cartp = CartProduct.objects.filter(
        client_id=user_id, product_id=product_id).first()
    if cartp:
        cartp.quantity = quantity
        cartp.total = quantity * p.price
        cartp.save()
        bot.send_message(user_id, 'Количество товара в корзине изменено')
    else:
        CartProduct.objects.create(
            client_id=user_id,
            product_id=product_id,
            quantity=quantity,
            total=quantity*p.price
        )
        bot.send_message(user_id, 'Товар добавлен в корзину')


def cart_show(user_id, count, page):
    '''
    Выводит пользователю корзину.
    count и page, аналогично выводу категорий, для пагинации кнопок удаления
    '''
    all_cproducts = CartProduct.objects.filter(client_id=user_id)
    if not all_cproducts:
        bot.send_message(user_id, 'Корзина пуста')
        return
    total_count = all_cproducts.count()
    cproducts = all_cproducts[count*page:count*(page+1)]

    rms = []
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('💳 Оплатить',
                                          callback_data='cart_buy'))

    for p in cproducts:
        markup.add(types.InlineKeyboardButton(
            f'❌ {p.product.name}',
            callback_data=f'cart_del_{p.product.id}'
        ))
        rms.append(markup)

    btns_page = []
    if page > 0:
        btns_page.append(types.InlineKeyboardButton(
            '<< пред. стр.', callback_data=f'cart_show_{count}_{page-1}'))
    if total_count > count:
        btns_page.append(types.InlineKeyboardButton(
            f'{page+1}/{(total_count + count - 1) // count}',
            callback_data=f'cart_show_{count}_{page}')
        )

    if count*(page+1) < total_count:
        btns_page.append(types.InlineKeyboardButton(
            'след. стр. >>',  callback_data=f'cart_show_{count}_{page+1}'))

    markup.row(*btns_page)

    text = ''
    for p in all_cproducts:
        text += f'{p.product.name} ({p.quantity} шт.) - {p.total:.2f} руб.\n'

    total_sum = all_cproducts.aggregate(Sum('total'))['total__sum']
    text += f'\n<B>Общая сумма: {total_sum:.2f} руб.</B>'

    bot.send_message(user_id, text, parse_mode='HTML', reply_markup=markup)


def cart_del(user_id, product_id):
    '''Удаляет товар из корзины'''
    CartProduct.objects.filter(
        client_id=user_id, product_id=product_id).delete()


def handle_address(message):
    '''Отправляет запрос о подтверждении адреса'''
    markup = types.InlineKeyboardMarkup()

    markup.add(types.InlineKeyboardButton(
        'Верно', callback_data=f'confirm_address_{message.text}'))
    markup.add(types.InlineKeyboardButton(
        'Нет, изменить', callback_data='cart_buy'))

    markup.add(types.InlineKeyboardButton('Вернуться назад',
                                          callback_data='cart_show_5_0'))
    bot.send_message(
        message.chat.id,
        f'Ваш адрес: {message.text}\n\nВсе верно?',
        reply_markup=markup
    )


def save_address(user_id, address):
    '''Сохраняет адрес'''
    user = Client.objects.get(id=user_id)
    user.address = address
    user.save()


def send_invoice(user_id):
    '''Отправляет  счет'''
    all_cproducts = CartProduct.objects.filter(client_id=user_id)
    if not all_cproducts:
        bot.send_message(user_id, 'Корзина пуста')
        return

    text = ''
    order = Order.objects.create(
        client_id=user_id,
        address=Client.objects.get(id=user_id).address
    )
    for p in all_cproducts:
        OrderProduct.objects.create(
            order=order,
            product=p.product,
            quantity=p.quantity,
            total=p.total
        )

        text += f'{p.product.name} ({p.quantity} шт.) - {p.total:.2f} руб.\n'

    total_sum = all_cproducts.aggregate(Sum('total'))['total__sum']

    order.total_amount = total_sum
    order.save()

    text += f'\nОбщая сумма: {total_sum:.2f} руб.'

    bot.send_invoice(
        user_id,
        title='Оплата',
        description=text,
        provider_token=settings.YK_TOKEN,
        currency='rub',
        is_flexible=False,
        prices=[types.LabeledPrice(
            label='Общая сумма',
            amount=int(total_sum * 100)
        )],
        invoice_payload=str(order.id),
        start_parameter='example'
    )


def get_faq(query):
    '''Получет вопросы по их началу и формирует список для inline ответа'''
    qs = Question.objects.filter(q__istartswith=query)
    result = []
    for i, q in enumerate(qs):
        result.append(
            telebot.types.InlineQueryResultArticle(
                id=i,
                title=q.q,
                description=q.a,
                input_message_content=telebot.types.InputTextMessageContent(
                    f'<b>Вопрос:</b> {q.q}\n<b>Ответ:</b>{q.a}',
                    parse_mode='HTML'
                )
            )
        )
    return result
