from .models import NhaCungCap, SanPham

def data(request):
    return {
        'hang': NhaCungCap.objects.all(),
        'giamgia': SanPham.objects.filter(giam_gia__isnull=False)
    }

def cart_count(request):
    cart = request.session.get('cart', {})
    total_qty = sum(item['qty'] for item in cart.values())
    return {
        'cart_count': total_qty
    }