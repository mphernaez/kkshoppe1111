import json
from django.core.mail import send_mail
from django.shortcuts import render
from .models import Item, Order, OrderItem
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string

@csrf_exempt
def item(request, code=None):
    if request.method == "GET":
        item = Item.objects.get(code=code)
        i = {
            "name": item.name,
            "quantity": item.quantity,
            "code": item.code,
            "price": item.price,
        }
        data = []
        if request.GET.get('orders') == 'True':
            orders = item.get_orders()
            o = []
            for order in orders:
                order_item =  OrderItem.objects.get(order=order, item=item, status=1)
                o.append({
                    "name": order.name,
                    "quantity": order_item.quantity,
                    "status": 'Confirmed',

                })
            data.append({
                "orders": o
            })
        
        return JsonResponse({"item": i, "data": data})
            

    elif request.method == "POST":
        try:
            item = Item.objects.create(
                name = request.POST.get('name'),
                quantity = request.POST.get('qunatity', 0),
                group = request.POST.get('group', ''),
                price = request.POST.get('price')
            )
            return JsonResponse({'status': 'created ' + item.name})
        except Exception as ex:
            print(ex)
            return JsonResponse({'status': 'failed'})

@csrf_exempt
def items(request):
    orders = Order.objects.filter(status=1)
    total = 0
    for order in orders:
        total += order.get_total()
    print('this is the total so far: ' + str(total))
    if request.method == 'GET':
        if request.GET.get('group'):
            items = Item.filter_group(request.GET.get('group'))
            i = []
            for item in items:
                i.append({
                    'name': item.name,
                    "quantity": item.quantity,
                    "code": item.code,
                    "price": item.price,
                })
            return JsonResponse({'group': request.GET.get('group'), 'items': i})

        elif request.GET.get('status'):
            items = Item.filter_status(request.GET.get('status'))
            i = []
            for item in items:
                i.append({
                    'name': item.name,
                    "quantity": item.quantity,
                    "code": item.code,
                    "price": item.price,
                })
            return JsonResponse({'status': request.GET.get('status'), 'items': i})

        items = Item.filter_status(request.GET.get('status'))
        i = []
        for item in items:
            i.append({
                'name': item.name,
                "quantity": item.quantity,
                "code": item.code,
                "price": item.price,
            })
        return JsonResponse({'items': i})

@csrf_exempt
def order(request, code=None):
    if request.method == 'POST':
        try:
            print(request.POST)
            name=request.POST.get('name')    
            item_list = request.POST.get('items')
            safekeeping = request.POST.get('safekeeping', 0)
            shipping = request.POST.get('shipping_method', 0)
            shiping_address = request.POST.get('shipping_address', '')
            payment_method = request.POST.get('payment_method', 0)
            email = request.POST.get('email')
            contact = request.POST.get('contact')
            order = Order.objects.create(
                name=name,
                safekeeping=safekeeping,
                shipping=shipping,
                shipping_address=shiping_address,
                payment_method=payment_method,   
                contact=contact,
                email=email,
            )

            shipping_fee = 0
            shipping = int(shipping)
            if shipping == 1:
                shipping_fee = 150.0
            elif shipping == 2:
                shipping_fee = 180.0
            elif shipping == 3:
                shipping_fee = 220.0
            elif shipping == 4:
                shipping_fee = 240.0

            safekeeping_fee = 0
            safekeeping = int(safekeeping)
            if safekeeping == 1:
                safekeeping_fee = 7
            elif safekeeping == 2:
                safekeeping_fee = 7
            elif safekeeping == 3:
                safekeeping_fee = 10
            elif safekeeping == 4:
                safekeeping_fee = 14
            
            cart = []
            item_list = json.loads(item_list)
            for item in item_list:
                status = 0
                price = 0
                i = Item.objects.get(code=item['code'])
                if i.quantity >= item['qty']:  
                    i.quantity -= item['qty']
                    i.save()
                    status = 1
                order_item = OrderItem.objects.create(
                    order=order,
                    item=i,
                    quantity=item['qty'],
                    status=status,
                )
                price = order_item.quantity * order_item.item.price
                if status == 1:
                    cart.append({
                        'name': order_item.item.group + ' ' + order_item.item.name,
                        'qty': order_item.quantity,
                        'price': price
                    })
            cart.append({
                'name': 'Shipping',
                'price': shipping_fee 
            })
            cart.append({   
                'name': 'Safekeeping',
                'price': safekeeping_fee
            })
            order.additional_fee = shipping_fee + safekeeping_fee
            order.status = 1
            order.save()
            
            total = order.get_total() + shipping_fee + safekeeping_fee
            print(cart)
            

            data = {'name': name, 'code': order.code, 'cart': cart, 'total': total}
            print(data)

            msg_html = render_to_string('email/confirmation.html', data)
            send_mail(
                'KKShoppe 11.11 Sale - Order Confirmation #' + order.code,
                '',
                'kkshoppedvo@gmail.com',
                [email],
                html_message=msg_html,
            )
            return JsonResponse({'status': 'created', 'order': data})
        except Exception as ex:
            print(ex)
            return JsonResponse({'status': 'failed'})
        


