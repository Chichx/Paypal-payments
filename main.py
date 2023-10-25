from flask import Flask, render_template, request, redirect, url_for
import paypalrestsdk as paypal
from paypalrestsdk import *

app = Flask(__name__)

paypal.configure({
    "mode": "live", # Aca hay 2 opciones: sandbox (Sandbox sirve para testear, es decir pagos falsos) o live (Ya son pagos reales)
    "client_id": "",
    "client_secret": ""
})

productos = [
    {
        "id": "1",
        "nombre": "Producto #1",
        "precio": 12.00,
        "descripcion": "Lorem ipsum dolor sit amet. (Producto #1)",
        "type": "autos"
    },
    {
        "id": "2",
        "nombre": "Producto #2",
        "precio": 10.00,
        "descripcion": "Lorem ipsum dolor sit amet. (Producto #2)",
        "type": "motos"
    },
    {
        "id": "3",
        "nombre": "Producto #3",
        "precio": 29.00,
        "descripcion": "Lorem ipsum dolor sit amet. (Producto #3)",
        "type": "autos"
    },
    {
        "id": "4",
        "nombre": "Producto #4",
        "precio": 29.00,
        "descripcion": "Lorem ipsum dolor sit amet. (Producto #4)",
        "type": "motos"
    },
        {
        "id": "5",
        "nombre": "Producto #5",
        "precio": 59.99,
        "descripcion": "Lorem ipsum dolor sit amet. (Producto #5)",
        "type": "autos"
    },
    {
        "id": "6",
        "nombre": "Producto #6",
        "precio": 79.99,
        "descripcion": "Lorem ipsum dolor sit amet. (Producto #6)",
        "type": "motos"
    }
]

@app.route("/")
def index():
    return render_template("index.html", productos=productos)

@app.route("/payment", methods=["POST"])
def payment():
    producto_id = request.form["product_id"]
    producto_seleccionado = next((p for p in productos if p["id"] == producto_id), None)

    if producto_seleccionado:
        payment = paypal.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": url_for("success", _external=True),
                "cancel_url": url_for("cancel", _external=True)
            },
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": producto_seleccionado["nombre"],
                        "sku": producto_seleccionado["id"],
                        "price": producto_seleccionado["precio"],
                        "currency": "USD",
                        "quantity": 1
                    }]
                },
                "amount": {
                    "total": producto_seleccionado["precio"],
                    "currency": "USD"
                },
                "description": producto_seleccionado["descripcion"]
            }]
        })

        if payment.create():
            for link in payment.links:
                if link.rel == "approval_url":
                    return redirect(link.href)
        else:
            return "Error al crear el pago con PayPal"
    else:
        return "Producto no encontrado"

@app.route("/success")
def success():
    payment_id = request.args.get("paymentId")
    payer_id = request.args.get("PayerID")

    payment = paypal.Payment.find(payment_id)
    if payment.execute({"payer_id": payer_id}):
        return "Pago exitoso"
    else:
        return "Error al procesar el pago con PayPal"

@app.route("/cancel")
def cancel():
    return "Compra cancelada"

if __name__ == "__main__":
    app.run(debug=True)
