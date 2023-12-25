from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from database import *


def send_contact():
    return ReplyKeyboardMarkup([
        [KeyboardButton(text='Share contacts', request_contact=True)]
    ], resize_keyboard=True)


def generate_main_menu():
    return ReplyKeyboardMarkup([
        [KeyboardButton(text='✅ Make an order')],
        [KeyboardButton(text='🕔 History'), KeyboardButton(text='🛒 Cart'), KeyboardButton(text='⚙ Settings')]
    ], resize_keyboard=True)


def category_products():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.row(
        InlineKeyboardButton(text='All menu', url='https://telegra.ph/Welocme-09-09')

    )
    categories = get_all_categories()
    button = []
    for category in categories:
        btn = InlineKeyboardButton(text=category[1], callback_data=f'category_{category[0]}')
        button.append(btn)
    markup.add(*button)
    return markup


def products_by_category(category_id):
    markup = InlineKeyboardMarkup(row_width=2)
    products = get_products_by_category_id(category_id)
    button = []
    for product_id, product_name in products:
        btn = InlineKeyboardButton(text=product_name, callback_data=f'product_{product_id}')
        button.append(btn)
    markup.add(*button)
    markup.row(
        InlineKeyboardButton(text='◀ Back', callback_data='main_menu')
    )
    return markup


# def generate_count_product(product_id, category_id, cart_id, product_name, c):
#     markup = InlineKeyboardMarkup(row_width=3)
#
#     try:
#         quantity = get_quantity(cart_id, product_name)
#     except:
#         quantity = c
#
#     btn_minus = InlineKeyboardButton(text='➖', callback_data=f'minus_{quantity}_{product_id}')
#     btn_plus = InlineKeyboardButton(text='➕', callback_data=f'plus_{quantity}_{product_id}')
#     btn_quantity = InlineKeyboardButton(text=str(quantity), callback_data='count')
#     markup.add(btn_minus, btn_quantity, btn_plus)
#
#     markup.row(
#         InlineKeyboardButton('🛒 Add to cart', callback_data=f'cart_{product_id}_{quantity}')
#     )
#
#     markup.row(
#         InlineKeyboardButton(text='◀ Back', callback_data=f'back_{category_id}')
#     )

def generate_count_product(product_id, category_id, cart_id, product_name='', c=0):
    markup = InlineKeyboardMarkup(row_width=3)
    try:
        quantity = get_quantity(cart_id, product_name)  # Функция для получения количества продукта если он есть
    except:
        quantity = c

    btn_minus = InlineKeyboardButton(text='➖', callback_data=f'minus_{quantity}_{product_id}')
    btn_plus = InlineKeyboardButton(text='➕', callback_data=f'plus_{quantity}_{product_id}')
    btn_quantity = InlineKeyboardButton(text=str(quantity), callback_data='count')
    markup.add(btn_minus, btn_quantity, btn_plus)

    markup.row(
        InlineKeyboardButton(text='Добавить в корзину', callback_data=f'cart_{product_id}_{quantity}')
    )
    markup.row(
        InlineKeyboardButton(text='◀ Назад', callback_data=f'back_{category_id}')
    )

    return markup

def generate_cart_menu(cart_id):
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton(text='Order', callback_data=f'order_{cart_id}')
    )

    cart_products = get_cart_product_for_delete(cart_id)

    for cart_product_id, product_name in cart_products:
        markup.row(
            InlineKeyboardButton(text=f'❌ {product_name}', callback_data=f'delete_{cart_product_id}')
        )

    return markup
