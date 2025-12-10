from django.urls import path
from shoes import views 


urlpatterns = [
    path('gioithieu/',views.gioithieu,name='gt'),
    path('',views.index,name='tc'),
    path('hang/<int:id_ncc>/',views.chitiethang,name='cth'),
    path('more/<str:tendm>/<int:idncc>',views.more,name='mr'),
    path('dangky/',views.dangky,name='dk'),
    path('verify-otp/<int:user_id>/', views.otp, name='xac_thuc_otp'),
    path('dangnhap/',views.dangnhap,name='dn'),
    path('dangxuat/',views.dangxuat,name='dx'),
    path('chitiet/<str:masp>/',views.chitiet,name='ct'),
    path('timkiem/',views.timkiem,name='tk'),
    path('themsanpham/',views.themsp,name='tsp'),
    path('themdanhmuc/',views.themdanhmuc,name='tdm'),
    path('themnhacungcap/',views.themncc,name='tncc'),
    
    path('xoasanpham/<str:masp>/',views.xoasp,name='x'),
    path('suasanpham/<str:masp>/',views.suasp,name='s'),
    path('themvaogio/',views.themvaogio,name='tvg'),
    path('giohang/',views.giohang,name='gh'),
    path('xoagiohang/<int:ct_id>/',views.xoagiohang,name='xgh'),
    path('thanhtoan/',views.thanhtoan,name='tt'),
    path('donhang/',views.donhang,name='dh'),
    path('xoadonhang/<int:dh_id>',views.xoa_donhang,name='xdh'),
    path('quantri/',views.quantri,name='qt'),
    path('capnhatdonhang/<int:order_id>',views.capnhattrangthai,name='cn'),

    path('quanlydanhmuc/',views.quanly_dm,name='qldm'),
    path('quanlysanpham/',views.quanly_sp,name='qlsp'),
    path('quanlynhacungcap/',views.quanly_ncc,name='qlncc'),
    path('quanlynguoidung/',views.quanly_nd,name='qlnd'),

    path('xoadanhmuc/<int:dm_xoa>',views.xoa_dm,name='xdm'),
    path('xoanhacungcap/<int:ncc_xoa>',views.xoa_ncc,name='xncc'),
     path('xoadanhmuc/<int:dm_xoa>',views.xoa_dm,name='xdm'),
    path('xoanguoidung/<int:nd_xoa>',views.xoa_nd,name='xnd'),
]
