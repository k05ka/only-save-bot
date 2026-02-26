from aiogram import Router, types, F, Bot
from aiogram.filters import Command, StateFilter, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.exceptions import TelegramBadRequest
from fluent.runtime import FluentLocalization
from .keyboards import *
from .states import *
import logging

stars_router = Router()
logging.basicConfig(level=logging.INFO)


@stars_router.callback_query(CallbackFactory.filter(F.action == 'donate'))
@stars_router.message(Command(commands='donate'))
async def cmd_technical(
    event: types.CallbackQuery | types.Message,
    state: FSMContext, 
    l10n: FluentLocalization   
):
    text = l10n.format_value('donate-form')
    keyboard = donate_fab()
    if isinstance(event, types.Message):
        await event.answer(text=text, reply_markup=keyboard)
    elif isinstance(event, types.CallbackQuery):
        await event.message.answer(text=text, reply_markup=keyboard)
        await event.answer()
    await state.set_state(ChatForm.choose_star)

@stars_router.callback_query(CallbackFactory.filter(F.action == 'pay'))
async def callback_pay(
    callback: types.CallbackQuery,
    callback_data: CallbackFactory,
    state: FSMContext,
    l10n: FluentLocalization,
):    
    await state.update_data(stars=callback_data.value)
    await callback.message.delete()
    user_data = await state.get_data()
    stars_amount = user_data.get("stars", 0)
    prices = [types.LabeledPrice(label="XTR", amount=stars_amount)]

    await callback.message.answer_invoice(
        title=l10n.format_value("invoice-title", {"stars_count": stars_amount}),
        description=l10n.format_value('invoice-description'),
        prices=prices,
        provider_token="",
        payload=f"{callback.from_user.id}_{stars_amount}_stars",
        currency="XTR",
        reply_markup=get_star_piece_fab(user_data=stars_amount)
    )

@stars_router.pre_checkout_query()
async def on_pre_checkout_query(
    pre_checkout_query: types.PreCheckoutQuery,
    l10n: FluentLocalization,
    state: FSMContext,
):
    await pre_checkout_query.answer(ok=True)
    # await pre_checkout_query.answer(
    #     ok=False,
    #     error_message=l10n.format_value("pre-checkout-failed-reason")
    # )
    await state.set_state(ChatForm.donate_success)

@stars_router.message(F.successful_payment, StateFilter(ChatForm.donate_success))
async def on_successful_payment(
    message: types.Message,
    l10n: FluentLocalization,
):
    await message.answer(
        l10n.format_value(
            "payment-successful",
            {"id": message.successful_payment.telegram_payment_charge_id}
        ),
        message_effect_id="5104841245755180586",
    )

@stars_router.message(Command("refund"))
async def cmd_refund(
    event: types.Message,
    command: CommandObject,
    l10n: FluentLocalization,
    bot: Bot,
):
    transaction_id = command.args
    if transaction_id is None:
        await event.answer(
            l10n.format_value("refund-no-code-provided")
        )
        return
    try:
        await bot.refund_star_payment(
            user_id=event.from_user.id,
            telegram_payment_charge_id=transaction_id
        )
        await event.answer(
            l10n.format_value("refund-successful")
        )
    except TelegramBadRequest as error:
        if "CHARGE_NOT_FOUND" in error.message:
            text = l10n.format_value("refund-code-not-found")
        elif "CHARGE_ALREADY_REFUNDED" in error.message:
            text = l10n.format_value("refund-already-refunded")
        else:
            text = l10n.format_value("refund-code-not-found")
        await event.answer(text)
        return