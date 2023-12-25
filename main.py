from aiogram import Bot, Dispatcher, executor
from aiogram.types import Message, CallbackQuery, LabeledPrice
from database import *
from keyboards import *

TOKEN = '' #copy and past your telegram token
PAYMENT = '' #copy and past your payment token
bot = Bot(TOKEN)

dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def command_start(message: Message):
    await message.answer(f'Hello, {message.from_user.full_name}. \nWelcome to Yami! bot')

    await register_or_authentication_user(message)


async def register_or_authentication_user(message: Message):
    chat_id = message.chat.id
    user = first_select_user(chat_id)

    if user:
        await message.answer('Authentication has successfully completed')
        await show_main_menu(message)
        # keyboad menu
    else:
        await message.answer('Click "Share contacts" in order to register', reply_markup=send_contact())


@dp.message_handler(content_types=['contact'])
async def finish_register(message: Message):
    chat_id = message.chat.id
    full_name = message.from_user.full_name
    phone = message.contact.phone_number
    first_register_user(full_name, chat_id, phone)
    await create_cart_for_user(message)
    await message.answer('Registration completed successfully')
    await show_main_menu(message)


async def create_cart_for_user(message):
    chat_id = message.chat.id
    try:
        insert_to_cart(chat_id)
    except:
        pass


async def show_main_menu(message: Message):
    await message.answer('Choose route', reply_markup=generate_main_menu())


@dp.message_handler(lambda message: '✅ Make an order' in message.text)
async def make_order(message: Message):
    await message.answer('Choose a category', reply_markup=category_products())


@dp.callback_query_handler(lambda call: 'category' in call.data)
async def show_products(call: CallbackQuery):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    _, category_id = call.data.split('_')
    category_id = int(category_id)
    await bot.edit_message_text('Choose a product:', chat_id, message_id,
                                reply_markup=products_by_category(category_id))


@dp.callback_query_handler(lambda call: 'main_menu' in call.data)
async def return_to_main_menu(call: CallbackQuery):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text='Choose category',
                                reply_markup=category_products())


@dp.callback_query_handler(lambda call: 'product' in call.data)
async def show_detail_product(call: CallbackQuery):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    _, product_id = call.data.split('_')
    product_id = int(product_id)

    quantity = 0
    product = get_product_detail(product_id)
    cart_id = get_user_cart_id(chat_id)

    await bot.delete_message(chat_id=chat_id, message_id=message_id)

    with open(product[-1], 'rb') as img:
        await bot.send_photo(chat_id=chat_id, photo=img, caption=f'''{product[2]}
Ingredients: {product[4]}

Price: {product[3]} UZS''', reply_markup=generate_count_product(product_id=product_id, category_id=product[1],
                                                                cart_id=cart_id, product_name=product[2], c=quantity))


@dp.callback_query_handler(lambda call: 'plus' in call.data)
async def add_product_cart(call: CallbackQuery):
    chat_id = call.message.chat.id
    _, quantity, product_id = call.data.split('_')
    quantity, product_id = int(quantity), int(product_id)
    message_id = call.message.message_id

    quantity += 1
    product = get_product_detail(product_id)
    cart_id = get_user_cart_id(chat_id)

    await bot.edit_message_caption(chat_id=chat_id, message_id=message_id, caption=f'''{product[2]}
Ingredients: {product[4]}

Price: {product[3]} UZS''', reply_markup=generate_count_product(product_id=product_id, category_id=product[1],
                                                                cart_id=cart_id, c=quantity))


@dp.callback_query_handler(lambda call: 'minus' in call.data)
async def minus_product_cart(call: CallbackQuery):
    chat_id = call.message.chat.id
    _, quantity, product_id = call.data.split('_')
    quantity, product_id = int(quantity), int(product_id)
    message_id = call.message.message_id

    if quantity <= 1:
        await bot.answer_callback_query(call.id, 'Cannot be below 1')
    else:
        quantity -= 1
        product = get_product_detail(product_id)
        cart_id = get_user_cart_id(chat_id)

        await bot.edit_message_caption(chat_id=chat_id, message_id=message_id, caption=f'''{product[2]}
Ingredients: {product[4]}
    
Price: {product[3]} UZS''', reply_markup=generate_count_product(product_id=product_id, category_id=product[1],
                                                                cart_id=cart_id, c=quantity))


@dp.callback_query_handler(lambda call: 'cart' in call.data)
async def add_product_to_cart_products(call: CallbackQuery):
    chat_id = call.message.chat.id
    _, product_id, quantity = call.data.split('_')
    product_id, quantity = int(product_id), int(quantity)
    product = get_product_detail(product_id)
    cart_id = get_user_cart_id(chat_id)
    final_price = quantity * product[3]

    if insert_or_update_cart_products(cart_id, product[2], quantity, final_price):
        await bot.answer_callback_query(call.id, 'Product was added successfully')
    else:
        await bot.answer_callback_query(call.id, 'Quantity has been updated')


@dp.callback_query_handler(lambda call: 'back' in call.data)
async def return_to_product(call: CallbackQuery):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    _, category_id = call.data.split('_')
    await bot.delete_message(chat_id, message_id)
    await bot.send_message(chat_id, 'Choose category', reply_markup=products_by_category(category_id))


@dp.message_handler(regexp='🛒 Cart')
async def show_cart(message: Message, edit_message: bool = False):
    chat_id = message.chat.id
    cart_id = get_user_cart_id(chat_id)

    try:
        update_carts(cart_id)


    except Exception as e:
        print(e)
        await message.answer('The cart is empty')
        return

    cart_products = get_cart_products(cart_id)
    total_products, total_price = get_total_products_total_price(cart_id)
    text = 'You order \n\n'
    i = 0
    for product_name, quantity, final_price in cart_products:
        i += 1
        text += f'''{i}, {product_name}
Quantity: {quantity}
Total price: {final_price} UZS\n\n'''
    text += f''' Total quantity of products: {0 if total_products is None else total_products}
Total price: {0 if total_price is None else total_price} UZS
'''
    if edit_message:
        await bot.edit_message_text(text, chat_id, message.message_id, reply_markup=generate_cart_menu(cart_id))
    else:
        await bot.send_message(chat_id, text, reply_markup=generate_cart_menu(cart_id))


@dp.callback_query_handler(lambda call: 'delete' in call.data)
async def delete_cart_product(call: CallbackQuery):
    _, cart_product_id = call.data.split('_')
    cart_product_id = int(cart_product_id)
    message = call.message
    delete_cart_product_from(cart_product_id)

    await bot.answer_callback_query(call.id, 'Product has been deleted from CART')
    await show_cart(message, edit_message=True)


@dp.callback_query_handler(lambda call: 'order' in call.data)
async def create_order(call: CallbackQuery):
    chat_id = call.message.chat.id
    _, cart_id = call.data.split('_')
    cart_id = int(cart_id)
    cart_products = get_cart_products(cart_id)
    total_products, total_price = get_total_products_total_price(cart_id)
    text = 'You order \n\n'
    i = 0
    for product_name, quantity, final_price in cart_products:
        i += 1
        text += f'''{i}, {product_name}
    Quantity: {quantity}
    Total price: {final_price} UZS\n\n'''
    text += f''' Total quantity of products: {0 if total_products is None else total_products}
    Total price: {0 if total_price is None else total_price} UZS
    '''

    await bot.send_invoice(
        chat_id=chat_id,
        title=f'Order: #{cart_id}',
        description=text,
        payload='bot-defined invoice payload',
        provider_token=PAYMENT,
        currency='UZS',
        prices=[
            LabeledPrice(label='Total price', amount=int(total_price) * 100),
            LabeledPrice(label='delivery', amount=1000000)
        ],
        start_parameter='start_parameter'
    )


@dp.pre_checkout_query_handler(lambda query: True)
async def check_out(pre_checkout_query):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True,
                                        error_message='Payment was not made, please check your card')


@dp.message_handler(content_types=['successful_payment'])
async def get_payment(message: Message):
    chat_id = message.chat.id
    await bot.send_message(chat_id, 'Payment was successfully made')
    cart_id = get_user_cart_id(chat_id)
    drop_cart_products_default(cart_id)


executor.start_polling(dp)
