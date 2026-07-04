@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    order_id = message.text.split()[1].split('_')[1]
    CLICK_TOKEN = CLICK_PROVIDER_TOKEN
    order: Payment = await sync_to_async(Payment.objects.select_related('course').get)(id=order_id)
    prices = [LabeledPrice(label=f"Course: {order.course.title}", amount=int(order.course.price * 1 * 100))]
    print("AMOUNT:", int(order.course.price))
    print("CURRENCY:", "UZS")
    await message.answer_invoice("LearnFlow", description="Kurs uchun to'lov", payload=order_id, currency="UZS", provider_token=CLICK_TOKEN, prices=prices)

@dp.pre_checkout_query()
async def success_handler(pre_checkout_query: PreCheckoutQuery) -> None:
    await pre_checkout_query.answer(True)

@dp.message(lambda message: bool(message.successful_payment))
async def confirm_handler(message: Message):
    if message.successful_payment:
        total_amount = message.successful_payment.total_amount//100
        order_id = int(message.successful_payment.invoice_payload)
        payment = await sync_to_async(Payment.objects.select_related('user', 'course').get)(id=order_id)
        await sync_to_async(Payment.objects.filter(id=order_id).update)( status=Payment.StatusType.COMPLETED, amount=total_amount)
        await sync_to_async(
            Enrollment.objects.filter(
                user=payment.user,
                course=payment.course
            ).update
        )(
            status=Enrollment.StatusType.ACTIVE
        )


        await message.answer(text=f'Thanks for your payment')
