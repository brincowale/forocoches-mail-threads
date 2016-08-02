# Forocoches mail
Envío de hilos destacados de Forocoches por mail de las categorías: general, informática, empleo y viajes.  
Recibe hilos cuyo título contenga: +prv, +hd, gratis, chollo.  
Recibe hilos con 5 estrellas.  
Evita hilos que contengan: +18, tema serio, tocho.

## Requisitos
* Python 2.7
* [Grab](https://github.com/lorien/grab)
* [Mailgun](http://www.mailgun.com/)
* [Pymongo](https://pypi.python.org/pypi/pymongo)
* [MongoDB](https://www.mongodb.org/)
* [Requests](http://docs.python-requests.org/en/master/)

## Instrucciones
1. Renombrar archivo _forocoches_config.py.sample_ a _forocoches_config.py_
2. Instalar dependencias y MongoDB
3. Crear cuenta en [Mailgun](http://www.mailgun.com/) para obtener una key
4. Configurar _forocoches_config.py_ con la URI de MongoDB y Mailgun para enviar mails
5. El script requiere la base de datos _forocoches_ y una tabla _threads_
