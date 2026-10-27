import os
import sys
import pytest
from decimal import Decimal
from cargar_csv import load_fixture
from app.domain import (
    DomainException,
    InvalidOrderData,
    InvalidOrderTransition,
    OrderItemLimitExceeded,
    Money,
    OrderItem,
)
from app.specifications import discount_rule

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def test_money_negativo():
    with pytest.raises(InvalidOrderData):
        Money(Decimal("-1"))

def test_pedido_o001_inicia_draft():
    orders = load_fixture()
    assert orders["O001"].status.value == "DRAFT"
    assert orders["O001"].units == 4
    assert orders["O001"].total.amount == Decimal("2100.00")

def test_confirmacion_doble():
    orders = load_fixture()
    order = orders["O013"]
    order.confirm()
    with pytest.raises(InvalidOrderTransition):
        order.confirm()

def test_cancelacion_desde_shipped():
    orders = load_fixture()
    order = orders["O013"]
    order.confirm()
    order.ship("TRK-999")
    with pytest.raises(InvalidOrderTransition):
        order.cancel("Intento cancelar enviado")

def test_escenario_e01():
    orders = load_fixture()
    order = orders["O001"]
    print(f"\n[E01] ID: {order.id} | Estado: {order.status} | Unidades: {order.units} | Total: {order.total.amount}")
    resultado = discount_rule.is_satisfied_by(order)
    precio_original = order.total.amount
    precio_final = precio_original * Decimal("0.90") if resultado else precio_original
    print(f"[E01 RESULTADO] ¿Aplica 10%?: {resultado} | Precio con descuento aplicado: {precio_final}")
    assert resultado is True

def test_escenario_e02():
    orders = load_fixture()
    order = orders["O002"]
    print(f"\n[E02] ID: {order.id} | Estado: {order.status} | Total: {order.total.amount}")
    resultado = discount_rule.is_satisfied_by(order)
    print(f"[E02 RESULTADO] ¿Aplica descuento?: {resultado}")
    assert resultado is False

def test_escenario_e03():
    orders = load_fixture()
    order = orders["O003"]
    print(f"\n[E03] ID: {order.id} | Cliente activo: {order.customer.active}")
    with pytest.raises((DomainException, InvalidOrderData)):
        order.confirm()
    print("[E03 RECHAZO] Bloqueado correctamente por cliente inactivo.")

def test_escenario_e04():
    orders = load_fixture()
    order = orders["O005"]
    print(f"\n[E04] ID: {order.id} | Promo activa: {order.has_promotion}")
    resultado = discount_rule.is_satisfied_by(order)
    print(f"[E04 RESULTADO] ¿Aplica descuento?: {resultado}")
    assert resultado is False

def test_escenario_e05():
    orders = load_fixture()
    order = orders["O006"]
    print(f"\n[E05] ID: {order.id} | Total: {order.total.amount} | Promo: {order.has_promotion}")
    resultado = discount_rule.is_satisfied_by(order)
    precio_original = order.total.amount
    precio_final = precio_original * Decimal("0.95") if resultado else precio_original
    print(f"[E05 RESULTADO] ¿Aplica 5%?: {resultado} | Precio con descuento aplicado: {precio_final}")
    assert resultado is True

def test_escenario_e06():
    orders = load_fixture()
    order = orders["O007"]
    print(f"\n[E06] ID: {order.id} | Unidades de artículos: {len(order.items)}")
    with pytest.raises((DomainException, InvalidOrderData)):
        order.confirm()
    print("[E06 RECHAZO] Bloqueado por pedido sin artículos.")

def test_escenario_e07():
    orders = load_fixture()
    order = orders["O008"]
    print(f"\n[E07] ID: {order.id} | Unidades: {order.units}")
    order.confirm()
    print(f"[E07 ÉXITO] Estado final: {order.status} | Eventos: {[e.name for e in order.events]}")
    assert order.status.value == "CONFIRMED"

def test_escenario_e08():
    orders = load_fixture()
    order = orders["O009"]
    print(f"\n[E08] ID: {order.id} | Unidades: {order.units}")
    item_extra = OrderItem(sku="SKU999", quantity=2, unit_price=Money(Decimal("100.00")))
    with pytest.raises((DomainException, InvalidOrderData, OrderItemLimitExceeded)):
        order.add_item(item_extra)
    unidades_intentadas = order.units + item_extra.quantity
    print(f"[E08 RECHAZO] Intento fallido al pasar de {order.units} a {unidades_intentadas} unidades (supera el límite de 20).")

def test_escenario_e09():
    orders = load_fixture()
    order = orders["O010"]
    print(f"\n[E09] ID: {order.id} | Total (umbral estricto): {order.total.amount}")
    resultado = discount_rule.is_satisfied_by(order)
    print(f"[E09 RESULTADO]: {resultado}")
    assert resultado is False

def test_escenario_e10():
    orders = load_fixture()
    order = orders["O011"]
    print(f"\n[E10] ID: {order.id} | Unidades: {order.units} (menor a 4)")
    resultado = discount_rule.is_satisfied_by(order)
    print(f"[E10 RESULTADO]: {resultado}")
    assert resultado is False

def test_escenario_e11():
    orders = load_fixture()
    order = orders["O012"]
    print(f"\n[E11] ID: {order.id} | Intentando enviar sin guía")
    order.confirm()
    with pytest.raises((DomainException, InvalidOrderData, InvalidOrderTransition)):
        order.ship("")
    print("[E11 RECHAZO] Bloqueado por falta de guía de envío.")

def test_escenario_e12():
    orders = load_fixture()
    order = orders["O013"]
    print(f"\n[E12] ID: {order.id} | Doble confirmación")
    order.confirm()
    with pytest.raises((DomainException, InvalidOrderTransition)):
        order.confirm()
    print("[E12 RECHAZO] No permite re-confirmar un pedido ya confirmado.")

def test_escenario_e13():
    orders = load_fixture()
    order = orders["O014"]
    print(f"\n[E13] ID: {order.id} | Intento cancelar desde SHIPPED")
    order.confirm()
    order.ship("TRK-999")
    with pytest.raises((DomainException, InvalidOrderTransition)):
        order.cancel("Intento cancelar enviado")
    print(f"[E13 RECHAZO] Bloqueado correctamente. Estado actual: {order.status}")
    assert order.status.value == "SHIPPED"

def test_escenario_e14():
    orders = load_fixture()
    order = orders["O015"]
    print(f"\n[E14] ID: {order.id} | Flujo de Devolución")
    order.confirm()
    order.ship("TRK-888")
    order.return_order()
    print(f"[E14 ÉXITO] Estado final: {order.status} | Eventos: {[e.name for e in order.events]}")
    assert order.status.value == "RETURNED"

def test_escenario_e15():
    orders = load_fixture()
    order = orders["O016"]
    print(f"\n[E15] ID: {order.id} | Flujo de Entrega")
    order.confirm()
    order.ship("TRK-777")
    order.deliver()
    print(f"[E15 ÉXITO] Estado final: {order.status} | Eventos: {[e.name for e in order.events]}")
    assert order.status.value == "DELIVERED"