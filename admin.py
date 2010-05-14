#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.contrib import admin
from .models import *


admin.site.register(Commodity)
admin.site.register(Cargo)
admin.site.register(Shipment)
admin.site.register(ShipmentRoute)
admin.site.register(ShipmentSighting)
