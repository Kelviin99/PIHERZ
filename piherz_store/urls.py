from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('producto/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
    path('agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito_simple'),
    path('agregar-al-carrito/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('remover/<int:producto_id>/', views.remover_del_carrito, name='remover_del_carrito'),
    path('actualizar/<int:producto_id>/', views.actualizar_carrito, name='actualizar_carrito'),
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro_view, name='registro'),
    path('logout/', views.logout_view, name='logout'),
    path('mis-compras/', views.mis_compras, name='mis_compras'),
    path('api/carrito-cantidad/', views.obtener_carrito_cantidad, name='obtener_carrito_cantidad'),
    path('checkout/', views.checkout, name='checkout'),
    path('pedidos/', views.historial_pedidos, name='historial_pedidos'),
    path('pedido/<int:pedido_id>/', views.detalle_pedido, name='detalle_pedido'),
    path('pedido-exito/', views.pedido_exito, name='pedido_exito'),
    path('perfil/', views.perfil_usuario, name='perfil_usuario'),
    path('agregar-direccion/', views.agregar_direccion, name='agregar_direccion'),
    path('cambiar-contrasena/', views.cambiar_contrasena, name='cambiar_contrasena'),
    path('producto/<int:producto_id>/agregar-resena/', views.agregar_resena, name='agregar_resena'),
    path('lista-deseos/', views.lista_deseos, name='lista_deseos'),
    path('producto/<int:producto_id>/agregar-deseos/', views.agregar_a_lista_deseos, name='agregar_a_lista_deseos'),
    path('producto/<int:producto_id>/quitar-deseos/', views.quitar_de_lista_deseos, name='quitar_de_lista_deseos'),
    path('contacto/', views.contacto, name='contacto'),
    path('sobre-nosotros/', views.sobre_nosotros, name='sobre_nosotros'),
    path('terminos-condiciones/', views.terminos_condiciones, name='terminos_condiciones'),
    path('politica-privacidad/', views.politica_privacidad, name='politica_privacidad'),
    path('newsletter/suscribir/', views.suscribir_newsletter, name='suscribir_newsletter'),
    # Sistema de recuperación de contraseña
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='piherz_store/password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='piherz_store/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='piherz_store/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='piherz_store/password_reset_complete.html'), name='password_reset_complete'),
]