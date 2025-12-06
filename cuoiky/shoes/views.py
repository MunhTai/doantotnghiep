from django.shortcuts import render,redirect,get_object_or_404
from shoes.models import Danhmuc,SanPham,HinhAnhSanPham,Size,SizeSanPham,Nguoidung,NhaCungCap,GioHang,Chitietgiohang,Hoadon,Chitiethoadon,Otp
from .form import dangkyform
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from decimal import Decimal
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum
from .utils import generate_otp, send_otp_email
# Create your views here.

def gioithieu(request):
    return render(request,'ss/gioithieu.html')

def index(request):

    hang = NhaCungCap.objects.all()
    giamgia = SanPham.objects.filter(giam_gia__isnull=False)
    return render(request,'ss/index.html',{'hang':hang,'giamgia':giamgia})

def chitiethang(request,id_ncc):
    hang = NhaCungCap.objects.get(id=id_ncc)
    dm = Danhmuc.objects.filter(ncc=hang)

    dm_sp_dict = []
    for d in dm:
        s = SanPham.objects.filter(danhmuc=d , nhacungcap=hang)[:4]
        dm_sp_dict.append((d,s))

    context = {
         'ncc':hang,
         'dm':dm,
         'dm_sp':dm_sp_dict
     }

    return render(request, 'ss/chitiethang.html/',context )
def more(request,tendm,idncc):
    ncc = NhaCungCap.objects.get(id=idncc)
    dm = Danhmuc.objects.get(ten_dm=tendm,ncc=ncc)
    more = SanPham.objects.filter(danhmuc=dm,nhacungcap=ncc)

    context = {
        'ncc':ncc,
        'dm':dm,
        'more':more
    }
    return render(request,'ss/more.html',context)

def chitiet(request, masp ):
    ctsp = SanPham.objects.get(ma_sp=masp)
    size_sl = SizeSanPham.objects.filter(sanpham=ctsp)

    context = {

        'ctsp':ctsp,
        'soluong':size_sl,
    }
    return render(request,'ss/chitietsanpham.html',context)


def dangky(request ):
    # if request.method == 'POST': 
    #     form = dangkyform(request.POST )
    #     if form.is_valid():
    #         user = form.save(commit=False)
    #         user.is_active = False
    #         user.save()

    #         code = generate_otp()
    #         Otp.objects.create(user=user, code=code)

    #         send_otp_email(user,code)
    #         return redirect('xac_thuc_otp',user_id=user.id)
    # else:
    #     form = dangkyform()
    # return render(request,'ss/dangky.html',{'form':form})

    if request.method == 'POST':
        ten = request.POST.get('username')
        mk = request.POST.get('password')
        mail = request.POST.get('email')

        if Nguoidung.objects.filter(username=ten).exists():
            messages.error(request,f'{ten} đã tồn tại.Hãy đặt tên khác ')
            return redirect('dk')
        
        user = Nguoidung.objects.create(
            username = ten,
            password = mk,
            email = mail,
            is_active = False

        )
        code = generate_otp()
        Otp.objects.create(user=user, code=code)
        send_otp_email(user,code)

        return redirect("xac_thuc_otp", user_id=user.id)

    return render(request, "ss/dangky.html")

def otp(request,user_id):
    user =Nguoidung.objects.get(id=user_id)

    if request.method == "POST":
        code = request.POST.get('otp')

        otp_obj = Otp.objects.filter(user=user, code=code).first()

        if otp_obj:
            user.is_active = True
            user.save()

            otp_obj.delete()

            return redirect('dn')
        return render (request, 'ss/otp.html',{'error': 'Sai mã OTP'})
    
    return render(request,'ss/otp.html')


def dangnhap(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Chào {username}")
                return redirect("tc")
            else:
                messages.error(request,"Bạn nhập sai thông tin đăng nhập!")
        else:
            messages.error(request,f"Chưa nhập đủ thông tin!")
        
    else:
        form = AuthenticationForm()
    return render(request,"ss/dangnhap.html",{'form':form})

def dangxuat(request):
    dx=logout(request )
    return redirect('tc')

def timkiem(request):
    tukhoa = request.GET.get('q').strip()
    kq = []

    if tukhoa:
        kq= SanPham.objects.filter(ten_sp__icontains = tukhoa)

    return render(request, 'ss/timkiem.html',{'tukhoa':tukhoa,'kq':kq})

def themsp (request):
    if request.method == "POST":
        ten = request.POST.get('t')
        gia = request.POST.get('g')
        giamgia = request.POST.get('gg')
        hinhanh = request.FILES.getlist('hinh')
        kichco = request.POST.getlist('s')
        soluong = request.POST.get('sl')
        hang = request.POST.get('h')
        danhmuc= request.POST.get('d')
        ncc = NhaCungCap.objects.get(ten_ncc=hang)
        dm = Danhmuc.objects.get(ten_dm=danhmuc)
     
        if not (ten and gia and hang and danhmuc and ncc and dm and hinhanh and kichco):
            messages.error(request, 'Vui lòng nhập đủ các dữ liệu của sản phẩm')
        else:
            sp = SanPham.objects.create(
                ten_sp=ten,
                gia=Decimal(gia),
                giam_gia=Decimal(giamgia)
                if giamgia
                else None,
                nhacungcap=ncc,
            )

            for hinh in hinhanh:
                HinhAnhSanPham.objects.create(hinh=hinh,san_pham=sp)
            
            for s in kichco:
                size = Size.objects.get(size=s)
                SizeSanPham.objects.create(
                    sanpham=sp,
                    size=size,
                    so_luong = soluong
                 )
            sp.danhmuc.add(dm)
            messages.success(request,f'Đã thêm mới sản phẩm {sp}')

    
    return render(request, 'ss/themsanpham.html',{'ncc_list':NhaCungCap.objects.all(),
                                                  'dm_list':Danhmuc.objects.all(),
                                                  'size_list':Size.objects.all()})

def themncc(request):
    dm = Danhmuc.objects.all()
    if request.method == 'POST':
        ten = request.POST.get('t')
        sodt= request.POST.get('sdt')
        mail = request.POST.get('e')
        diachi= request.POST.get('dc')
        danhmuc = request.POST.getlist('d')

        taoncc = NhaCungCap.objects.create(
            ten_ncc= ten,
            sdt = sodt,
            email = mail,
            dia_chi = diachi
        )

        for d in danhmuc:
            dm_obj = Danhmuc.objects.get(id=d)
            dm_obj.ncc.add(taoncc)
            messages.success(request,f'Đã thêm mới nhà cung cấp {taoncc.ten_ncc}')


    context ={
        'dm_list':dm
    }
    return render(request,'ss/themncc.html',context)

def themdanhmuc(request):
    ncc_list = NhaCungCap.objects.all()
    if request.method == 'POST':
        ten = request.POST.get('t')
        mota = request.POST.get('m')
        ncc = request.POST.getlist('n')

        taodm = Danhmuc.objects.create(
            ten_dm = ten,
            mo_ta = mota
        )

        for n in ncc:
            n_obj = NhaCungCap.objects.get(ten_ncc=n)
            taodm.ncc.add(n_obj)
        
    context={
        'ncc_list':ncc_list
    }

    return render(request,'ss/themdanhmuc.html',context)
def xoasp(request,masp):
    sp = get_object_or_404(SanPham, ma_sp=masp)

    if request.method == 'POST':
        sp.delete()
        messages.success(request,f'Đã xóa {sp.ten_sp}')
        return redirect('tc')
    else:
        messages.error(request,'Không thể xóa')
        return redirect('ct')
    
def suasp(request,masp):
    sp = get_object_or_404(SanPham,ma_sp=masp)

    hinhsanpham = HinhAnhSanPham.objects.filter(san_pham=sp)
    sizesanpham = SizeSanPham.objects.filter(sanpham=sp)
    dmsanpham = sp.danhmuc.filter()
    nccsanpham = sp.nhacungcap.ten_ncc

    hinh_list = HinhAnhSanPham.objects.all()
    size_list = Size.objects.all()
    ncc_list = NhaCungCap.objects.all()
    dm_list = Danhmuc.objects.all()

    if request.method == 'POST':
        ten = request.POST.get('t')
        gia = request.POST.get('g')
        giamgia = request.POST.get('gg')
        hinhanh = request.FILES.getlist('hinh')
        kichco = request.POST.getlist('s')
        soluong = request.POST.get('sl')
        hang = request.POST.get('h')
        danh_muc = request.POST.getlist('d')

        # Kiểm tra dữ liệu bắt buộc
        if not (ten and gia and hang and kichco):
            messages.error(request, 'Vui lòng nhập đủ các dữ liệu bắt buộc')
        else:
            sp.ten_sp=ten
            sp.gia=Decimal(gia)
            sp.giam_gia = Decimal(giamgia) if giamgia is not None else None
            sp.nhacungcap = NhaCungCap.objects.get(ten_ncc=hang)
            sp.save()

            for hinh in hinhanh:
                HinhAnhSanPham.objects.create(hinh=hinh,san_pham=sp)

            for s in kichco:
                size_obj = Size.objects.get(size=s)
                SizeSanPham.objects.update_or_create(
                    sanpham = sp,
                    size = size_obj,
                    defaults={'so_luong':soluong or 1}
                )

            sp.danhmuc.clear()

            for dm in danh_muc:
                dm_obj = Danhmuc.objects.get(ten_dm=dm)
                sp.danhmuc.add(dm_obj)

            messages.success(request, f'Đã cập nhật thành công sản phẩm {sp.ten_sp}')
            return redirect('ct',masp=sp.ma_sp)
        
        context = {
        'sp': sp,
        'hinh_list': hinh_list,
        'size_list': size_list,
        'size_da_co': sizesanpham,
        'ncc_list': ncc_list,
        'dm_list': dm_list,
        'dm_da_co': dmsanpham,
        'hinh_da_co':hinhsanpham,
        'ncc_da_co':nccsanpham
    }
    return render(request,'ss/suasanpham.html',context)




def themvaogio(request):

    # kiểm tra có submit form không và form có phải phương thức POST không

    if request.method == "POST":
        user = request.user # lấy user đang đăng nhập

        # Lấy các thông tin được gửi từ form 
        masp = request.POST.get('masp')
        size = request.POST.get('size_id')
        soluong = int(request.POST.get('sl')) #chuyển từ dạng string sang int
        action = request.POST.get('action') # lấy loại hành động để phân biệt

        #kiểm tra chọn size sản phẩm chưa
        if not size:
            messages.error(request,'Chưa chọn Size sản phẩm')

        #lấy dữ liệu size từ db.Và dùng size_obj là một instance
        size_obj = SizeSanPham.objects.get(id=size)

        #kiểm tra giỏ hàng của người dùng có hay chưa
        giohang, create = GioHang.objects.get_or_create(nguoi_dung=user)


        if action == 'add':
            chitiet = Chitietgiohang.objects.filter(
                gio_hang=giohang,
                size_sanpham = size_obj,
            )
            if chitiet:
                chitiet.so_luong += soluong
                chitiet.save()
            else:
                Chitietgiohang.objects.create(
                    gio_hang=giohang,
                    size_sanpham = size_obj,
                    so_luong = soluong,
                    don_gia= size_obj.gia_tuy_chinh
                )
            messages.success(request,f"Đã thêm vào giỏ hàng")
            return redirect('gh')
        
        elif action == 'buy':
            request.session['mua_ngay'] = {
                "masp": masp,
                "size_id": size,
                "soluong": soluong,
            }

            return redirect('tt')
    

def giohang(request):
    user = request.user

    giohang , create = GioHang.objects.get_or_create(nguoi_dung=user)

    chitiet_list = Chitietgiohang.objects.filter(gio_hang=giohang)

    context = {
        'ct':chitiet_list,
        'tongtien':giohang.tongtien
        
    }
    return render(request, 'ss/giohang.html',context)

def xoagiohang(request, ct_id):
    xoa = Chitietgiohang.objects.get(id=ct_id)
    xoa.delete()
    return redirect('gh')




def thanhtoan(request):
    user = request.user

    # ------------------------------
    # 1. Lấy giỏ hàng người dùng
    # ------------------------------
    giohang = GioHang.objects.get(nguoi_dung=user)
    ctgh = Chitietgiohang.objects.filter(gio_hang=giohang)

    # ------------------------------
    # 2. Kiểm tra nếu có mua ngay
    # ------------------------------
    muangay = request.session.get("mua_ngay")

    sanpham_muangay = None
    if muangay:
        try:
            size_obj = SizeSanPham.objects.get(id=muangay['size_id'])
            sanpham_muangay = {
                'size': size_obj,
                'soluong': int(muangay['soluong']),
                'dongia': size_obj.gia_tuy_chinh
            }
        except:
            sanpham_muangay = None

    # ------------------------------
    # 3. TÍNH TỔNG TIỀN (cho GET và POST)
    # ------------------------------
    tongtien = giohang.tongtien

    if sanpham_muangay:
        tongtien += sanpham_muangay['dongia'] * sanpham_muangay['soluong']

    # ------------------------------
    # 4. XỬ LÝ POST (nhấn nút thanh toán)
    # ------------------------------
    if request.method == "POST":
        diachi = request.POST.get("dia_chi")
        phuongthuc = request.POST.get("phuong_thuc")

        # 4.1 Tạo hóa đơn
        hoadon = Hoadon.objects.create(
            nguoidung=user,
            dia_chi=diachi,
            phuong_thuc=phuongthuc,
            trang_thai='pending',
            tong_tien=tongtien
        )

        # 4.2 Nếu thanh toán từ giỏ hàng → tạo chi tiết hóa đơn từ giỏ
        for item in ctgh:
            Chitiethoadon.objects.create(
                hoa_don=hoadon,
                size_sanpham=item.size_sanpham,
                so_luong=item.so_luong,
                don_gia=item.don_gia
            )

        # 4.3 Nếu thanh toán từ mua ngay → thêm sản phẩm mua ngay
        if sanpham_muangay:
            Chitiethoadon.objects.create(
                hoa_don=hoadon,
                size_sanpham=sanpham_muangay['size'],
                so_luong=sanpham_muangay['soluong'],
                don_gia=sanpham_muangay['dongia']
            )

        # 4.4 Sau khi thanh toán → xóa dữ liệu
        if ctgh.exists():
            Chitietgiohang.objects.filter(gio_hang=giohang).delete()

        if muangay:
            del request.session['mua_ngay']

        return redirect("tc")

    # ------------------------------
    # 5. RENDER GIAO DIỆN THANH TOÁN
    # ------------------------------
    context = {
        'giohang': giohang,
        'ct': ctgh,
        'mua_ngay': sanpham_muangay,
        'tongtien': tongtien
    }

    return render(request, 'ss/thanhtoan.html', context)



def donhang(request):
    user = request.user
    list_hd = Hoadon.objects.filter(nguoidung=user).order_by('-ngay_tao')
    chitiet_list = Chitiethoadon.objects.filter(hoa_don__in=list_hd)

    context = {
        'list_hd':list_hd,
        'ct':chitiet_list,
    }
    return render (request,'ss/donhang.html',context )

def xoa_donhang(request, dh_id):
    dh = Hoadon.objects.get(id=dh_id)

    dh.delete()
    return redirect('dh')


@staff_member_required
def quantri(request):
    tong_don = Hoadon.objects.count()
    don_cho = Hoadon.objects.filter(trang_thai='pending').count()
    da_xac_nhan = Hoadon.objects.filter(trang_thai='confirmed').count()
    dang_giao = Hoadon.objects.filter(trang_thai='shipping').count()
    hoan_tat = Hoadon.objects.filter(trang_thai='delivered')
    doanh_thu = 0
    for dt in hoan_tat:
        doanh_thu += (dt.tong_tien) + (dt.phi_ship)
    
    don_huy = Hoadon.objects.filter(trang_thai='cancelled').count()

    nd = Nguoidung.objects.all()

    ds_don = Hoadon.objects.select_related('nguoidung').order_by('ngay_tao').prefetch_related('cthd__size_sanpham__sanpham')
    context = {
        'td':tong_don,
        'dxn':da_xac_nhan,
        'dc':don_cho,
        'dg':dang_giao,
        'ht':hoan_tat.count(),
        'dt':doanh_thu,
        'dh':don_huy,
        'ds':ds_don,
        'nd':nd
    }
    return render(request,'ss/quantri.html',context)

def capnhattrangthai(request, order_id):
    hoadon = Hoadon.objects.get(id=order_id)
    status = request.POST.get('trang_thai')

    if status in dict(Hoadon.trangthai_choices).keys():
        hoadon.trang_thai = status
        hoadon.save()
    else:
        messages.error(request,'Trạng thái không hợp lệ')
    
    return redirect('qt')


def quanly_dm(request):
    all_dm=Danhmuc.objects.all()
    
    context = {
        'dm':all_dm,
        
    }
    return render(request,'ss/danhsach_dm.html',context)

def quanly_sp(request):
    all_sp=SanPham.objects.all()
    
    context = {
        'sp':all_sp,
    }
    return render(request,'ss/danhsach_sp.html',context)

def quanly_ncc(request):
    all_ncc=NhaCungCap.objects.all()

    context = {
        'ncc':all_ncc
    }
    return render(request,'ss/danhsach_ncc.html',context)

def quanly_nd(request):
    all_nd=Nguoidung.objects.all()
    context = {
        'nd':all_nd
    }
    return render(request,'ss/danhsach_nd.html',context)