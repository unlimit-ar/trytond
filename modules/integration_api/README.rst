Integration API
===============

El modulo ``integration_api`` agrega integraciones HTTP configurables y
asincronicas para Tryton 8.0.

Permite definir endpoints externos que se ejecutan automaticamente cuando se
crean, modifican o eliminan registros de un modelo de Tryton. Cada endpoint
indica el modelo, el evento, la URL, el metodo HTTP, los encabezados, el cuerpo
del request, una condicion opcional, el timeout y la cantidad de reintentos.

Funcionamiento
--------------

Al registrar el modulo se parchean los metodos ``create``, ``write`` y
``delete`` de ``ModelSQL``. Cuando ocurre uno de esos eventos, el modulo busca
endpoints activos de ``integration.endpoint`` cuyo ``model_name`` coincida con
el nombre tecnico del modelo y cuyo ``event`` sea ``create``, ``write`` o
``delete``.

Si el endpoint tiene una condicion, esta se evalua antes de encolar la
integracion. Cuando la condicion es verdadera, la ejecucion se envia a la cola
de Tryton y el request HTTP se realiza de forma asincronica.

Los modelos internos de integracion, y los modelos que empiezan con ``ir.`` o
``res.``, no disparan integraciones para evitar ciclos y llamadas no deseadas
sobre datos base del sistema.

Configuracion de endpoints
--------------------------

Los endpoints se administran desde el menu ``Integrations``. Un endpoint tiene
estos campos principales:

``Name``
    Nombre descriptivo de la integracion.

``Model Name``
    Nombre tecnico del modelo que dispara el endpoint, por ejemplo
    ``party.party`` o ``sale.sale``.

``Event``
    Evento que dispara la llamada: ``create``, ``write`` o ``delete``.

``URL``
    URL destino. Se renderiza como plantilla Jinja2.

``Method``
    Metodo HTTP. Puede ser ``GET``, ``POST``, ``PUT``, ``PATCH`` o ``DELETE``.
    El valor por defecto es ``POST``.

``Headers Template``
    Plantilla Jinja2 que debe renderizar un objeto JSON. Si se deja vacia, se
    usan encabezados vacios.

``Payload Template``
    Plantilla Jinja2 para el cuerpo o parametros del request. Si renderiza JSON,
    el modulo lo decodifica antes de enviarlo.

``Condition Expression``
    Expresion Python opcional. Si esta vacia, el endpoint siempre se ejecuta.
    Si existe, debe devolver un valor verdadero para que se encole la llamada.

``Timeout``
    Timeout del request en segundos. El valor por defecto es ``30``.

``Retry Count``
    Cantidad de reintentos cuando falla la llamada. El valor por defecto es
    ``0``.

Plantillas y contexto
---------------------

La URL, los encabezados y el payload se renderizan con Jinja2 usando
``StrictUndefined``. Esto hace que una variable inexistente produzca error en
lugar de renderizarse silenciosamente.

Las plantillas y condiciones reciben este contexto:

``record``
    Registro que disparo la integracion. En eventos ``delete`` es una captura
    de los datos del registro antes de eliminarlo.

``user``
    Usuario actual de la transaccion, cuando esta disponible.

``company``
    Compania actual del contexto, cuando esta disponible y el modulo de
    companias esta instalado.

``datetime``, ``date`` y ``time``
    Clases de Python disponibles para construir fechas u horas.

``config``
    Acceso por atributo a parametros de ``ir.config_parameter`` con prefijo
    ``integration_api.``. Por ejemplo, ``config.token`` lee el parametro
    ``integration_api.token``.

Ejemplos
--------

Ejemplo de URL:

.. code-block:: jinja

   https://api.example.com/customers/{{ record.id }}

Ejemplo de encabezados:

.. code-block:: json

   {
     "Content-Type": "application/json",
     "Authorization": "Bearer {{ config.token }}"
   }

Ejemplo de payload:

.. code-block:: json

   {
     "id": {{ record.id }},
     "name": "{{ record.rec_name }}"
   }

Ejemplo de condicion:

.. code-block:: python

   record.active and record.id

Ejecucion HTTP
--------------

Para metodos ``GET`` y ``DELETE``, si el payload renderizado es un objeto JSON,
se envia como parametros de query. Para ``POST``, ``PUT`` y ``PATCH``, si el
payload es un objeto o una lista JSON, se envia como JSON. En los demas casos se
envia como datos planos.

La llamada se considera exitosa cuando ``requests`` no levanta error y el
servidor responde con un estado HTTP exitoso. Errores de red, timeouts, errores
HTTP, errores de plantillas y JSON invalido generan un log fallido y, si
corresponde, un nuevo intento.

Logs
----

Cada ejecucion crea un registro en ``integration.log`` con:

* endpoint ejecutado;
* modelo y registro de origen;
* fecha de ejecucion;
* URL, metodo, encabezados y payload enviados;
* estado, encabezados y cuerpo de la respuesta;
* tiempo de ejecucion;
* indicador de exito;
* mensaje de error, si lo hubo.

Los logs se crean con usuario ``0`` para asegurar que queden registrados aunque
el usuario que disparo el evento no tenga permisos de escritura sobre el modelo
de logs.

Prueba manual
-------------

Desde el formulario de un endpoint se puede ejecutar la accion ``Test
Integration``. El asistente pide un ``Record ID`` del modelo configurado,
evalua la condicion del endpoint para ese registro y encola la integracion si
la condicion es verdadera.

Seguridad
---------

El modulo crea el grupo ``Integration Administration``. Solo los usuarios de
ese grupo pueden crear, modificar y eliminar endpoints. Tambien pueden consultar
los logs, pero los logs no se pueden crear, modificar ni eliminar manualmente
desde la interfaz.

Dependencias
------------

El paquete depende de:

* ``trytond>=8.0,<8.1``;
* ``Jinja2``;
* ``requests``.

Consideraciones
---------------

Las condiciones se evaluan como expresiones Python con ``__builtins__``
deshabilitado, pero siguen siendo configuracion tecnica. Deben ser mantenidas
por usuarios administradores de confianza.

Los eventos ``delete`` usan una captura serializable del registro porque el
registro original ya no existe cuando se ejecuta la llamada asincronica.
