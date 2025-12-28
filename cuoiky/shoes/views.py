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
from django.urls import reverse
from django.contrib.auth.hashers import check_password
# Create your views here.

def gioithieu(request):
    return render(request,'ss/gioithieu.html')

def index(request):

    
    giamgia = SanPham.objects.filter(giam_gia__isnull=False)
    return render(request,'ss/index.html',{'giamgia':giamgia})

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
  
    if request.method == 'POST':
        ten = request.POST.get('username')
        mk1 = request.POST.get('password1')
        mk2 = request.POST.get('password2')
        mail = request.POST.get('email')
        phone = request.POST.get('phone')
        so_nha = request.POST['so_nha']
        duong = request.POST['duong']
        phuong = request.POST['phuong']
        district = request.POST['district']
        city = request.POST['city']

        if Nguoidung.objects.filter(username=ten).exists():
            messages.error(request, 'Username đã tồn tại')
            return redirect('dk')

        if Nguoidung.objects.filter(email=mail).exists():
            messages.error(request, 'Email đã tồn tại')
            return redirect('dk')

        if Nguoidung.objects.filter(phone=phone).exists():
            messages.error(request, 'Số điện thoại đã tồn tại')
            return redirect('dk')
        
        if mk1 != mk2:
            messages.error(request,'Mật khẩu nhập chưa khớp! Hãy kiểm tra lại')
            return redirect('dk')
        
        user = Nguoidung.objects.create_user(
            username=ten,
            password=mk1,    
            email=mail,
            phone=phone,
            so_nha=so_nha,
            duong=duong,
            phuong=phuong,
            quan=district,
            tinh=city,
            is_active=False
        )
        code = generate_otp()
        Otp.objects.create(user=user, code=code)
        send_otp_email(user,code)

        return redirect("xac_thuc_otp", user_id=user.id)

    return render(request, "ss/dangky.html")



def otp(request):
    user =request.user

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
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request,"Chưa nhập đủ thông tin")
            return redirect('dn')
        
        user = Nguoidung.objects.get(username=username)
        if not user:
            messages.error(request,"Sai thông tin đăng nhập")
            return redirect('dn ')
        
        if not user.is_active:
            messages.error(request,"Tài khoản chưa xác thực OTP")
            return redirect('dn')
        
        if not check_password(password, user.password):
            messages.error(request, "Sai mật khẩu")
            return redirect('dn')
        
        login(request, user)
        messages.success(request, f"Chào {username}")
        return redirect("tc")
    
    return render(request,"ss/dangnhap.html")

def dangxuat(request):
    dx=logout(request )
    return redirect('tc')

def timkiem(request):
    tukhoa = request.GET.get('q').strip()
    kq = []

    if tukhoa:
        kq= SanPham.objects.filter(ten_sp__icontains = tukhoa)

    return render(request, 'ss/timkiem.html',{'tukhoa':tukhoa,'kq':kq})

@ staff_member_required
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

@ staff_member_required
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

@ staff_member_required
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
    


def suasp(request, masp):
    sp = get_object_or_404(SanPham, ma_sp=masp)

    hinh_da_co = HinhAnhSanPham.objects.filter(san_pham=sp)
    size_da_co = SizeSanPham.objects.filter(sanpham=sp)
    size_id_daco = size_da_co.values_list('size_id', flat=True)
    dm_da_co = sp.danhmuc.all()
    ncc_da_co = sp.nhacungcap

    size_list = Size.objects.all()
    ncc_list = NhaCungCap.objects.all()
    dm_list = Danhmuc.objects.all()
    

    if request.method == 'POST':
        
        ten = request.POST.get('t')
        gia = request.POST.get('g')
        giamgia = request.POST.get('gg')
        hinh_moi = request.FILES.getlist('hinh')
        size_ids = request.POST.getlist('s')      
        ncc_id = request.POST.get('n')            
        dm_ids = request.POST.getlist('d')         

        
        if not ten or not gia or not ncc_id:
            messages.error(request, 'Vui lòng nhập đủ các dữ liệu bắt buộc')
            return redirect(request.path)

      
        sp.ten_sp = ten
        sp.gia = Decimal(gia)
        sp.giam_gia = Decimal(giamgia) if giamgia else None
        sp.nhacungcap = NhaCungCap.objects.get(id=ncc_id)
        sp.save()

        
        for h in hinh_moi:
            HinhAnhSanPham.objects.create(
                san_pham=sp,
                hinh=h
            )

        SizeSanPham.objects.filter(sanpham=sp)\
            .exclude(size_id__in=size_ids).delete()

        for s_id in size_ids:
            size_obj = Size.objects.get(id=s_id)

            so_luong = request.POST.get(f"sl_{s_id}") or 1
            loai_gia = request.POST.get(f"lg_{s_id}") or 'none'
            gia_custom = request.POST.get(f"gc_{s_id}") or None

            if loai_gia == 'custom' and gia_custom not in ['', None]:
                gia_custom = Decimal(gia_custom)
            else:
                gia_custom = None
                loai_gia = 'none'
            SizeSanPham.objects.update_or_create(
                sanpham=sp,
                size=size_obj,
                defaults={
                    'so_luong': so_luong,
                    'loai_gia': loai_gia,
                    'gia_custom': Decimal(gia_custom) if gia_custom else None
                }
             )

    
        sp.danhmuc.set(dm_ids)

        messages.success(request, f'Đã cập nhật sản phẩm {sp.ten_sp}')
        return redirect('ct', masp=sp.ma_sp)
    
    context = {
        'sp': sp,
        'hinh_da_co': hinh_da_co,
        'size_list': size_list,
        'size_da_co': size_da_co,
        'ncc_list': ncc_list,
        'ncc_da_co': ncc_da_co,
        'dm_list': dm_list,
        'dm_da_co': dm_da_co,
    }

    return render(request, 'ss/suasanpham.html', context)


def themvaogio(request):


    if request.method == "POST":
        user = request.user 

        masp = request.POST.get('masp')
        size = request.POST.get('size_id')
        soluong = int(request.POST.get('sl')) 
        action = request.POST.get('action') 

        if not size:
            return redirect(request.META.get('HTTP_REFERER'))

        size_obj = SizeSanPham.objects.get(id=size)
        if size_obj.so_luong == 0:
            return redirect(request.META.get('HTTP_REFERER'))

        giohang, create = GioHang.objects.get_or_create(nguoi_dung=user)


        if action == 'add':
            chitiet = Chitietgiohang.objects.filter(
                gio_hang=giohang,
                size_sanpham = size_obj,
                
            ).first()
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
            return redirect(request.META.get('HTTP_REFERER'))
            
        elif action == 'buy':
            request.session['mua_ngay'] = {
                "masp": masp,
                "size_id": size,
                "soluong": soluong,
            }

            return redirect(f'{reverse('tt')}?buy_now=1') 
    

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
    diachi_mac_dinh = request.user.diachi_daydu
    ten_nguoi_nhan = request.user.username
    sdt = request.user.phone


    giohang = GioHang.objects.get(nguoi_dung=user)
    ctgh = Chitietgiohang.objects.filter(gio_hang=giohang)


    muangay = request.session.get("mua_ngay")

    if not ctgh.exists() and not muangay:
        messages.warning(request,'Chưa có sản phẩm trong giỏ hàng')
        return redirect('gh')

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

    
    phiship = Decimal(30000)

    if sanpham_muangay:
         tam_tinh = sanpham_muangay['dongia'] * sanpham_muangay['soluong']
    else:
         tam_tinh = giohang.tongtien

    tongtien = tam_tinh + phiship
  
    if request.method == "POST":
        diachi = request.POST.get('dia_chi')
        phuongthuc = request.POST.get("phuong_thuc")

      
        hoadon = Hoadon.objects.create(
            nguoidung=user,
            dia_chi=diachi,
            phuong_thuc=phuongthuc,
            trang_thai='pending',
            tong_tien=tam_tinh,
            phi_ship=phiship,
        )

        for item in ctgh:
            Chitiethoadon.objects.create(
                hoa_don=hoadon,
                size_sanpham=item.size_sanpham,
                so_luong=item.so_luong,
                don_gia=item.don_gia
            )
           

            item.size_sanpham.so_luong -= item.so_luong
            item.size_sanpham.save()

        if sanpham_muangay:
            Chitiethoadon.objects.create(
                hoa_don=hoadon,
                size_sanpham=sanpham_muangay['size'],
                so_luong=sanpham_muangay['soluong'],
                don_gia=sanpham_muangay['dongia']
            )

            sanpham_muangay['size'].so_luong -= sanpham_muangay['soluong']
            sanpham_muangay['size'].save()


       
        if ctgh.exists():
            Chitietgiohang.objects.filter(gio_hang=giohang).delete()

        if muangay:
            del request.session['mua_ngay']
        messages.success(request,'Đã đặt đơn thành công')

        return redirect("dh")

  
    context = {
        'giohang': giohang,
        'ct': ctgh,
        'mua_ngay': sanpham_muangay,
        'tongtien': tongtien,
        'tamtinh': tam_tinh,
        'ship':phiship,
        'dc':diachi_mac_dinh,
        'ten':ten_nguoi_nhan,
        'sdt':sdt,
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

    if dh.trang_thai != 'pending':
        return redirect('dh')
    
    for ct in dh.cthd.all():
        ct.size_sanpham.so_luong += ct.so_luong
        ct.size_sanpham.save()

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
def xoa_dm(request, dm_xoa):
    xoa_dm = Danhmuc.objects.get(id=dm_xoa)
    xoa_dm.delete()

    
    return redirect ('qldm')
 
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

def xoa_ncc(request, ncc_xoa):
    xoa_ncc = NhaCungCap.objects.get(id=ncc_xoa)
    xoa_ncc.delete()
    return redirect('qlncc')

def quanly_nd(request):
    all_nd=Nguoidung.objects.all()
    context = {
        'nd':all_nd
    }
    return render(request,'ss/danhsach_nd.html',context)
def xoa_nd(request, nd_xoa):
    xoa_nd = Nguoidung.objects.get(id=nd_xoa)
    xoa_nd.delete()
    return redirect('qlnd')

def thongtin_nguoidung(request):
    thongtin = request.user

    context = {
        'tt':thongtin
    }
    return render(request,'ss/thongtin.html',context)

def sua_thongtin(request):
    user = request.user

    if request.method == 'POST':
        user.username = request.POST.get('username') or user.username
        user.phone    = request.POST.get('phone')    or user.phone
        user.so_nha   = request.POST.get('so_nha')   or user.so_nha
        user.duong    = request.POST.get('duong')    or user.duong
        user.phuong   = request.POST.get('phuong')   or user.phuong
        user.quan     = request.POST.get('quan')     or user.quan
        user.tinh     = request.POST.get('tinh')     or user.tinh
        user.save()

        messages.success(request, "Đã cập nhật thông tin thành công!")
        return redirect('ttnd')

    return render(request, 'ss/sua_thongtin.html')

    
    