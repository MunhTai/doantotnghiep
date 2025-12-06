from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils.text import slugify
from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.db.models import Max
# Create your models here.

# custom user(mở rộng)
class Nguoidung(AbstractUser):
    email = models.EmailField("email", max_length=254,unique=True)
    phone = models.CharField("Số điện thoại", max_length=20, blank=True, null=True, unique=True)
    address = models.TextField("Địa chỉ", blank=True)

    def __str__(self):
        return self.get_username()
    
class Otp(models.Model):
    user = models.ForeignKey(Nguoidung,on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    create = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.code}"
    
#Bảng Danh Mục
class Danhmuc(models.Model):
    ten_dm = models.CharField("Tên danh mục", max_length=255)
    mo_ta = models.TextField("Mô tả", blank=True)
    khoi_tao = models.DateTimeField(auto_now_add=True)
    ncc = models.ManyToManyField("NhaCungCap",related_name='ncc_dm',blank=True)

    class Meta:
        verbose_name_plural = "Danh mục"


    def __str__(self):
        return self.ten_dm
    
    
    
    
    
# Bảng Nhà Cung Cấp
class NhaCungCap(models.Model):
    ten_ncc = models.CharField("Tên nhà cung cấp", max_length=255)
    email = models.EmailField("Email", blank=True)
    sdt = models.CharField("Điện thoại", max_length=30, blank=True)
    dia_chi = models.TextField("Địa chỉ", blank=True)

    class Meta:
        verbose_name_plural = "Nhà cung cấp"

    def __str__(self):
        return self.ten_ncc
    
#Bảng Sản Phẩm
class SanPham(models.Model):
    ma_sp = models.CharField(max_length=20, primary_key=True, blank=True)
    ten_sp = models.CharField("Tên sản phẩm", max_length=255)
    mo_ta = models.TextField("Mô tả", blank=True)
    nhacungcap = models.ForeignKey(NhaCungCap, on_delete=models.PROTECT, related_name="sanphams")
    danhmuc = models.ManyToManyField(Danhmuc, related_name="sanphams", blank=True)
    gia = models.DecimalField("Giá gốc", max_digits=12, decimal_places=2)
    giam_gia = models.DecimalField("Giá khuyến mãi", max_digits=12, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    khoi_tao = models.DateTimeField(auto_now_add=True,null=True)

    class Meta:
        verbose_name_plural = "Sản phẩm"


             #xử lý giá bán
        #----------------------------#
    @property
    def gia_ban(self):
        if self.giam_gia is not None and self.giam_gia < self.gia:
            return self.giam_gia
        else:
            return self.gia
        #----------------------------#



    def save(self,*args, **kwargs):

        #tạo mã sản phẩm
    #----------------------------#
        # xử lý mã sản phẩm
        if not self.ma_sp:

        #lấy kí tự đầu của tên ncc nếu không có thì lấy 4 kí tự đầu của tên sp
            if self.nhacungcap :
                prefix = self.nhacungcap.ten_ncc[:1].upper()
            else:
                prefix = self.ten_sp[:4].upper()

            max= (
                SanPham.objects.filter(ma_sp__startswith = prefix)
                .aggregate(max_code=Max('ma_sp'))
            )
            max_none = max['max_code']

        #đếm mã cộng dồn
            if max_none is None:
                count =1
                
            else:
                count = int(max_none[len(prefix):]) +1
            self.ma_sp = f"{prefix}{count:03d}"
        #----------------------------#


          
        super().save(*args, **kwargs)


    def __str__(self): 
        return f"{self.ten_sp})"
        

class HinhAnhSanPham(models.Model):
    san_pham = models.ForeignKey(SanPham, on_delete=models.CASCADE, related_name="hinh_anh")
    hinh = models.ImageField(upload_to="sanpham/")  


    class Meta:
        verbose_name_plural = "Hình Ảnh Sản phẩm"
    def __str__(self):
        return f"Hình của {self.san_pham.ten_sp}"
    
    
#Bảng size
class Size(models.Model):
    size = models.FloatField("Size", max_length=50, unique=True)  

    class Meta:
        verbose_name_plural = "Size"
  
    def __str__(self):
        return str(self.size)
    
    
#Bảng size_Sanpham
class SizeSanPham(models.Model):

    thaydoi = [
        ('none','Mặc định'),
        ('custom','Giá tùy chỉnh')
    ]
    sanpham = models.ForeignKey(SanPham, on_delete=models.CASCADE, related_name="size_sp")
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    so_luong = models.PositiveIntegerField("Số lượng tồn", default=0)
    loai_gia = models.CharField(max_length=20,choices=thaydoi,default="none")
    gia_custom = models.DecimalField("Giá tùy chỉnh",max_digits=20,decimal_places=2,null=True,blank=True)

    class Meta:
        unique_together = ("sanpham", "size") 
        verbose_name_plural = "Sản phẩm theo size"

    def __str__(self):
        return f"{self.sanpham.ten_sp} -{int(self.size.size)} "
    
    @property
    def gia_tuy_chinh(self):
           # lấy giá của sản phẩm
        #----------------------------#
        gia_mac_dinh = self.sanpham.gia_ban or Decimal('0')

        # tính giá tùy chỉnh
        if self.loai_gia == 'custom' and self.gia_custom is not None:
            return self.gia_custom
        else:
            return gia_mac_dinh
       
        #----------------------------#
    
    
         

class GioHang(models.Model): 
    nguoi_dung = models.ForeignKey(Nguoidung, on_delete=models.CASCADE, null=True, blank=True)
    khoi_tao = models.DateTimeField(auto_now_add=True)
    cap_nhat = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Giỏ hàng"

    def __str__(self):
        return f"Giỏ Hàng {self.id} (Người Dùng={self.nguoi_dung})"
    
    
    @property
    def tongtien(request):
        return sum([item.thanhtien for item in request.chitiet.all()])

class Chitietgiohang(models.Model):
    gio_hang = models.ForeignKey(GioHang, on_delete=models.CASCADE, related_name="chitiet")
    size_sanpham = models.ForeignKey(SizeSanPham, on_delete=models.PROTECT)
    so_luong = models.PositiveIntegerField(default=1)
    don_gia = models.DecimalField(max_digits=12, decimal_places=2,null=True)  
    khoi_tao = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("gio_hang", "size_sanpham")


    @property
    def thanhtien(self):
        return self.so_luong*self.don_gia

    

class Hoadon(models.Model):
    thanhtoan_choices = [
        ('cod',"thanh toán khi nhận hàng"),
        ('online',"thanh toán qua ngân hàng"),
    ]
    
    trangthai_choices = [
        ('pending', 'Chờ xác nhận'),
        ('confirmed', 'Đã xác nhận'),
        ('shipping', 'Đang giao hàng'),
        ('delivered', 'Đã giao'),
        ('cancelled', 'Đã hủy'),
    ]

    nguoidung = models.ForeignKey(Nguoidung,on_delete=models.CASCADE, related_name='hoadon')
    ngay_tao= models.DateTimeField(auto_now_add=True)
    dia_chi = models.CharField(max_length=255)
    phuong_thuc = models.CharField(max_length=25,choices=thanhtoan_choices,default='cod')
    trang_thai = models.CharField(max_length=25,choices=trangthai_choices,default='pending')
    phi_ship = models.DecimalField(max_digits=100,decimal_places=2,default=30000)
    tong_tien = models.DecimalField(max_digits=100,decimal_places=2,default=0)

    def tongcong(self):
        return self.tong_tien + self.phi_ship
    
    def __str__(self):
        return f"Đơn hàng #{self.id} - {self.nguoidung.username }"

class Chitiethoadon(models.Model):
    hoa_don = models.ForeignKey(Hoadon,on_delete=models.CASCADE, related_name='cthd')
    size_sanpham = models.ForeignKey(SizeSanPham,on_delete=models.CASCADE)
    so_luong = models.PositiveIntegerField(default=1)
    don_gia = models.DecimalField(max_digits=12, decimal_places=2)

    def thanhtien(self):
        return self.don_gia * self.so_luong
    

 